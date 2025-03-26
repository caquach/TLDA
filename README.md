# Too Lazy Didn't Add

Do you ever feel too lazy to add videos to your watch later playlist or miss a video in the sea of subscribed channels?

Well no need to fear, this Python script retrieves most recent videos from specified channel handles and insert them into your desired playlist (provided it exists)

Note: The Watch Later playlist (ID of `WL`) is unfortunately inaccessible through YouTube API v3, so please create your own playlist and grab its ID from the url.

For example from the url https://www.youtube.com/playlist?list=abcd, the ID would be `abcd`

### Usage
- cd to the directory with the Python files
- Provide 3 files to the data folder:
    1. client_secrets.json
    2. handles.txt
    3. my-pl.txt
```bash
python app.py
```

### client_secrets.json
- Create your own project on [Google Cloud Console](https://console.cloud.google.com/)
    - Web Application, Redirect URL: http://localhost:8080/

### Bugs
- Token refresh requests in oauth_initialize() doesn't work sometimes
    1. Delete client.pickle in the data folder as a temporary fix

### TODO
- Fix oauth_initialize() refresh token sometimes not working
- get_upload_playlists(): maybe rename function
- validate_playlists(): filter by desired playlist: videos, shorts, streams, etc
- make a GUI for this


# References:
1. YouTube API v3: https://developers.google.com/youtube/v3
2. Playlist Prefix Codes (coco0419): https://stackoverflow.com/questions/71192605/how-do-i-get-youtube-shorts-from-youtube-api-data-v3
3. OAuth Initialization: https://www.youtube.com/watch?v=vQQEaSnQ_bs
4. YouTube Time Format: https://www.w3.org/TR/NOTE-datetime