from flask import Flask, render_template, request, send_file, jsonify
from app import spotify_playlist_info, download_song
import concurrent.futures
import ast
import os


DOWNLOAD_PATH = "PASTE YOUR FILE PATH HERE"

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def generate():
    playlist_data = None
    if request.method == 'POST':
        url = request.form.get('url')
        playlist_data = spotify_playlist_info(url)
    # temp data delete it
    vi_lst = [{"video_id": '_fgXpX1vEQA', "playlist_name": 'tsting', "song_name": 'Hey Stupid, I Love You'},
              {"video_id": 'GkPuGN38jJs', "playlist_name": 'tsting', "song_name": 'I Still Wait For You'}]

    return render_template("index.html", songs=vi_lst)


@app.route('/download', methods=['POST'])
def download():
    # json return value
    data = {"value": True}

    received_data = request.get_json()
    raw_song_data = received_data.get('songInfo')

    # Remove the surrounding single quotes
    raw_song_data = raw_song_data.strip("'")
    # Use ast.literal_eval to safely evaluate the string as a Python literal
    parsed_song_data = ast.literal_eval(raw_song_data)

    # return jsonify(data)

    # check if song data is a list or dict
    if type(parsed_song_data) == list:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_song, song, DOWNLOAD_PATH) for song in parsed_song_data]
        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        return jsonify(data)
    else:
        # pass the song data over to download song
        download_song(parsed_song_data, DOWNLOAD_PATH)
        return jsonify(data)


@app.route('/save', methods=['POST'])
def save():
    song_info = request.form.get('song_info').strip("'")
    # Use ast.literal_eval to safely evaluate the string as a Python literal
    parsed_song_data = ast.literal_eval(song_info)

    if type(parsed_song_data) == list:
        playlist_name = parsed_song_data[0]["playlist_name"]
        file_path = os.path.join(DOWNLOAD_PATH, playlist_name)
        file_name = f"{playlist_name}.zip"
        return send_file(path_or_file=f"{file_path}/{file_name}", as_attachment=True)
    else:
        playlist_name = parsed_song_data["playlist_name"]
        song_name = parsed_song_data["song_name"]
        file_path = os.path.join(DOWNLOAD_PATH, playlist_name)
        file_name = f"{song_name}.mp3"

        return send_file(path_or_file=f"{file_path}/{file_name}", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
