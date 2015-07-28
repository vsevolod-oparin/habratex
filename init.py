#!/usr/bin/env python

import os
import subprocess
import platform
import argparse

from   include.settings   import    Settings

parser = argparse.ArgumentParser(description='Init script.')
parser.add_argument("-l", "--link", action='store_true', help = "make symbolic link /usr/bin/poster")
args = vars(parser.parse_args())

default = "default.json"
poster  = "poster.py"
link    = "/usr/bin/poster"
settings = Settings(default)

place = "__DEFAULT_SETTINGS__"
path = os.path.dirname(os.path.abspath(default)).replace("\\", "\\\\")
with open("poster.py", "r") as f:
    code = f.read()
code = code.replace(place, "\"{0}\"".format(path))
with open("poster.py", "w") as f:
    f.write(code)

if os.name == 'nt' or platform.system() == 'Windows':
        settings.set_encoding('cp1251')

if args["link"]:
    print "Asked"
    if os.name != 'nt' and platform.system() != 'Windows':
        if not os.path.isfile(link):
            subprocess.call(["ln", "-s", os.path.abspath(poster), link])


