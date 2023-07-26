from random import randint

from googleapiclient.discovery import build

videos = []


def get_random_podcast_link(playlist_id):
    global videos
    next_page_token = None

    youtube = build("youtube", "v3", developerKey="API KEY", cache_discovery=False)

    while True:
        pl_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        pl_response = pl_request.execute()
        videos.extend(
            list(
                "https://www.youtube.com/watch?v="
                + item["snippet"]["resourceId"]["videoId"]
                for item in pl_response["items"]
            )
        )

        next_page_token = pl_response.get("nextPageToken")

        if not next_page_token:
            break
    start, end = 1, len(videos) - 1
    return videos[randint(start, end)]
