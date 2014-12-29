#!/usr/bin/python3


from bs4 import BeautifulSoup
import urllib
import os
import yaml

INFO = "INFO"
ERROR = "ERROR"
log_level = INFO

def log(level, msg):
        if log_level == INFO:
            print(level + ': ' + msg)
        elif log_level == ERROR:
            if level == ERROR:
                print(level + ': ' + msg)

class grabber(object):
    def getImage():
        
        while(True):
            url =  'http://c.xkcd.com/random/comic'
            found = False
                
            with urllib.request.urlopen(url) as conn:
                page = conn.read()

            soup = BeautifulSoup(page)
            image_tags = soup.find_all('img')


            for img in image_tags:
                # img[src] is the contents of the src field
                # http://imgs.xkcd.com/comics/xxxx.png
                if 'comics' in img['src']: 
                    log(INFO, 'Getting ' + img['src'])
                    
                    filename = ''
                    if '.jpg' in  img['src']:
                        filename = 'foo.jpg'
                    elif '.png' in img['src']:
                        filename = 'foo.png'
                        found = True
                    else:
                        log(ERROR, 'Did not recognize image format: ' + img['src'])
                        break
                    if(found):    
                        urllib.request.urlretrieve(img['src'], filename)
                        return filename

grabber.getImage()