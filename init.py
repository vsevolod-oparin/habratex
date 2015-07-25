#!/usr/bin/env python

import os

default = "default.json"
place = "__DEFAULT_SETTINGS__"
path = os.path.abspath(default).replace("\\", "\\\\")
with open("poster.py", "r") as f:
    code = f.read()
code = code.replace(place, "\"{0}\"".format(path))
with open("poster.py", "w") as f:
    f.write(code)

