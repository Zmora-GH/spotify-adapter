import os
import re
import spotipy

from colorama import Fore, Style


def clean_data(line):
	""""""
	pattern1 = r'([\[\(][^\]\)]{0,}[\]\)])'
	pattern2 = r'[\(\[].{0,}'
	line = re.sub(pattern1, '', line)
	line = re.sub(pattern2, '', line)
	lines = line.split('-', 1)
	lines = [l.strip() for l in lines]
	return lines


def lazy_search(track, spoti):
	""""""
	result = spoti.search(f'{track[0]} - {track[1]}', limit=1, type='track')
	if result['tracks']['items']:
		return result['tracks']['items'][0]['uri']
	return None


def semihard_search(track, spoti):
	""""""
	result = spoti.search(track[1], limit=50, type='track')
	items = result['tracks']['items']
	if not items: return None
	for item in items:
		if not item: continue #None иногда прилетает от spotify
		if track[0].lower() == item['artists'][0]['name'].lower():
			return item['uri']
	return None


def search_from_file(tracklist, spoti):
	""""""
	hit, miss, missed = 0, 0, []
	with open(tracklist, 'r') as file, open('track_uris', 'w') as temp_uri_list:
		for n, track in enumerate(file.readlines()):
			clean_track = clean_data(track)
			result = lazy_search(clean_track, spoti)
			if not result:
				result = semihard_search(clean_track, spoti)
			if result:
				temp_uri_list.write(result + '\n')
				hit+=1
				print(Fore.GREEN + f'\t[{n:^4}][  OK  ] "{clean_track[0]} - {clean_track[1]}"')
			else:
				missed.append(track)
				miss+=1
				print(Fore.RED + f'\t[{n:^4}][  NF  ] "{clean_track[0]} - {clean_track[1]}"')	
	with open('missed', 'w') as missed_file:
		for item in missed:
			missed_file.write(item)
	search_from_file.count = {'hit': hit, 'miss': miss}


def add_to_playlist(playlist_uri, spoti):
	""""""
	try:
		with open('track_uris', 'r') as temp_uri_list:
			track_uris = [line.strip() for line in temp_uri_list.readlines()]
			tq = tqg(track_uris, N=50)
			for i, t in enumerate(tq):
				r = spoti.playlist_add_items(playlist_uri, t)
				ccount = i
			tcount = len(track_uris)
	except Exception as e:
		print('\t[FUCK] ', e.msg)
	finally:
		os.remove('track_uris')
		add_to_playlist.added = {'tracks':tcount, 'chunks':ccount}


def tqg(tlist, N=10):
	""""""
	L = list(tlist)
	while True:
		if len(L) > N:
			yield L[:N]
			del L[:N]
		else:
			yield L
			return []


def authorization():
	""""""
	scope = 'playlist-modify-public'
	spoti = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyOAuth(scope=scope))
	user_id = spoti.me()['id']
	return user_id, spoti


def main(tracklist, playlist):
	""""""
	#
	print('[] Authorization')
	user_id, spoti = authorization()
	#
	print(f'[] Search from {tracklist}')
	search_from_file(tracklist, spoti)
	#
	rate = search_from_file.count
	count = rate['hit'] + rate['miss']
	p = int(rate['hit'] * 100 / count)
	print(Style.RESET_ALL)
	print(f'[  Found: {p}%   {rate["hit"]} of  {count}  ]')
	#
	print(f'[] Create playlist {playlist}')
	playlist = spoti.user_playlist_create(user_id, playlist)
	#
	print('[] Add tracks to playlist')
	add_to_playlist(playlist['uri'], spoti)
	#
	added = add_to_playlist.added
	print(f'[  Added: {added["tracks"]} tracks in  {added["chunks"]} chunks  ]')


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print ('Please provide a tracklist file and playlist name!')
