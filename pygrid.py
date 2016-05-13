#!/usr/bin/env python3
"""
PyGrid - M.Shepanski 2014
Easily organize open windows on X11 desktop.
"""
import copy, json, os
import gi, signal
from itertools import product
from Xlib import display, X
from Xlib.keysymdef import miscellany
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject  # noqa
from gi.repository import Gdk, GdkX11  # noqa


CONFIG_PATH = os.path.expanduser('~/.config/pygrid.json')
DEFAULT_CONFIG = {
    'default': {
        'xdivs': 3,                 # number of x divisions for the screen
        'ydivs': 2,                 # number of y divisions for the screen
        'padding': [0, 0, 0, 0],    # additional top, right, bottom, left padding (pixels)
        #'spacing': 4,               # spacing between windows (pixels)
        'minwidth': 0.25,           # min percent width of window
        'maxwidth': 0.67,           # max percent width of window
        'minheight': 0.33,          # min percent height of window
        'maxheight': 0.67,          # max percent height of window
    },
}


class PyGrid(object):
    KEYS = {
        miscellany.XK_KP_1: {'name':'bottomleft',  'filter':lambda x1p,x2p,y1p,y2p: x1p == 0.0 and y2p == 1.0},
        miscellany.XK_KP_2: {'name':'bottom',      'filter':lambda x1p,x2p,y1p,y2p: y2p == 1.0 and _center(x1p,x2p)},
        miscellany.XK_KP_3: {'name':'bottomright', 'filter':lambda x1p,x2p,y1p,y2p: x2p == 1.0 and y2p == 1.0},
        miscellany.XK_KP_4: {'name':'left',        'filter':lambda x1p,x2p,y1p,y2p: x1p == 0.0 and _center(y1p,y2p)},
        miscellany.XK_KP_5: {'name':'middle',      'filter':lambda x1p,x2p,y1p,y2p: _center(x1p,x2p) and _center(y1p,y2p)},
        miscellany.XK_KP_6: {'name':'right',       'filter':lambda x1p,x2p,y1p,y2p: x2p == 1.0 and _center(y1p,y2p)},
        miscellany.XK_KP_7: {'name':'topleft',     'filter':lambda x1p,x2p,y1p,y2p: x1p == 0.0 and y1p == 0.0},
        miscellany.XK_KP_8: {'name':'top',         'filter':lambda x1p,x2p,y1p,y2p: y1p == 0.0 and _center(x1p,x2p)},
        miscellany.XK_KP_9: {'name':'topright',    'filter':lambda x1p,x2p,y1p,y2p: x2p == 1.0 and y1p == 0.0},
    }

    def __init__(self):
        self.display = display.Display()
        self.root = self.display.screen().root
        self.keys = {}

    def start(self):
        # watch for keyboard events
        self.root.change_attributes(event_mask=X.KeyPressMask)
        self.keys = {self.display.keysym_to_keycode(k):v for k,v in self.KEYS.items()}
        for keycode in self.keys:
            self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
            self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        for event in range(0, self.root.display.pending_events()):
            self.root.display.next_event()
        GObject.io_add_watch(self.root.display, GObject.IO_IN, self.handle_event)
        Gtk.main()

    def handle_event(self, source, condition, handle=None):
        handle = handle or self.root.display
        for _ in range(0, handle.pending_events()):
            event = handle.next_event()
            if event.type == X.KeyPress:
                try:
                    # get window and screen details
                    keypos = self.keys[event.detail]
                    screen = Gdk.Screen.get_default()
                    screen_num = screen.get_number()
                    window = self._get_active_window(screen)
                    window_frame = window.get_frame_extents()
                    workarea = screen.get_monitor_workarea(screen_num)
                    config = self._get_config(screen_num)
                    print('Move window %s: %s' % (window.get_xid(), keypos['name']))
                    print('  window_frame: %s' % _rstr(window_frame))
                    print('  workarea: %s (screen: %s)' % (_rstr(workarea), screen_num))
                    print('  config %s' % config)
                    positions = self._generate_positons(workarea, keypos, config)
                except Exception as err:
                    print('Err: %s' % err)
                    raise
        return True

    def _get_active_window(self, screen):
        window = screen.get_active_window()
        if not screen.supports_net_wm_hint(Gdk.atom_intern('_NET_ACTIVE_WINDOW', True)): return None
        if not screen.supports_net_wm_hint(Gdk.atom_intern('_NET_WM_WINDOW_TYPE', True)): return None
        if window.get_type_hint().value_name == 'GDK_WINDOW_TYPE_HINT_DESKTOP': return None
        return window

    def _get_config(self, screen_num):
        config = copy.deepcopy(DEFAULT_CONFIG)['default']
        if os.path.exists(CONFIG_PATH):
            try:
                userconfig = json.load(CONFIG_PATH)
                config.update(userconfig.get('default', {}))
                config.update(userconfig.get('monitor%s' % screen_num, {}))
            except Exception as err:
                print('Unable to parse userconfig: %s; %s' % (CONFIG_PATH, err))
                raise
        return config

    def _generate_positons(self, workarea, keypos, config):
        positions = []
        for x1p, x2p in product(_iter_percent(config['xdivs']), repeat=2):
            for y1p, y2p in product(_iter_percent(config['ydivs']), repeat=2):
                wp, hp = round(x2p-x1p,3), round(y2p-y1p,3)
                if x1p >= x2p or y1p >= y2p: continue
                if not keypos['filter'](x1p, x2p, y1p, y2p): continue
                if keypos['name'] not in ['top', 'middle', 'bottom'] and not config['minwidth'] <= wp <= config['maxwidth']: continue
                if keypos['name'] not in ['left', 'middle', 'right'] and not config['minheight'] <= hp <= config['maxheight']: continue
                print('  x1p:%-6s x2p:%-6s y1p:%-6s y2p:%-6s wp:%-6s hp:%-6s' % (x1p, x2p, y1p, y2p, wp, hp))
                positions.append((x1p, x2p, y1p, y2p, wp, hp))
        return positions


