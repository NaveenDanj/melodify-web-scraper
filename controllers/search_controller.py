# song_controller.py
from flask_restful import Resource
import requests
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
from fake_useragent import UserAgent
from lib.Lib import select_engine_and_search , select_engine_and_scrape
import json
from google.cloud.firestore_v1.base_query import FieldFilter, Or
from main import initialize_download_from_out_list

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


init_firebase()

# Example:
class SearchAPI(Resource):

    def get(self , query):
        search_url = "https://api.deezer.com/search?q=" + query
        response = requests.get(search_url)
        json_data = response.json()

        return {
            "data" : json_data
        } , 200
    
class DownloadAPI(Resource):

    def get(self):
        db = firestore.client()
        ref = db.collection("search_results")
        out = []

        q = ref.where( filter=FieldFilter("count", ">", 1) ).where(filter=FieldFilter("downloaded", "==", False) ).where( filter=FieldFilter("available", "==", False) ).limit(10)
        docs = q.stream()
        
        for doc in docs:
            data = doc.to_dict()
            print("data ->>>> " , data)
            data['artist'] = data['artist_name']
            title = data['title']
            data['title'] = data['artist_name'] + " " + data['title']
            data['original_title'] = title
            out.append(data)

        initialize_download_from_out_list(out)

        return {
            "data" : out
        }