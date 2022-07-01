import os
import re
import socket
import subprocess

from typing import List
from zlib import ZLIB_VERSION  # noqa: F401

# import widgets and bar
from libqtile.widget.groupbox import GroupBox
from libqtile.widget.currentlayout import CurrentLayout
from libqtile.widget.window_count import WindowCount
from libqtile.widget.windowname import WindowName
from libqtile.widget.prompt import Prompt
from libqtile.widget.cpu import CPU
from libqtile.widget.memory import Memory
from libqtile.widget.net import Net
from libqtile.widget.systray import Systray
from libqtile.widget.clock import Clock
from libqtile.widget.spacer import Spacer

from libqtile.config import Click, Drag, Group, Key, Match, Screen, Rule
from libqtile import layout, bar, widget, hook
from libqtile.command import lazy
from libqtile.utils import guess_terminal

from colors import gruvbox

# mod4 or mod = super key
mod = "mod4"
mod1 = "alt"
mod2 = "control"
terminal = guess_terminal()
home = os.path.expanduser('~')


@lazy.function
def window_to_prev_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i - 1].name)


@lazy.function
def window_to_next_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i + 1].name)


keys = [

    # Most of my other keybindings are in sxhkd file - except these

    # Toggle floating and fullscreen
    Key([mod], "f",
        lazy.window.toggle_fullscreen(),
        desc='toggle fullscreen'
        ),
    Key([mod, "shift"], "f",
        lazy.window.toggle_floating(),
        desc='toggle floating'
        ),

    # Switch focus of monitors
    Key([mod], "l",
        lazy.next_screen(),
        desc='Move focus to next monitor'
        ),
    Key([mod], "h",

        lazy.prev_screen(),
        desc='Move focus to prev monitor'
        ),

    # Window controls

    Key([mod], "j",
        lazy.layout.down(),
        desc='Move focus down in current stack pane'),
    Key([mod], "k",
        lazy.layout.up(), desc='Move focus up in current stack pane'),
    Key([mod, "shift"], "j",
        lazy.layout.shuffle_down(),
        desc='Move windows down in current stack'),
    Key([mod, "shift"], "k",
        lazy.layout.shuffle_up(),
        desc='Move windows up in current stack'),

    Key([mod, "shift"], "h",
        lazy.layout.shrink(),
        lazy.layout.decrease_nmaster(),
        desc='Shrink window (MonadTall), decrease number in master pane (Tile)'
        ),
    Key([mod, "shift"], "l",
        lazy.layout.grow(),
        lazy.layout.increase_nmaster(),
        desc='Expand window (MonadTall), increase number in master pane (Tile)'
        ),

    Key([mod], "n",
        lazy.layout.normalize(),
        desc='normalize window size ratios'
        ),
    Key([mod], "m",
        lazy.layout.maximize(),
        desc='toggle window between minimum and maximum sizes'
        ),

    Key([mod], "q", lazy.window.kill()),

    Key([mod, "shift"], "q", lazy.window.kill()),
    Key([mod, "shift"], "r", lazy.reload_config()),

    # Stack controls
    Key([mod, "shift"], "Tab",
        lazy.layout.rotate(),
        lazy.layout.flip(),
        desc='Switch which side main pane occupies (XmonadTall)'
        ),
    Key([mod], "space",
        lazy.layout.next(),
        desc='Switch window focus to other pane(s) of stack'
        ),
    Key([mod, "shift"], "space",
        lazy.layout.toggle_split(),
        desc='Toggle between split and unsplit sides of stack'
        ),
]

# groups = []
# group_names = ["1", "2", "3", "4", "5"]
# group_labels = ["I", "II ", "III", "IV", "V "]
# group_layouts = ["monadtall", "monadtall",
#                  "monadtall", "monadtall", "monadtall"]
# for i in range(len(group_names)):
#     groups.append(
#         Group(
#             name=group_names[i],
#             layout=group_layouts[i].lower(),
#             label=group_labels[i],
#         ))

groups = [
    Group('1', label="一", matches=[
          Match(wm_class='brave')], layout="monadtall"),
    Group('2', label="二", layout="monadtall", matches=[
          Match(wm_class='code')]),
    Group('3', label="三", matches=[Match(wm_class='spotify'),
                                   Match(wm_class='discord')], layout="monadtall"),
    Group('4', label="四", layout="monadtall"),
    Group('5', label="五", layout="monadtall"),
    Group('6', label="六", layout="monadtall"),
    Group('7', label="七", layout="monadtall"),
    Group('8', label="八", layout="monadtall"),
    Group('9', label="九", layout="monadtall"),
    Group('0', label="十", layout="monadtall"),
]

