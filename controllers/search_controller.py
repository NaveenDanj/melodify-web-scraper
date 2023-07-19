# song_controller.py
from flask_restful import Resource
import requests


# Example:
class SearchAPI(Resource):
    
    def get(self , query):
        search_url = "https://api.deezer.com/search?q=" + query
        response = requests.get(search_url)
        json_data = response.json()

        return {
            "data" : json_data
        } , 200