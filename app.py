import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from youtubesearchpython import VideosSearch
import os
import re
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()


def download_song(song_info, download_path=None):
    video_id = song_info["video_id"]
    playlist_name = song_info["playlist_name"]
    song_name = song_info["song_name"]

    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        try:
            audio = yt.streams.get_audio_only()
            try:
                if download_path:
                    download_file_path = download_path
                else:
                    download_file_path = os.getcwd()
                file_path = os.path.join(download_file_path, playlist_name)
                os.makedirs(exist_ok=True, name=file_path)
                # check file if already exists or not
                download_file = audio.download(output_path=file_path)
                if download_file:
                    # if file exists getting error fix it
                    new_file = f"{file_path}/{song_name}.mp3"
                    os.rename(download_file, new_file)
            except Exception as download_error:
                print(f"Error in download for '{song_name}': {download_error}")
        except Exception as audio_error:
            print(f"Error in audio stream for '{song_name}': {audio_error}")
    except Exception as youtube_error:
        print(f"Error in YouTube video ID for '{song_name}': {youtube_error}")


def search_song(song_info):
    song_name = song_info["song_name"]
    artist = song_info["artist"]
    if "playlist_name" in song_info:
        playlist_name = song_info["playlist_name"]
    else:
        playlist_name = "Track"
    try:
        search_results = VideosSearch(f"{song_name} {artist}", limit=1).result()
        if search_results:
            video_id_result = search_results["result"][0]["id"]
            return {
                'video_id': video_id_result,
                'playlist_name': playlist_name,
                'song_name': song_name
            }
        else:
            print(f"No search results found for '{song_name}'")
            return None
    except Exception as search_error:
        print(f"Error in search for '{song_name}': {search_error}")
        return None


def check_url(url):
    # Regular expressions to match playlist and track URLs
    playlist_pattern = r'^https://open\.spotify\.com/playlist/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?$'
    track_pattern = r'^https://open\.spotify\.com/track/[a-zA-Z0-9]+(\?si=[a-zA-Z0-9]+)?$'

    # Check if the URL matches the playlist pattern
    if re.match(playlist_pattern, url):
        return "Playlist"
    # Check if the URL matches the track pattern
    elif re.match(track_pattern, url):
        return "Track"
    else:
        return "Invalid URL"


def spotify_playlist_info(playlist_link):
    seen_song_name = set()
    filtered_song_list = []

    # Authentication - without user
    client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('CLIENT_ID'),
                                                          client_secret=os.getenv('CLIENT_SECRET'))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    playlist_uri = playlist_link.split("/")[-1].split("?")[0]
    url_check_result = check_url(playlist_link)

    if url_check_result == "Track":
        track = sp.track(playlist_uri)
        song_name = track["name"]
        artist = track["artists"][0]["name"]
        song_info = {'song_name': song_name, 'artist': artist}
        search_result = search_song(song_info)
        return search_result
    elif url_check_result == "Playlist":
        playlist = sp.playlist(playlist_uri)
        playlist_name = playlist['name'].strip()  # remove blank spaces
        playlist_image = playlist["images"][0]["url"]

        for item in playlist["tracks"]["items"]:
            song_name = item["track"]["name"]
            artist = item["track"]["artists"][0]["name"]
            if song_name not in seen_song_name:
                seen_song_name.add(song_name)
                filtered_song_list.append({
                    'song_name': song_name,
                    'artist': artist,
                    'playlist_name': playlist_name,
                    'playlist_image': playlist_image
                })

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(search_song, song) for song in filtered_song_list]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)
        search_result = [future.result() for future in futures]
        return search_result
    else:
        return None


# test links
playlist_link = "https://open.spotify.com/playlist/37i9dQZF1DX2czWA9hqErK?si=18a643db8f414ddb"  # playlist
track_link = "https://open.spotify.com/track/4IhsInWIIjUg9Q04eqgnGl?si=4adb185291f04f62"  # track