def _center(p1, p2):
    return round(1.0 - p2, 4) == p1


def _iter_percent(divs):
    for p in range(0, 1000001, int(1000000 / divs)):
        yield int(round(p / 100.0)) / 10000.0


def _rstr(rect):
    return 'x:%s y:%s w:%s h:%s' % (rect.x, rect.y, rect.width, rect.height)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    PyGrid().start()


#     # Load user-defined config if it exists
#     configfile = os.path.join(os.getenv("HOME"), '.config', 'pygridrc.py')
#     if os.path.isfile(configfile):
#         try:
#             print "Reading configuration file: %s" % configfile
#             exec(open(configfile).read())
#         except Exception, err:
#             raise SystemExit("INVALID CONFIG: %s\n%s" % (configfile, err))
#     # Start the PyGrid daemon
#     positions = PositionGenerator(XDIVS, YDIVS).positions()
#     PyGrid(positions).start_daemon()



#from heapq import heappop, heappush
#from itertools import product
# pygtk.require('2.0')
# import gobject, gtk  # noqa

# try:
#     import xlib
#     # from Xlib import X
#     # from Xlib.display import Display
#     # from Xlib.keysymdef import miscellany
# except ImportError:
#     raise SystemExit('Could not find python-xlib. Cannot bind keys.')

