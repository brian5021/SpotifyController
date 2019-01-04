import sys
import spotipy
from model import Track
import spotipy.util as util
import requests
import asyncio
from configparser import ConfigParser
from threading import Thread

sp = None
token = None

parser = ConfigParser()
parser.read('config.ini')

username = '126442621'
playlist_id = '0fXCWK0ZDlntNKnIZs1GE1'

queue = []


def show_tracks(tracks):
    results = []
    for i, track in enumerate(tracks['items']):
        results.append(
            Track(track['name'], track['artists'][0]['name'], track['id'], track['album']['images'][0]['url'], None,
                  track['duration_ms']))
    return results


def show_tracks_in_playlist(playlist):
    results = []
    for i, item in enumerate(playlist['items']):
        track = item["track"]
        results.append(
            Track(track['name'], track['artists'][0]['name'], track['id'], track['album']['images'][0]['url'], None,
                  track['duration_ms']))
    return results


def find_song_position_in_playlist(id):
    tracks = playlist()
    for i, track in enumerate(tracks):
        if track.id == id:
            return i, tracks.__len__()


def get_queue():
    global queue
    print(queue)
    return queue


def queue_song(id):
    global queue
    track_to_queue = get_track(id)
    queue.append(track_to_queue)
    current = currently_playing()
    new_loop = asyncio.new_event_loop()
    t = Thread(target=start_loop, args=(new_loop, current, track_to_queue.id,))
    t.start()


def start_loop(loop, current, id):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(wait_and_play(current, id))


@asyncio.coroutine
def wait_and_play(track, id):
    global queue
    yield from asyncio.sleep((track.duration_ms - track.progress_ms) / 1000)
    if (queue[0].id == id):
        play_song(id)
        yield from asyncio.sleep(queue[0].duration_ms / 1000 - 2)
        queue.pop(0)
    else:
        yield from asyncio.sleep(2)
        yield from wait_and_play(currently_playing(), id)


def search(term):
    authenticate()
    tracks = sp.search(term)
    return show_tracks(tracks['tracks'])


def playlist():
    authenticate()
    playlist = sp.user_playlist_tracks(username, playlist_id=playlist_id)
    return show_tracks_in_playlist(playlist)


def add_id_to_playlist(id):
    global queue
    authenticate()
    current = currently_playing()
    if current is not None:
        current_offset, playlist_length = find_song_position_in_playlist(current.id)
        queue_offset = queue.__len__()
        for track in queue:
            if track.id == current.id:
                queue_offset = queue_offset - queue.index(track) - 1
                break
        sp.user_playlist_add_tracks(username, playlist_id=playlist_id,
                                    tracks=[id], position=(current_offset + 1 + queue_offset) % playlist_length)
    else:
        sp.user_playlist_add_tracks(username, playlist_id=playlist_id,
                                    tracks=[id])


def get_track(id):
    track = sp.track(id)
    return Track(track['name'], track['artists'][0]['name'], track['id'], track['album']['images'][0]['url'], None,
                 track['duration_ms'])


def play_song(id):
    authenticate()
    uri = str('spotify:track:' + id)
    # payload = {'context_uri':'spotify:playlist:0fXCWK0ZDlntNKnIZs1GE1'}
    payload = {"context_uri": 'spotify:playlist:0fXCWK0ZDlntNKnIZs1GE1', "offset": {"uri": uri}}
    result = requests.put(url='https://api.spotify.com/v1/me/player/play',
                          json=payload,
                          headers={'Authorization': "Bearer " + token})


def currently_playing():
    authenticate()
    result = requests.get(url='https://api.spotify.com/v1/me/player/currently-playing',
                          headers={'Authorization': "Bearer " + token})
    result_json = result.json()
    track = result_json["item"]
    return Track(track['name'], track['artists'][0]['name'], track['id'], track['album']['images'][0]['url'],
                 result_json['progress_ms'], track['duration_ms'])


def authenticate():
    global sp, token
    token = util.prompt_for_user_token(username='126442621',
                                       scope='playlist-modify-public user-modify-playback-state user-read-currently-playing',
                                       client_id=parser['SPOTIFY_CREDS']['SPOTIPY_CLIENT_ID'],
                                       client_secret=parser['SPOTIFY_CREDS']['SPOTIPY_CLIENT_SECRET'],
                                       redirect_uri=parser['SPOTIFY_CREDS']['SPOTIPY_REDIRECT_URI'])
    sp = spotipy.Spotify(auth=token)


if __name__ == '__main__':
    term = sys.argv[1]
    current = currently_playing()
    position, playlist_length = find_song_position_in_playlist(current.id)
    add_id_to_playlist(current.id)
    print("nothing")
