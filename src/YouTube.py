from GoogleOauth2API import *
from apiclient.http import MediaFileUpload

class YouTube(GoogleOauth2API):

    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    YOUTUBE_API_SCOPE = "https://www.googleapis.com/auth/youtube " + \
        "https://www.googleapis.com/auth/youtube.upload " + \
        "https://www.googleapis.com/auth/youtubepartner"

    # Privacy settings for uploaded video
    PRIVACY_OPTIONS = [
        # Value    Name      Description
        ("private", "Private", "Only you can see the video"),
        ("unlisted", "Unlisted", "Anyone can see the video with the link"),
        ("public", "Public", "Everyone can see the video"),
    ]


    def __init__(self):
        self.api_info(self.YOUTUBE_API_SERVICE_NAME,
                self.YOUTUBE_API_VERSION,
                self.YOUTUBE_API_SCOPE
        )


    def get_usable_category_ids(self):
        categories = self.service.videoCategories().list(part='snippet', regionCode='US').execute()
        category_ids=[]
        for item in categories['items']:
            if item['snippet']['assignable']:
                category_ids.append((item['id'],item['snippet']['title']))

        return category_ids


    def get_all_categories(self):
        results = self.service.videoCategories().list(part='snippet', regionCode='US').execute()
        return results


    def upload_video(self,
        video_path=None,
        title="",
        description="",
        tags=None,
        category=22,
        privacy="private",
        progress_callback=None):
        """
        Upload a video file. Metadata is set at the same time. 

        :param video_path: The filepath of the video to upload
        :param title: Video title
        :param description: Video description
        :param tags: Tags to add to the video
        :param category: Numerical ID for the video category
        :param privacy: The privacy setting for the video

        :return: The response from the server
        """
        body=dict(
            snippet=dict(
                title=title,
                description=description,
                tags=tags,
                categoryId=category
            ),
            status=dict(
            privacyStatus=privacy
            )
        )

        insert_request = self.service.videos().insert(
            part=",".join(list(body.keys())),
            body=body,
            media_body=MediaFileUpload(
                video_path, 
                chunksize=4*1024*1024,
                resumable=True
            )
        )

        return self.resumable_upload(insert_request,progress_callback)


    def upload_thumbnail(self,video_id,image_path):
        """
        Upload and image to use a a thumbnail for a given video id

        :param video_id: The ID for the video to add the thumbnail to
        :param image_path: The filepath for the image to upload
        """
        self.service.thumbnails().set(
            videoId=video_id,
            media_body=image_path
        ).execute()


