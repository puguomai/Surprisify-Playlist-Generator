import sys
import os
import spotipy
import spotipy.util as util
import random
import string
import requests
from urllib.parse import quote
import base64
import json
import datetime

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
redirect_uri = os.environ.get('REDIRECT_URI')

scope = 'user-top-read user-library-read playlist-modify-public'


def req_auth():

    show_dialog = "false"

    AUTH_FIRST_URL = f'https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={quote(redirect_uri)}&show_dialog={show_dialog}&scope={scope}'
    return AUTH_FIRST_URL


def req_token(code):

    # B64 encode variables
    client_creds = f"{client_id}:{client_secret}"
    client_creds_b64 = base64.b64encode(client_creds.encode())

    # Token data
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    # Token header
    token_header = {
        "Authorization": f"Basic {client_creds_b64.decode()}"
    }

    # Make request post for token info
    token_json = requests.post(
        'https://accounts.spotify.com/api/token', data=token_data, headers=token_header)

    # Checking if token is still valid, otherwise, refresh

    if "expires_in" in token_json.json():

        now = datetime.datetime.now()
        expires_in = token_json.json()['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)

        if now > expires:

            refresh_token_data = {
                "grant_type": "refresh_token",
                "refresh_token": token_json.json()['refresh_token']
            }

            refresh_token_json = requests.post(
                'https://accounts.spotify.com/api/token', data=refresh_token_data, headers=token_header)
            token = refresh_token_json.json()['access_token']

            return token
        else:
            token = token_json.json()['access_token']
            return token
    else:

        token = token_json.json()['access_token']

        return token


def get_obscure_artist(artist_id, levels, spotifyObject):

    rnd_artist = random.randint(0, 11)

    if (levels == 1):
        return artist_id

    temp_id = artist_id
    new_id = ''
    while levels >= 1:
        new_id = spotifyObject.artist_related_artists(
            temp_id)['artists'][rnd_artist]['id']
        temp_id = new_id
        levels -= 1

    return new_id


def generate(token, levels, name, desc):

    spotifyObject = spotipy.Spotify(auth=token)

    user_id = str(spotifyObject.current_user()['id'])
    first_name = spotifyObject.current_user()['display_name'].split()[0]

    # Get user top artists
    user_top_artists = spotifyObject.current_user_top_artists(
        limit=5, time_range='medium_term')

    # Put top artists in dictionary
    artist_ids = []
    for artist in user_top_artists['items']:
        artist_ids.append(artist['id'])

    # Try and get obscure artists by going deep into related artists
    related_artist_ids = []
    for i in artist_ids:
        artist_id = get_obscure_artist(i, levels, spotifyObject)
        while artist_id in related_artist_ids:
            artist_id = get_obscure_artist(i, levels, spotifyObject)
        related_artist_ids.append(artist_id)

    # Get list of recommended songs and put ID's in a list
    tracks = spotifyObject.recommendations(
        seed_artists=related_artist_ids, limit=50)
    track_ids = []
    for track in tracks['tracks']:
        track_ids.append(track['id'])

    # Put recommended songs into playlist

    playlist_name = "Surprisify playlist for {}".format(first_name)
    playlist_desc = "{} level(s) deep / surprisify.me".format(levels)

    if name:
        playlist_name = name

    if desc:
        playlist_desc = "{} / {} level(s) deep, made in surprisify.me".format(
            desc, levels)

    recommended_playlist = spotifyObject.user_playlist_create(
        user_id, playlist_name, description=playlist_desc)

    recommended_playlist_id = recommended_playlist['id']
    spotifyObject.user_playlist_add_tracks(
        user_id, recommended_playlist_id, track_ids)

    return [first_name, user_id, recommended_playlist_id]
