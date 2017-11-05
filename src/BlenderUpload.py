bl_info = {
    "name": "Youtube Uploader",
    "author": "Shelby Jueden",
    "version": (0,8),
    "blender": (2,78,0),
    "description": "Uploads a video file to Youtube from the Blender GUI",
    "warning": "Requires install of Google APIs for python",
    "category": "Render",
}

# python
import http.client
import httplib2
import os
import random
import sys
import time
import webbrowser
import threading

# blender
import bpy

# Youtube
from YouTube import *

youtube = YouTube()

def get_privacy_options(scene, context):
    youtube.authorize()

    items = []
    i = 1
    for option in youtube.PRIVACY_OPTIONS:
        items.append((option[0],option[1],option[2]))
        i += 1

    return items


def get_category_options(scene, context):
    youtube.authorize()

    items = []
    i = 1
    for option in youtube.get_usable_category_ids():
        items.append((option[0],option[1],option[1]))
        i += 1

    return items


def progress_update(status):
    print(str(status*100))
    scene = bpy.context.scene
    scene.youtube_upload.upload_progress = status * 100

def upload_begin():
    scene = bpy.context.scene
    scene.youtube_upload.video_upload_progress = 0
    if scene.youtube_upload.upload_file_use_render:
        scene.youtube_upload.upload_video_path = scene.render.filepath

    youtube.authorize()

    try:
        result = youtube.upload_video(
            video_path = bpy.path.abspath(scene.youtube_upload.upload_video_path),
            title=scene.youtube_upload.video_title,
            description=scene.youtube_upload.video_description,
            privacy="unlisted",
            progress_callback=progress_update
        )
        scene.youtube_upload.video_id = result['id']

        youtube.upload_thumbnail(
            scene.youtube_upload.video_id,
            bpy.path.abspath(scene.youtube_upload.upload_thumbnail_path))

    except HttpError as e:
        print(("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)))


class YoutubeKeyLink(bpy.types.Operator):
    '''Open web browser to API key creation guide'''
    bl_idname = "youtube_upload.open_key_link"
    bl_label = "Open page to get API Key"
    bl_options = {'REGISTER'}

    def execute(self, context):
        webbrowser.open(
            'https://developers.google.com/youtube/v3/getting-started'
        )

        privacy_options.append(("fake","Not an option","don't use this",4))
        return {'FINISHED'}   


#class AuthStorage(bpy.types.PropertyGroup):
#    token = bpy.props.StringProperty(name="Auth Token")
#    name = bpy.props.StringProperty(
#        name="Account Name", default="My Youtube Channel")


class YoutubeAddonPreferences(bpy.types.AddonPreferences):
    '''Preferences to store API key and auth tokens'''
    bl_idname = __name__
    
    client_id = bpy.props.StringProperty(name="client_id")
    client_secret = bpy.props.StringProperty(name="client_secret")
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="The API key for YouTube")
        layout.prop(self, "client_id")
        layout.prop(self, "client_secret")
        layout.operator(YoutubeKeyLink.bl_idname)


class YoutubeProperties(bpy.types.PropertyGroup):
    '''Video information for scene'''
    upload_video_path = bpy.props.StringProperty(
        name="Video", subtype="FILE_PATH")
    upload_thumbnail_path = bpy.props.StringProperty(
        name="Thumbnail", subtype="FILE_PATH")
    upload_file_use_render = bpy.props.BoolProperty(
        name="Use Video Render Path", default=True)
    upload_progress = bpy.props.FloatProperty(
        name = "Upload Progress", default=0,min=0,max=100,subtype="PERCENTAGE")
    
    video_title = bpy.props.StringProperty(
        name="Title")
    video_description = bpy.props.StringProperty(
        name="Description")
    video_privacy = bpy.props.EnumProperty(
        items=get_privacy_options, name = "Privacy")
    video_category = bpy.props.EnumProperty(
        items=get_category_options, name = "Category")
    video_id = bpy.props.StringProperty(
        name="Video ID", default="")

    youtube = YouTube()
    
    
class YoutubePanel(bpy.types.Panel):
    '''Properties panel to configure video information and start upload'''
    bl_idname = "RENDER_PT_youtube_upload"
    bl_label = "Youtube Upload"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    def draw(self, context):
        layout = self.layout
        
        scene = context.scene

        self.layout.label(text="File Settings:")
        col = layout.column()
        col.prop(scene.youtube_upload,"upload_file_use_render")
        sub = col.column()
        sub.prop(scene.youtube_upload,"upload_video_path")
        sub.enabled = (not scene.youtube_upload.upload_file_use_render)
        col.prop(scene.youtube_upload,"upload_thumbnail_path")
        
        self.layout.label(text="Video Info:")
        col = layout.column()
        col.prop(scene.youtube_upload,"video_title")
        sub = col.row()
        sub.prop(scene.youtube_upload,"video_description")
        col.prop(scene.youtube_upload,"video_privacy")
        col.prop(scene.youtube_upload,"video_category")
        col.prop(scene.youtube_upload,"video_id")
        col = layout.column()
        col.operator(YoutubeUpload.bl_idname)
        col.prop(scene.youtube_upload,"upload_progress")
        
        
class YoutubeUpload(bpy.types.Operator):
    '''Start thread to upload video'''
    bl_idname = "youtube_upload.upload"
    bl_label = "Upload Video"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        print("Start thread...")
        # Upload in thread to prevent locking UI
        t = threading.Thread(target=upload_begin)
        t.start()
        return {'FINISHED'}   


def register():
    bpy.utils.register_class(YoutubeProperties)
    bpy.utils.register_class(YoutubePanel)
    bpy.utils.register_class(YoutubeUpload)
    bpy.utils.register_class(YoutubeKeyLink)
    bpy.utils.register_class(YoutubeAddonPreferences)
    
    bpy.types.Scene.youtube_upload = \
        bpy.props.PointerProperty(type=YoutubeProperties)


def unregister():
    bpy.utils.unregister_class(YoutubeProperties)
    bpy.utils.unregister_class(YoutubePanel)
    bpy.utils.unregister_class(YoutubeUpload)
    bpy.utils.unregister_class(YoutubeKeyLink)
    bpy.utils.unregister_class(YoutubeAddonPreferences)
    
    del bpy.types.Scene.youtube_upload
    
    
if __name__ == "__main__":
    register() 
