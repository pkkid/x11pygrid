#!/usr/bin/env python3
"""
PyGrid - M.Shepanski 2016
Easily organize open windows on X11 desktop.
"""
import copy, json, os, signal, socket
from collections import namedtuple
from itertools import product
from Xlib import display, X
from Xlib.keysymdef import latin1

try:
    # Create singleton using abstract socket (prefix with null)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind('\0pygrid_singleton_lock')
except socket.error as err:
    raise SystemExit('PyGrid already running, exiting.')

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject  # noqa
from gi.repository import Gdk  # noqa

Seq = namedtuple('Seq', ['x1','x2', 'y1', 'y2', 'w', 'h'])
CONFIG_PATH = os.path.expanduser('~/.config/pygrid.json')
DEFAULT_CONFIG = {
    'default': {
        'snaptocursor': False,      # window will be moved to cursor's monitor
        'xdivs': 3,                 # number of x divisions for the screen
        'ydivs': 2,                 # number of y divisions for the screen
        'padding': [0, 0, 0, 0],    # additional top, right, bottom, left padding (pixels)
        'spacing': 4,               # spacing between windows (pixels)
        'minwidth': 0.25,           # min percent width of window
        'maxwidth': 0.67,           # max percent width of window
        'minheight': 0.33,          # min percent height of window
        'maxheight': 0.67,          # max percent height of window
    },
}


