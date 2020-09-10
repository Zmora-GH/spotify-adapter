wwimport base64
import json
import requests

import config


def b64code(message):
	messageBytes = message.encode('ascii')
	base64Bytes = base64.b64encode(messageBytes)
	return base64Bytes.decode('ascii')


def make_auth_request(message):
	headers = {'Authorization': f'Basic {message}'}
	data = {'grant_type': 'client_credentials'}
	r = requests.post(url=config.auth_url, headers=headers, data=data)
	print(r.json())
	return r.json()['access_token']


def get_token():
	clientId = config.clientId
	clientSecret = config.clientSecret
	message = b64code(f"{clientId}:{clientSecret}")
	return make_auth_request(message)


def search_track(track_name, artist, token):
	headers = {
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': f'Bearer {token}',
	}
	search_template = f'search?q={track_name}+artist:{artist}&type=track&limit=1'
	r = requests.get(url=config.api_url+search_template, headers=headers)
	res = {
		'artist_name': r.json()['tracks']['items'][0]['artists'][0]['name'],
		'track_name': r.json()['tracks']['items'][0]['name'],
		'track_uri': r.json()['tracks']['items'][0]['uri'],
	}
	return res


def create_playlist(name):
	#POST
	url = config.api_url + 'users/{user_id}/playlists'
	pass


def add_track_to_playlist():
	#POST
	url = config.api_url + 'playlists/{playlist_id}/track'
	pass

def get_my_id():
	#GET
	url = config.api_url + 'me'
	pass




def main():
	track_name = 'numb'
	artist = 'linkin+park'
	track = search_track(track_name, artist, get_token())
	print(track['track_uri'])
	


if __name__ == '__main__':
	main()
