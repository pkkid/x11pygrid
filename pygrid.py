#!/usr/bin/env python
"""
PyGrid - M.Shepanski 2014
Grid placement like Compiz in Python.
Based on QuickTile by ssokolow.
"""
import gobject, gtk, os, pygtk
from heapq import heappop, heappush
from itertools import product
pygtk.require('2.0')

try:
    from Xlib import X
    from Xlib.display import Display
    from Xlib.keysymdef import miscellany
except ImportError:
    raise SystemExit("Could not find python-xlib. Cannot bind keys.")


centered = lambda a,b: a == round(1.0-b, 2)
XDIVS = [0.0, 0.33, 0.5, 0.67, 1.0]
YDIVS = [0.0, 0.5, 1.0]
DESKTOP_PADDING_TOP = 28
DESKTOP_PADDING_RIGHT = 0
DESKTOP_PADDING_BOTTOM = 0
DESKTOP_PADDING_LEFT = 0
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


class PositionGenerator(object):    

    def __init__(self, xdivs, ydivs):
        self.xdivs = xdivs
        self.ydivs = ydivs

    def positions(self):
        positions = {}
        for position in FILTERS:
            positions[position] = set()
            for x1,x2 in product(self.xdivs, repeat=2):
                for y1,y2 in product(self.ydivs, repeat=2):
                    w, h = round(x2-x1, 2), round(y2-y1, 2)
                    if w <= 0 or h <= 0: continue
                    if not FILTERS[position](x1,y1,x2,y2,w,h): continue
                    positions[position].add((x1,y1,w,h))
        return positions


class WindowManager(object):

    def __init__(self, commands):
        self.commands = commands
        self.screen = gtk.gdk.screen_get_default()
    
    def run_command(self, command):
        if command in self.commands:
            return self.cycle_dimensions(self.commands[command])
        command_func = getattr(self, command, None)
        if command_func:
            return command_func()
        print "Unknown command: %s" % command

    def get_active_window(self):
        if (not self.screen.supports_net_wm_hint('_NET_ACTIVE_WINDOW') or
            not self.screen.supports_net_wm_hint('_NET_WM_WINDOW_TYPE')):
            return None
        win = self.screen.get_active_window()
        wintype = win.property_get('_NET_WM_WINDOW_TYPE')
        if not wintype or wintype[-1][0] == '_NET_WM_WINDOW_TYPE_DESKTOP':
            return None
        return win

    def get_frame_thickness(self, win):
        origin, root_origin = win.get_origin(), win.get_root_origin()
        border, titlebar = origin[0] - root_origin[0], origin[1] - root_origin[1]
        return border, titlebar

    def get_window_state(self):
        win = self.get_active_window()
        if not win: return None, None
        # Get the window details
        border, titlebar = self.get_frame_thickness(win)
        winw, winh = win.get_geometry()[2:4]
        winw, winh = winw+(border*2), winh+(titlebar+border)
        winx, winy = win.get_root_origin()
        # Get the monitor details
        monid = self.screen.get_monitor_at_window(win)
        mongeo = self.screen.get_monitor_geometry(monid)
        mongeo.width = mongeo.width - DESKTOP_PADDING_LEFT - DESKTOP_PADDING_RIGHT
        mongeo.height = mongeo.height - DESKTOP_PADDING_TOP - DESKTOP_PADDING_BOTTOM
        if not mongeo: return None, None, None, None
        # Reutrn the details
        wingeo = gtk.gdk.Rectangle(winx-mongeo.x, winy-mongeo.y, winw, winh)
        return win, wingeo, monid, mongeo

    def reposition(self, win, wingeo, mongeo):
        border, titlebar = self.get_frame_thickness(win)
        win.move_resize(wingeo.x+mongeo.x, wingeo.y+mongeo.y,
            wingeo.width-(border*2), wingeo.height-(titlebar+border))

    def cycle_dimensions(self, positions):
        win, wingeo, monid, mongeo = self.get_window_state()
        dimensions = []
        for pos in positions:
            dimensions.append([int(pos[0]*mongeo.width), int(pos[1]*mongeo.height),
                int(pos[2]*mongeo.width), int(pos[3]*mongeo.height)])
        euclid_distance = []
        for pos, val in enumerate(dimensions):
            distance = sum([(wg-vv)**2 for (wg, vv) in zip(tuple(wingeo), tuple(val))])
            heappush(euclid_distance, (distance, pos))
        pos = heappop(euclid_distance)[1]
        newwingeo = gtk.gdk.Rectangle(*dimensions[(pos+1) % len(dimensions)])
        newwingeo.x = newwingeo.x + DESKTOP_PADDING_LEFT
        newwingeo.y = newwingeo.y + DESKTOP_PADDING_TOP
        self.reposition(win, newwingeo, mongeo)

    
class PyGrid(object):
    KEYS = {
        miscellany.XK_KP_1: 'bottomleft',
        miscellany.XK_KP_2: 'bottom',
        miscellany.XK_KP_3: 'bottomright',
        miscellany.XK_KP_4: 'left',
        miscellany.XK_KP_5: 'middle',
        miscellany.XK_KP_6: 'right',
        miscellany.XK_KP_7: 'topleft',
        miscellany.XK_KP_8: 'top',
        miscellany.XK_KP_9: 'topright',
    }

    def __init__(self, positions):
        self.positions = positions
        self.display = Display()
        self.root = self.display.screen().root
        self.winman = WindowManager(self.positions)
        self.keys = {}

    def handle_event(self, source, condition, handle=None):
        handle = handle or self.root.display
        for i in range(0, handle.pending_events()):
            event = handle.next_event()
            if event.type == X.KeyPress:
                keycode = event.detail
                self.winman.run_command(self.keys[keycode])
        return True

    def start_daemon(self):
        try:
            self.root.change_attributes(event_mask=X.KeyPressMask)
            self.keys = {self.display.keysym_to_keycode(k):self.KEYS[k] for k in self.KEYS}
            for keycode in self.keys:
                self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
                self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
            for event in range(0, self.root.display.pending_events()):
                self.root.display.next_event()
            gobject.io_add_watch(self.root.display, gobject.IO_IN, self.handle_event)
            gtk.main()
        except KeyboardInterrupt:
            print "Stopping PyGrid daemon"


if __name__ == '__main__':
    # Load user-defined config if it exists
    configfile = os.path.join(os.getenv("HOME"), '.config', 'pygridrc.py')
    if os.path.isfile(configfile):
        try:
            print "Reading configuration file: %s" % configfile
            exec(open(configfile).read())
        except Exception, err:
            raise SystemExit("INVALID CONFIG: %s\n%s" % (configfile, err))
    # Start the PyGrid daemon
    positions = PositionGenerator(XDIVS, YDIVS).positions()
    PyGrid(positions).start_daemon()


