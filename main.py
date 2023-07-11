import requests
from bs4 import BeautifulSoup
import youtube_dl
from yt_dlp import YoutubeDL
import time

PROJECT_ID = 'melodify-2c4eb'
IS_EXTERNAL_PLATFORM = True # False if using Cloud Functions
firebase_app = None

def init_firebase():
    global firebase_app
    if firebase_app:
        return firebase_app
    import firebase_admin
    from firebase_admin import credentials

    if IS_EXTERNAL_PLATFORM:
        cred = credentials.Certificate('secrets/melodify-2c4eb-firebase-adminsdk-ydnyn-0b47ca4a6d.json')
    else:
        cred = credentials.ApplicationDefault()
    firebase_app = firebase_admin.initialize_app(cred, {
        # 'projectId': PROJECT_ID,
        'storageBucket': f"{PROJECT_ID}.appspot.com"
    })

    return firebase_app


from firebase_admin import storage
init_firebase()

bucket = storage.bucket()
blob = bucket.blob('hello.txt')
blob.upload_from_string('hello world')







def search_and_download_song(song_name):
    
    query = f"site:youtube.com {song_name}"
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('a')
    
    for result in search_results:
        # Extract the URL and title of the search result
        url = result.get("href")
        has_title = result.find("h3")
        if not has_title:
            continue
        title = has_title.text
        url = url.split("%3Fv%3D")
        url = url[1].split("&")
        url = "https://www.youtube.com/watch?v=" + url[0]

        download_song(url)
        return



def download_song(url):
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': '/out/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download([url])
    

song_name = input("Enter the song name: ")
search_and_download_song(song_name)