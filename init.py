#!/usr/bin/env python

import os
import subprocess
import platform
import argparse

parser = argparse.ArgumentParser(description='Init script.')
parser.add_argument("-l", "--link", action='store_true', help = "make symbolic link /usr/bin/poster")
args = vars(parser.parse_args())

default = "default.json"
poster  = "poster.py"
link    = "/usr/bin/poster"

place = "__DEFAULT_SETTINGS__"
path = os.path.abspath(default).replace("\\", "\\\\")
with open("poster.py", "r") as f:
    code = f.read()
code = code.replace(place, "\"{0}\"".format(path))
with open("poster.py", "w") as f:
    f.write(code)

if args["link"]:
    print "Asked"
    if os.name == 'nt' or platform.system() == 'Windows':
        os.mkdir("win")
        subprocess(["mklink", "win\\poster", os.path.abspath(poster)])
        subprocess(["setx", "PATH", "%PATH%;{0}".format(os.path.abspath("win"))])
    else:
        if not os.path.isfile(link):
            subprocess.call(["ln", "-s", os.path.abspath(poster), link])


