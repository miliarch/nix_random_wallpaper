# Gnome Random Wallpaper

A simple program that sets random wallpaper images as desktop backgrounds in Gnome based window managers. It fetches images from a local directory or Unsplash, composes a new image to match display size and arrangement, and sets the new image as the desktop background.

![Example Arrangement](example_arrangement.png)
![Example Wallpaper](example_wallpaper.jpg)

## Configuration

Default configuration can be found in [gnome_random_wallpaper/config.yaml](gnome_random_wallpaper/config.yaml). This file can be copied to `$HOME/.config/gnome_random_wallpaper/config.yaml` and modified to override the defaults.

## Supported display configurations

Any number of displays that are arranged horizontally (side-by-side) within the vertical (height) bounds of the largest display should be supported.

## Unsupported configurations

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
