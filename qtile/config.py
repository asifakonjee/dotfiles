#-----------------------------------------------------------
#     _        _  __      _    _                _
#    / \   ___(_)/ _|    / \  | | _____  _ __  (_) ___  ___
#   / _ \ / __| | |_    / _ \ | |/ / _ \| '_ \ | |/ _ \/ _ \
#  / ___ \\__ \ |  _|  / ___ \|   < (_) | | | || |  __/  __/
# /_/   \_\___/_|_|   /_/   \_\_|\_\___/|_| |_|/ |\___|\___|
#                                            |__/
#-----------------------------------------------------------
#   ___  _   _ _
#  / _ \| |_(_) | ___
# | | | | __| | |/ _ \
# | |_| | |_| | |  __/
#  \__\_\\__|_|_|\___|
#------------------------------------------------------------

from typing import List  # noqa: F401

from scripts import storage

import os
import re
import socket
import subprocess
from libqtile import qtile
from libqtile import bar, layout, widget, hook
from libqtile.widget import base
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal

# default variables
mod = "mod4"
terminal = 'alacritty'
home_dir = os.path.expanduser("~")

keys = [
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),

    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),

    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),

    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key([mod, "control"], "Return", lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack"),

    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "c", lazy.window.kill(), desc="Kill focused window"),

    Key(["control", "shift"], "r", lazy.restart(), desc="Restart Qtile"),
    Key(["control", "shift"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
]

# custom workspace names and initialization
class Groupings:

    def init_group_names(self):
        return [("I", {"layout": "monadtall"}),     # Terminals
                ("II", {"layout": "monadtall"}),     # Web Browser
                ("III", {"layout": "monadtall"}),     # File Manager
                ("IV", {"layout": "monadtall"}),     # Text Editor
                ("V", {"layout": "monadtall"}),     # Media
                ("VI", {"layout": "monadtall"}),     # Music/Audio
                ("VII", {"layout": "monadtall"})]    # Settings
                
#                return [("", {"layout": "monadtall"}),     # Terminals
#                ("", {"layout": "monadtall"}),     # Web Browser
#                ("", {"layout": "monadtall"}),     # File Manager
#                ("", {"layout": "monadtall"}),     # Text Editor
#                ("", {"layout": "monadtall"}),     # Media
#                ("", {"layout": "monadtall"}),     # Music/Audio
#                ("漣", {"layout": "monadtall"})]    # Settings

    def init_groups(self):
        return [Group(name, **kwargs) for name, kwargs in group_names]


if __name__ in ["config", "__main__"]:
    group_names = Groupings().init_group_names()
    groups = Groupings().init_groups()

for i, (name, kwargs) in enumerate(group_names, 1):
    keys.append(Key([mod], str(i), lazy.group[name].toscreen()))        # Switch to another group
    keys.append(Key([mod, "shift"], str(i), lazy.window.togroup(name))) # Send current window to another group

##### DEFAULT THEME SETTINGS FOR LAYOUTS #####
layout_theme = {"border_width": 3,
                "margin": 5,
                "font": "Source Code Pro Medium",
                "font_size": 10,
                "border_focus": "#81a2be",
                "border_normal": "#1d1f21"
                }

# window layouts
layouts = [
    layout.MonadTall(**layout_theme),
    layout.Max(**layout_theme),
    layout.Floating(**layout_theme),
    layout.Stack(num_stacks=2, **layout_theme),
    layout.Bsp(**layout_theme),
    layout.Tile(**layout_theme),

    # Try more layouts by unleashing below layouts.
    # layout.Columns(**layout_theme),
    # layout.Matrix(**layout_theme),
    # layout.MonadWide(**layout_theme),
    # layout.RatioTile(**layout_theme),
    # layout.TreeTab(**layout_theme),
    # layout.VerticalTile(**layout_theme),
    # layout.Zoomy(**layout_theme),
]


# colors for the bar/widgets/panel
def init_colors():
    return [["#1d1f21", "#1d1f21"], # color 0 | bg
            ["#1d1f21", "#1d1f21"], # color 1 | bg
            ["#c5c8c6", "#c5c8c6"], # color 2 | fg
            ["#d90202", "#d90202"], # color 3 | red
            ["#28e302", "#28e302"], # color 4 | green
            ["#e6c547", "#e6c547"], # color 5 | yellow
            ["#81a2be", "#81a2be"], # color 6 | blue
            ["#b294bb", "#b294bb"], # color 7 | magenta
            ["#70c0ba", "#70c0ba"], # color 8 | cyan
            ["#373b41", "#373b41"]] # color 9 | white

def init_separator():
    return widget.Sep(
                size_percent = 60,
                margin = 5,
                linewidth = 2,
                background = colors[1],
                foreground = "#555555")

def nerd_icon(nerdfont_icon, fg_color):
    return widget.TextBox(
                font = "Iosevka Nerd Font",
                fontsize = 15,
                text = nerdfont_icon,
                foreground = fg_color,
                background = colors[1])

def init_edge_spacer():
    return widget.Spacer(
                length = 5,
                background = colors[1])


colors = init_colors()
sep = init_separator()
space = init_edge_spacer()

widget_defaults = dict(
    font='Iosevka Nerd Font',
    fontsize=15,
    padding=5,
)
extension_defaults = widget_defaults.copy()


def init_widgets_list():
    widgets_list = [
            # Left Side of the bar

            space,
            #widget.Image(
            #    filename = "/usr/share/pixmaps/archlinux-logo.png",
            #    background = colors[1],
            #    margin = 3
            #),
            widget.Image(
                filename = "~/.config/qtile/python.png",
                background = colors[1],
                margin = 3,
                mouse_callbacks = {
                    'Button1': lambda : qtile.cmd_spawn(
                        'j4-dmenu'
                    ),
                    'Button3': lambda : qtile.cmd_spawn(
                        f'{terminal} -e vim {home_dir}/.config/qtile/config.py'
                    )
                }
            ),
            widget.GroupBox(
                font = "Iosevka Nerd Font",
                fontsize = 15,
                foreground = colors[2],
                background = colors[1],
                borderwidth = 2,
                highlight_method = "text",
                this_current_screen_border = colors[3],
                active = colors[4],
                inactive = colors[2]
            ),
            sep,
            nerd_icon(
                "",
                colors[7]
            ),
            widget.CurrentLayout(
                foreground = colors[4],
                background = colors[1]
            ),            
            widget.Spacer(
                length = bar.STRETCH,
                background = colors[1]
            ),

            # Center bar

            sep,
            nerd_icon(
                "",
                colors[3]
            ),
            widget.Clock(
                format = '%b %d-%Y',
                foreground = colors[2],
                background = colors[1]
            ),
            nerd_icon(
                "",
                colors[4]
            ),
            widget.Clock(
                format = '%I:%M %p',
                foreground = colors[2],
                background = colors[1]
            ),
            sep,
#            nerd_icon(
#                "",
#                colors[4]
#            ),
#            widget.GenPollText(
#                foreground = colors[2],
#                background = colors[1],
#                update_interval = 5,
#                func = lambda: subprocess.check_output(f"{home_dir}/.config/qtile/scripts/num-installed-pkgs").decode("utf-8")
#            ),

            # Left Side of the bar

            widget.Spacer(
                length = bar.STRETCH,
                background = colors[1]
            ),
            sep,
            nerd_icon(
                "",
                colors[4]
            ),
            widget.Net(
                format = "{down}↓↑{up}",
                foreground = colors[2],
                background = colors[1],
                update_interval = 2,
                mouse_callbacks = {
                    'Button1': lambda : qtile.cmd_spawn("def-nmdmenu")
                }
            ),
            sep,
            nerd_icon(
                "墳",
                colors[3]
            ),
            widget.Volume(
                foreground = colors[2],
                background = colors[1]
            ),
            sep,
            nerd_icon(
                "",
                colors[4]
            ),
            widget.Battery(
                foreground = colors[2],
                background = colors[1],
                format = "{percent:2.0%}"
            ),
                       
#            nerd_icon(
#                "﬙",
#                colors[3]
#            ),
#            widget.CPU(
#                format = "{load_percent}%",
#                foreground = colors[2],
#                background = colors[1],
#                update_interval = 2,
#                mouse_callbacks = {
#                    'Button1': lambda : qtile.cmd_spawn(f"{terminal} -e gtop")
#                }
#            ),
#            nerd_icon(
#                "",
#                colors[4]
#            ),
#            widget.Memory(
#                format = "{MemUsed:.0f}{mm}",
#                foreground = colors[2],
#                background = colors[1],
#                update_interval = 2,
#                mouse_callbacks = {
#                    'Button1': lambda : qtile.cmd_spawn(f"{terminal} -e gtop")
#                }
#            ),
#            nerd_icon(
#                "",
#                colors[6]
#            ),
#            widget.GenPollText(
#                foreground = colors[2],
#                background = colors[1],
#                update_interval = 5,
#                func = lambda: storage.diskspace('FreeSpace'),
#                mouse_callbacks = {
#                    'Button1': lambda : qtile.cmd_spawn(f"{terminal} -e gtop")
#                }
#            ),
            sep,
            widget.Systray(
                background = colors[1]
            ),
            space
        ]
    return widgets_list


# screens/bar
def init_screens():
    return [Screen(top=bar.Bar(widgets=init_widgets_list(), size=30, opacity=0.8, margin=[4,5,0,5]))]

screens = init_screens()

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front())
]

