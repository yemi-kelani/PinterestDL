"""
Very useful for downloading references for artwork.
Batch download all pins, on all boards, saved or created by a specified user.
Simply modify the pinterestUsername and run the script.


This only works on the first 10 boards a user has and only copies up to 25 pins per board
with file types: ['.jpg', 'jpeg', 'webp', '.png', '.gif']. (Beatiful Soup doesn't work 
well with javascript rendered pages so this isn't very comprehensive.) 
Feel free to fork this repo and modify it to pull in more pins.
@author: aak
"""

import os
import re
import json
import random
import requests
from bs4 import BeautifulSoup
pinterestUsername="" # enter username
pinterestURL="https://www.pinterest.com"

board_page = requests.get(pinterestURL + "/" + pinterestUsername + "/")
doc = BeautifulSoup(board_page.text, "html.parser")
# print(doc.prettify())
del board_page

# find boards associated with user
boards = []
for a_tag in doc.find_all('a', href=re.compile("/" + pinterestUsername + "/*")):
    boards.append(a_tag["href"])

if ("/" + pinterestUsername + "/_created") in boards:  
    boards.remove("/" + pinterestUsername + "/_created")
if ("/" + pinterestUsername + "/_saved") in boards:
    boards.remove("/" + pinterestUsername + "/_saved")

print('\n'.join('{}: {}'.format(*k) for k in enumerate(boards)))

def get_vals(pkg, key_list, randomize):
    if isinstance(pkg, dict):
        for i, j in pkg.items():
            if i in key_list:
                newkey = i+str(random.random()) if randomize else i
                yield (newkey, j)
            elif isinstance(j, list):
                for item in j:
                    yield from get_vals(item, key_list, randomize)
            else:
                yield from [] if not isinstance(j, dict) else get_vals(j, key_list, randomize)
    elif isinstance(pkg, list):
        for item in pkg:
            yield from get_vals(item, key_list, randomize)
    else:
        yield from []

def discrepancy(n, p, name):
    print(f"\n*** SUMMARY: {name}... {p} pins, expected {n} pins")
    if p - n >= 0:
        print(f"*** DISCREPENCY (+): Downloaded {p - n} extra pins \n")
    else:
        print(f"*** DISCREPENCY (-): Missing {abs(p - n)} pins \n")

# for each board associated with user, download pins
pins_downloaded = 0 
for b in boards:
    folder_name = "pins/" + b.split("/")[-2]
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    pinterestBoardURL = pinterestURL + b
    page = requests.get(pinterestBoardURL)
    doc = BeautifulSoup(page.text, "html.parser")
    pins = []
    
    # *** PULL INDIRECT LINKS ***
    
    for pin in doc.find_all('a', href=re.compile("/pin/")):
        if pinterestURL + str(pin["href"]) not in pins:
            pins.append(pinterestURL + str(pin["href"]))
    
    # *** PULL DIRECT LINKS ***
    
    # data = json.loads(doc.find("script", id="__PWS_DATA__").text)
    # data = data["props"]["initialReduxState"]
    # data = dict(get_vals(data, ["images"], True))
    # for k, v in data.items():
    #     if isinstance(v, dict) and "orig" in v.keys():
    #         url = v["orig"]["url"]
    #         if "https://i.pinimg.com/originals" in url and url not in pins:
    #             pins.append(url)
    
    n = json.loads(doc.find("script", type="application/ld+json").text)
    n = int(dict(get_vals(n, ["numberOfItems"], False))["numberOfItems"])
    p = len(pins)
    del page, doc
    
    cwd = os.getcwd()
    os.chdir(folder_name)
    print("Current working directory: {0}".format(os.getcwd()))
    
    for pin in pins:
        os.system(f"gallery-dl {pin}")
    
    os.chdir(cwd)
    print("Current working directory: {0}".format(os.getcwd()))
    pins_downloaded += p
    discrepancy(n, p, folder_name.split("/")[-1])
    
print(f"Total pins downloaded: {pins_downloaded} pins")

# organize the folders
import glob
import shutil

m = 0
cwd = os.getcwd()
folders = next(os.walk("pins"))[1]
for f in folders:
    source = cwd + "/pins/" + f + "/gallery-dl/pinterest/*"
    dest = cwd + "/pins/" + f 

    files = glob.glob(os.path.join(source), recursive=True)
    for file in files:
        if file[-4:].lower() in ('.jpg', 'jpeg', 'webp', '.png', '.gif'):
            dst = os.path.join(dest, os.path.basename(file))
            shutil.move(file, dst)
            m += 1
        else:
            print(file[-4:].lower())
    
    shutil.rmtree(cwd + "/pins/" + f + "/gallery-dl")

print(f"Organized {m} files.")