#!/usr/bin/env python
# Vsevolod Oparin, 2015

import json
import shutil
import os.path
import subprocess
import sys
import argparse
import re

import attached.pyperclip as pyperclip
import attached.markdown2 as markdown2

default_setfile  = __DEFAULT_SETTINGS__

parser = argparse.ArgumentParser(description='Convert Markdown + LaTeX to habrahabr\'s format.')
parser.add_argument('infile', metavar='INFILE', nargs=1,
                   help='Name of input file')
parser.add_argument("-o", "--outfile", help = "Name of output file")
parser.add_argument("-s", "--habrasid", help = "Habrastorage session id")
parser.add_argument("-e", "--encoding", help = "Name of output file")
parser.add_argument("-c", "--clipboard", action='store_true', help = "Copy result to clipboard")
args = vars(parser.parse_args())

default_habrasid  = None # '1tdl7igaof40l7rjcvjrsfgd57'
default_encoding  = None # 'utf-8'
default_directory = os.path.dirname(os.path.abspath(default_setfile))

key_habrasid = "habrasid"
key_encoding = "encoding"

with open(default_setfile, "r") as f:
    settings = json.loads(f.read())
    default_habrasid  = settings[key_habrasid]
    default_encoding  = settings[key_encoding]

habrasid = args["habrasid"] or default_habrasid
encoding = args["encoding"] or default_encoding

