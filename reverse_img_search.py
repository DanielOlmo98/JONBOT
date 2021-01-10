import requests
import discord
from bs4 import BeautifulSoup

img_extensions = [
    '.jpg',
    '.png',
    '.jpeg'
]


# adapted from https://github.com/Pruffer-zz/discord-tagger-bot/tree/4c2353b01dea23d70b8d10ed6a150e9331b2eac4
async def get_vtuber(url):
    print("cock")
    res = requests.get('https://iqdb.org/?url=' + url)
    soup = BeautifulSoup(res.text, 'html.parser')
    elems = soup.select("a[href*=danbooru] > img")
    try:
        tags = elems[0].get('title').split()[5:]
        return 'virtual_youtuber' in tags

    except:
        return False
