# Author: Vsevolod Oparin, 2015

import subprocess
import shutil
import json
import os.path
import sys

class LinkPool:
    FILEPATH_ = "path"
    HABRLINK_ = "link"

    def __init__(self, poolname, settings):
        self.poolname = poolname
        self.pooldesc = poolname + ".json"
        self.settings = settings
        self.counter  = 0

        self.links = dict()
        if os.path.isfile(self.pooldesc):
            with open(self.pooldesc, 'r') as f:
                self.links = json.loads(f.read())
        elif not os.path.isdir(poolname):
            os.mkdir(poolname)

    def post(self, filename):        
        done = False
        habrasid = self.settings.habrasid()
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
        if habrasid != self.settings.habrasid():
            self.settings.set_habrasid(habrasid)
        return res['files'][0]['url']
    
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
            habrlink = self.post(os.path.abspath(fname))
            self.links[link] = {LinkPool.HABRLINK_ : habrlink,\
                                LinkPool.FILEPATH_ : fname}
        return self.links[link][LinkPool.HABRLINK_]
        
    def save(self):
        with open(self.pooldesc, 'w') as f:
            f.write(json.dumps(self.links))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.save()