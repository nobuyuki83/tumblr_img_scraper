import cv2
import urllib.request
import os, sys
from bs4 import BeautifulSoup
import shutil, glob, random, pickle

def get_csv_data(path_csv):
    assert os.path.isfile(path_csv)
    path_input = path_csv.rsplit('/', 1)[0]
    bn = os.path.basename(path_csv)
    assert bn.rsplit(".", 1)[1] == "csv"  # check extension
    lines = []
    with open(path_csv, 'r') as fin:
        lines = fin.readlines()
    #    print(lines)
    dict_data = {}
    for line in lines:
        aS = line.split(',', 1)
        if len(aS) != 2: continue
        name = aS[0]
        data = aS[1]
        if data.endswith("\n"):
            data = data.split("\n")[0]
        #        print(name,data)
        dict_data[name] = data
    return dict_data

def get_list_img_url(url):
    url_list = []

    try:
        page = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print(e.reason)
        return url_list
    except UnicodeError:
        return url_list

    soup = BeautifulSoup(page, 'html.parser')

    for link in soup.find_all('img'):
        src = link.get("src")
        if src is None:
            continue
        if src.endswith(".jpg") or src.endswith(".png"):
            url_list.append(src)

    for link in soup.find_all('div'):
        src = link.get("data-imageurl")
        if src is None: continue
        if src.endswith(".gif"):  continue
        url_list.append(src)

    return url_list


def save_image_in_url(url_img, dir_dist_root,
                      set_ignore_old, set_ignore_new, set_ignore_name):

    list_url_img = get_list_img_url(url_img)

    print(len(list_url_img),"figures in the"+url_img)

    for url_img in list_url_img:

        #### check if it is already looked
        if not url_img.startswith('http'):
            continue
        if (url_img in set_ignore_new) or (url_img in set_ignore_old):
            continue
        bn = os.path.basename(url_img)
        if bn in set_ignore_name:
            set_ignore_new.add(url_img)
            print("name found!",bn)
            continue

        #### get image and load
        try:
            urllib.request.urlretrieve(url_img, bn)
        except urllib.error.URLError as e:
            print(e.reason)
            continue

        img = cv2.imread(bn)
        cv2.imshow('img', img)
        cv2.waitKey(50)
        set_ignore_new.add(url_img)
        shutil.move(bn, dir_dist_root + "/xinbox/" + bn)

    cv2.destroyAllWindows()


def initialize_dir(path_dir):
    hex = [str(format(i,'x')) for i in range(0,16)]
    hex.append('xinbox')
    hex.append('xtrash')
    print(hex)
    for ch in hex:
        if not os.path.isdir(path_dir+"/"+ch):
            os.mkdir(path_dir+"/"+ch)

def load_ignore(path_dir):
    set_ignore_url_old = []
    for ind_ignore_url in range(100):
        if not os.path.isfile(path_dir + "/list_ignore_url_" + str(ind_ignore_url) + ".txt"):
            break
        with open(path_dir + "/list_ignore_url_" + str(ind_ignore_url) + ".txt", 'r') as f:
            data = f.read()
            set_ignore_url_old += data.split('\n')
    set_ignore_url_old = set(set_ignore_url_old)

    #    print(list_usr)
    print("size_ignore_url:", len(set_ignore_url_old), ind_ignore_url)

    set_ignore_name = []
    if os.path.isfile(path_dir+"/set_ignore_name.p"):
        set_ignore_name = pickle.load(open(path_dir + "/set_ignore_name.p", "rb"))
    else:
        for path_csv in glob.glob(path_dir + "/**/*.csv", recursive=True):
            dict_data = get_csv_data(path_csv)
            if "url_name" in dict_data:
                set_ignore_name.append(dict_data["url_name"])
    set_ignore_name = set(set_ignore_name)
    for path_img in glob.glob(path_dir + "/xtrash/*"):
        name = path_img.rsplit("/", 1)[1]
        set_ignore_name.add(name)
    for path_img in glob.glob(path_dir + "/xinbox/*"):
        name = path_img.rsplit("/", 1)[1]
        set_ignore_name.add(name)
    print("size_ignore_name:", len(set_ignore_name))
    pickle.dump(set_ignore_name, open(path_dir + "/set_ignore_name.p", "wb"))
    return set_ignore_url_old,set_ignore_name,ind_ignore_url

def main():
    if len(sys.argv) != 2:
        print("argument missing")
        exit()

    path_dir = sys.argv[1]
    assert os.path.isdir(path_dir)

    initialize_dir(path_dir)

    list_usr = []
    with open(path_dir + "/usr_tumblr.txt", 'r') as f:
        data = f.read()
        list_usr = data.split('\n')

    set_ignore_url_old, set_ignore_name, ind_ignore_url = load_ignore(path_dir)
    set_ignore_url_new = set()

    order = list(range(len(list_usr)))
    random.shuffle(order)
    for ind_usr in order:
        usr = list_usr[ind_usr]
        if usr.find('@') != -1: continue
        url = "http://" + usr + ".tumblr.com/"
        save_image_in_url(url, path_dir,
                          set_ignore_url_old, set_ignore_url_new, set_ignore_name)
        url = "http://" + usr + ".tumblr.com/archive"
        save_image_in_url(url, path_dir,
                          set_ignore_url_old, set_ignore_url_new, set_ignore_name)

        print(ind_usr, len(list_usr))

        if ind_usr % 10 != 1: continue
        pickle.dump(set_ignore_name, open(path_dir + "/set_ignore_name.p", "wb"))
        with open(path_dir + "/list_ignore_url_"+str(ind_ignore_url)+".txt", 'w') as f:
            list_url = list(set_ignore_url_new)
            for url in list_url:
                f.write(url + "\n")


if __name__ == "__main__":
    main()
