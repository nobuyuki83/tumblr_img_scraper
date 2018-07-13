import cv2, matplotlib
import numpy as np
import matplotlib.pyplot as plt
import urllib.request
import os, sys
from bs4 import BeautifulSoup


def getUrlListUsr_Pages(usr, ipage):
    url = "https://" + usr + ".tumblr.com/following/page/" + str(ipage)

    req = urllib.request.Request(url)
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
        exit()

    soup = BeautifulSoup(page, 'html.parser')

    usr_list = []
    for link in soup.find_all('a'):
        src = link.get("href")
        if src == None: continue
        tokens = src.split(".")
        usr = tokens[0]
        iu = usr.rfind('/')
        usr = usr[iu + 1:]
        if usr == "likes": continue
        if usr == "following": continue
        if usr == "archive": continue
        if usr == 'staff': continue
        if usr == 'www': continue
        if usr == 'ask': continue
        if usr == 'blog': continue
        if usr == 'last': continue
        if usr == 'faq': continue
        if len(usr) < 3: continue
        usr_list.append(usr)
    usr_list = list(set(usr_list))
    return usr_list


def main():
    if len(sys.argv) != 2:
        print("argument missing")
        exit()

    usr = sys.argv[1]
    usr_list = []
    for ipage in range(500):
        ul = getUrlListUsr_Pages(usr, ipage)
        print(ul)
        print(ipage, len(ul))
        nul0 = len(usr_list)
        usr_list.extend(ul)
        usr_list = list(set(usr_list))
        nul1 = len(usr_list)
        if nul0 == nul1: break
    print(usr_list)
    print(len(usr_list))
    with open("usr_tumblr.txt", "w") as fout:
        for usr in usr_list:
            fout.write(usr + "\n")


if __name__ == "__main__":
    main()


