import requests
from bs4 import BeautifulSoup
import youtube_dl
from yt_dlp import YoutubeDL
import time
import glob
import os
import uuid
from firebase_admin import storage
import csv
from firebase_admin import firestore
import random


PROJECT_ID = 'melodify-78c44'
IS_EXTERNAL_PLATFORM = True # False if using Cloud Functions
firebase_app = None

def init_firebase():
    global firebase_app
    if firebase_app:
        return firebase_app
    import firebase_admin
    from firebase_admin import credentials

    if IS_EXTERNAL_PLATFORM:
        cred = credentials.Certificate('secrets/melodify-78c44-firebase-adminsdk-fu3dg-64f4f032d9.json')
    else:
        cred = credentials.ApplicationDefault()
    firebase_app = firebase_admin.initialize_app(cred, {
        # 'projectId': PROJECT_ID,
        'storageBucket': f"{PROJECT_ID}.appspot.com"
    })

    return firebase_app

def get_files_inside_out_folder():
    folder_path = 'out'
    # Get all file names in the folder
    file_names = os.listdir(folder_path)
    return [os.path.join(folder_path, file_name) for file_name in file_names]

def upload_file_to_firebase(path , upload_dict):
    bucket = storage.bucket()
    local_file_path = path

    try:
        destination_filename = str(uuid.uuid4()) + ".m4a"
        destination_blob_name = 'songs/' + destination_filename

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        db = firestore.client()

        data = upload_dict
        data['destination_path'] = destination_blob_name

        data = preprocess_data(data)

        doc_ref = db.collection('songs').add(data)
        print(f"Document added with ID: {doc_ref[1].id}")
    except OSError as e:
        print(f"Error deleting the file: {e}")


def search_and_download_song(song_name):
    
    query = f"site:youtube.com {song_name}"
    search_url = f"https://www.google.com/search?q={query}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('a')
    
    # print("soup is -> " , soup)

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

        thumbnail = fetch_thumbnail(url)
        saved_path = download_song(url)
        
        out_dict = {
            "url" : url,
            "thumbnail" : thumbnail,
            "path" : saved_path
        }
        
        return out_dict

def fetch_thumbnail(url):
    video_url = url
    response = requests.get(video_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    thumbnail_element = soup.find('meta', property='og:image')
    thumbnail_url = thumbnail_element['content']

    return thumbnail_url

def download_song(url):
    uuid_string = str(uuid.uuid4())
    title_save_name = '/out/'+uuid_string+'.%(ext)s'
    title_return_name = 'out/'+uuid_string+'.%(ext)s'

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': title_save_name,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }

    try:

        with YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', None)
            ext = 'm4a'
            return title_return_name

    except Exception as e:
        print(str(e))

def read_data_file():

    data_files = ['data/1.csv']
    out_list = []

    with open(data_files[0], 'r' , encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            out_list.append(
                {
                    "title" : row[1] + " " + row[2],
                    "artist" : row[1],
                    "original_title" : row[2]
                }
            )

    return out_list

def initialize_download_from_out_list(out_list):
    out_list.reverse()
    dict_list = []

    for song in out_list[0:10]:
        out = search_and_download_song(song["title"])
        print("out is " , out)
        out["artist"] = song["artist"]
        out['original_title'] = song["original_title"]
        dict_list.append(out)
        time.sleep(random.choice([1,2,3,4,5]))

    return dict_list

def upload_process(dict_list):
    for song in dict_list:
        upload_file_to_firebase(song['path'] , song)

def preprocess_data(data):
    search_url = "https://api.deezer.com/search?q=" + data['original_title'] + " " + data['artist']
    # search_url = "https://api.deezer.com/search?q=many men 50 cent"
    response = requests.get(search_url)
    json_data = response.json()

    if len(json_data['data']) == 0:
        return {} 

    data['meta'] = json_data['data'][0]
    return data

init_firebase()

out_list = read_data_file()
dict_list = initialize_download_from_out_list(out_list)
upload_process(dict_list)


def _test_firebase_upload():
    folder_path = 'out'
    file_paths = []

    for root, directories, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))

    for path in file_paths:
        sample_dict = {
            "sample" : "data",
            "path" : path
        }
        upload_file_to_firebase(path , sample_dict)