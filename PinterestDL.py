"""
Very useful for downloading references for artwork.
Batch download all pins, on all boards, saved or created by a specified user.
Simply modify the pinterestUsername and run the script.
@author: aak
"""

import os
import re
import requests
from bs4 import BeautifulSoup
pinterestUsername=""
pinterestURL="https://www.pinterest.com"

board_page = requests.get(pinterestURL + "/" + pinterestUsername + "/")
doc = BeautifulSoup(board_page.text, "html.parser")
del board_page
# print(doc.prettify())

# find boards associated with user
boards = []
for a_tag in doc.find_all('a', href=re.compile("/" + pinterestUsername + "/*")):
    boards.append(a_tag["href"])

boards.remove("/" + pinterestUsername + "/_created")
boards.remove("/" + pinterestUsername + "/_saved")

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
    for pin in doc.find_all('a', href=re.compile("/pin/")):
        pins.append(pin["href"])
    
    del page, doc
    
    
    os.system(f"pushd {folder_name}; pwd")
    for pin in pins:
        os.system(f"gallery-dl {pinterestURL + pin}")
    
    os.system("popd; pwd")
    pins_downloaded += len(pins)
    print(f"{folder_name}: {len(pins)}")

print(f"Total pins downloaded: {pins_downloaded} pins")