import requests
from PIL import Image
from io import BytesIO
import os
import csv

# Set your Spotify API credentials
client_id = 'f6426338aeab4625af5a2a54d6dd2329'
client_secret = '6b0ad361fd374d978efc83a589e796b8'

# Get access token using client credentials flow
def get_access_token(client_id, client_secret):
    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    response = requests.post(token_url, data=payload)
    token_data = response.json()
    return token_data['access_token']

# Get tracks from multiple playlists
def get_tracks_from_playlists(access_token, playlist_urls):
    all_tracks = []
    headers = {'Authorization': f'Bearer {access_token}'}

    for playlist_url in playlist_urls:
        response = requests.get(playlist_url, headers=headers)
        tracks = response.json()['tracks']['items']
        all_tracks.extend(tracks)

    return all_tracks

# Extract genres for a given artist ID
def get_artist_genres(access_token, artist_id):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(artist_url, headers=headers)
    genres = response.json().get('genres', [])
    return genres

# Extract information from the API response
def extract_information(track, access_token):
    song_name = track['track']['name']
    album_name = track['track']['album']['name']
    album_cover_url = track['track']['album']['images'][0]['url']
    genres = set()  # Using a set to automatically remove duplicates

    for artist in track['track']['artists']:
        artist_id = artist['id']
        artist_genres = get_artist_genres(access_token, artist_id)
        genres.update(artist_genres)

    # Convert the set of genres back to a list
    genres = list(genres)

    # Extract the release year from the album's release_date
    release_date = track['track']['album']['release_date']
    release_year = release_date.split('-')[0]

    return song_name, album_name, album_cover_url, genres, release_year

# Download and save image to a folder
def download_image(url, image_path):
    response = requests.get(url)
    with open(image_path, 'wb') as f:
        f.write(response.content)
        
def display_image_with_caption(image_path, caption):
    img = Image.open(image_path)
    img.show()
    print(f"Caption: {caption}")

# Main script
access_token = get_access_token(client_id, client_secret)

# Define playlist URLs
playlist_urls = [
    'https://api.spotify.com/v1/playlists/6fWJDsgWRJpr43kuUNKmzj',
    'https://api.spotify.com/v1/playlists/2x8usH5GeAjOgiG5mODaK6',
    'https://api.spotify.com/v1/playlists/37i9dQZF1DX26DKvjp0s9M',
    'https://api.spotify.com/v1/playlists/37i9dQZF1DWWOaP4H0w5b0',
    'https://api.spotify.com/v1/playlists/1MOCkrecw4VsUKgwoIRGaU'
]

# Get tracks from playlists
top_tracks = get_tracks_from_playlists(access_token, playlist_urls)

# Create a folder to store images
image_folder = 'album-mixed/train'
os.makedirs(image_folder, exist_ok=True)

# Create and write to metadata.csv
with open('album-mixed/metadata.csv', 'w', newline='') as csvfile:
    fieldnames = ['file_name', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    processed_album_covers = set()

    # Print or store the information as needed
    for playlist_url in playlist_urls:
        top_tracks = get_tracks_from_playlists(access_token, [playlist_url])
        playlist_index = playlist_urls.index(playlist_url)

        # Counter for the actual number of songs added to the playlist
        playlist_song_count = 0

        for index, track in enumerate(top_tracks, start=1):
            if playlist_song_count >= 50:
                break  # Stop processing after 50 songs from each playlist

            song_name, album_name, album_cover_url, genres, release_year = extract_information(track, access_token)
            print(f"Playlist {playlist_index + 1}, Song: {song_name}, Album: {album_name}, Year: {release_year}")

            # Check for duplicate album cover
            if album_cover_url in processed_album_covers:
                print(f"Skipping duplicate album cover: {album_cover_url}")
                continue

            # Add album cover to the processed set
            processed_album_covers.add(album_cover_url)

            # Generate caption based on playlist index
            genre = ['rap', 'pop', 'indie', 'heavy metal', 'edm'][playlist_index]
            caption = f"for genres {genre} for album titled '{album_name}' from the year {release_year}"

            # Save the image to the folder with zero-padded index
            image_name = f"train_{playlist_index * 50 + playlist_song_count + 1:04d}.png"
            image_path = os.path.join(image_folder, image_name)
            download_image(album_cover_url, image_path)

            # Increment the counter for the actual number of songs added to the playlist
            playlist_song_count += 1

            # Display the album cover image
            # display_image_with_caption(image_path, caption)
            print(caption)

            # Write to metadata.csv
            writer.writerow({'file_name': 'train/' + image_name, 'text': caption})