class PyGrid(object):
    KEYS = {
        latin1.XK_1: {'name':'bottomleft',  'filter':lambda s: s.x1 == 0.0 and s.y2 == 1.0},
        latin1.XK_2: {'name':'bottom',      'filter':lambda s: s.y2 == 1.0 and _center(s.x1,s.x2)},
        latin1.XK_3: {'name':'bottomright', 'filter':lambda s: s.x2 == 1.0 and s.y2 == 1.0},
        latin1.XK_4: {'name':'left',        'filter':lambda s: s.x1 == 0.0 and _center(s.y1,s.y2)},
        latin1.XK_5: {'name':'middle',      'filter':lambda s: _center(s.x1,s.x2) and _center(s.y1,s.y2)},
        latin1.XK_6: {'name':'right',       'filter':lambda s: s.x2 == 1.0 and _center(s.y1,s.y2)},
        latin1.XK_7: {'name':'topleft',     'filter':lambda s: s.x1 == 0.0 and s.y1 == 0.0},
        latin1.XK_8: {'name':'top',         'filter':lambda s: s.y1 == 0.0 and _center(s.x1,s.x2)},
        latin1.XK_9: {'name':'topright',    'filter':lambda s: s.x2 == 1.0 and s.y1 == 0.0},
    }

    def __init__(self):
        self.display = display.Display()
        self.root = self.display.screen().root
        self.keys = {}

    def start(self):
        """ Write config if not found and watch for keyboard events. """
        self._get_config()
        self.root.change_attributes(event_mask=X.KeyPressMask)
        self.keys = {self.display.keysym_to_keycode(k):v for k,v in self.KEYS.items()}
        for keycode in self.keys:
            self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
            self.root.grab_key(keycode, X.ControlMask | X.Mod1Mask | X.Mod2Mask, 1, X.GrabModeAsync, X.GrabModeAsync)
        for event in range(0, self.root.display.pending_events()):
            self.root.display.next_event()
        GObject.io_add_watch(self.root.display, GObject.IO_IN, self._check_event)
        print('PyGrid running. Press CTRL+C to cancel.')
        Gtk.main()

    def _check_event(self, source, condition, handle=None):
        """ Check keyboard event has all the right buttons pressed. """
        handle = handle or self.root.display
        for _ in range(0, handle.pending_events()):
            event = handle.next_event()
            if event.type == X.KeyPress:
                keypos = self.keys[event.detail]
                self._handle_event(keypos)
        return True

    def _handle_event(self, keypos):
        try:
            screen = Gdk.Screen.get_default()
            window = self._get_active_window(screen)
            if not window: return
            if self._get_config()['snaptocursor']:
                cursor = screen.get_display().get_default_seat().get_pointer().get_position()
                monitorid = screen.get_monitor_at_point(cursor.x, cursor.y)
            else:
                monitorid = screen.get_monitor_at_window(window)
            windowframe = window.get_frame_extents()
            config = self._get_config(monitorid)
            workarea = self._get_workarea(screen, monitorid, config)
            seqs = self._generate_sequence_percents(workarea, keypos, config)
            dists = self._get_seq_distances(windowframe, seqs)
            currindex = sorted(dists)[0][1]
            nextindex = (currindex + 1) % len(seqs)
            print('\nMove window %s to %s..' % (window.get_xid(), keypos['name']))
            print('  config: xdivs={xdivs}, ydivs={ydivs}, minw={minwidth}, maxw={maxwidth}, '
                'minh={minheight}, maxh={maxheight}, padding={padding}'.format(**config))
            print('  workarea: %s (monitorid:%s)' % (_rstr(workarea), monitorid))
            print('  windowframe: %s' % _rstr(windowframe))
            for i, seqp in enumerate(seqs):
                print('  %s; dist=%s' % (str(seqp), dists[i][0]))
            self._move_window(window, seqs[nextindex])
        except Exception as err:
            print('  Unable to move window: %s' % err)

    def _get_active_window(self, screen):
        """ Get the current active window. """
        window = screen.get_active_window()
        if not screen.supports_net_wm_hint(Gdk.atom_intern('_NET_ACTIVE_WINDOW', True)): return None
        if not screen.supports_net_wm_hint(Gdk.atom_intern('_NET_WM_WINDOW_TYPE', True)): return None
        if window.get_type_hint().value_name == 'GDK_WINDOW_TYPE_HINT_DESKTOP': return None
        return window

    def _get_config(self, monitorid=0):
        """ Get the configuration for the specified monitorid. Write config file if not found. """
        config = copy.deepcopy(DEFAULT_CONFIG)['default']
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as handle:
                    userconfig = json.load(handle)
                    config.update(userconfig.get('default', {}))
                    config.update(userconfig.get('monitor%s' % monitorid, {}))
            except Exception as err:
                print('Unable to parse userconfig: %s; %s' % (CONFIG_PATH, err))
        else:
            print('Writing default config: %s' % CONFIG_PATH)
            with open(CONFIG_PATH, 'w') as handle:
                json.dump(DEFAULT_CONFIG, handle, indent=2, sort_keys=True)
        return config

    def _get_workarea(self, screen, monitorid, config):
        """ get the monitor workarea taking into account config padding. """
        workarea = screen.get_monitor_workarea(monitorid)
        workarea.x += config['padding'][3]
        workarea.y += config['padding'][0]
        workarea.width -= config['padding'][3] + config['padding'][1]
        workarea.height -= config['padding'][0] + config['padding'][2]
        return workarea

    def _generate_sequence_percents(self, workarea, keypos, config):
        """ Generate a list of sequence positions (as percents). """
        seqs = []
        for x1, x2 in product(_iter_percent(config['xdivs']), repeat=2):
            for y1, y2 in product(_iter_percent(config['ydivs']), repeat=2):
                seqp = Seq(x1, x2, y1, y2, round(x2-x1,4), round(y2-y1,4))
                if seqp.x1 >= seqp.x2 or seqp.y1 >= seqp.y2: continue
                if not keypos['filter'](seqp): continue
                if keypos['name'] not in ['top', 'middle', 'bottom'] and not config['minwidth'] <= seqp.w <= config['maxwidth']: continue
                if keypos['name'] not in ['left', 'middle', 'right'] and not config['minheight'] <= seqp.h <= config['maxheight']: continue
                seqs.append(self._seqp_to_seq(seqp, workarea, config))
        return seqs

    def _seqp_to_seq(self, seqp, workarea, config):
        """ Convert sequence from percents to coordinates taking into account config spacing. """
        seq = Seq(
            x1=int(round(workarea.x + (workarea.width * seqp.x1))),
            x2=int(round(workarea.x + (workarea.width * seqp.x2))),
            y1=int(round(workarea.y + (workarea.height * seqp.y1))),
            y2=int(round(workarea.y + (workarea.height * seqp.y2))),
            w=int(round(workarea.width * seqp.w)),
            h=int(round(workarea.height * seqp.h)),
        )
        if config['spacing']:
            halfspace = int(config['spacing'] / 2)
            if seqp.x1 != 0.0: seq = seq._replace(x1=seq.x1+halfspace, w=seq.w-halfspace)
            if seqp.y1 != 0.0: seq = seq._replace(y1=seq.y1+halfspace, h=seq.h-halfspace)
            if seqp.x2 != 1.0: seq = seq._replace(x2=seq.x2-halfspace, w=seq.w-halfspace)
            if seqp.y2 != 1.0: seq = seq._replace(y2=seq.y2-halfspace, h=seq.h-halfspace)
        return seq

    def _get_seq_distances(self, wf, seqs):
        dists = []
        windata = (wf.x, wf.y, wf.width, wf.height)
        for i, seq in enumerate(seqs):
            seqdata = (seq.x1, seq.y1, seq.w, seq.h)
            dist = sum([abs(w-s) for w,s in zip(windata, seqdata)])
            dists.append((dist, i))
        return dists

    def _move_window(self, window, seq):
        # get the windowframe offset and move
        # TODO: we shouldn't assume the bottom thickness equals the side thickness.
        # TODO: we should read shadow width and adjust accordingly instead of setting it.
        origin, root = window.get_origin(), window.get_root_origin()
        offx, offy = origin.x - root.x, origin.y - root.y
        print('  newpos: x=%s, y=%s, w=%s, h=%s (offx:%s, offy:%s)' % (seq.x1, seq.y1,
            seq.w-(offx*2), seq.h-(offx+offy), offx, offy))
        window.unmaximize()
        window.set_shadow_width(0,0,0,0)
        window.move_resize(seq.x1, seq.y1, seq.w-(offx*2), seq.h-(offx+offy))


def _center(p1, p2):
    return round(1.0 - p2, 4) == p1


def _iter_percent(divs):
    for p in range(0, 1000001, int(1000000 / divs)):
        yield int(round(p / 100.0)) / 10000.0


def _rstr(rect):
    return 'x=%s y=%s w=%s h=%s' % (rect.x, rect.y, rect.width, rect.height)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    PyGrid().start()
