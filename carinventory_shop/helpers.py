import requests
import requests_cache
import decimal 
import json 



requests_cache.install_cache(cache_name = 'image_cache', backend='sqlite', expire_after=900)


def get_image(search):


    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "04bd23c124msh6c39650b033b03bp1d8216jsn17b18c8a57a1",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    img_url = data['items'][0]['originalImageUrl']
    return img_url 




class JSONENcoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj) #there might be things like decimals that we want to basically stringify
        return json.JSONEncoder(JSONENcoder, self).default(obj)