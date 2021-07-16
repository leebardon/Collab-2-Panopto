import json
import requests
from tqdm import tqdm
from config import Config as Conf
from src.models import CollabJWT as Jwt
from src.models import CollabSessions as Session
from src.views import Logger

LOGGER = Logger.init_logger(__name__)


class WebService:
    def __init__(self):
        self.collab_key = Conf.credentials["collab_key"]
        self.collab_secret = Conf.credentials["collab_secret"]
        self.collab_domain = Conf.credentials["collab_base_url"]
        self.jsession = None
        self.cert = True if Conf.credentials["verify_certs"] == "True" else False

    def get_context(self):
        LOGGER.debug("")
        self.jsession = Jwt.CollabJWT(
            self.collab_domain, self.collab_key, self.collab_secret, self.cert
        )
        self.jsession.set_JWT()
        return self.jsession.get_JWT()

    def courses_data_from_collab(self):
        LOGGER.info("Contacting Collab API")
        json_pages = []
        token = self.get_context()

        def get_page(offset=0):
            url = f"https://{self.collab_domain}contexts?offset={offset}"
            r = requests.get(url, headers={"Authorization": "Bearer " + token})
            res = json.loads(r.text)

            if bool(res["results"]) == True:
                json_pages.append(res)
                # breakpoint()
                # offset += 1000
                # get_page(offset)

        if bool(json_pages) == False:
            get_page()

        return json_pages

    def search_for_recordings_by_uuid(self, course_uuid, search_from):
        LOGGER.debug(f"{course_uuid}, {search_from}")
        session = Session.CollabSessions(
            self.collab_domain, self.get_context(), self.cert
        )
        recordings = session.get_recordings(course_uuid, search_from)
        return recordings

    def get_recording_data(self, recording_id):
        LOGGER.debug(f"{recording_id}")
        session = Session.CollabSessions(
            self.collab_domain, self.get_context(), self.cert
        )
        rec_data = session.get_data(recording_id)
        return rec_data

    def delete_recording_from_collab(self, recording_id):
        LOGGER.debug(f"{recording_id}")
        session = Session.CollabSessions(
            self.collab_domain, self.get_context(), self.cert
        )
        delete_info = session.delete_recording(recording_id)
        return delete_info

    # def recordings_data_from_collab(self, start_time):
    #     url = f"https://{self.collab_domain}recordings?startTime={start_time}"
    #     token = self.get_context()
    #     res = requests.get(url, headers={"Authorization": "Bearer " + token})
    #     if res.status_code == 200:
    #         return json.loads(res.text)
