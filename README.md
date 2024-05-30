#  SyncGroove V2

## Table of Content
* [Introduction](#introduction)
* [Languages](#languages)
* [Usage](#usage)
* [Installation](#installation)
* [License](#license)
* [Authors](#authors)

## Introduction
SyncGroove is a web application that uses Spotify API to give the user cool features. Music is universal and many people can agree that they find it therapeutic. For me, I love listening music for virtually every occasion including when I am working. To serve this purpose, I find Spotify to be a good application especially due to how good its algorithm is when it comes to recommending users with new music. With over half a billion (600) average monthly listeners, it is clear many use the application to satisfy this need (Chartmasters.org). 
One playlist in particular called Discover Weekly provides users with a curation of new music specific to them is a personal favorite. However, the playlist is updated every monday and even if the user has saved the playlists some of these songs disappear. For this reason, I decided to create a web application that allows the users to save the playlist to a playlist called SyncGroove. This playlist contains all the unique songs that have been featured in discover weekly as some songs are repeated. To work, the user must first save Discover Weekly. On top of this feature, the users can see their top artists in the last six months, a feature spotify gives the user once at the end of year in Spotify Wrap. Due to this need, SyncGroove was born



Here is a [YouTube link](https://youtu.be/cKMZVlDJAh8) showing how the app works.
Here is the yet to be integrated landing page [SyncGroove](https://koomemc.wixsite.com/syncgroove-1)
[Blog Post](https://medium.com/@koomemc/syncgroove-2f0ed6db3e99)

## Instalation
* Must have Spotify Premium account
* Go to `https://developer.spotify.com/` to create web application
* Substitute the values in `spotify.py` called `c_id`, `c_secret`, `r_uri`(eg `localhost:5000` depending on port provided) with your `client id`, `client secret`, and `redirect uri` respectively.
* Clone this repository: `git clone "https://github.com/koome00/SyncGroove-V2.git"`
* Access app directory: `cd app`
* Run `routes.py`


## Languages
The project uses flask Framework for the back end and HTML and CSS in the frontend
The Spotify API is used to make the application possible

## Usage

[/app/spotify.py]([/app/spotify.py) - Contains the functions necessary for making API calls

* `def user_authorization()`- creates authorization url
* `def request_access_token(authorization_code)` - this function is meant to get a refresh token if the current access token has expired the new access token is added to the auth_header and a new expires at is calculated auth_header and expires_ar are returned 
* `def check_expired(expired_at)` - This function checks whether token has expired or not. The function then returns True or False
* `def current_user_profile(auth_header)` - GET request to get the current user's profile
* `def current_user_playlists(auth_header)` - GET request to get the currently playing song in the user's profile. Returns: name of device playing, song and artist
* `def get_featured_playlists(auth_header)` -  GET requests to get Spority featured playlists
* `def get_playlist_items(auth_header, playlist_id):` -  GET request to get the items in a playlists
* `def update_playlist_items(auth_header, playlist_id, uris)` - UPDATE request to add songs to a playlists
* `def save_discover_weekly_playlist(auth_header, user_id)` - Checks whether SyncGroove is present or not, if absent, it is created and unique songs added to it
    
* `def get_users_top_artists(auth_header)` -  GET request to get the users top artists in the last six months

[/app/routes.py](/app/routes.py) - Contains the Flask routes
* `def home()` - route handling the login page
* `def login()` - redirects user to spotify to give authorization code used to get access token is in the redirect uri paramaters
* `def authorized()` - if user gives permission, they will be redirected here the code parameter is extracted to get token information. The user is then redirected to the home page after their code is captured and stored in their session
* `def profile()` - route to user's profile page
* `def logout()` - checks the state of access_token expiry if expired, refresh token is requested and the information stored in the session

## Authors
Collins Koome - [Github](https://github.com/koome00)/ [Twitter](https://twitter.com/khvfv_)/ [LinkedIn](https://www.linkedin.com/in/collins-koome-728544261/)

## License
Spotify API