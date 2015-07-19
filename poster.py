#!/usr/bin/python

import json
import os.path
import subprocess
import sys

habrasid = 'da7l78sajmjs9ogtjn52sa3q04'
boyarski = '/Users/majorm/Downloads/346272.jpg'
harrison = 'harrison.jpg'


def post(filename):
    res = json.loads(subprocess.Popen(["curl",\
        "--cookie", "habrastorage_sid={0}".format(habrasid),\
        "--form", "files[]=@{0}".format(filename),\
        "--header", "X-Requested-With: XMLHttpRequest",\
        "--header", "Referer: http://habrastorage.org/",\
        "--request", "POST", "https://habrastorage.org/main/upload",\
        "2&>/dev/null"],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])    
    if "error" in res:
        code = res['error']['code']
        if code == 578:
            print "Error: refresh habrastorage_sid"
        else:
            print "Error: code {0}".format(code)
        sys.exit(1)
    return res['files'][0]['url']

class FormulaPool:
    FORMULAPATH_ = "path"
    FORMULALINK_ = "link"

    def getname(self, counter):
        return "{0}/f_{1}".format(self.poolname, counter)

    def __init__(self, poolname):
        self.poolname = poolname
        self.pooldesc = poolname + ".json"
        self.counter  = 0
        self.formulas = dict()
        if os.path.isfile(self.pooldesc):
            with open(self.pooldesc, 'r') as f:
                self.formulas = json.loads(f.read())
        elif not os.path.isdir(poolname):
            os.mkdir(poolname)
    
    def formula_link(self, formula):
        formula = formula.\
                    replace('+', '&plus;').\
                    replace(' ', '&space;').\
                    replace('\n', '&space;')
        return 'http://latex.codecogs.com/gif.latex?{0}'.format(formula)

    def put(self, formula):
        if formula not in self.formulas:
            while os.path.isfile(self.getname(self.counter)):
                self.counter += 1
            fname = self.getname(self.counter)
            subprocess.call(['curl', self.formula_link(formula),\
                            '-o', fname],\
                            stderr=subprocess.PIPE)
            link = post(os.path.abspath(fname))
            self.formulas[formula] = {FormulaPool.FORMULALINK_ : link,\
                                     FormulaPool.FORMULAPATH_ : fname}
        return self.formulas[formula][FormulaPool.FORMULALINK_]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        with open(self.pooldesc, 'w') as f:
            f.write(json.dumps(self.formulas))

# post(harrison)
with FormulaPool("formula") as pool:
    print pool.put('x^3')


# print post(harrison)