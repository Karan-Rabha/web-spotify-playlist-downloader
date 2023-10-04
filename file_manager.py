import zipfile
import os


def create_zip_file(file_path, filename):
    playlist_songs = os.listdir(file_path)
    with zipfile.ZipFile(f'{file_path}/{filename}.zip', 'w') as zipf:
        for file in playlist_songs:
            fp = os.path.join(file_path, file)
            zipf.write(fp, os.path.basename(fp))
