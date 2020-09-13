import os
import re
import spotipy
import time
import random

from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


def clean_data(line):
	""""""
	pattern = r'([\[\(][^\]\)]{0,}[\]\)])'
	line = re.sub(pattern, '', line)
	lines = line.split('-', 1)
	lines = [l.strip() for l in lines]
	return f'{lines[0]} - {lines[1]}'


def search_from_file(tracklist, spoti):
	""""""
	count = {'hit': 0, 'miss': 0}
	missed = []
	with open(tracklist, 'r') as file, open('track_uris.txt', 'w') as temp_uri_list:
		for n, track in enumerate(file.readlines()):
			clean_track = clean_data(track)
			result = spoti.search(clean_track, limit=1, type='track')
			if result['tracks']['items']:
				temp_uri_list.write(result['tracks']['items'][0]['uri']+'\n')
				count['hit']+=1
				print(f'\t[{n:^4}][  OK  ] "{clean_track}" ')
			else:
				missed.append(track)
				count['miss']+=1
				print(f'\t[{n:^4}][  NF  ] "{clean_track}" ')
	with open('missed.txt', 'w') as missed_file:
		for item in missed:
			missed_file.write(item)
	search_from_file.count = count


def add_to_playlist(playlist_uri, spoti):
	""""""
	try:
		with open('track_uris.txt', 'r') as temp_uri_list:
			track_uris = [line.strip() for line in temp_uri_list.readlines()]


			for track_uri in track_uris:
				test_res = spoti.playlist_add_items(playlist_uri, [track_uri,])
	except FileNotFoundError as e1:
		print('[FileNotFound]')
		print(e1)
	except spotipy.exceptions.SpotifyException as e2:
		print('[!!!!!!!!!!!!!!]')
		print(e2.msg)
	finally:
		os.remove('track_uris.txt')
		

def authorization():
	""""""
	scope = 'playlist-modify-public'
	spoti = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_id = spoti.me()['id']
	return user_id, spoti


def main(tracklist, playlist):
	""""""

	print('[] Authorization')
	user_id, spoti = authorization()

	print(f'[] Search from {tracklist}')
	search_from_file(tracklist, spoti)

	rate = search_from_file.count
	print(f'[] Results: {rate}')

	print(f'[] Create playlist {playlist}')
	playlist = spoti.user_playlist_create(user_id, playlist)

	print('[] Add tracks to playlist')
	add_to_playlist(playlist['uri'], spoti)

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print ('Please provide a tracklist file and playlist name!')

	