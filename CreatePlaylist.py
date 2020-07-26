# PYTHON IS AN INTERPRETTED LANGUAGE (COMPILE BUTTON) AND OBJECT ORIENTED.

# format for storing and transporting data.  A key and value data format to transfer data (part of python)
import json
import os  # (part of python)

import google_auth_oauthlib.flow
import googleapiclient.discovery  # youtube APIv3
import googleapiclient.errors
# an HTTP library  (communication from user to code) (not part of python)
import requests
import youtube_dl

# takes the variable we want from secret file
from secret import spotify_user_id, spotify_token


class CreatePlaylist:

    def __init__(self):  # why 2 underscores?
        self.user_id = spotify_user_id  # takes the username in our secret file
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    # STEP 1: Sign into youtube  #Perfect
    def get_youtube_client(self):
        # COPIED FROM YOUTUE DATA API
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        # this is MY special info file to give me access to the goods.
        client_secrets_file = "client_secret.json"

        # “unverified,” it has not fully completed the OAuth app verification.
        # When your app is successfully verified, the unverified app screen is removed from your client.
        # Get credentials and create an API client      #There is something wrong starting here. with scope.
        # youtube data API is examples of sensitive scopes are some of the scopes
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # From YOUTUBE_API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    # STEP 2: grab like song on youtube // and create a dictionary of important song info
    def get_liked_videos(self):  # Perfect
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        # collect each video and get important info #loops through all song called item
        for item in response["items"]:
            video_title = item["snippet"]["title"]    # Up to here
            # plug in URL HERE (not done)
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])

            # use youtube_dl lib to collect the song name and artist
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download=False)

            song_name = video["track"]
            artist = video["artist"]

            # add a warning message when videos can't be processed****

            # save imported information
            self.all_song_info[video_title] = {
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,

                # add the uri, easy to get song to put into Playlist
                # call the function we wrote
                "spotify_uri": self.get_spotify_uri(song_name, artist)
            }

    # STEP 3: create a new playlist album  // Perfect function
    def create_playlist(self):
        # given information from site
        request_body = json.dumps({
            "name": "Youtube Liked Vids",
            "description": "All Liked Youtube Videos",
            "public": True
        })

        # endpoint (query)
        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id -- so we know where to save song to which playlist.
        return response_json["id"]

    # STEP 4: search for song  //should be perfect if not its bc of query.
    # Input -
    # Output -
    # rad the & as actual 'and'. I set it so only search for 20 songs (max)
    def get_spotify_uri(self, song_name, artist):

        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(  # double check  this
            song_name,
            artist
        )
        # get users artist and song name
        response = requests.get(  # get is the http method given in API
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        # recieve users song and artist data
        songs = response_json["tracks"]["items"]

        # only use the first song
        uri = songs[0]["uri"]

        return uri  # the specific song to add to album.

    # STEP 5: add song into album.  #perfect function
    # Putting the project together
    def add_song_to_playlist(self):
        # populate our songs dictionary
        self.get_liked_videos()

        # get all of uris
        uris = [info["spotify_uri"]
                for song, info in self.all_song_info.items()]

        # create a new playlist
        playlist_id = self.create_playlist()

        # add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        return response_json


if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()
