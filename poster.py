#!/usr/bin/python

import json
import subprocess

habrasid = 'v963oee7u4gurtkqkufleu7qn1'
boyarski = '/Users/majorm/Downloads/346272.jpg'
harrison = 'harrison.jpg'

def post(filename):
    res = subprocess.Popen(["curl",\
        "--cookie", "habrastorage_sid={0}".format(habrasid),\
        "--form", "files[]=@{0}".format(filename),\
        "--header", "X-Requested-With: XMLHttpRequest",\
        "--header", "Referer: http://habrastorage.org/",\
        "--request", "POST", "https://habrastorage.org/main/upload",\
        "2&>/dev/null"],\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    return json.loads(res)['files'][0]['url']

print post(harrison)