## PyGrid ##
Keyboard-driven Window Tiling for your existing X11 window manager

### Requirements ###
* X11-based desktop and Python 2.x
* python-gtk2
* python-xlib

### Keyboard Shortcuts ###
ALT + CTRL + &lt;NUMPAD 1-9&gt;
Each number will push the current window to a different edge of the screen.

### Configuration Options ###

**XDIVS**
List of horizontal window percentages. *default: [0.0, 0.33, 0.5, 0.67, 1.0]*

**YDIVS**
List of vertical window percentages. *default: [0.0, 0.5, 1.0]*

**DESKTOP_PADDING_TOP, DESKTOP_PADDING_RIGHT,
  DESKTOP_PADDING_BOTTOM, DESKTOP_PADDING_LEFT**
Number of pixels to pad the top of the screen. Useful to help PyGrid to know about status bars or application launchers.

**FILTERS**
Dictionary containing rules to filter out any unwanted window sizes for each postion.  The following positions can be defined: {top, right, bottom, left, topleft, topright, bottomright, bottomleft, middle}. Each rule is a function that takes the arguments (x1,y1,x2,y2,w,h).  The function should return a boolean true for allowed and false for not allowed.

The default filters are as follows (I apologize for formatting):

    FILTERS = {
        'top':          lambda x1,y1,x2,y2,w,h: (y1 == 0.0) and (y2 != 1.0) and centered(x1,x2) and (h <= 0.5),
        'right':        lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (x2 == 1.0) and centered(y1,y2) and (w <= 0.7),
        'bottom':       lambda x1,y1,x2,y2,w,h: (y1 != 0.0) and (y2 == 1.0) and centered(x1,x2) and (h <= 0.5),
        'left':         lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (x2 != 1.0) and centered(y1,y2) and (w <= 0.7),
        'topleft':      lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (y1 == 0.0) and (x2 != 1.0) and (y2 != 1.0) and (w <= 0.7) and (h <= 0.5),
        'topright':     lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (y1 == 0.0) and (x2 == 1.0) and (y2 != 1.0) and (w <= 0.7) and (h <= 0.5),
        'bottomright':  lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (y1 != 0.0) and (x2 == 1.0) and (y2 == 1.0) and (w <= 0.7) and (h <= 0.5),
        'bottomleft':   lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (y1 != 0.0) and (x2 != 1.0) and (y2 == 1.0) and (w <= 0.7) and (h <= 0.5),
        'middle':       lambda x1,y1,x2,y2,w,h: centered(x1,x2) and centered(y1,y2) and (w != 1.0) and (h != 1.0),
    }

### Credit ###
PyGrid is a simpler version of the QuickTile project by ssokolow:
https://github.com/ssokolow/quicktile