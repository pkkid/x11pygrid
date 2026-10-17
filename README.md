# x11pygrid

Snap, tile and resize X11 windows to a grid with numpad shortcuts, across one or many monitors.

[![PyPI](https://img.shields.io/pypi/v/x11pygrid)](https://pypi.org/project/x11pygrid/) [![Python](https://img.shields.io/pypi/pyversions/x11pygrid)](https://pypi.org/project/x11pygrid/) [![License: GPL v2](https://img.shields.io/pypi/l/x11pygrid)](https://github.com/pkkid/x11pygrid/blob/master/LICENSE.txt)

<p align="center">
  <img src="https://raw.githubusercontent.com/pkkid/x11pygrid/master/docs/images/hero.svg" alt="Animation: holding Ctrl+Alt and pressing numpad 4 snaps a window to the left third of the screen, pressing 4 again widens it to two thirds, 9 moves it to the top right, and 0 maximizes it." width="760">
</p>

Floating window managers leave you dragging window edges around by hand, and switching to a full tiling window manager is a big commitment. x11pygrid sits in the background of your existing X11 desktop (Xfce, MATE, Cinnamon, Openbox and friends) and gives it keyboard tiling: focus a window, hold <kbd>Ctrl</kbd>+<kbd>Alt</kbd>, and press the numpad key that matches where you want it. Press the same key again to cycle through sizes. It began as a fork of [QuickTile](https://github.com/ssokolow/quicktile) and was rewritten around one small JSON config file.

## Features

- **One keystroke per position**: the 3×3 numpad maps directly onto the screen.
- **Press again to cycle sizes**: tap <kbd>4</kbd> to snap left, then tap again to switch between ⅓ and ⅔ width.
- **Your grid, your rules**: choose the number of columns, and padding between windows.
- **Multi-monitor aware**: per-monitor settings, a key to send a window to the next monitor.
- **Edits apply instantly**: layout and config settings are re-read on every keypress.
- **Fits any keyboard**: rebind to number-row keys, letters, or any other modifier.
- **Tiny and unobtrusive**: a single Python file that runs in the background.

## Quick Start

On Ubuntu or Debian, in an X11 session:

```bash
sudo apt install pipx python3-gi gir1.2-gtk-3.0  # Install dependancies
pipx install --system-site-packages x11pygrid    # Install PyGrid
x11pygrid                                        # Run PyGrid
```

Make sure <kbd>Num Lock</kbd> is on, click any window, and press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 4</kbd>. The window snaps to the left edge of the screen; press it again to switch between ⅓ and ⅔ width.

## Installation

### Requirements

1.  An **X11 session**. Wayland is not supported; `echo $XDG_SESSION_TYPE` should print `x11`.
2. **Python 3.6+** with **PyGObject** and **GTK 3**.

```bash
# Ubuntu / Debian
sudo apt install pipx python3-gi gir1.2-gtk-3.0
pipx install --system-site-packages x11pygrid

# Fedora
sudo dnf install pipx python3-gobject gtk3
pipx install --system-site-packages x11pygrid

# Arch Linux
sudo pacman -S python-pipx python-gobject gtk3
pipx install --system-site-packages x11pygrid

# openSUSE
sudo zypper install python3-pipx python3-gobject python3-gobject-Gdk typelib-1_0-Gtk-3_0
pipx install --system-site-packages x11pygrid

# FreeBSD (replace py311 with the prefix of your default Python version)
sudo pkg install py311-pipx py311-gobject3 gtk3
pipx install --system-site-packages x11pygrid
```

### From source

```bash
git clone https://github.com/pkkid/x11pygrid.git    # Clone the repo
cd x11pygrid                                        # Navigate into the dir
pipx install --system-site-packages .               # Install packages
```

The whole program is the single file [`src/x11pygrid/x11pygrid.py`](https://github.com/pkkid/x11pygrid/blob/master/src/x11pygrid/x11pygrid.py). You can also run it directly with `python3` as long as `gi`, `Xlib` and `single_process` are importable.

### Upgrade and uninstall

```bash
pipx upgrade x11pygrid      # Upgrade
pipx uninstall x11pygrid    # Uninstall
```

Uninstalling leaves your config at `~/.config/x11pygrid.json`; delete it if you don't want it.

## Usage

Run `x11pygrid`. It stays in the foreground, logs each window it moves, and stops with <kbd>Ctrl</kbd>+<kbd>C</kbd>. It takes no command-line options; everything is set in the [config file](#configuration). Only one copy can run at a time, so starting a second one exits immediately.

Hold <kbd>Ctrl</kbd>+<kbd>Alt</kbd> and press a key on the numeric keypad. <kbd>Num Lock</kbd> must be on.

| Shortcut                                              | Command         | What happens                                    |
|-------------------------------------------------------|-----------------|-------------------------------------------------|
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 7</kbd>       | `topleft`       | Top left corner                                 |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 8</kbd>       | `top`           | Top edge, centered horizontally                 |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 9</kbd>       | `topright`      | Top right corner                                |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 4</kbd>       | `left`          | Left edge, full height                          |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 5</kbd>       | `middle`        | Centered, full height                           |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 6</kbd>       | `right`         | Right edge, full height                         |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 1</kbd>       | `bottomleft`    | Bottom left corner                              |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 2</kbd>       | `bottom`        | Bottom edge, centered horizontally              |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 3</kbd>       | `bottomright`   | Bottom right corner                             |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num 0</kbd>       | `maximize`      | Maximize the window                             |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num Enter</kbd>   | `cycle-monitor` | Move the window to the next monitor             |
| <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>Num /</kbd>       | `max-stretch`   | Stretch the window across all monitors          |

Press the same shortcut repeatedly to cycle through every size that fits that position. With the default 3×2 grid, <kbd>Num 4</kbd> alternates between the left ⅓ and left ⅔ of the screen, and <kbd>Num 7</kbd> between the top-left ⅓ and ⅔ (both half height). The sizes on offer come from your grid and the min/max settings in the [config](#configuration).

### All commands

Any of these can be bound to a key in the config file.

| Command         | Effect                                                                       |
|-----------------|------------------------------------------------------------------------------|
| `topleft`       | Cycle sizes touching the top and left edges.                                 |
| `top`           | Cycle sizes touching the top edge, centered horizontally.                    |
| `topright`      | Cycle sizes touching the top and right edges.                                |
| `left`          | Cycle sizes touching the left edge, centered vertically.                     |
| `middle`        | Cycle sizes centered both horizontally and vertically.                       |
| `right`         | Cycle sizes touching the right edge, centered vertically.                    |
| `bottomleft`    | Cycle sizes touching the bottom and left edges.                              |
| `bottom`        | Cycle sizes touching the bottom edge, centered horizontally.                 |
| `bottomright`   | Cycle sizes touching the bottom and right edges.                             |
| `noclampleft`   | Cycle widths on the left side, keeping the window's current vertical size.   |
| `noclampright`  | Cycle widths on the right side, keeping the window's current vertical size.  |
| `noclamptop`    | Cycle heights at the top, keeping the window's current horizontal size.      |
| `noclampbottom` | Cycle heights at the bottom, keeping the window's current horizontal size.   |
| `maximize`      | Maximize the window.                                                         |
| `cycle-monitor` | Move the window to the next monitor, keeping its relative position and size. |
| `max-stretch`   | Resize the window to cover the whole X screen, spanning every monitor.       |

### What the log shows

Each move prints the grid settings, the work area and every candidate position, which helps when tuning the config:

```text
Move window 62914571 to left..
  config: xdivs=3, ydivs=2, minw=0.25, maxw=0.67, minh=0.33, maxh=0.67, padding=[0, 0, 0, 0]
  workarea: x=0 y=0 w=1920 h=1048 (monitorid:0)
  windowframe: x=412 y=230 w=900 h=600
  Seq(x1=0, x2=638, y1=0, y2=1048, w=638, h=1048); dist=1352
  Seq(x1=0, x2=1278, y1=0, y2=1048, w=1278, h=1048); dist=1468
  newpos: x=0, y=0, w=1278, h=1048 (offx:0, offy:0)
```

### Start at login

Add `x11pygrid` to your desktop's *Startup Applications* or *Autostart* settings, or create the autostart entry from a terminal:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/x11pygrid.desktop <<EOF
[Desktop Entry]
Type=Application
Name=x11pygrid
Exec=$(command -v x11pygrid)
EOF
```

This writes the full path to the program, since pipx's `~/.local/bin` is often not on the `PATH` that autostart uses. Don't start it from `cron`; it needs your X session.

## Configuration

Settings live in `~/.config/x11pygrid.json`, which is created with the defaults below the first time x11pygrid starts. The file must be plain JSON: no comments and no trailing commas.

```json
{
  "default": {
    "maxheight": 0.67,
    "maxwidth": 0.67,
    "minheight": 0.33,
    "minwidth": 0.25,
    "padding": [0, 0, 0, 0],
    "snaptocursor": false,
    "spacing": 4,
    "xdivs": 3,
    "ydivs": 2
  },
  "keys": {
    "accelerator": "<Ctrl><Mod1><Mod2>",
    "commands": {
      "KP_0": "maximize",
      "KP_1": "bottomleft",
      "KP_2": "bottom",
      "KP_3": "bottomright",
      "KP_4": "left",
      "KP_5": "middle",
      "KP_6": "right",
      "KP_7": "topleft",
      "KP_8": "top",
      "KP_9": "topright",
      "KP_Divide": "max-stretch",
      "KP_Enter": "cycle-monitor"
    }
  }
}
```

**Layout changes take effect on the next keypress. Changes to the `keys` section need a restart** of x11pygrid, because shortcuts are registered at startup.

### Layout options (`default`)

| Key            | Type          | Default        | Description                                                                                     |
|----------------|---------------|----------------|-------------------------------------------------------------------------------------------------|
| `xdivs`        | int           | `3`            | Number of columns the screen is divided into.                                                    |
| `ydivs`        | int           | `2`            | Number of rows the screen is divided into.                                                       |
| `minwidth`     | float         | `0.25`         | Smallest window width offered, as a fraction of the screen. Ignored by `top`, `middle`, `bottom`. |
| `maxwidth`     | float         | `0.67`         | Largest window width offered. Ignored by `top`, `middle`, `bottom`.                              |
| `minheight`    | float         | `0.33`         | Smallest window height offered. Ignored by `left`, `middle`, `right`.                            |
| `maxheight`    | float         | `0.67`         | Largest window height offered. Ignored by `left`, `middle`, `right`.                             |
| `padding`      | [int ×4]      | `[0, 0, 0, 0]` | Extra space in pixels to keep clear at the top, right, bottom and left of the screen.           |
| `spacing`      | int           | `4`            | Gap in pixels between neighbouring windows.                                                      |
| `snaptocursor` | bool          | `false`        | Move the window to the monitor under the mouse pointer instead of the one it's on.               |

### Per-monitor overrides

Add `monitor0`, `monitor1`, … sections next to `default` to change settings for one monitor. Anything you leave out falls back to your `default` section, then to the built-in defaults. Monitor numbers follow GTK's ordering, which usually matches `xrandr --listmonitors`. `snaptocursor` is only read from `default` and `monitor0`.

For example, to use two columns and keep 30 px clear at the top of the second monitor (alongside your existing `keys` section):

```json
"default": { "xdivs": 3, "ydivs": 2 },
"monitor1": { "xdivs": 2, "padding": [30, 0, 0, 0] }
```

### Key bindings (`keys`)

| Key           | Description                                                                                                       |
|---------------|-------------------------------------------------------------------------------------------------------------------|
| `accelerator` | Modifiers that must be held, in GTK accelerator syntax. `<Ctrl>`, `<Shift>`, `<Mod1>` (Alt), `<Mod2>` (usually Num Lock), `<Mod4>` (usually Super/Windows). |
| `commands`    | Map of key name to [command](#all-commands). Key names are [GDK keysym names](https://gitlab.gnome.org/GNOME/gtk/-/blob/gtk-3-24/gdk/gdkkeysyms.h) without the `GDK_KEY_` prefix, such as `KP_1`, `KP_Enter`, `1`, `a`, `Return`, `F5`. |

Things to know:

- The modifiers must match **exactly**, including lock keys. The default includes `<Mod2>` because Num Lock is on; if you keep Num Lock off, drop `<Mod2>`. Run `xmodmap -pm` to see which keys your system assigns to each modifier.
- Use `<Mod4>` for the Super/Windows key; `<Super>` does not work.
- The `keys` section is not merged with the defaults. If you change it, keep the whole block, `accelerator` and all.

### Recipes

<details>
<summary>Laptop without a numpad: Alt+Super with the number row</summary>

```json
"keys": {
  "accelerator": "<Mod1><Mod4>",
  "commands": {
    "1": "bottomleft", "2": "bottom", "3": "bottomright",
    "4": "left",       "5": "middle", "6": "right",
    "7": "topleft",    "8": "top",    "9": "topright",
    "0": "maximize",
    "Return": "cycle-monitor"
  }
}
```

Add `<Mod2>` to the accelerator if you normally have Num Lock on.
</details>

<details>
<summary>Cycle widths through ⅓ → ½ → ⅔</summary>

Use six columns so halves and thirds both line up with the grid, and keep the default width limits:

```json
"default": {
  "xdivs": 6,
  "minwidth": 0.33,
  "maxwidth": 0.67
}
```
</details>

<details>
<summary>Leave room for a panel or dock</summary>

x11pygrid already respects the work area your window manager reports. If a panel isn't accounted for, reserve the space yourself, here 32 px at the top:

```json
"default": { "padding": [32, 0, 0, 0] }
```
</details>

## Troubleshooting

**The shortcuts do nothing.**
Check three things: that you're in an X11 session (`echo $XDG_SESSION_TYPE` prints `x11`, not `wayland`); that Num Lock is on, since the default accelerator includes `<Mod2>`; and that x11pygrid is still running. Watch its terminal output while pressing a shortcut; every move is logged.

**Startup fails with `Xlib.error.BadAccess`.**
Another program already owns one of the key combinations. Remove the clashing shortcut in your desktop's keyboard settings, or choose a different `accelerator` in the config.

**Startup fails with `KeyError: 'keys'` or `KeyError: 'commands'`.**
The config file isn't valid JSON (look for an `Unable to parse userconfig` line just above), or the `keys` section is missing. Fix the JSON, or delete the file and restart to get fresh defaults.

**`pipx install` fails building PyGObject** (`Dependency 'gobject-introspection-1.0' is required but not found`).
Either install your distro's PyGObject and use `pipx install --system-site-packages x11pygrid` ([recommended](#recommended-pipx-with-your-distros-pygobject)), or install the [build dependencies](#alternative-pipx-building-pygobject-from-source) first.

**Some windows end up a few pixels off.**
Apps that draw their own title bars and shadows (many GTK and Qt programs) report their frame size differently, so they can land slightly off-grid. These are known issues ([#1](https://github.com/pkkid/x11pygrid/issues/1), [#37](https://github.com/pkkid/x11pygrid/issues/37)).

**I'm upgrading from the old `pygrid` package.**
The config file was renamed. Move it across:

```bash
mv ~/.config/pygrid.json ~/.config/x11pygrid.json
```

## License

Released under the GNU General Public License v2. See [LICENSE.txt](https://github.com/pkkid/x11pygrid/blob/master/LICENSE.txt).

## Acknowledgments

- Created by [Michael Shepanski](https://github.com/pkkid), originally as a fork of [QuickTile](https://github.com/ssokolow/quicktile) by ssokolow, rewritten for Python 3 and GTK 3 with a simpler config.
- PyPI packaging and the pipx install instructions by Hilary Jendrasiak.
