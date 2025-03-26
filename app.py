from pathlib import Path

from youtube_tools import YoutubeTools

if __name__ == "__main__":
    # workflow
    yt = YoutubeTools()
    yt.get_upload_playlists()  # build list of channels to retrieve from
    video_list = yt.get_videos_ids("videos", 3)

    pl_path = str(Path.cwd() / Path(__file__).parent / "data" / "my-pl.txt")
    with open(pl_path, "r") as p:
        yt.add_to_playlist(video_list, p.read())

    input("Press Enter To Exit")
