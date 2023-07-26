from random import randint
from typing import List

from googleapiclient.discovery import build

from .consts import SHORT_WELCOME_VIDEO


def get_random_podcast_link(playlist_id: str) -> str:
    """Gets random podcast link for YouTube."""
    videos = []
    next_page_token = None

    youtube = build(
        "youtube",
        "v3",
        developerKey="YouTube API Token",
        cache_discovery=False,
    )

    while True:
        youtube_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        youtube_response = youtube_request.execute()
        videos.extend(
            list(
                "https://www.youtube.com/watch?v="
                + item["snippet"]["resourceId"]["videoId"]
                for item in youtube_response["items"]
            )
        )

        next_page_token = youtube_response.get("nextPageToken")

        if not next_page_token:
            break
    return validate_podcast(videos)


def validate_podcast(videos: List[str]) -> str:
    """Checks if podcast link is not for short video."""
    start, end = 1, len(videos) - 1
    podcast = videos[randint(start, end)]
    while podcast == SHORT_WELCOME_VIDEO:
        podcast = videos[randint(start, end)]
    return podcast
