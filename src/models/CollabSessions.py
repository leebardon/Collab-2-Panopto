import requests
from src.views import Logger
from src.models import Utilities as Utils

LOGGER = Logger.init_logger(__name__)


class CollabSessions:
    def __init__(self, url, token, cert):
        LOGGER.debug("")
        self.url = url
        self.token = token
        self.cert = cert

    def get_recordings(self, course_uuid, start_time):
        LOGGER.debug(f"{course_uuid}, {start_time}")
        endpoint = (
            "https://"
            + self.url
            + "/recordings"
            + "?contextId="
            + course_uuid
            + "&startTime="
            + str(start_time)
        )
        bearer = "Bearer " + self.token
        rheaders = Utils.get_headers(bearer)
        r = requests.get(endpoint, headers=rheaders, verify=self.cert)
        return Utils.handle_response(r)

    def get_data(self, recording_id):
        LOGGER.debug(f"recording_id = {recording_id}")
        auth_str = "Bearer " + self.token
        url = "https://" + self.url + "/recordings/" + recording_id + "/data"
        headers = Utils.get_headers(auth_str)
        r = requests.get(url, headers, verify=self.cert)
        return Utils.handle_response(r)

    def delete_recording(self, recording_id):
        LOGGER.debug(f"{recording_id}")
        auth_str = "Bearer " + self.token
        url = f"https://{self.url}/recordings/{recording_id}"
        try:
            headers = Utils.get_headers(auth_str)
            r = requests.delete(url, headers, verify=self.cert,)
            r.raise_for_status()
            if r.status_code == 200:
                return True
            elif r.status_code == 404:
                LOGGER.warning(f"404 => {recording_id} not deleted from Collab.")
                return False
            else:
                return None
        except requests.exceptions.HTTPError as e:
            LOGGER.warning(str(e))
            pass


# NOTE function not used
# def get_recordings_data_secure(self, recording_id):
#     LOGGER.debug(f"{recording_id}")
#     auth_str = "Bearer " + self.token
#     url = "https://" + self.url + "/recordings/" + recording_id + "/data/secure"
#     headers = Utils.get_headers(auth_str)
#     r = requests.get(url, headers, verify=self.cert,)
#     return Utils.handle_response(r)
