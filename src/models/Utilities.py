import datetime
import requests
import json
import re
import os
import csv
from src.models.Uploads import Uploads
from src.models import Emails as Email
from src.views import Logger

BASE = os.getcwd()
LOGGER = Logger.init_logger(__name__)


def clean_filename(course_id: str, fname: str):
    """Cleans up given filename, removing undesired punctuation
    Args:
        course_id (str): course id
        fname (str): file name to clean up
    Returns:
        str: either cleaned filename or course_id if filename is over 160 chars long
    """
    LOGGER.debug(f"{course_id}, {fname}")
    handle_types(*[(course_id, ""), (fname, "")])

    file = re.sub(r"[^\w\s]", "", fname)
    filename = file.replace("recording", "").rstrip().replace(" ", "-")
    return course_id if len(filename) > 160 else filename


def create_dir_if_not_exists(path: str):
    """Creates directory if it doesn't exist already
    Args:
        path (str): path to directory
    Returns:
        str: path to directory
    """
    LOGGER.debug(f"{path}")
    handle_types(*[(path, "")])
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        msg = str(e)
        LOGGER.error(msg)
        raise e

    return path


def calculate_time(secs: int):
    """Converts given number of seconds into "%H:%M:%S" format
    Args:
        secs (int): number of seconds
    Returns:
        str: "%H:%M:%S" time format
    """
    LOGGER.debug(f"{secs}")
    handle_types(*[(secs, 0)])
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    time_in_session = datetime.time(hours, mins, secs)
    return time_in_session.strftime("%H:%M:%S")


def convert_date(date: str):
    """Converts given date to "%b %d,%Y" format. Example : Sep 03,2021
    Args:
        date (str): date
    Returns:
        str: date in "%b %d,%Y" format
    """
    LOGGER.debug(f"{date}")
    handle_types(*[(date, "")])
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        msg = "Incorrect data format, should be %Y-%m-%dT%H:%M:%S.%fZ"
        LOGGER.error(msg)
        raise ValueError(msg)
    return date_obj.strftime("%b %d,%Y")


def set_search_start_date(weeks: int):
    """Returns date {weeks} from now
    Args:
        weeks (int): number of weeks to go back
    Returns:
        str: date in "%Y-%m-%d" format
    """
    LOGGER.debug(f"Setting search from {weeks} weeks ago")
    handle_types(*[(weeks, 0)])

    start_date = datetime.datetime.now() - datetime.timedelta(weeks=int(weeks))
    return start_date.strftime("%Y-%m-%d")


