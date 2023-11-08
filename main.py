import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import os

# Spotify Initialization

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
CLIENT_USERNAME = ""         # Enter your username here as a string

sp = spotipy.Spotify(
	auth_manager=SpotifyOAuth(
		scope="playlist-modify-private",
		redirect_uri="https://example.com",
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		show_dialog=True,
		cache_path="token.txt",
		username=CLIENT_USERNAME,
	)
)
user_id = sp.current_user()["id"]


# Get date from user
def get_date():
	date = ""
	while len(date) != 10:
		date = input(
			"Which year do you want to travel to? Type the date in this format YYYY-MM-DD, including the dashes:\n")
	return date


user_date = get_date()

# Scrape Billboard page for 100 songs

URL = f"https://www.billboard.com/charts/hot-100/{user_date}"

response = requests.get(URL)
user_billboard_page = response.text

soup = BeautifulSoup(user_billboard_page, "html.parser")
song_titles = soup.select("li ul li h3")
song_list = [song.getText().strip() for song in song_titles]

# Use Spotipy to search Spotify for tracks, create playlist, and add successfully found tracks.
song_uris = []
year = user_date.split("-")[0]
for song in song_list:
	result = sp.search(q=f"track: {song} year:{year}", type="track")
	print(result)
	try:
		uri = result["tracks"]["items"][0]["uri"]
		song_uris.append(uri)
	except IndexError:
		print(f"{song} doesn't exist in Spotify, Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{user_date} Billboard Top 100", public=False,
								   collaborative=False, description="Created using Brett Sports Billboard Scraper")
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
