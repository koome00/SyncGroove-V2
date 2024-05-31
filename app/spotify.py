import os
from dotenv import load_dotenv
import requests
import base64
import time
from db import DB


# Allow loading environment variables from .env file to get
# client_id and client_secret
load_dotenv()
c_id = os.getenv('CLIENT_ID')
c_secret = os.getenv("CLIENT_SECRET")
r_uri = 'http://localhost:5000/home/'
db = DB()


def user_authorization():
    """
    request user authorization
    """
    # scope are permisions given by user
    scope = 'user-read-private user-read-email user-top-read playlist-read-private user-read-currently-playing playlist-modify-public playlist-modify-private'
    
    # authorization url
    OAUTH_AUTHORIZE_URL= 'https://accounts.spotify.com/authorize'

    # create query for authorization code flow check documentation
    # https://developer.spotify.com/documentation/web-api/tutorials/code-flow
    q = f"client_id={c_id}&response_type=code&redirect_uri={r_uri}&scope={scope}"
    
    # authorization url to be used by GET method
    authorization_url = f"{OAUTH_AUTHORIZE_URL}?{q}"    

    return authorization_url


def request_access_token(authorization_code):
    """
    requests access token after user has given authorization
    this function makes a post requests given the the required header
    and data parameters 
    """
    # endpoint to make post request
    OAUTH_TOKEN_URL= 'https://accounts.spotify.com/api/token'

    # encode client_id and secret_id in base64
    auth = c_id + ":" + c_secret
    auth_string = auth.encode('utf-8')
    auth64 = str(base64.b64encode(auth_string), 'utf-8')
    
    # body parameters
    # code is retrived from the redirect_uri query paramaters
    # and given to body
    data = {"grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": r_uri,
            }
    
    # header for the POST request
    headers = {"Authorization": "Basic " + auth64,
               "Content-type": "application/x-www-form-urlencoded"}
    
    # make post request
    response = requests.post(OAUTH_TOKEN_URL, headers=headers, data=data)

    # get response body and parse it using .json()
    response_data = response.json()
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    expires_in = response_data["expires_in"]

    expires_at = int(time.time()) + expires_in
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    return response_data, auth_header, refresh_token, expires_at


def get_refresh_token(refresh_token):
    """
    this function is meant to get a refresh token if the current access token has expired
    the new access token is added to the auth_header and a new expires at is calculated 
    auth_header and expires_ar are returned
    """
    auth = c_id + ":" + c_secret
    auth_string = auth.encode('utf-8')
    auth64 = str(base64.b64encode(auth_string), 'utf-8')
    body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    headers = {
        'content-Type': 'application/x-www-form-urlencoded',
        'Authorization': "Basic " + auth64
    }
    
    url = "https://accounts.spotify.com/api/token"
    post_refresh = requests.post(url, data=body, headers=headers)
    response_data = post_refresh.json()
    access_token = response_data["access_token"]
    expires_in = response_data["expires_in"]
    expires_at = int(time.time()) + expires_in

    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    return auth_header, expires_at


def check_expired(expired_at):
    """
    This function checks whether token has expired or not
    The function then returns True or False
    """
    now = int(time.time())
    if expired_at - now <= 0:
        return True
    return False


def current_user_profile(auth_header):
    """
    GET request to get the current user's profile
    """
    url = "https://api.spotify.com/v1/me"

    response = requests.get(url, headers=auth_header)
    r = response.json()
    name = r['display_name']
    followers = r['followers']['total']
    p_pic = r['images'][0]['url']
    user_id = r['id']
    email = r["email"]
    return name, followers, p_pic, user_id, email


def current_user_playlists(auth_header):
    """
    GET request to get the current user's saved playlists
    """
    url = "https://api.spotify.com/v1/me/playlists?offset=0&limit=50"
    response = requests.get(url, headers=auth_header)
    return response.json()


def currently_playing(auth_header):
    """
    GET request to get the currently playing song in the user's profile
    Returns: name of device playing, song and artist
    """
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    response = requests.get(url, headers=auth_header)
    r = response.json()
    name = r['device']['name']
    song = r['item']['name']
    artist = r['item']['artists']['name']
    return name, song, artist


