from psycopg2 import extras 
from bs4 import BeautifulSoup
from string import ascii_lowercase
from datetime import date
from secrets import ip, name, user, pssw, key

import requests, random, time, lyricsgenius, psycopg2

connection = psycopg2.connect(dbname=name, user=user, password=pssw, host=ip)
sql = connection.cursor()


def sql_insert(band_name=None, album=None, song_name=None, lyrics=None, image_url=None, year=None, url=None):
    t = date.today()

    print("*"*50)
    print("band_name", band_name)
    print("album", album)
    print("song_name", song_name)
    print("lyrics", lyrics[0])
    print("image_url", image_url)
    print("year", year)
    print("url", url)
    print("*"*50)
    
    sql.execute(f"""INSERT INTO "Lyrics"."Genius" (band_name, album, song_name, lyrics, image_url, year, date_added, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (band_name, album, song_name, lyrics, image_url, year, t, url))

    connection.commit()

    

def get_artists():
    f = open("artists.txt", "a+")
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"}

    for letter in ascii_lowercase:
        print(letter)
        url = f"https://genius.com/artists-index/{letter}"
        req = requests.get(url, headers= headers)
        soup = BeautifulSoup(req.text, "lxml")

        try:
            cont = soup.find("ul", {"class": "artists_index_list"})

            bands = cont.find_all("li", {"class": "artists_index_list-popular_artist"})
            for band in bands:
                bName = band.find("a")
                f.write(bName.text + "\n")

            indiv_cont = soup.find_all("ul", {"class": "artists_index_list"})[1]
            artists = indiv_cont.find_all("a")
            for artist in artists:
                f.write(artist.text + "\n")
            time.sleep(3)

        except:
            print(url)
            f.close()
            break
    f.close()


def find(data):
    final = {}
    final["lyrics"] = data["lyrics"]

    if data["album"]:
        if data["album"]["name"] is not None:
            final["album"] = data["album"]["name"]
        else: final["album"] = None
    else: final["album"] = None

    if data["title"] is not None:
        final["song_name"] = data["title"]
    else: final["song_name"] = None

    if data["song_art_image_url"] is not None:
        final["image"] = data["song_art_image_url"]
    else: final["image"] = None

    if data["release_date"] is not None:
        final["date"] = data["release_date"]
    else: final["date"] = None

    if data["media"]:
        if data["media"][0]:
            if data["media"][0]["url"] is not None:
                final["url"] = data["media"][0]["url"]
            else: final["url"] = None
        else: final["url"] = None
    else: final["url"] = None

    return final


def get_lyrics():
    genius = lyricsgenius.Genius(key, sleep_time=20, timeout=10000000)
    genius.verbose = True # For debug set to True
    f = open("artists.txt", "r")
    artists = [artist.replace("\n", "") for artist in f]
    for artist in artists:
        art = genius.search_artist(artist, sort="title")
        for song in art.songs:
            d = song.to_dict()
            data = find(d)
            try:
                if data["lyrics"][0]:
                    sql_insert(band_name=artist, album=data["album"], song_name=data["song_name"], lyrics=data["lyrics"], image_url=data["image"], year=data["date"], url=data["url"])
            except IndexError:
                pass

        time.sleep(5)
    time.sleep(120)


get_lyrics()
