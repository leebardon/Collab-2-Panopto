from src.models.Limiter import RateLimiter
import requests
import urllib.parse
import time


class PanoptoFolders:
    def __init__(self, server, ssl_verify, oauth2, username, password):
        """
        Constructor of folders API handler instance.
        This goes through authorization step of the target server.
        """
        self.server = server
        self.ssl_verify = ssl_verify
        self.oauth2 = oauth2
        self.requests_session = requests.Session()
        self.requests_session.verify = self.ssl_verify
        # self.__setup_or_refresh_access_token()

        # NEW - JBRUYLANT 230621
        self.username = username
        self.password = password
        self.__setup_resource_owner_grant_access_token()

    def __setup_or_refresh_access_token(self):
        """
        This method invokes OAuth2 Authorization Code Grant authorization flow.
        It goes through browser UI for the first time.
        It refreshes the access token after that and no user interfaction is requetsed.
        This is called at the initialization of the class, as well as when 401 (Unaurhotized) is returend.
        """
        access_token = self.oauth2.get_access_token_authorization_code_grant()
        self.requests_session.headers.update(
            {"Authorization": "Bearer " + access_token}
        )

    def __setup_resource_owner_grant_access_token(self,):
        """
        This method invokes OAuth2 Authorization Code Resource Owner Grant authorization flow.
        No browser required!
        """
        access_token = self.oauth2.get_access_token_resource_owner_grant(
            self.username, self.password
        )
        self.requests_session.headers.update(
            {"Authorization": "Bearer " + access_token}
        )

    def __check_retry_needed(self, response):
        """
        Inspect the response of a requets' call.
        True indicates the retry needed, False indicates success. Othrwise an exception is thrown.
        Reference: https://stackoverflow.com/a/24519419

        This method detects 401 (Unauthorized), refresh the access token, and returns as "is retry needed".
        This method also detects 429 (Too many request) which means API throttling by the server. Wait a sec and return as "is retry needed".
        Prodcution code should handle other failure cases and errors as appropriate.
        """
        if response.status_code == 200:
            return False

        if response.status_code == 401:
            print("Unauthorized. Refresh access token.")
            self.__setup_or_refresh_access_token()
            return True

        if response.status_code == 429:
            print("Too many requests. Wait one sec, and retry.")
            time.sleep(1)
            return True

        # Throw unhandled cases. Returns HTTPError object.
        response.raise_for_status()

    @RateLimiter(max_calls=5, period=1)
    def search_folders(self, course_id):
        """ Calls GET /api/v1/folders/search on course_id and returns Panopto folder/s.
        Args:
            course_id (str): Course_id
        Returns:
            [list]: Returns Panopto folder/s linked to course_id
        """
        result = []
        page_number = 0
        while True:
            url = (
                f"https://{self.server}/Panopto/api/v1/folders/search?searchQuery="
                f"{urllib.parse.quote_plus(course_id)}&pageNumber={page_number}"
            )
            resp = self.requests_session.get(url=url)
            if self.__check_retry_needed(resp):
                continue
            data = resp.json()
            entries = data["Results"]
            if len(entries) == 0:
                break
            for entry in entries:
                result.append(entry)
            page_number += 1
        return result