def get_featured_playlists(auth_header):
    """
    GET requests to get Spority featured playlists
    """
    url = "https://api.spotify.com/v1/browse/featured-playlists?limit=50"
    response = requests.get(url, headers=auth_header)
    return response.json()


def get_playlist_items(auth_header, playlist_id):
    """
    GET request to get the items in a playlists
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50"
    response = requests.get(url, headers=auth_header)
    return response.json()


def update_playlist_items(auth_header, playlist_id, uris):
    """
    UPDATE request to add songs to a playlists
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    auth_header.update({'Content-Type': 'application/json'})
    requests.post(url, headers=auth_header, json=uris)   


def save_discover_weekly_playlist(auth_header, user_id):
    """
    Checks whether SyncGroove is present or not, if absent, 
    it is created and unique songs added to it
    """
    # get current playlists
    playlists = current_user_playlists(auth_header)
    # iterate through the playlists items to find Discover Weekly id
    # and to see if Saved Discover Weekly is present to get its id
    discover_weekly_id = ""
    saved_discover_weekly_id = ""
    url = ""
    uris = {}
    user_details = current_user_profile(auth_header)
    user_name = user_details[0]
    p_pic = user_details[2]
    email = user_details[4]
    user = db.add_user(email, user_name, p_pic)
    for item in playlists['items']:
        if item['name'] == "Discover Weekly":
            discover_weekly_id = item['id']
    for item in playlists['items']:       
        if item['name'] == "SyncGroove":
            url = item["external_urls"]["spotify"]
            saved_discover_weekly_id = item['id']
            if len(saved_discover_weekly_id) == 0:
                db.remove_all_songs_from_user(user)

    r = get_playlist_items(auth_header, discover_weekly_id)
    songs_to_add = []
    for item in r['items']:
        for key in item.keys():
            if key == 'track':
                songs_to_add.append(item[key]["uri"])
                song_dict = {"song_name": item[key]["name"],
                             "image_url": item[key]["album"]["images"][0]["url"],
                             "link": item[key]["external_urls"]["spotify"],
                             "song_uri": item[key]["uri"]}
                song = db.add_song(user, **song_dict)


    song_uris = db.get_user_song_uris(user)

    if len(saved_discover_weekly_id) == 0:
        urls = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        body = {'name': "SyncGroove"}
        response = requests.post(urls, headers=auth_header, json=body)
        print(response.status_code)
        res = response.json()
        print(res['id'])
        saved_discover_weekly_id = res['id']
        url = res["external_urls"]["spotify"]
        uris["uris"] = songs_to_add
        update_playlist_items(auth_header, saved_discover_weekly_id, uris)
        return url

    unique = []

    # check for duplicate songs 
    for song in songs_to_add:
        if song not in song_uris:
            unique.append(song)
    uris["uris"] = unique
    # Saved discover weekly is updated with the songs
    update_playlist_items(auth_header, saved_discover_weekly_id, uris)

    r_3 = get_playlist_items(auth_header, saved_discover_weekly_id)
    print(len(r_3["items"]))
    print(len(song_uris))
    if len(r_3["items"]) == 0:
        update_playlist_items(auth_header, saved_discover_weekly_id, uris)
        print("w")
        return url
    if len(r_3["items"]) < len(song_uris):
        current_songs = [item["track"]["uri"] for item in r_3["items"] if "track" in item]
        set1 = set(current_songs)
        set2 = set(song_uris)
        unique_items = set1.symmetric_difference(set2)
        unique_items = list(unique_items)
        update_playlist_items(auth_header, saved_discover_weekly_id, {"uris": unique_items})
        return  url
    return  url


def get_users_top_artists(auth_header):
    """
    GET request to get the users top artists in the last six months
    """
    url = "https://api.spotify.com/v1/me/top/artists?limit=15"
    response = requests.get(url, headers=auth_header)
    return response.json()

def get_users_top_tracks(auth_header):
    """
    GET request to get the users top tracks in the last six months
    """
    url = "https://api.spotify.com/v1/me/top/tracks?limit=15"
    response = requests.get(url, headers=auth_header)
    res = response.json()   
    return res