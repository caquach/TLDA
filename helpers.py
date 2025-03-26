import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

PLAYLIST_PREFIX = {"videos": "UULF", "shorts": "UUSH", "streams": "UULV"}
PATH_DATA = Path.cwd() / Path(__file__).parent / "data"
PATH_CHANNEL = str(PATH_DATA / "channels.pickle")
PATH_HANDLES = str(PATH_DATA / "handles.txt")


def oauth_initialize():
    """
    Helper function to initialize OAuth 2.0 Client for Youtube account modification within scope
    Scope: https://www.googleapis.com/auth/youtube.force-ssl

    Returns:
        OAuth Credentials: Authorization token for managing YouTube account
    """
    # Verify if secret json exists
    secrets = str(PATH_DATA / "client_secrets.json")
    if not Path(secrets).exists():
        return None

    # Verify if token already exists
    credentials, client_token = None, str(PATH_DATA / "client.pickle")
    if Path(client_token).exists():
        print("Loading Past Credentials...")
        with open(client_token, "rb") as token:
            credentials = pickle.load(token)

    # Token creation/refresh
    if not credentials or not credentials.valid:
        # if token expired -> refresh it, otherwise -> create new one
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing Token...")
            credentials.refresh(Request())
        else:
            print("Fetching New Tokens...")

            flow = InstalledAppFlow.from_client_secrets_file(
                secrets,
                scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
            )

            flow.run_local_server(
                port=8080, prompt="consent", authorization_prompt_message=""
            )
            credentials = flow.credentials

        # Save the credentials for the next run
        with open(client_token, "wb") as f:
            print("Saving Credentials...")
            pickle.dump(credentials, f)

    return credentials


def validate_playlists(youtube, type, channels):
    """
    Helper Function to validate playlists
    TODO: filter by desired playlist: videos, shorts, streams, etc

    Args:
        type (str): upload type such as videos, shorts, streams
        channels_txt (str): Path to channels.txt

    Returns:
        list: Valid playlists to retrieve from
    """

    with open(channels, "rb") as f:
        ch = pickle.load(f)

        # create comma-separated string of playlists with "videos" prefix
        pl_prefixes = ",".join(
            PLAYLIST_PREFIX[type] + url[2:] for name, url in ch.items()
        )

    # if videos exist in the playlist, grab the playlist
    return {
        item["id"]
        for item in youtube.playlists()
        .list(part="id", id=pl_prefixes)
        .execute()["items"]
    }


def my_valid_playlist(youtube, playlist_id: str):
    """
    Helper to verify if playlist belongs to the signed in user

    Args:
        youtube (resource): YouTube resource object that interacts with API
        playlist_id (str): Your inputted playlist id to be added to

    Returns:
        bool: True if playlist belongs to user, False otherwise
    """
    found = False
    for item in (
        youtube.playlists().list(part="id", mine=True).execute()["items"]
    ):
        if item["id"] == playlist_id:
            found = True
            break

    return found


def get_handles():
    """
    Helper to retrieve user inputted handles along with id handle pairs from past runs.

    Returns:
        youtubers (set): set of new youtuber handles
        id_channel (set): set of id handle pairs from past runs
    """
    with open(PATH_HANDLES, "r") as f:
        handles = {y.lower().strip() for y in f}

    handles_past = set()
    id_channel = {}
    if Path(PATH_CHANNEL).exists():
        with open(PATH_CHANNEL, "rb") as f:
            id_channel = pickle.load(f)
            handles_past = {names for names, url in id_channel.items()}

    # create set of new youtubers to add, remove old entries if deleted from handles
    youtubers = handles ^ handles_past
    handles_remove = youtubers & handles_past
    for handle in handles_remove:
        print(f"Removed {handle} with id: {id_channel.pop(handle)}")
        youtubers.remove(handle)

    return youtubers, id_channel