def post(filename):
    global habrasid
    done = False
    old = habrasid
    while not done:
        jres = subprocess.Popen(["curl",\
            "-k",\
            "--cookie", "habrastorage_sid={0}".format(habrasid),\
            "--form", "files[]=@{0}".format(filename),\
            "--header", "X-Requested-With: XMLHttpRequest",\
            "--header", "Referer: http://habrastorage.org/",\
            "--request", "POST", "https://habrastorage.org/main/upload",\
            "2&>/dev/null"],\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        res = json.loads(jres)    
        if "error" in res:
            code = res['error']['code']
            if code == 578:
                print "Refresh habrastorage_sid: ",
                habrasid = sys.stdin.readline().strip()
            else:
                print "Error: code {0}".format(code)
            if habrasid in ["", "exit", "quit", "q", "e"]:
                sys.exit(1)
        else:
            done = True
    if habrasid != old:
        settings = {}
        with open(default_setfile, "r") as f:
            settings = json.loads(f.read())
        settings[key_habrasid] = habrasid
        with open(default_setfile, "w") as f:
            f.write(json.dumps(settings))
    return res['files'][0]['url']

class LinkPool:
    FILEPATH_ = "path"
    HABRLINK_ = "link"

    def __init__(self, poolname):
        self.poolname = poolname
        self.pooldesc = poolname + ".json"
        self.counter  = 0
        self.links = dict()
        if os.path.isfile(self.pooldesc):
            with open(self.pooldesc, 'r') as f:
                self.links = json.loads(f.read())
        elif not os.path.isdir(poolname):
            os.mkdir(poolname)
    
    def getname(self, counter):
        return os.path.join(self.poolname, "f_{0}".format(counter))

    def getnext(self):
        while os.path.isfile(self.getname(self.counter)):
            self.counter += 1
        return self.getname(self.counter)
    
    def put_formula(self, formula):
        return self.put_link(self.formula_link(formula))

    def put_link(self, link):
        if link not in self.links:
            print "Uploading link {0}".format(link)
            fname = self.getnext()
            if os.path.isfile(link):
                shutil.copyfile(link, fname)
            else:
                subprocess.call(['curl', link,\
                                '--globoff',\
                                '-o', fname],\
                                stderr=subprocess.PIPE)
            habrlink = post(os.path.abspath(fname))
            self.links[link] = {LinkPool.HABRLINK_ : habrlink,\
                                LinkPool.FILEPATH_ : fname}
        return self.links[link][LinkPool.HABRLINK_]

    @staticmethod
    def formula_link(formula):
        formula = formula.\
                    replace('+', '&plus;').\
                    replace(' ', '&space;').\
                    replace('\n', '&space;')
        return 'http://latex.codecogs.com/gif.latex?{0}'.format(formula)

    def save(self):
        with open(self.pooldesc, 'w') as f:
            f.write(json.dumps(self.links))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()

class Processor:

    @staticmethod
    def source(group):
        body = group[0]
        splitter = body.find('\n')
        if splitter == -1:
            return body
        lang = body[0 : body.find('\n')].strip()
        result = "<source"
        if lang != "":
            result += " lang=\"{0}\"".format(lang)
        result += ">{0}</source>".format(body[splitter : ])
        return result

    @staticmethod
    def cut(group):
        if (len(group) > 0):
            title = group[0].strip()
            return "<cut>" if title == "" else "<cut title=\"{0}\">".format(title)
        return "<cut>"

    @staticmethod
    def centerformula(group):
        template = "<img align=\"center\" src=\"{0}\">"
        return template.format(LinkPool.formula_link(group[0]))

    @staticmethod
    def inlineformula(group):
        template = "<img src=\"{0}\" alt=\"inline_formula\">"
        return template.format(LinkPool.formula_link("\inline " + group[0]))

    
    @staticmethod
    def is_cut(text):
        return "<cut" in text

    @staticmethod
    def not_inline(text):
        return "inline_formula" not in text and "<cut" not in text



class Convertor:

    def __init__(self):        
        self.placecnt = 0
        self.postproc = {}

    def convert(self, text):
        rules = [\
            ("```((.*?\\s?)*?)```", Processor.source),\
            ("\$\$((.*?\\s?)*?)\$\$", Processor.centerformula),\
            ("\$((.*?\\s?)*?)\$", Processor.inlineformula),\
            ("<!--cut(.*?)-->", Processor.cut)] 

        for regexp, processor in rules:
            text = self.translator(text, regexp, processor)
        text = markdown2.markdown(text)
        text = self.refine(text)
        text = self.expand(text)
        with LinkPool("links") as pool:
            text = self.upload(text, pool) 
        return text.encode(encoding)

    def translator(self, text, regexp, processor):
        habraplacer = "HABRAPLACER{0}H"
        cur = 0
        result = ""
        pattern = re.compile(regexp)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            placer = habraplacer.format(self.placecnt)
            self.placecnt += 1
            result += placer
            self.postproc[placer] = processor(m.groups())
            cur = m.end()
        result += text[cur : ]
        return result

    
    def expand(self, text):
        expandpattern = "HABRAPLACER[0-9]*?H"
        cur = 0
        result = ""
        pattern = re.compile(expandpattern)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            result += self.postproc[m.group()].decode(encoding)
            cur = m.end()
        result += text[cur : ]
        return result

    
    def upload(self, text, pool):
        habraind = "habrastorage"
        uploadpattern = "(<img .*?src=\\\")(.*?)(\\\".*?/?>)"
        cur = 0
        result = ""
        pattern = re.compile(uploadpattern)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            link = m.group(2)
            if habraind not in link:
                #print "Uploading {0}".format(link)
                link = pool.put_link(link)
            result += "{0}{1}{2}".format(m.group(1), link, m.group(3))
            cur = m.end()
        result += text[cur : ]
        return result

    def placement_refine(self, text, regex, format, pred):
        pattern = re.compile(regex)
        tokens = pattern.split(text)
        outtok = []
        for t in tokens:
            if pattern.match(t) != None\
                and pred(self.postproc[t.strip()]):
                    outtok.append(format.format(t.strip()))
            else:
                outtok.append(t)
        return "".join(outtok)


    def refine(self, text):
        placepatternb = re.compile("(\\s*HABRAPLACER[0-9]*?H)")
        text = text.replace("<p>", "").\
                    replace("</p>", "")
        reline_tags = ["h1", "h2", "h3", "h4", "h5", "ol", "ul"]
        for tag in reline_tags:
            text = re.sub("\\s*(<{0}.*?>)".format(tag), "\\n\\n\\1", text)
        text = self.placement_refine(text, "(\\s*HABRAPLACER[0-9]*?H\\s*)", "{0}\n\n", Processor.is_cut)        
        text = self.placement_refine(text, "(\\s*HABRAPLACER[0-9]*?H)", "\n\n{0}", Processor.not_inline)
        text = self.placement_refine(text, "(HABRAPLACER[0-9]*?H\\s*)", "{0}\n", Processor.not_inline)
        
        for tag in reline_tags:
            text = re.sub("(</{0}.*?>)\\s*".format(tag), "\\1\n", text)            
        return text.strip()
    
conv = Convertor()
inname = args["infile"][0]
markdown = ""
if inname == "clipboard":
    args["clipboard"] = True
    if not os.path.isdir(default_directory):
        os.mkdir(default_directory)
    os.chdir(default_directory)
    markdown = pyperclip.paste()
    with open(inname + ".md", "w") as infile:
        to_save = markdown
        if encoding != 'utf-8':
            to_save = markdown.encode(encoding)
        infile.write(to_save)
else:
    inname = os.path.abspath(inname)
    os.chdir(os.path.dirname(inname))
    with open(inname, "r") as infile:
        markdown = infile.read()

outname = args["outfile"] or (re.sub("\..*?$", "", inname) + ".txt")
result = conv.convert(markdown)
if "clipboard" in args:
    pyperclip.copy(result)
with open(outname, "w") as outfile:
    outfile.write(result)
print "Done"