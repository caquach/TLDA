import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path

from googleapiclient.discovery import build

from helpers import (
    get_handles,
    my_valid_playlist,
    oauth_initialize,
    validate_playlists,
)

PATH_DATA = Path.cwd() / Path(__file__).parent / "data"
PATH_CHANNEL = str(PATH_DATA / "channels.pickle")
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class YoutubeTools:
    def __init__(self):
        token = oauth_initialize()
        self.youtube = build("youtube", "v3", credentials=token)

    def get_upload_playlists(self):
        """
        Function to retrieve overall uploads playlist ID by user handle and write to a file

        """
        youtubers, id_channel = get_handles()
        if not youtubers:
            print("No new channels to be added")
        else:
            print(f"Retrieving {len(youtubers)} new upload ID(s)")

        for channel in youtubers:
            c = (
                self.youtube.channels()
                .list(part="contentDetails", forHandle=channel)
                .execute()
            )

            if c["pageInfo"]["totalResults"] > 0:
                id_channel[channel] = c["items"][0]["contentDetails"][
                    "relatedPlaylists"
                ]["uploads"]

        with open(PATH_CHANNEL, "wb") as f:
            pickle.dump(id_channel, f)

    def get_videos_ids(self, type: str, max_vids: int):
        """
        Retrieve a list of video IDs from the given file of upload playlist IDs since last time checked.
        TODO: per channel upload type toggle

        Args:
            type (str): Type of upload to retrieve
            max_vids (int): Max amount of videos retrieved in each playlist
        Returns:
            list : uploaded videos in the given playlists within the last time checked
        """
        if not Path(PATH_CHANNEL).exists():
            return []

        valid_playlists = validate_playlists(self.youtube, type, PATH_CHANNEL)
        if not valid_playlists:
            return []

        vids = []
        past_check = str(PATH_DATA / "time.pickle")
        if Path(past_check).exists():
            with open(past_check, "rb") as time_check:
                last_time = pickle.load(time_check)
            print(f"Last Checked: {last_time} UTC")
        else:
            last_time = (
                (datetime.now(timezone.utc) - timedelta(days=1))
                .replace(microsecond=0)
                .isoformat()
            )
            print(f"No previous check, setting to yesterday: {last_time} UTC")

        for pl in valid_playlists:
            response = (
                self.youtube.playlistItems()
                .list(
                    part="contentDetails", playlistId=pl, maxResults=max_vids
                )
                .execute()
            )

            # only add IDs since last time checked
            vids.extend(
                i["contentDetails"]["videoId"]
                for i in response["items"]
                if datetime.strptime(
                    i["contentDetails"]["videoPublishedAt"], DATETIME_FORMAT
                )
                > datetime.strptime(last_time, DATETIME_FORMAT)
            )

        with open(past_check, "wb") as f:
            last_time = (
                datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            )
            pickle.dump(last_time, f)

        return vids

    def add_to_playlist(self, videos: list[str], playlist_id: str):
        """
        Add videos found to the specified playlist.
        The watch later playlist is unfortunately inaccessible through YouTube API v3.

        Args:
            videos (list[str]): List of video IDs.
            playlist_id (str): ID of the playlist to add to.
        """

        if not my_valid_playlist(self.youtube, playlist_id):
            print("Invalid user playlist")
            return None
        else:
            print("Found valid user playlist")

        if not videos:
            print("No videos to be added")
            return None

        # need OAuth with scope force.ssl
        for vid in videos:
            # reponse =
            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": vid,
                        },
                    }
                },
            ).execute()
            # response.execute()

        print(
            f"Successfully added {len(videos)} videos to your specified playlist"
        )
