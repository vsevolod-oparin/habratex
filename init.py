#!/usr/bin/env python

import os
import subprocess

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

if os.name == 'nt' or platform.system() == 'Windows':
    os.mkdir("win")
    subprocess(["mklink", "win\\poster", os.path.abspath(poster)])
    subprocess(["setx", "PATH", "%PATH%;{0}".format(os.path.abspath("win"))])
else:
    subprocess.call(["ln", "-s", os.path.abspath(poster), link])


