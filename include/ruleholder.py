import urllib

fsources = {\
    'codecogs': 'http://latex.codecogs.com/gif.latex?{0}',\
    'texsvg': "http://tex.s2cms.ru/svg/{0}",\
    'texpng': 'http://tex.s2cms.ru/png/{0}'
}
default_key = 'codecogs'

class RuleHolder:
    fsource = fsources['codecogs']

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
            return "<cut>" if title == "" else "<cut text=\"{0}\">".format(title)
        return "<cut>"

    @staticmethod
    def formula_link(formula):    
        return RuleHolder.fsource.format(\
                    urllib.quote(formula).\
                    replace("/", "%2F").\
                    replace("\\", "%5C"))
        
    @staticmethod
    def centerformula(group):
        template = "<img align=\"center\" src=\"{0}\">"
        return template.format(RuleHolder.formula_link(group[0]))

    @staticmethod
    def inlineformula(group):
        template = "<img src=\"{0}\" alt=\"inline_formula\">"
        return template.format(RuleHolder.formula_link("\inline " + group[0]))

    @staticmethod
    def img_align(group, pool):
        if group[2] in ["left", "right", "center"]:
            return "".join([group[0], "align=\"{0}\"".format(group[2]), group[3]])
        return "".join([group[0], group[1], group[3]])

    @staticmethod
    def upload(group, pool):
        habraind = "habrastorage"
        texs2svg = "tex.s2cms.ru/svg"
        link = group[1]
        if habraind not in link and texs2svg not in link:
            link = pool.put_link(link)
        return "{0}{1}{2}".format(group[0], link, group[2])
    
    @staticmethod
    def is_cut(text):
        return "<cut" in text

    @staticmethod
    def not_inline(text):
        return "inline_formula" not in text and "<cut" not in text

    
rules = [\
    ("```((.*?\\s?)*?)```",     RuleHolder.source),\
    ("\$\$((.*?\\s?)*?)\$\$",   RuleHolder.centerformula),\
    ("\$((.*?\\s?)*?)\$",       RuleHolder.inlineformula),\
    ("<!--\s*?cut(.*?)-->",     RuleHolder.cut),\
    ] 


postrules = [("(<img .*?src=\\\")(.*?)(\\\".*?/?>)", RuleHolder.upload),\
             ("(<img.*?)(alt=\"(.*?)\")(.*?/?>)",    RuleHolder.img_align)]
