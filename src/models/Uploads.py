import os
import time
from config import Config
from src.views import Logger
from src.models.PanoptoFolders import PanoptoFolders
from src.models.PanoptoOAuth2 import PanoptoOAuth2
from src.models.PanoptoUploader import PanoptoUploader
from src.models.PanoptoSessions import PanoptoSessions
from src.models import Utilities as Utils
from src.views import Logger


LOGGER = Logger.init_logger(__name__)


class Uploads:
    def __init__(self) -> None:
        self.__ppto_server = Config.credentials["ppto_server"]
        self.__ppto_client_id = Config.credentials["ppto_client_id"]
        self.__ppto_client_secret = Config.credentials["ppto_client_secret"]
        self.__ppto_username = Config.credentials["ppto_username"]
        self.__ppto_password = Config.credentials["ppto_password"]
        self.__ssl_verify = True

        self.oauth2 = PanoptoOAuth2(
            self.__ppto_server,
            self.__ppto_client_id,
            self.__ppto_client_secret,
            self.__ssl_verify,
        )
        self.uploader = PanoptoUploader(
            self.__ppto_server,
            self.__ssl_verify,
            self.oauth2,
            self.__ppto_username,
            self.__ppto_password,
        )
        self.folders = PanoptoFolders(
            self.__ppto_server,
            self.__ssl_verify,
            self.oauth2,
            self.__ppto_username,
            self.__ppto_password,
        )
        self.sessions = PanoptoSessions(
            self.__ppto_server,
            self.__ssl_verify,
            self.oauth2,
            self.__ppto_username,
            self.__ppto_password,
        )

    def upload_video(
        self, file_path: str, date_created: str, ppto_folder_id: str
    ) -> dict:
        """Uploads video to given folder in Panopto
        Args:
            file_path (str): Path to file that will be uploaded
            ppto_folder_id (str): Upload destination folder ID in Panopto
        Returns:
            dict: Upload status {int: 'Status'}
        """
        LOGGER.debug("")
        Utils.handle_types([(file_path, ""), (ppto_folder_id, "")])
        file_name = os.path.basename(file_path)
        LOGGER.info(f"Uploading {file_name} => {ppto_folder_id}")

        return self.uploader.upload(file_path, date_created, ppto_folder_id)

    def get_folder_id_from_course_id(self, course_id: str) -> str:
        """Retrieves folder ID in panopto from given course ID
        Args:
            course_id (str): Course ID as found in Collaborate
        Raises:
            IndexError: No folder found
            ValueError: More than one folder found
        Returns:
            str: Folder ID in Panopto corresponding to given Course ID
        """
        LOGGER.debug(f"{course_id}")
        Utils.handle_types([course_id, ""])

        result = self.folders.search_folders(course_id)
        if len(result) == 0:
            msg = f"No Panopto folder found for: {course_id}"
            # print(msg)
            LOGGER.error(msg)
            # raise IndexError(msg)

        elif len(result) > 1:
            matched_folders = []
            for res in result:
                matched_folders.append({res["Name"]: res["Id"]})

            msg = f"More than one folder found for course_id: {course_id}. See dbg.log for full list"
            LOGGER.error(msg)
            LOGGER.debug(f"List of matched folders:\n{matched_folders}")

        else:
            return result[0]["Id"]

    def check_recordings_on_panopto(
        self, list_of_recordings: list, ppto_folder_id: str
    ):
        """Retrieves all sessions (aka recordings) in panopto folder
           Compares with given list of recordings
           Tells you which ones from list_of_recordings are not online on panopto
        Args:
            folder_id (str): folder id to search for sessions in
            list_of_recordings (list): list of recordings you want to compare to those online
        Returns:
            list: list of sessions from list_of_recordings that are not on panopto
        """
        LOGGER.debug(f"{list_of_recordings}, {ppto_folder_id}")
        Utils.handle_types([(list_of_recordings, []), (ppto_folder_id, "")])

        session_result = self.sessions.search_sessions(ppto_folder_id)
        present_on_ppto = []
        [present_on_ppto.append({s["Name"]: s["Id"]}) for s in session_result]
        # Go through downloaded Collab recordings and check if present on Panopto
        absent, present = Utils.return_absent_present(
            present_on_ppto, list_of_recordings
        )

        return absent, present

    def upload_list_of_recordings(
        self, recording_paths: list, rec_ids_date_created: dict, ppto_folder_id: str
    ):
        LOGGER.debug(f"{ppto_folder_id}, {recording_paths}")
        LOGGER.info(f"Uploading to {ppto_folder_id}")
        unsuccessful_uploads = []
        for path in recording_paths:
            date_created = Utils.get_date_created(path, rec_ids_date_created)
            upload_status = self.upload_video(path, date_created, ppto_folder_id)
            if upload_status["Status_Value"] != 4:
                msg = f"Something went wrong during upload. {upload_status['Status_Value']}: {upload_status['Status_Name']}"
                LOGGER.error(msg)
                unsuccessful_uploads.append(path)
                # Try to delete failed session
                print("  Something went wrong, deleting failed upload...")
                LOGGER.info("Attempting to delete failed session")
                time.sleep(3)
                try:
                    failed_session_id = self.sessions.search_sessions(
                        os.path.basename(path)
                    )[0]["Id"]
                    self.sessions.delete_session(failed_session_id)
                except Exception as e:
                    LOGGER.error("Deletion failed. {0}".format(e))
            else:
                LOGGER.info("Upload successful!")

        return unsuccessful_uploads