for i in groups:
    keys.extend([

        # CHANGE WORKSPACES
        Key([mod], i.name, lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # MOVE WINDOW TO SELECTED WORKSPACE 1-10 AND STAY ON WORKSPACE
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            desc="Move focused window to group {}".format(i.name)),

        Key([mod], "comma",
            lazy.screen.prev_group(),
            desc='Move focus to next monitor'
            ),
        Key([mod], "period",
            lazy.screen.next_group(),
            desc='Move focus to prev monitor'
            ),
    ])


def init_layout_theme():
    return {"margin": 8,
            "border_width": 3,
            "border_focus": gruvbox['yellow'],
            "border_normal": gruvbox['dark-gray']
            }


layout_theme = init_layout_theme()

layouts = [
    layout.MonadTall(**layout_theme),
    layout.MonadWide(**layout_theme),
    layout.Matrix(**layout_theme),
    layout.Bsp(**layout_theme),
    layout.Floating(**layout_theme),
    layout.RatioTile(**layout_theme),
    layout.Max(**layout_theme)
]


# WIDGETS FOR THE BAR
def init_widgets_defaults():
    return dict(font="Hack",
                fontsize=13,
                padding=10,
                background=gruvbox['bg'],
                foreground=gruvbox['fg'])


widget_defaults = init_widgets_defaults()


def init_widgets_list():
    prompt = "{0}@{1}: ".format(os.environ["USER"], socket.gethostname())
    widgets_list = [
        widget.Sep(
            linewidth=0,
            padding=6,
            foreground=gruvbox['bg'],
            background=gruvbox['bg']
        ),
        widget.GroupBox(
            font="Ubuntu Bold",
            fontsize=16,
            margin_y=2,
            margin_x=0,
            padding_y=6,
            padding_x=5,
            borderwidth=3,
            disable_drag=True,
            active=gruvbox['yellow'],
            inactive=gruvbox['dark-gray'],
            rounded=False,
            highlight_method="line",
            highlight_color=gruvbox['bg'],
            this_current_screen_border=gruvbox['yellow'],
            this_screen_border=gruvbox['dark-gray'],
            # other_current_screen_border=gruvbox['dark-blue'],
            # other_screen_border=gruvbox['red'],
        ),
        widget.Sep(
            linewidth=0,
            padding=10,
            foreground=gruvbox['fg'],
            background=gruvbox['bg']
        ),
        # widget.CurrentLayout(
        #     custom_icon_paths=[os.path.expanduser("~/.config/qtile/icons")],
        #     font="Ubuntu Bold",
        #     foreground=gruvbox['fg'],
        #     background=gruvbox['bg'],
        #     scale=0.7
        # ),
        # widget.Sep(
        #     linewidth=0,
        #     padding=10,
        #     foreground=gruvbox['fg'],
        #     background=gruvbox['bg']
        # ),
        widget.WindowName(
            font="Ubuntu Bold",
            fontsize=13,
            foreground=gruvbox['fg'],
            background=gruvbox['bg'],
        ),
        # widget.Sep(
        #     linewidth=0,
        #     padding=10,
        #     foreground=gruvbox['fg'],
        #     background=gruvbox['bg']
        # ),

        # ThemalSensor
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['bg'],
            foreground=gruvbox['blue'],
            padding=0,
            fontsize=51
        ),
        widget.CheckUpdates(
            update_interval=1800,
            distro="Arch_checkupdates",
            display_format="Updates: {updates} ",
            foreground=gruvbox['fg0'],
            colour_have_updates=gruvbox['fg0'],
            colour_no_updates=gruvbox['fg0'],
            padding=5,
            background=gruvbox['blue'],
            no_update_string="No update's"
        ),
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['blue'],
            foreground=gruvbox['bg'],
            padding=0,
            fontsize=51
        ),

        # Updates
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['bg'],
            foreground=gruvbox['green'],
            padding=0,
            fontsize=51
        ),
        # do not activate in Virtualbox - will break qtile
        # widget.ThermalSensor(
        #     foreground=gruvbox['fg0'],
        #     background=gruvbox['green'],
        #     threshold=90,
        #     fmt='Temp: {}',
        #     padding=5
        # ),
        # widget.TextBox(
        #     text='',
        #     font="Ubuntu Mono",
        #     background=gruvbox['green'],
        #     foreground=gruvbox['bg'],
        #     padding=0,
        #     fontsize=51
        # ),

        # Memory
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['bg'],
            foreground=gruvbox['dark-yellow'],
            padding=0,
            fontsize=51
        ),
        widget.Memory(
            foreground=gruvbox['fg0'],
            background=gruvbox['dark-yellow'],
            fmt='Mem: {}',
            padding=5
        ),
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['dark-yellow'],
            foreground=gruvbox['bg'],
            padding=0,
            fontsize=51
        ),

        # Volume
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['bg'],
            foreground=gruvbox['red'],
            padding=0,
            fontsize=51
        ),
        widget.Volume(
            foreground=gruvbox['fg0'],
            background=gruvbox['red'],
            fmt='Vol: {}',
            padding=5
        ),
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['red'],
            foreground=gruvbox['bg'],
            padding=0,
            fontsize=51
        ),

        # KeyboardLayout
        # widget.TextBox(
        #     text='',
        #     font="Ubuntu Mono",
        #     background=gruvbox['bg'],
        #     foreground=gruvbox['cyan'],
        #     padding=0,
        #     fontsize=51
        # ),
        # widget.KeyboardLayout(
        #     foreground=gruvbox['fg0'],
        #     background=gruvbox['cyan'],
        #     fmt='Keyboard: {}',
        #     padding=5
        # ),
        # widget.TextBox(
        #     text='',
        #     font="Ubuntu Mono",
        #     background=gruvbox['cyan'],
        #     foreground=gruvbox['bg'],
        #     padding=0,
        #     fontsize=51
        # ),

        # Clock
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['bg'],
            foreground=gruvbox['magenta'],
            padding=0,
            fontsize=51
        ),
        widget.Clock(
            foreground=gruvbox['fg0'],
            background=gruvbox['magenta'],
            format="%b %d - %H:%M "
        ),
        widget.TextBox(
            text='',
            font="Ubuntu Mono",
            background=gruvbox['magenta'],
            foreground=gruvbox['bg'],
            padding=0,
            fontsize=51
        ),

        widget.Systray(
            background=gruvbox['bg'],
            foreground=gruvbox['fg'],
            padding=5
        ),

        widget.Sep(
            linewidth=0,
            padding=6,
            foreground=gruvbox['bg'],
            background=gruvbox['bg']
        ),
    ]
    return widgets_list