def get_headers(auth_or_bearer):
    """Helper function - template for returning headers to make API calls depending on auth or bearer being required
    Args:
        auth_or_bearer (str): String variable for header
    Returns:
        [dict]: Header for making requests
    """
    LOGGER.debug(f"{auth_or_bearer}")
    handle_types(*[(auth_or_bearer, "")])

    return {
        "Authorization": auth_or_bearer,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def clean_chat_message(message):
    """Removes unwanted whitespace and characters from Collab chat entries prior to saving
    Args:
        message (str): Chat message on given recording
    Returns:
        [str]: Cleaned message
    """
    LOGGER.debug(f"{message}")
    handle_types(*[(message, "")])
    clean = re.compile("<.*?>")
    return re.sub(clean, "", message)


def save_chatfile_as_csv(fname, json_info, header):
    file = open(fname, "w", encoding="utf-8")
    writer = csv.writer(file)
    writer.writerow(header)
    for json_row in json_info:
        writer.writerow(
            [
                json_row["userName"],
                clean_chat_message(json_row["body"]),
                json_row["relativeEventTime"],
                json_row["id"],
            ]
        )
    file.close()


def list_entry(results, size=None, recording_type=0):
    """Generates download report entry data depending on recording found or not found
    Returns:
        [dict]: Dict of data for entry to Collab download report
    """
    LOGGER.debug(f"{results}, {size}, {recording_type}")
    handle_types(*[(results, {}), (recording_type, 0)])

    if not type(size) is int and size != None:
        msg = f"Recording size should be type(int) and not None"
        LOGGER.error(msg)
        raise TypeError(msg)

    try:
        if recording_type == 1:
            list_data = {
                "recording_id": results["id"],
                "recording_name": results["name"],
                "duration": results["duration"],
                "storage_size": size,
                "created": results["created"],
            }
        else:
            list_data = {
                "recording_id": results["id"],
                "recording_name": results["name"],
                "msg": 403,
            }
    except KeyError as ke:
        raise KeyError(f"Expected key in dict: {ke}")

    return list_data


def recording_storage_size(url: str):
    """returns content length for given recording url
    Args:
        url (str): recording url
    Returns:
        int: size of content length
    """
    LOGGER.debug(f"{url}")
    handle_types(*[(url, "")])

    try:
        r = requests.get(url, stream=True, headers={"Accept-Encoding": None})
    except requests.exceptions.MissingSchema as e:
        LOGGER.error(str(e))
        raise requests.exceptions.MissingSchema(str(e))

    return int(r.headers.get("content-length", 0))


def return_filename(course_id, rec, filetype, chat=""):
    LOGGER.debug(f"{course_id}, {rec}, {filetype}, {chat}")
    handle_types(*[(course_id, ""), (rec, {}), (filetype, ""), (chat, "")])

    try:
        return (
            f"Collab-2-Panopto-",
            f"{chat}"
            f"{course_id}-{rec['recording_id']}_"
            f"{clean_filename(course_id, rec['recording_name'])}"
            f"{filetype}"
        )

    except KeyError as ke:
        raise KeyError(f"Expected key in dict: {ke}")


def get_courseId_folderId_pairs(uuid_id_pairs):
    """Takes dict of uuid:course_id mappings from Collab data, uses course_id to search
        for corresponding Panopto folder_id
    Args:
        uuid_id_pairs ([dict]): uuid to course_id mappings
    Returns:
        [dict]: Course_id to Panopto folder_id mappings 
    """
    LOGGER.debug(f"{uuid_id_pairs}")
    handle_types(*[(uuid_id_pairs, {})])

    uploader = Uploads()
    courseId_folderId_pairs = check_json_exists()

    missing_folders_list = []
    for courseId in uuid_id_pairs.values():
        if courseId in courseId_folderId_pairs.keys():
            continue
        else:
            folderId = uploader.get_folder_id_from_course_id(courseId)
            if folderId is not None:
                courseId_folderId_pairs[courseId] = folderId
            else:
                missing_folders_list.append(courseId)

    save_as_json(courseId_folderId_pairs, f"{BASE}/data")

    # message = Email.create_email()
    # email = Email.attach_missing_folders_csv(message, missing_folders_list)
    # Email.send_info_email(email)

    return courseId_folderId_pairs, missing_folders_list


def save_as_json(courseId_folderId_pairs, json_dir_path):
    """Saves or updates courseId_folderId_pairs as json to /data folder
    Args:
        courseId_folderId_pairs (dict): Dict of course_id to Panopto folder_id mappings
        json_dir_path (path): Path to /data folder
    """
    LOGGER.debug(f"{courseId_folderId_pairs}, {json_dir_path}")
    handle_types(*[(courseId_folderId_pairs, {}), (json_dir_path, "")])
    dir = create_dir_if_not_exists(json_dir_path)
    with open(f"{dir}/courseId_folderId_pairs.json", "w") as fp:
        json.dump(courseId_folderId_pairs, fp, indent=4)

    return courseId_folderId_pairs


def get_downloads_list(downloads_path):
    """Gets list of mp4 files in Collab /downloads folder 
    Args:
        downloads_path (path): Path to Collab downloads folder
    Returns:
        [list]: List of paths to each mp4 download file
    """
    LOGGER.debug(f"{downloads_path}")
    handle_types(*[(downloads_path, "")])

    downloads_list = []
    for file in os.scandir(downloads_path):
        if file.path.endswith(".mp4"):
            downloads_list.append(file.path)

    return downloads_list


def get_folder_download_matches(courseIds_folderIds, downloads_list):
    """ Matches course_id strings from mp4 files in Collab /downloads to Panopto folder_id
        Adds {folder_id: [download]} to matches dict if not exists, else appends download
    Args:
        courseIds_folderIds (dict): Dict of course_id:folder_id mappings
        downloads_list (list(mp4)): List of mp4 recordings in Collab /downloads
    Returns:
        [dict]: Mapping of course downloads to corresponding Panopto folder_ids
    """
    LOGGER.debug(f"{courseIds_folderIds}, {downloads_list}")
    handle_types(*[(courseIds_folderIds, {}), (downloads_list, [])])

    matches = {}
    for download in downloads_list:
        for course_id, folder_id in courseIds_folderIds.items():
            if course_id in download:
                if folder_id in matches:
                    matches[folder_id].append(download)
                else:
                    matches[folder_id] = [download]
    return matches


def logger_msg(*vars):
    return [str(type(var)) for var in vars]


def handle_response(r):
    """Generic function for API response handling and error logging.
    Args:
        r (res): Response from API call
    Returns: 
        Parsed json or None, depending on status_code
    """
    if r.status_code == 200:
        res = json.loads(r.text)
        return res
    elif r.status_code == 403:
        LOGGER.warning(f"Status code 403: (might be private recording!) - {r}")
        return None
    elif r.status_code == 404:
        LOGGER.warning(f"Status code 404: Not Found - {str(r)}")
        return None
    else:
        LOGGER.warning(f"Unknown response for: {str(r)}")
        return None


def handle_types(*received_expected):
    """Generic helper function for handling TypeErrors
    Args:
        rec_exp (list(tuples)): Unpackable list of (rec, exp) tuples of arbitrary length
    Raises:
        TypeError: if type(rec) != type(exp)
    """
    for pair in received_expected:
        if not type(pair[0]) is type(pair[1]):
            msg = f"Type {type(pair[1])} expected, received: {type(pair[0])}"
            LOGGER.error(msg)
            raise TypeError(msg)


def handle_res_content(key, json):
    if not key in json:
        raise KeyError(f"Expected key {key} in response json")


def check_json_exists():
    """Loads courseId_folderId_pairs.json as dict if exists, returns empty dict if not
    Returns:
        [dict]: dict(courseId_folderId_pairs)
    """
    try:
        with open(f"{BASE}/data/courseId_folderId_pairs.json") as f:
            courseId_folderId_pairs = json.load(f)
    except:
        courseId_folderId_pairs = {}

    return courseId_folderId_pairs


def return_absent_present(present_on_ppto, list_of_recordings):
    absent, present = [], []

    # Turn list of dicts into a single dict
    dict_present_recordings = {}
    for item in present_on_ppto:
        dict_present_recordings[list(item.keys())[0]] = list(item.values())[0]

    # Check if recording is already present on panopto
    for rec in list_of_recordings:
        rec_short_name = get_new_name(os.path.basename(rec))

        # Check for both the short name and the full name.
        # Full name can be on panopto when we are checking before the recording has been renamed
        if not rec_short_name in list(
            dict_present_recordings.keys()
        ) and not os.path.basename(rec) in list(dict_present_recordings.keys()):
            # Neither were found, the recording is absent on panopto
            absent.append(rec)
        else:
            # Present with short name
            if rec_short_name in dict_present_recordings:
                present.append(
                    {rec_short_name: dict_present_recordings[rec_short_name]}
                )
            # Present with full name
            else:
                present.append(
                    {
                        os.path.basename(rec): dict_present_recordings[
                            os.path.basename(rec)
                        ]
                    }
                )

    return absent, present


def check_upload_results(failed_uploads, recordings_not_uploaded):
    if len(recordings_not_uploaded) > 0:
        LOGGER.warning(
            f"Some recordings weren't uploaded properly : {recordings_not_uploaded }"
        )
    if failed_uploads != recordings_not_uploaded:
        LOGGER.warning(
            f"failed_uploads and recordings_not_uploaded should be identical - they aren't!!!"
        )


def get_date_created(path, rec_ids_date_created):
    for ele in rec_ids_date_created:
        for id, date in ele.items():
            if id in path:
                return date.rsplit("T", 1)


def get_new_name(old_name):
    return old_name.rsplit("_", 1)[1]
