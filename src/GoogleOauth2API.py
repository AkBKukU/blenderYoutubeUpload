import httplib2
import http.client
import os
import logging
import socket
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client import _helpers
from oauth2client import client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow 
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
class GoogleOauth2API:
    path_client_secret = "client_secret.json"
    path_access_token = "youtube-token.json"

    key_client_id = ""
    key_client_secret = ""

    API_SERVICE_NAME = ""
    API_VERSION = ""
    API_SCOPE = ""

    service = None

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, 
        http.client.NotConnected, http.client.IncompleteRead, 
        http.client.ImproperConnectionState, http.client.CannotSendRequest, 
        http.client.CannotSendHeader, http.client.ResponseNotReady,
        http.client.BadStatusLine
    )

    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

   
    def set_client_secret_path(self,path_client_secret):
        self.path_client_secret = path_client_secret


    def set_access_token_path(self,path_access_token):
        self.path_access_token = path_access_token


    def api_info(self, API_SERVICE_NAME, API_VERSION, API_SCOPE):
        """ 
        Setup the access information for the service

        :param API_SERVICE_NAME: Name for the service API
        :param API_VERSION: version number for the API
        :param API_SCOPE: Scope for access permissions

        :returns: JSON text of token

        """
        self.API_SERVICE_NAME = API_SERVICE_NAME
        self.API_VERSION = API_VERSION
        self.API_SCOPE = API_SCOPE


    def api_key(self, client_id="",client_secret=""):
        """
        Specify an API key to use instead of using a JSON file

        :param client_id: client_id from the JSON file
        :param client_secret: client_secret from the JSON file
        """
        self.key_client_id = client_id
        self.key_client_secret = client_secret


    def authorize(self, use_token_file=True, token_contents = ""):
        """ 
        Creates an authorized service object to use the given API.

        :param use_token_file: Bool to use file or string based token
        :parma token_contents: String contents of an access token

        :returns: JSON text of token

        """
        flow = self.get_flow()
        if not use_token_file:
            # Use string token
            if not token_contents:
                # No token given, create new
                credentials = run_flow_storageless(flow)
            else:
                # Use given token
                credentials = client.Credentials.new_from_json(
                    token_contents)
        else:
            # Use file token
            storage = Storage(self.path_access_token)
            credentials = storage.get()
            if credentials is None or credentials.invalid:
                # No token found, create new
                credentials = run_flow(flow, storage)

        # Build the service object
        self.service = build(self.API_SERVICE_NAME,
            self.API_VERSION,
            http=credentials.authorize(httplib2.Http()))
        return credentials.to_json()


    def get_flow(self):
        """ 
        Gets authentication to use the API from given keys. Either as file or
        strings.

        :returns: flow object with API access credentials

        """
        if self.key_client_id and self.key_client_secret:
            # Create flow from API key strings
            return OAuth2WebServerFlow(client_id=self.key_client_id,
                client_secret=self.key_client_secret,           
                scope=self.API_SCOPE,
                redirect_uri="http://localhost"
            )
        else:
            # Create flow from file
            return flow_from_clientsecrets(self.path_client_secret,
                scope=self.API_SCOPE,
                message="API key file \"" + self.path_client_secret + \
                    "\" not found"
            )


    def resumable_upload(self,insert_request,progress_callback=None):
        """
        Proccess a MediaFileUpload insert request in chunks

        :param insert_request: The file upload request
        :param progress_callback: Function pointer to pass the progress to the application

        :return: The response from the server
        """
        response = None
        error = None
        retry = 0
        
        httpretry = httplib2.RETRIES
        httplib2.RETRIES = 1

        # Upload file until response is received
        while response is None:
            try:
                # Upload file chunk
                status, response = insert_request.next_chunk()
                # Use status for progress
                if status and progress_callback:
                    # MediaFileUpload chunksize determines the frequency of this
                        progress_callback(status.progress())
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" \
                        % (e.resp.status,e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e
            
            # Handle errors
            if error is not None:
                print( error)
                error = None
                retry += 1
                if retry > self.MAX_RETRIES:
                    print("Out of retries")
                    return
        
                # Wait semi-random time before retrying upload
                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                time.sleep(sleep_seconds)

        httplib2.RETRIES = httpretry

        return response






    def run_flow_storageless(flow, flags=None, http=None):
        """ 
        Modified version of the built in run_flow to eliminate need for
        Storage object.

        Original: http://oauth2client.readthedocs.io/en/latest/_modules/oauth2client/tools.html#run_flow
        """
        if flags is None:
            flags = argparser.parse_args()
        logging.getLogger().setLevel(getattr(logging, flags.logging_level))
        if not flags.noauth_local_webserver:
            success = False
            port_number = 0
            for port in flags.auth_host_port:
                port_number = port
                try:
                    httpd = ClientRedirectServer((flags.auth_host_name, port),
                                                 ClientRedirectHandler)
                except socket.error:
                    pass
                else:
                    success = True
                    break
            flags.noauth_local_webserver = not success
            if not success:
                print(_FAILED_START_MESSAGE)

        if not flags.noauth_local_webserver:
            oauth_callback = 'http://{host}:{port}/'.format(
                host=flags.auth_host_name, port=port_number)
        else:
            oauth_callback = client.OOB_CALLBACK_URN
        flow.redirect_uri = oauth_callback
        authorize_url = flow.step1_get_authorize_url()

        if not flags.noauth_local_webserver:
            import webbrowser
            webbrowser.open(authorize_url, new=1, autoraise=True)
            print(_BROWSER_OPENED_MESSAGE.format(address=authorize_url))
        else:
            print(_GO_TO_LINK_MESSAGE.format(address=authorize_url))

        code = None
        if not flags.noauth_local_webserver:
            httpd.handle_request()
            if 'error' in httpd.query_params:
                sys.exit('Authentication request was rejected.')
            if 'code' in httpd.query_params:
                code = httpd.query_params['code']
            else:
                print('Failed to find "code" in the query parameters '
                      'of the redirect.')
                sys.exit('Try running with --noauth_local_webserver.')
        else:
            code = input('Enter verification code: ').strip()

        try:
            credential = flow.step2_exchange(code, http=http)
        except client.FlowExchangeError as e:
            sys.exit('Authentication has failed: {0}'.format(e))

        print('Authentication successful.')

        return credential



