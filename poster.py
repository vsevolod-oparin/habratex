#!/usr/bin/env python
# Author: Vsevolod Oparin, 2015

import re
import os.path
import argparse

import include.pyperclip  as        pyperclip
from   include.linkpool   import    LinkPool
from   include.settings   import    Settings
from   include.convertor  import    Convertor

default_directory   = "/Users/majorm/project/habratex"
pool_name           = "links"
default_setfile     = os.path.join(default_directory, "default.json")
settings            = Settings(default_setfile)

parser = argparse.ArgumentParser(description='Convert Markdown + LaTeX to habrahabr\'s format.')
parser.add_argument('infile', metavar='INFILE', nargs=1,
                   help='Name of input file')
parser.add_argument("-o", "--outfile", help = "Name of output file")
parser.add_argument("-c", "--clipboard", action='store_true', help = "Copy result to clipboard")
args = vars(parser.parse_args())


inname = args["infile"][0]
markdown = ""
if inname == "clipboard":
    args["clipboard"] = True
    if not os.path.isdir(default_directory):
        os.mkdir(default_directory)
    os.chdir(default_directory)
    markdown = pyperclip.paste()
    with open(inname + ".md", "w") as savefile:
        to_save = markdown
        if settings.encoding() != 'utf-8':
            to_save = markdown.encode(settings.encoding())
        savefile.write(to_save)
else:
    inname = os.path.abspath(inname)
    os.chdir(os.path.dirname(inname))
    with open(inname, "r") as infile:
        markdown = infile.read()

with LinkPool(pool_name, settings) as pool:    
    conv = Convertor(settings, pool)
    result = conv.convert(markdown)

if "clipboard" in args:
    pyperclip.copy(result)
outname = args["outfile"] or (re.sub("\..*?$", "", inname) + ".txt")
with open(outname, "w") as outfile:
    outfile.write(result)

print "Done"