# centered = lambda a,b: a == round(1.0-b, 2)
# XDIVS = [0.0, 0.33, 0.5, 0.67, 1.0]
# YDIVS = [0.0, 0.5, 1.0]
# DESKTOP_PADDING_TOP = [28]
# DESKTOP_PADDING_RIGHT = [0]
# DESKTOP_PADDING_BOTTOM = [0]
# DESKTOP_PADDING_LEFT = [0]
# FILTERS = {
#     'top':          lambda x1,y1,x2,y2,w,h: (y1 == 0.0) and (y2 != 1.0) and centered(x1,x2) and (h <= 0.5),
#     'right':        lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (x2 == 1.0) and centered(y1,y2) and (w <= 0.7),
#     'bottom':       lambda x1,y1,x2,y2,w,h: (y1 != 0.0) and (y2 == 1.0) and centered(x1,x2) and (h <= 0.5),
#     'left':         lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (x2 != 1.0) and centered(y1,y2) and (w <= 0.7),
#     'topleft':      lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (y1 == 0.0) and (x2 != 1.0) and (y2 != 1.0) and (w <= 0.7) and (h <= 0.5),
#     'topright':     lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (y1 == 0.0) and (x2 == 1.0) and (y2 != 1.0) and (w <= 0.7) and (h <= 0.5),
#     'bottomright':  lambda x1,y1,x2,y2,w,h: (x1 != 0.0) and (y1 != 0.0) and (x2 == 1.0) and (y2 == 1.0) and (w <= 0.7) and (h <= 0.5),
#     'bottomleft':   lambda x1,y1,x2,y2,w,h: (x1 == 0.0) and (y1 != 0.0) and (x2 != 1.0) and (y2 == 1.0) and (w <= 0.7) and (h <= 0.5),
#     'middle':       lambda x1,y1,x2,y2,w,h: centered(x1,x2) and centered(y1,y2) and (w != 1.0) and (h != 1.0),
# }


# class PositionGenerator(object):    

#     def __init__(self, xdivs, ydivs):
#         self.xdivs = xdivs
#         self.ydivs = ydivs

#     def positions(self):
#         positions = {}
#         for position in FILTERS:
#             positions[position] = set()
#             for x1,x2 in product(self.xdivs, repeat=2):
#                 for y1,y2 in product(self.ydivs, repeat=2):
#                     w, h = round(x2-x1, 2), round(y2-y1, 2)
#                     if w <= 0 or h <= 0: continue
#                     if not FILTERS[position](x1,y1,x2,y2,w,h): continue
#                     positions[position].add((x1,y1,w,h))
#         return positions


# class WindowManager(object):

#     def __init__(self, commands):
#         self.commands = commands
#         self.screen = gtk.gdk.screen_get_default()
    
#     def run_command(self, command):
#         if command in self.commands:
#             return self.cycle_dimensions(self.commands[command])
#         command_func = getattr(self, command, None)
#         if command_func:
#             return command_func()
#         print 'Unknown command: %s' % command

#     def get_active_window(self):
#         if (not self.screen.supports_net_wm_hint('_NET_ACTIVE_WINDOW') or
#             not self.screen.supports_net_wm_hint('_NET_WM_WINDOW_TYPE')):
#             return None
#         win = self.screen.get_active_window()
#         wintype = win.property_get('_NET_WM_WINDOW_TYPE')
#         if not wintype or wintype[-1][0] == '_NET_WM_WINDOW_TYPE_DESKTOP':
#             return None
#         return win

#     def get_frame_thickness(self, win):
#         origin, root_origin = win.get_origin(), win.get_root_origin()
#         border, titlebar = origin[0] - root_origin[0], origin[1] - root_origin[1]
#         return border, titlebar

#     def get_window_state(self):
#         win = self.get_active_window()
#         if not win: return None, None
#         # Get the window details
#         border, titlebar = self.get_frame_thickness(win)
#         winw, winh = win.get_geometry()[2:4]
#         winw, winh = winw+(border*2), winh+(titlebar+border)
#         winx, winy = win.get_root_origin()
#         # Get the monitor details
#         monid = self.screen.get_monitor_at_window(win)
#         mongeo = self.screen.get_monitor_geometry(monid)
#         mongeo.width = mongeo.width - self.padding_left(monid) - self.padding_right(monid)
#         mongeo.height = mongeo.height - self.padding_top(monid) - self.padding_bottom(monid)
#         if not mongeo: return None, None, None, None
#         # Reutrn the details
#         wingeo = gtk.gdk.Rectangle(winx-mongeo.x, winy-mongeo.y, winw, winh)
#         return win, wingeo, monid, mongeo

#     def reposition(self, win, wingeo, mongeo):
#         border, titlebar = self.get_frame_thickness(win)
#         win.move_resize(wingeo.x+mongeo.x, wingeo.y+mongeo.y,
#             wingeo.width-(border*2), wingeo.height-(titlebar+border))

