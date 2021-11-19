# Gnome Random Wallpaper

A simple program that sets random wallpaper images as desktop backgrounds in Gnome based window managers. It fetches images from a local directory or Unsplash, composes a new image to match display size and arrangement, and sets the new image as the desktop background.

**Example arrangement**

![Example Arrangement](example_arrangement.png)

**Example wallpaper**

![Example Wallpaper](example_wallpaper.jpg)

## Usage

Gnome Random Wallpaper (`grw`) currently makes the following assumptions about the user:
* The user will configure some external scheduler to prompt the `grw` command to run in the background
* The user doesn't usually want to keep the generated wallpaper images forever
  * The last image that was generated is replaced by the newly generated image
  * The default output directory is `/tmp/random` - `/tmp` is commonly a tmpfs filesystem and exists only in memory (while the system remains powered on)
    * Note: The default output directory can and probably should be changed to a non-volatile location in [configuration](#configuration). Specifying a non-volatile directory will prevent temporary auto-selection of a system default wallpaper by the window manager on login after a fresh boot cycle, which can be disorienting.
* The user won't interact directly with the program often, making command line argument support unnecessary

Simply running `grw` will fetch images from either the [Unsplash API](https://source.unsplash.com/) or the image directory (`images_dir`) defined in configuration, resize and compose the images on a spanned canvas matching your current display arrangement, save the resulting wallpaper image to the output directory (`output_dir`), and update your desktop background.

Some suggested steps to take in your environment:
* Configure a cron job or timer of some sort to run `grw` at regular intervals (every 15 minutes works well for me - `*/15 * * * * /path/to/grw`)
* Configure a Startup Application to run `grw` on login

## Installation

Install with pip using a command like:
```
pip install git+https://github.com/miliarch/gnome_random_wallpaper.git
```

After installation, a `grw` executable link should be placed in your `$HOME/.local/bin` directory (this may vary depending on distro). If this directory is included in your PATH environment variable, the `grw` command should be available for use without any further steps. Otherwise, you'll need to either specify the full path to run the program, or add the `$HOME/.local/bin` directory to your PATH environment variable.

Alternatively, clone this repository to your preferred installation directory and manually link `./gnome_random_wallpaper/gnome_wallpaper.py` in the execution directory of your choice.

## Configuration

Default configuration can be found in [gnome_random_wallpaper/config.yaml](gnome_random_wallpaper/config.yaml). This file can copied to `$HOME/.config/gnome_random_wallpaper/config.yaml` and modified to override the default options.

Each configuration option in the file includes an in-line comment that details its function. If you have any questions about how existing options behave, or requests for new options, please raise an issue in this repository.

## Supported display configurations

Any number of displays that are arranged horizontally (side-by-side) within the vertical (height) bounds of the largest display should be supported.

## Unsupported display configurations

Vertical arrangements, including mixed vertical/horizontal arrangements, are currently unsupported. Support may be implemented in the future.

## Tested configurations

### Window managers

* Cinnamon 5.0.5

### Resolutions
* 1920x1080
* 2560x1440
* 3840x2160

### Display arrangements
* Dual monitor, landscape orientation, horizontal arrangement (side-by-side)
