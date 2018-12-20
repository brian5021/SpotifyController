import sys
import spotipy
from model import Track
import spotipy.util as util
import requests
import json
import os
from simplejson.scanner import JSONDecodeError

sp = None
token = None
username = '126442621'
playlist_id = '0fXCWK0ZDlntNKnIZs1GE1'
def show_tracks(tracks):
    results = []
    for i, track in enumerate(tracks['items']):
        results.append(Track(track['name'], track['artists'][0]['name'], track['id']))
    return results

def show_tracks_in_playlist(playlist):
    results = []
    for i, item in enumerate(playlist['items']):
        track = item["track"]
        results.append(Track(track['name'], track['artists'][0]['name'], track['id']))
    return results

def search(term):
    authenticate('playlist-modify-public')
    tracks = sp.search(term)
    return show_tracks(tracks['tracks'])

def playlist():
    authenticate('playlist-modify-public')
    playlist = sp.user_playlist_tracks(username, playlist_id=playlist_id)
    return show_tracks_in_playlist(playlist)

def add_track_to_playlist(track):
    authenticate('playlist-modify-public')
    sp.user_playlist_add_tracks(username, playlist_id= playlist_id,
                                tracks=[track.id])

def add_id_to_playlist(id):
    authenticate('playlist-modify-public')
    sp.user_playlist_add_tracks(username, playlist_id= playlist_id,
                                tracks=[id])

def play_song(id):
    authenticate('user-read-playback-state')
    uri = str('spotify:track:' + id)
    #payload = {'context_uri':'spotify:playlist:0fXCWK0ZDlntNKnIZs1GE1'}
    payload = {"uris": [uri]}
    result = requests.put(url='https://api.spotify.com/v1/me/player/play',
                          json=payload,
                          headers={'Authorization': "Bearer " + token})
    print result

def currently_playing():
    authenticate('user-read-playback-state')
    result = requests.get(url='https://api.spotify.com/v1/me/player/currently-playing', headers={'Authorization': "Bearer " + token})
    result_json = result.json()
    track = result_json["item"]
    return Track(track['name'], track['artists'][0]['name'], track['id'])

def authenticate(scope):
    global sp, token
    test = 'user-modify-playback-state'
    token = util.prompt_for_user_token('126442621', test)
    print token
    sp = spotipy.Spotify(auth=token)

if __name__ == '__main__':
    term = sys.argv[1]
    results = search("baby")
    play_song(results[0].id)