widgets_list = init_widgets_list()


def init_widgets_screen1():
    widgets_screen1 = init_widgets_list()
    return widgets_screen1


def init_widgets_screen2():
    widgets_screen2 = init_widgets_list()
    return widgets_screen2


widgets_screen1 = init_widgets_screen1()
widgets_screen2 = init_widgets_screen2()


def init_screens():
    return [Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=26, opacity=1)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26, opacity=1))]


screens = init_screens()


# MOUSE CONFIGURATION
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size())
]

dgroups_key_binder = None
dgroups_app_rules = []

main = None


@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/scripts/autostart.sh'])


@hook.subscribe.startup
def start_always():
    # Set the cursor to something sane in X
    subprocess.Popen(['xsetroot', '-cursor_name', 'left_ptr'])


@hook.subscribe.client_new
def set_floating(window):
    if (window.window.get_wm_transient_for()
            or window.window.get_wm_type() in floating_types):
        window.floating = True


floating_types = ["notification", "toolbar", "splash", "dialog"]


follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(float_rules=[
    # Run the utility of `xprop` to see the wm class and name of an X client.
    *layout.Floating.default_float_rules,
    Match(wm_class='confirmreset'),  # gitk
    Match(wm_class='makebranch'),  # gitk
    Match(wm_class='maketag'),  # gitk
    Match(wm_class='ssh-askpass'),  # ssh-askpass
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
    Match(wm_class='Arcolinux-welcome-app.py'),
    Match(wm_class='Arcolinux-tweak-tool.py'),
    Match(wm_class='Arcolinux-calamares-tool.py'),
    Match(wm_class='confirm'),
    Match(wm_class='dialog'),
    Match(wm_class='download'),
    Match(wm_class='error'),
    Match(wm_class='file_progress'),
    Match(wm_class='notification'),
    Match(wm_class='splash'),
    Match(wm_class='toolbar'),
    Match(wm_class='Arandr'),
    Match(wm_class='feh'),
    Match(wm_class='Galculator'),
    Match(wm_class='arcolinux-logout'),
    Match(wm_class='xfce4-terminal'),

],  fullscreen_border_width=0, border_width=0)
auto_fullscreen = True

focus_on_window_activation = "focus"  # or smart

wmname = "LG3D"
