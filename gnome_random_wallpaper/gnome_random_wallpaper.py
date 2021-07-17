#!/usr/bin/env python3
import yaml
from datetime import datetime
from io import BytesIO
from os import environ
from pathlib import Path
from PIL import Image
from random import choice
from requests import get
from shutil import move, copy
from subprocess import run
from sys import exit
from time import sleep

# Path configuration
BASE_DIR = Path(__file__).resolve().parents[0]
USER_HOME_PATH = Path.home()
CONFIG_DIR = Path(f"{USER_HOME_PATH}/.config/gnome_random_wallpaper")
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = Path(f'{CONFIG_DIR}/config.yaml')

try:
    with open(CONFIG_FILE, 'r') as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)
except IOError:
    # Config file doesn't exist - load the default
    with open(BASE_DIR.joinpath('config.yaml'), 'r') as f:
        CONFIG = yaml.load(f, Loader=yaml.FullLoader)

# Unsplash configuration
UNSPLASH = CONFIG['unsplash']
UNSPLASH_COLLECTIONS = CONFIG['unsplash_collections']
UNSPLASH_MAX_RESOLUTION_W = CONFIG['unsplash_resolution_w']
UNSPLASH_MAX_RESOLUTION_H = CONFIG['unsplash_resolution_h']
UNSPLASH_ORIENTATION = CONFIG['unsplash_orientation']

# File path configuration
IMAGES_DIR = Path(CONFIG['images_dir']) if CONFIG['images_dir'] else None
IMAGE_FORMAT = CONFIG['output_image_format']
OUTPUT_DIR = Path(CONFIG['output_dir'])
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
TEMP_FILE = Path(f'{OUTPUT_DIR}/{TIMESTAMP}.{IMAGE_FORMAT}')
OUTPUT_FILE = Path(f'{OUTPUT_DIR}/{CONFIG["output_image_name"]}')

# Ensure provided IMAGES_DIR, if specified, exists
if IMAGES_DIR:
    if not IMAGES_DIR.exists() or not IMAGES_DIR.is_dir():
        help_str = f"IMAGES_DIR is invalid: {IMAGES_DIR}"
        exit(help_str)
elif not UNSPLASH:
    help_str = "No file source specified, check configuration"
    exit(help_str)


class Display:
    def __init__(self, resolution, offset_w, offset_h):
        self.resolution_w, self.resolution_h = map(int, resolution.split('x'))
        self.offset_w = int(offset_w)
        self.offset_h = int(offset_h)


def calculate_crop_box(display, image):
    top_left = 0
    top_right = 0
    bottom_right = display.resolution_w
    bottom_lower = display.resolution_h

    if display.resolution_w < image.width:
        excess = image.width - display.resolution_w
        top_left = int(excess / 2)
        bottom_right = display.resolution_w + (int(excess / 2) + excess % 2)

    if display.resolution_h < image.height:
        excess = image.height - display.resolution_h
        top_right = int(excess / 2)
        bottom_lower = display.resolution_h + (int(excess / 2) + excess % 2)

    return (top_left, top_right, bottom_right, bottom_lower)


def calculate_proportional_dimensions(display, image):
    adjusted_width = int(display.resolution_h * image.width / image.height)
    adjusted_height = int(display.resolution_w * image.height / image.width)

    if adjusted_height < display.resolution_h:
        # Return size based on display height - adjusted image width is
        # too small to fill display
        return (adjusted_width, display.resolution_h)
    # Return size based on display width in the common case
    return (display.resolution_w, adjusted_height)


def get_unsplash_image(resolution_w=UNSPLASH_MAX_RESOLUTION_W,
                       resolution_h=UNSPLASH_MAX_RESOLUTION_H,
                       collections=UNSPLASH_COLLECTIONS,
                       orientation=UNSPLASH_ORIENTATION):
    endpoint = 'https://source.unsplash.com/random'
    resolution = f'{resolution_w}x{resolution_h}'
    orientation = f'orientation={orientation}'
    collections = f'&{",".join(collections)}'
    url = f'{endpoint}/{resolution}?{orientation}{collections}'
    response = get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))


def select_random_child_path(parent_path):
    return str(choice([x for x in Path(parent_path).glob('*')]))


def main():
    # Identify PID of gnome session
    cmd_str = 'pgrep -f "gnome-session" | head -n1'
    cmd = run(cmd_str, shell=True, capture_output=True)
    pid = int(cmd.stdout.decode('utf-8').replace('\n', ''))

    # Get DBUS_SESSION_BUS_ADDRESS from environment
    cmd_str = f'grep -z DBUS_SESSION_BUS_ADDRESS /proc/{pid}/environ|cut -d= -f2-'
    cmd = run(cmd_str, shell=True, capture_output=True)
    dbus_sba = cmd.stdout.decode('utf-8').replace('\n', '').replace('\x00', '')

    # Configure environment
    env = environ.copy()
    env['DISPLAY'] = ':0'
    env['DBUS_SESSION_BUS_ADDRESS'] = dbus_sba

    # Capture display resolution and arrangement information
    cmd_str = 'xrandr | grep " connected"'
    cmd = run(cmd_str, env=env, shell=True, capture_output=True)
    displays_raw = cmd.stdout.decode('utf-8').split('\n')[0:-1]

    # Generate list of Display object instances
    displays = []
    for dr in displays_raw:
        if 'primary' in dr:
            dimensions = dr.split(' ')[3]
        else:
            dimensions = dr.split(' ')[2]
        displays.append(Display(*dimensions.split('+')))

    # Sort displays by offset_w (arrangement based on offset, left to right)
    displays.sort(key=lambda x: x.offset_w)

    # Assume a horizontal layout - sum width, largest height - sorry future me
    total_width = sum([d.resolution_w for d in displays])
    total_height = max(displays, key=lambda x: x.resolution_h).resolution_h

    # Stage canvas Image object
    canvas = Image.new('RGB', (total_width, total_height))

    # Stage Image objects for composition
    if UNSPLASH:
        # Fetch unsplash images
        images = []
        for idx, display in enumerate(displays):
            image = get_unsplash_image(
                resolution_w=display.resolution_w,
                resolution_h=display.resolution_h)
            images.append(image)
            if idx < len(displays) - 1:
                # Slow down between requests - unsplash rate limits
                sleep(1)
    else:
        # Fetch random image paths
        image_paths = []
        for i in range(len(displays)):
            image_paths.append(select_random_child_path(IMAGES_DIR))
        images = [Image.open(ip) for ip in image_paths]

    # Process images
    for display in displays:
        image = images.pop(0)
        new_dimensions = calculate_proportional_dimensions(display, image)
        image = image.resize(new_dimensions)
        image = image.crop(box=calculate_crop_box(display, image))
        canvas.paste(image, (display.offset_w, display.offset_h))

    # Save canvas to temp file
    canvas.save(TEMP_FILE, format=IMAGE_FORMAT)

    # Copy temp file to output file (initial image write is slow)
    move(TEMP_FILE, OUTPUT_FILE)

    # Set newly generated image as background
    cmd_list = [
        'gsettings',
        'set',
        'org.gnome.desktop.background',
        'picture-uri',
        f'file://{str(OUTPUT_FILE)}'
    ]
    cmd = run(cmd_list, env=env, capture_output=True)


if __name__ == '__main__':
    main()
