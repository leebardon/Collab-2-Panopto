import os
import requests
import codecs
import time
from datetime import datetime
import copy
import boto3  # AWS SDK (boto3)
import urllib3
from src.views import Logger

LOGGER = Logger.init_logger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Size of each part of multipart upload must be between 5MB and 25MB or Panopto server may fail.
PART_SIZE = 5 * 1024 * 1024
MANIFEST_FILE_TEMPLATE = "upload_manifest_template.xml"
MANIFEST_FILE_NAME = "upload_manifest_generated.xml"

UPLOAD_STATUS = {
    0: "UploadStart",
    1: "Uploading",
    2: "UploadCancelled",
    3: "Processing",
    4: "Complete",
    5: "ProcessingError",
    6: "DeletingFiles",
    7: "Deleted",
    8: "DeletingError",
}


class PanoptoUploader:
    def __init__(
        self, server, ssl_verify, oauth2, username, password
    ):  # mbk added username pass for user auth.
        """
        Constructor of uploader instance. 
        This goes through authorization step of the target server.
        """
        self.server = server
        self.ssl_verify = ssl_verify
        self.oauth2 = oauth2
        self.username = username  # mbk for 2lo
        self.password = password  # mbk for 2lo
        self.requests_session = requests.Session()
        self.requests_session.verify = self.ssl_verify
        self.__setup_resource_owner_grant_access_token()

    # def __setup_or_refresh_access_token(
    #     self,
    # ):  # Used for 3LO flow... we're going to just get a token with 2LO
    #     """
    #     This method invokes OAuth2 Authorization Code Grant authorization flow.
    #     It goes through browser UI for the first time.
    #     It refreshes the access token after that and no user interfaction is requetsed.
    #     This is called at the initialization of the class, as well as when 401 (Unaurhotized) is returend.
    #     """
    #     access_token = self.oauth2.get_access_token_authorization_code_grant()
    #     self.requests_session.headers.update(
    #         {"Authorization": "Bearer " + access_token}
    #     )

    def __setup_resource_owner_grant_access_token(
        self,
    ):  # Used for 3LO flow... we're going to just get a token with 2LO
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
        Inspect the response of a request call.
        True indicates  retry needed, False indicates success. Othrwise an exception is thrown.
        """
        LOGGER.debug("")
        if response.status_code // 100 == 2:
            return False

        if response.status_code == requests.codes.forbidden:
            LOGGER.debug(
                "Forbidden. This may mean token expired. Refresh access token."
            )
            self.__setup_resource_owner_grant_access_token()  # NEW JBRUYLANT 280621
            return True

        response.raise_for_status()

    def upload(self, file_path, date_created, folder_id):
        """Main upload method to go through all required steps.
        Returns:
            dict: {"Status_Value": int, "Status_Name": str}. Indicates how the upload went
        """
        LOGGER.debug("")
        session_upload = self.__create_session(folder_id)
        upload_id = session_upload["ID"]
        upload_target = session_upload["UploadTarget"]
        self.__multipart_upload_single_file(upload_target, file_path)
        self.__create_manifest_for_video(file_path, date_created, MANIFEST_FILE_NAME)
        self.__multipart_upload_single_file(upload_target, MANIFEST_FILE_NAME)
        self.__finish_upload(session_upload)
        upload_status = self.__monitor_progress(upload_id)

        # if upload_status["Status_Value"] == 5:  # Processing error
        #     time.sleep(3)
        #     self.__delete_upload(session_upload)
        #     upload_status = self.__monitor_progress(upload_id)

        return upload_status

    def __create_session(self, folder_id):
        """   Creates an upload session. Return sessionUpload object.
        Args:
            folder_id (str): Panopto folder_id
        Returns:
            [obj]: sessionUpload object
        """
        LOGGER.debug("")
        while True:
            print("Calling POST PublicAPI/REST/sessionUpload endpoint")
            url = f"https://{self.server}/Panopto/PublicAPI/REST/sessionUpload"
            payload = {"FolderId": folder_id}
            headers = {"content-type": "application/json"}
            resp = self.requests_session.post(url=url, json=payload, headers=headers)
            if not self.__check_retry_needed(resp):
                break

        return resp.json()

    def __multipart_upload_single_file(self, upload_target, file_path):
        """
        Upload a single file by using Multipart upload protocol.
        We use AWS SDK (boto3) underneath for this step.
        """
        LOGGER.debug("")
        elements = upload_target.split("/")
        service_endpoint = "/".join(elements[0:-2:])
        bucket = elements[-2]
        prefix = elements[-1]
        object_key = "{0}/{1}".format(prefix, os.path.basename(file_path))

        print(f"Upload {file_path} with multipart upload protocol")

        s3 = boto3.session.Session().client(
            service_name="s3",
            endpoint_url=service_endpoint,
            verify=self.ssl_verify,
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )

        mpu = s3.create_multipart_upload(Bucket=bucket, Key=object_key)
        mpu_id = mpu["UploadId"]
        parts = []
        transferred_bytes = 0
        total_bytes = os.stat(file_path).st_size
        with open(file_path, "rb") as f:
            i = 1
            while True:
                data = f.read(PART_SIZE)
                if not len(data):
                    break
                part = s3.upload_part(
                    Body=data,
                    Bucket=bucket,
                    Key=object_key,
                    UploadId=mpu_id,
                    PartNumber=i,
                )
                parts.append({"PartNumber": i, "ETag": part["ETag"]})
                transferred_bytes += len(data)
                print(f"-- {transferred_bytes} of {total_bytes} bytes transferred")
                i += 1

        result = s3.complete_multipart_upload(
            Bucket=bucket,
            Key=object_key,
            UploadId=mpu_id,
            MultipartUpload={"Parts": parts},
        )

    # TODO This is where we can add custom description to our video uploads
    def __create_manifest_for_video(self, file_path, date_created, manifest_file_name):
        """ Creates manifest XML file for a single video file, based on template.
        Args:
            file_path (path): Path to recording (to used as upload file name)
            manifest_file_name (str): Filename to call generated manifest
        """
        file_name = os.path.basename(file_path)
        with open(MANIFEST_FILE_TEMPLATE) as fr:
            template = fr.read()
        content = (
            template.replace("{Title}", file_name)
            .replace(
                "{Description}",
                f"Created: {date_created[0] if date_created != None else 'unknown date'} => Transferred to Panopto:  {datetime.today().strftime('%Y-%m-%d')}",
            )
            .replace("{Filename}", file_name)
            .replace("{Date}", datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f-00:00"))
        )
        with codecs.open(manifest_file_name, "w", "utf-8") as fw:
            fw.write(content)

    def __finish_upload(self, session_upload):
        """
        Finish upload.
        """
        upload_id = session_upload["ID"]
        upload_target = session_upload["UploadTarget"]

        while True:
            url = f"https://{self.server}/Panopto/PublicAPI/REST/sessionUpload/{upload_id}"
            payload = copy.copy(session_upload)
            payload["State"] = 1
            headers = {"content-type": "application/json"}
            resp = self.requests_session.put(url=url, json=payload, headers=headers)
            if not self.__check_retry_needed(resp):
                break

        print("Waiting for upload to complete, this can take a while...")

    def __monitor_progress(self, upload_id):
        """
        Polling status API until process completes.
        """
        previous_state = None
        while True:
            time.sleep(5)
            url = f"https://{self.server}/Panopto/PublicAPI/REST/sessionUpload/{upload_id}"
            resp = self.requests_session.get(url=url)
            if self.__check_retry_needed(resp):
                continue
            session_upload = resp.json()
            state = int(session_upload["State"])
            if state != previous_state:
                previous_state = state
                print(
                    "  State: {0}".format(
                        UPLOAD_STATUS.get(session_upload["State"], "Unkown State")
                    )
                )

            if int(session_upload["State"]) in [
                4,
                5,
                7,
                8,
            ]:  # Status requiring a break in monitoring
                break

        upload_status = {
            "Status_Value": int(session_upload["State"]),
            "Status_Name": UPLOAD_STATUS.get(session_upload["State"], "Unkown State"),
        }
        return upload_status

    # This doesn't work very well, I've not managed to delete a file
    # But in conjunction with the session_delete higher up in Uploads.upload_list_of_recordings
    # It does the job of deleting the failed session
    def __delete_upload(self, session_upload):
        upload_id = session_upload["ID"]
        session_upload["SessionId"] = upload_id

        while True:
            url = "https://{0}/Panopto/PublicAPI/REST/sessionUpload/{1}".format(
                self.server, upload_id
            )
            payload = copy.copy(session_upload)
            payload["State"] = 6  # Deleting Files
            headers = {"content-type": "application/json"}
            resp = self.requests_session.delete(url=url, json=payload, headers=headers)
            if not self.__check_retry_needed(resp):
                break
