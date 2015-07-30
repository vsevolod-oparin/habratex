# Author: Vsevolod Oparin, 2015

import re
import markdown2
import sys

from ruleholder import RuleHolder
import ruleholder

class Convertor:

    def __init__(self, settings, pool):        
        self.placecnt = 0
        self.postproc = {}
        self.settings = settings
        self.pool = pool
        while settings.formulas() not in ruleholder.fsources:
            print "Key {0} has not been found. Try the next options:\n{1}".\
                format(settings.formulas(), " ".join(list(ruleholder.fsources)))
            print ">", 
            formulas = sys.stdin.readline().strip()
            if formulas in ruleholder.fsources:
                settings.set_formulas(formulas)
            else:
                print "Bad name"
                exit(1)
        RuleHolder.fsource = ruleholder.fsources[settings.formulas()]

    def convert(self, text):
        for regexp, processor in ruleholder.rules:
            text = self.translator(text, regexp, processor)
        text = markdown2.markdown(text)
        text = self.refine(text)
        text = self.expand(text)
        for regexp, processor in ruleholder.postrules:
            text = self.posttran(text, regexp, processor)
        return text.encode(self.settings.encoding())

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
            result += self.postproc[m.group()].decode(self.settings.encoding())
            cur = m.end()
        result += text[cur : ]
        return result

    def posttran(self, text, regexp, processor):
        cur = 0
        result = ""
        pattern = re.compile(regexp)
        for m in pattern.finditer(text):
            result += text[cur : m.start()]
            result += processor(m.groups(), self.pool)
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
        text = self.placement_refine(text, "(\\s*HABRAPLACER[0-9]*?H\\s*)", "{0}\n\n", RuleHolder.is_cut)        
        text = self.placement_refine(text, "(\\s*HABRAPLACER[0-9]*?H)", "\n\n{0}", RuleHolder.not_inline)
        text = self.placement_refine(text, "(HABRAPLACER[0-9]*?H\\s*)", "{0}\n", RuleHolder.not_inline)
        
        for tag in reline_tags:
            text = re.sub("(</{0}.*?>)\\s*".format(tag), "\\1\n", text)            
        return text.strip()
