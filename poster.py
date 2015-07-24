#!/usr/local/bin/python

import json
import shutil
import os.path
import subprocess
import sys
import markdown2
import codecs
import argparse
import re

habrasid = '1tdl7igaof40l7rjcvjrsfgd57'

parser = argparse.ArgumentParser(description='Convert Markdown + LaTeX to habrahabr\'s format.')
parser.add_argument("-f", "--infile", required = "True", help = "Name of input file")
parser.add_argument("-o", "--outfile", required = "True", help = "Name of output file")
args = vars(parser.parse_args())


def post(filename):
    jres = subprocess.Popen(["curl",\
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
            print "Error: refresh habrastorage_sid"
        else:
            print "Error: code {0}".format(code)
        sys.exit(1)
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
        return "{0}/f_{1}".format(self.poolname, counter)

    def getnext(self):
        while os.path.isfile(self.getname(self.counter)):
            self.counter += 1
        return self.getname(self.counter)
    
    def put_formula(self, formula):
        print "Convert formula {0}".format(formula)
        return self.put_link(self.formula_link(formula))

    def put_link(self, link):
        if link not in self.links:
            fname = self.getnext()
            print link
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
        template = "<img src=\"{0}\">"
        return template.format(LinkPool.formula_link("\inline " + group[0]))



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
            print regexp
            text = self.translator(text, regexp, processor)
        text = markdown2.markdown(text)
        text = self.expand(text)
        with LinkPool("links") as pool:
            text = self.upload(text, pool)
        return text

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
        print self.postproc
        expandpattern = "HABRAPLACER[0-9]*?H"
        cur = 0
        result = ""
        pattern = re.compile(expandpattern)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            print m.group()
            result += self.postproc[m.group()].decode('utf-8')
            cur = m.end()
        result += text[cur : ]
        return result

    
    def upload(self, text, pool):
        habraind = "habrastorage"
        uploadpattern = "(<img .*?src=\\\")(.*?)(\\\">)"
        cur = 0
        result = ""
        pattern = re.compile(uploadpattern)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            link = m.group(2)
            if habraind not in link:
                print "Uploading {0}".format(link)
                link = pool.put_link(link)
            print m.group(0)
            result += "{0}{1}{2}".format(m.group(1), link, m.group(3))
            cur = m.end()
        result += text[cur : ]
        return result


 

    

conv = Convertor()
result = ""
with open(args["infile"], "r") as infile:
    result = conv.convert(infile.read()).encode('utf-8')
with open(args["outfile"], "w") as outfile:
    outfile.write(result)