Blender Youtube Upload
=======================

This is a add-on for Blender that allows you upload videos to Youtube directly from the GUI. 


Installing Dependencies
-----------------------

You will need to install google-api-python-client with pip so blender can use the Youtube API

1. Download https://bootstrap.pypa.io/get-pip.py 
2. Run get-pip.py with the version of python blender is using. Likely "sudo python3 ./get-pip.py"
3. Use that pip install to install google-api-python-client. Likely "sudo pip3 install google-api-python-client"


Installing Add-On
-----------------

1. You will need to download `src/YouTubeUpload.py`.
2. Then in Blender open `File>User Prefrences>Add-ons` and select `Install from file` at the bottom.
3. Open the file you downloaded.
4. After it successfully installs it the list of add-ons will be filtered to just Youtube Upload. Expand the options for it.
5. You will need to put in credentials for a Google API key. You can click the button bellow the fields to find a guide for getting your own API key.


Features
--------

- Oauth2 athentication
- Set most of video metadata(Title, Description, Privacy)
- Custom thumbnail
- Upload progress bar


Not Yet Implemented
-------------------

 - Set category
 - Add tags


Known Issues
------------

 - Progress bar only redraws when you hover back and forth over it

Screenshots
-----------

![Upload Panel UI]https://raw.githubusercontent.com/AkBKukU/blenderYoutubeUpload/master/doc/img/2017-10-30_Panel.png
![User Prefs UI]https://raw.githubusercontent.com/AkBKukU/blenderYoutubeUpload/master/doc/img/2017-10-30_UserPrefs.png