#
# assign apps to groups/workspace
#
@hook.subscribe.client_new
def assign_app_group(client):
    d = {}

    # assign deez apps
    d[group_names[0][0]] = ['Alacritty', 'xfce4-terminal']
    d[group_names[1][0]] = ['Navigator', 'discord', 'brave-browser', 'midori', 'qutebrowser']
    d[group_names[2][0]] = ['pcmanfm', 'thunar']
    d[group_names[3][0]] = ['code', 'geany']
    d[group_names[4][0]] = ['vlc', 'obs', 'mpv', 'mplayer', 'lxmusic', 'gimp']
    d[group_names[5][0]] = ['spotify']
    d[group_names[6][0]] = ['lxappearance', 'gpartedbin', 'lxtask', 'lxrandr', 'arandr', 'pavucontrol', 'xfce4-settings-manager']

    wm_class = client.window.get_wm_class()[0]
    for i in range(len(d)):
        if wm_class in list(d.values())[i]:
            group = list(d.keys())[i]
            client.togroup(group)
            client.group.cmd_toscreen(toggle=False)


main = None
@hook.subscribe.startup
def start_once():
    start_script = os.path.expanduser("~/.config/qtile/scripts/autostart.sh")
    subprocess.call([start_script])

@hook.subscribe.startup_once
def start_always():
    # fixes the cursor
    subprocess.Popen(['xsetroot', '-cursor_name', 'left_ptr'])


dgroups_key_binder = None
dgroups_app_rules = []  # type: List
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
    Match(wm_class='Viewnior'),  # Photos/Viewnior 
    Match(wm_class='Alafloat'),  # Floating Alacritty Terminal 
    Match(title='branchdialog'),  # gitk
    Match(title='pinentry'),  # GPG key password entry
], **layout_theme)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "Qtile"
