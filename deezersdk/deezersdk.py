#!/usr/bin/env python

import requests
import webbrowser


class Track:

    deezer = None

    id_ = None
    title = None
    duration = None
    release_date = None

    def __init__(self, deezer, id, title, duration, release_date=None, **kwargs):
        """
        Create a Track
        :param Deezer deezer: obj to make other requests
        :param str id:
        :param str title:
        :param int duration:
        :param date release_date:
        :param kwargs: other params (see Deezer's documentation : https://developers.deezer.com/api/track)
        """

        self.deezer = deezer

        self.id_ = id
        self.title = title
        self.duration = duration
        self.release_date = release_date


class Playlist:

    deezer = None

    id_ = None
    title = None
    picture = None
    is_loved_track = None

    def __init__(self, deezer, id, title, picture, is_loved_track, **kwargs):
        """
        Create a Playlist
        :param Deezer deezer: obj to make other requests
        :param str id:
        :param str title:
        :param str picture:
        :param boolean is_loved_track:
        :param kwargs: other params (see Deezer's documentation : https://developers.deezer.com/api/playlist)
        """
        self.deezer = deezer

        self.id_ = id
        self.title = title
        self.picture = picture
        self.is_loved_track = is_loved_track


class Artist:

    deezer = None

    id_ = None
    name = None
    picture = None
    tracklist_url = None

    def __init__(self, deezer, id, name, picture, tracklist, **kwargs):
        """
        Create an Artist object
        :param Deezer deezer: obj to make other requests
        :param str id:
        :param str name:
        :param str picture: url of the artist picture
        :param tracklist: API Link to the top of this artist
        :param kwargs: other params (see Deezer's documentation : https://developers.deezer.com/api/artist)
        """
        self.deezer = deezer

        self.id_ = id
        self.name = name
        self.picture = picture
        self.tracklist_url = tracklist

    def get_tracks(self):
        """
        get artist track list
        :rtype: List of Track
        """
        response = self.deezer.req_get(url=self.tracklist_url)

        tracks = []
        for row in response.get('data'):
            tracks.append(Track(deezer=self.deezer, **row))

        return tracks


class Deezer:

    app_id = None
    access_token = None

    user_id = None
    tracklist = None

    def __init__(self, app_id, app_secret, code, token):
        self.app_id = app_id

        if token is None:
            url = f'https://connect.deezer.com/oauth/access_token.php?app_id={app_id}&secret={app_secret}&code={code}&output=json'
            print(url)
            user_response = requests.get(url)
            print(user_response.json())
            # TODO get token
            # TODO get expires
        else:
            self.access_token = token

    def req_get(self, url=None, uri=None,):
        """
        Perform a GET request
        :param str url:
        :param str uri: partial url
        :return: json response
        """
        if uri:
            url = f'https://api.deezer.com{uri}'
        response = requests.get(url, {'access_token': self.access_token})
        if response is not None:
            return response.json()

    def get_flow(self):
        """
        Get use flow (list of tracks
        :rtype: list of Track
        """
        response = self.req_get(uri='/user/me/flow')

        tracks = []
        for row in response.get('data'):
            tracks.append(Track(deezer=self, **row))

        return tracks

    def get_my_playlists(self):
        """
        Get my playlists
        :rtype: list of Playlist
        """
        response = self.req_get(uri='/user/me/playlists')

        playlists = []
        for row in response.get('data'):
            playlists.append(Playlist(deezer=self, **row))

        return playlists

    def get_my_favorite_artists(self):
        """
        Get the list of my favorites artists
        :rtype: List of Artist
        """
        all_loaded = False
        artists = []
        url = None

        while not all_loaded:
            if url is None:
                response = self.req_get(uri=f'/user/me/artists')
            else:
                response = self.req_get(url=url)

            for row in response.get('data'):
                artists.append(Artist(deezer=self, **row))

            if response.get('next'):
                url = response['next']
            else:
                all_loaded = True

        return artists

    def get_widget(self, tracks=None, playlist=None, width=700, height=400):
        """
        Play a list of tracks or a playlist
        :param List[Track] tracks:
        :param Playlist playlist:
        :param number width: width of the widget
        :param number height: height of the widget
        """
        ids = None
        type_ = None

        if tracks is not None:
            ids = []
            for track in tracks:
                ids.append(track.id_)
            type_ = 'tracks'
        elif playlist is not None:
            ids = playlist.id_
            type_ = 'playlist'

        url = f'https://www.deezer.com/plugins/player?' \
              f'app_id={self.app_id}' \
              '&format=classic' \
              '&autoplay=true' \
              '&playlist=true' \
              f'&width={width}&height={height}&color=ff0000' \
              '&layout=dark' \
              '&size=medium' \
              f'&type={type_}' \
              f'&id={ids}' \
              '&popup=true' \
              '&repeat=' \
              '0&current_song_index=0' \
              '&current_song_time=2' \
              '&playing=true'

        return url