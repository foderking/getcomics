#!/usr/bin/python3
import re, requests
from bs4 import BeautifulSoup
import shutil, os, sys

c = {
    "h": "\033[95m",
    "b": "\033[94m",
    "g": "\033[92m",
    "r": "\033[91m",
    "end": "\033[0m",
}

valid = re.compile("https:\/\/www.comicextra.com\/comic\/[a-z0-9-]+")
links = [each.strip().lower() for each in open("links.txt").readlines()]

def getHtmlSoup(link):
    source = requests.get(link)
    text = source.text
    return BeautifulSoup(text, "html.parser")

       
def parseComicName(link):
    # Gets the url and name of the comic
    if not valid.match(link):
        raise ValueError(f'\n{ c["r"] }The Link is not in the proper format.\nOnly comicextra links are supported...\n{link}{ c["end"] }')
    tmp = link.split("/")
    return tmp[4]

def getChapterLinks(comic):
    s = getHtmlSoup(comic)
    return [each["href"] for each in s.table.find_all("a")][::-1] # reversed cause I noticed chapters are sorted by newest

def getChapterPages(page_link):
    soup = getHtmlSoup(page_link+"/full")
    return [each["src"] for each in soup.find_all("img", class_="chapter_img")]

def makeTmpFolder(root, comic):
    # An error would be raised if something goes wrong
    try:
        dirName = f"{root}/{comic}"
        os.mkdir(dirName)
        print(c["g"], "[+] Created tmp folder: " , dirName, c["end"]) 
    except BaseException as err:
        print(c["r"], "Unable to create tmp folder. Maybe you're downloading a duplicate?", c["end"])
        #raise

def downloadAllPages(pages, base_folder):
    all = enumerate(pages)
    for i, name in all:
        print(f" Downloading page {i}", end="\r")
        r = requests.get(name, stream=True)
        if r.status_code == requests.codes.ok:
            with open(f"downloads/{base_folder}/{i}.jpg", 'wb') as f:
                for data in r:
                    f.write(data)
    print()

def zipFile(filename, desination_folder):
    shutil.make_archive(filename, "zip", desination_folder)

def printinfo(message):
    print(c["g"], "[+]", message, c["end"])

def printblue(message):
    print(c["b"], "[+]", message, c["end"])

def printwarn(message):
    print(c["r"], "[+]", message, c["end"])

def doComic(comic_url):
    # get name
    comic_name = parseComicName(comic_url)
    # create tmp folder
    makeTmpFolder("downloads", comic_name)
    makeTmpFolder("comics", comic_name)
    # get links to all chapters of the comic 
    chapters = getChapterLinks(comic_url)
    print("="*30)
    printinfo(f"To download: {len(chapters)} chapters for {comic_name}")
    print("="*30)
    for chapter in chapters:
        chp = chapter.split("/")
        folder_name = comic_name + "/" + chp[-1]

        if os.path.exists("downloads/"+folder_name):
            printwarn(f"{chp[-1]} has already been downloaded")
            continue
        printblue(f"Working on {chp[-1]}")
        # create folder for each chapter
        makeTmpFolder("downloads", folder_name)
        # downloads all the pages in chapter
        all_pages = getChapterPages(chapter)
        downloadAllPages(all_pages, folder_name)

        print(" Download success!.")
        # creates a zipped file of the whole chapter in working directory
        printinfo("Moving file to comic dir")
        zipFile(chp[-1], "downloads/"+folder_name)
        # moves the file in cbz format to the comics folder
        renameFile(chp[-1], comic_name)
        print(" Finished download all chapters")

def renameFile(filename, root):
    os.rename(filename+".zip", "comics/"+root+"/"+filename+".cbz")

def main():
    try:
        os.mkdir("downloads")
    except:
        pass
    try:
        os.mkdir("comics")
    except:
        pass
    
    links = [each.strip() for each in open("links.txt", "r").readlines()]
    for link in links:
        doComic(link)


# TODO: 
# - continue downloads from where they stop
# - choose between zip and cbz
if __name__ == "__main__":
    main()