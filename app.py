import csv
import os
import shutil
import spotipy

import converter

from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials


def search_from_file(csv_file, spoti):
	shutil.rmtree('temp')
	os.mkdir('temp')
	count = {'hit': 0, 'miss': 0}
	missed = []
	with open(csv_file, 'r') as file, open('temp/list.txt', 'w') as temp_list:
		track_list = csv.reader(file)
		for track in track_list:
			request = f'{track[1]} artist:{track[0]}'
			result = spoti.search(request, limit=1, type='track')
			if result['tracks']['items']:
				temp_list.write(result['tracks']['items'][0]['uri']+'\n')
				count['hit']+=1
			else:
				missed.append(track)
				print(f'\t[!] NotFound: {track}')
				count['miss']+=1
	with open('missed.csv', 'w') as missed_file:
		writer = csv.writer(missed_file)
		writer.writerows(missed)
	search_from_file.count = count


def add_to_playlist(playlist_uri, spoti):
	try:
		with open('temp/list.txt', 'r') as temp_list:
			track_uris = [line.strip() for line in temp_list.readlines()]
			for track_uri in track_uris:
				test_res = spoti.playlist_add_items(playlist_uri, [track_uri,])
	except FileNotFoundError as e1:
		print('[FileNotFound]')
	except spotipy.exceptions.SpotifyException as e2:
		print('[!!!!!!!!!!!!!!]')
		print(e2.msg)


def authorization():
	scope = 'playlist-modify-public'
	spoti = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_id = spoti.me()['id']
	return user_id, spoti


def file_preparation(file):
	fname, fext = file.rsplit('.', 1)
	if fext == 'txt':
		converter.convert_to_csv(file, fname + '.csv')
		return fname + '.csv'
	elif fext == 'csv':
		return file
	else:
		print('Bad file format! Exiting ...')
		exit()


def main(tracklist, playlist):

	print('[] Preparation')
	csv_file = file_preparation(tracklist)

	print('[] Authorization')
	user_id, spoti = authorization()

	print(f'[] Search from {csv_file}')
	search_from_file(csv_file, spoti)

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

	