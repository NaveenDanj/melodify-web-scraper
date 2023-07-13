import requests
from fake_useragent import UserAgent


def select_engine_and_search(song_name , _type):

    ua = UserAgent()
    user_agent = ua.random
    query = f"site:youtube.com {song_name}"

    headers = {
        'User-Agent': user_agent
    }

    if _type == 'google':

        # https://www.google.com/search?q=asdasd
        search_url = f"https://www.google.com/search?q={query}&ei=6SevZJznFbW94-EPk7-u0A8&ved=0ahUKEwjc_4HWmoqAAxW13jgGHZOfC_oQ4dUDCA8&uact=5&oq=asdasd&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQRxDWBBCwAzIKCAAQigUQsAMQQzIPCC4QigUQyAMQsAMQQxgBMg8ILhCKBRDIAxCwAxBDGAEyDwguEIoFEMgDELADEEMYATIPCC4QigUQyAMQsAMQQxgBSgQIQRgAUABYAGCdEWgBcAF4AIABAIgBAJIBAJgBAMABAcgBDdoBBAgBGAg&sclient=gws-wiz-serp"
        response = requests.get(search_url , headers )
        return response
    else:


        # https://search.brave.com/search?q=site%3Ayoutube.com+killshot+eminem+song&source=web
        # search_url = f"https://duckduckgo.com/?hps=1&q={query}&ia=web"
        # https://html.duckduckgo.com/html/?q=site:youtube.com killshot eminem
        search_url = f"https://html.duckduckgo.com/html/?q={query}"
        response = requests.get(search_url , headers )
        return response



def select_engine_and_scrape(result , _type):

    if _type == 'google':

        # Extract the URL and title of the search result
        url = result.get("href")
        has_title = result.find("h3")

        if not has_title or "music.youtube.com" in url :
            return None
        
        if "music.youtube.com" in url :
                return None

        title = has_title.text
        url = url.split("%3Fv%3D")
        url = url[1].split("&")
        url = "https://www.youtube.com/watch?v=" + url[0]

        return url

    else:

    
        url = result.get("href")

        if not url:
            return None 

        if "music.youtube.com" in url :
            return None

        if "youtube.com" in result.text:
            out = result.text
            out.replace(" " , "")
            out.replace("\\n" , "")
            out = "".join(out.split())

            return out