#     def cycle_dimensions(self, positions):
#         win, wingeo, monid, mongeo = self.get_window_state()
#         dimensions = []
#         for pos in positions:
#             dimensions.append([int(pos[0]*mongeo.width), int(pos[1]*mongeo.height),
#                 int(pos[2]*mongeo.width), int(pos[3]*mongeo.height)])
#         euclid_distance = []
#         for pos, val in enumerate(dimensions):
#             distance = sum([(wg-vv)**2 for (wg, vv) in zip(tuple(wingeo), tuple(val))])
#             heappush(euclid_distance, (distance, pos))
#         if not euclid_distance:
#             print 'No positions to enumerate.'
#             return
#         pos = heappop(euclid_distance)[1]
#         newwingeo = gtk.gdk.Rectangle(*dimensions[(pos+1) % len(dimensions)])
#         newwingeo.x = newwingeo.x + self.padding_left(monid)
#         newwingeo.y = newwingeo.y + self.padding_top(monid)
#         self.reposition(win, newwingeo, mongeo)

#     def padding_top(self, monid):
#         index = monid if len(DESKTOP_PADDING_TOP) > monid else 0
#         return DESKTOP_PADDING_TOP[index]

#     def padding_right(self, monid):
#         index = monid if len(DESKTOP_PADDING_RIGHT) > monid else 0
#         return DESKTOP_PADDING_RIGHT[index]

#     def padding_bottom(self, monid):
#         index = monid if len(DESKTOP_PADDING_BOTTOM) > monid else 0
#         return DESKTOP_PADDING_BOTTOM[index]

#     def padding_left(self, monid):
#         index = monid if len(DESKTOP_PADDING_LEFT) > monid else 0
#         return DESKTOP_PADDING_LEFT[index]

    
# class PyGrid(object):
#     KEYS = {
#         miscellany.XK_KP_1: 'bottomleft',
#         miscellany.XK_KP_2: 'bottom',
#         miscellany.XK_KP_3: 'bottomright',
#         miscellany.XK_KP_4: 'left',
#         miscellany.XK_KP_5: 'middle',
#         miscellany.XK_KP_6: 'right',
#         miscellany.XK_KP_7: 'topleft',
#         miscellany.XK_KP_8: 'top',
#         miscellany.XK_KP_9: 'topright',
#     }

#     def __init__(self, positions):
#         self.positions = positions
#         self.display = Display()
#         self.root = self.display.screen().root
#         self.winman = WindowManager(self.positions)
#         self.keys = {}

#     def handle_event(self, source, condition, handle=None):
#         handle = handle or self.root.display
#         for i in range(0, handle.pending_events()):
#             event = handle.next_event()
#             if event.type == X.KeyPress:
#                 keycode = event.detail
#                 self.winman.run_command(self.keys[keycode])
#         return True

#     def start_daemon(self):
#         try:
#             self.root.change_attributes(event_mask=X.KeyPressMask)
#             self.keys = {self.display.keysym_to_keycode(k):self.KEYS[k] for k in self.KEYS}
#             for keycode in self.keys:
#                 self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
#                 self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
#             for event in range(0, self.root.display.pending_events()):
#                 self.root.display.next_event()
#             gobject.io_add_watch(self.root.display, gobject.IO_IN, self.handle_event)
#             gtk.main()
#         except KeyboardInterrupt:
#             print "Stopping PyGrid daemon"


# if __name__ == '__main__':
#     # Load user-defined config if it exists
#     configfile = os.path.join(os.getenv("HOME"), '.config', 'pygridrc.py')
#     if os.path.isfile(configfile):
#         try:
#             print "Reading configuration file: %s" % configfile
#             exec(open(configfile).read())
#         except Exception, err:
#             raise SystemExit("INVALID CONFIG: %s\n%s" % (configfile, err))
#     # Start the PyGrid daemon
#     positions = PositionGenerator(XDIVS, YDIVS).positions()
#     PyGrid(positions).start_daemon()