from flask import Flask
from flask import request
from flask_cors import CORS
from SpotifyController import spotify_controller
import json

app = Flask(__name__)
CORS(app)


@app.route('/spotipi')
def index():
    return "Hello World"


@app.route('/playlist')
def playlist():
    data = request.json
    return json.dumps([ob.__dict__ for ob in spotify_controller.playlist()])
    return "Ok"


@app.route('/search')
def search():
    term = request.args["term"]
    return json.dumps([ob.__dict__ for ob in spotify_controller.search(term)])


@app.route('/play', methods=['OPTIONS', 'POST'])
def play():
    if request.method == 'POST':
        data = request.json
        id = data['id']
        spotify_controller.play_song(id)
        return "OK"
    else:
        return "OK"


@app.route('/playing')
def playing():
    return json.dumps(spotify_controller.currently_playing().__dict__)


@app.route('/add', methods=['OPTIONS', 'POST'])
def add():
    if request.method == 'POST':
        data = request.json
        id = data['id']
        spotify_controller.add_id_to_playlist(id)
        spotify_controller.queue_song(id)
        return "Ok"
    else:
        return "Ok"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
