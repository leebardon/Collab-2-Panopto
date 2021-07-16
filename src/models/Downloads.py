import requests
from tqdm import tqdm
import json
import os
import ntpath
from src.models import CollabWebService as Ws
from src.models import Utilities as Utils
from src.views import Reports
from src.views import Logger

WEBSERVICE = Ws.WebService()
LOGGER = Logger.init_logger(__name__)
PATH = "./downloads/"


def search_by_uuid(uuid: str, start_time: str):
    """Obtains json of data associated with each recording.
    Args:
        uuid (str): Course UUID
        start_time (str): date in "%Y-%m-%dT%H:%M:%SZ" format 
    Returns:
        list[dict]: None, or list of dicts containing recording info 
    """
    LOGGER.debug(f"{uuid}, {start_time}")
    Utils.handle_types([(uuid, ""), (start_time, "")])
    recs_json = WEBSERVICE.search_for_recordings_by_uuid(uuid, start_time)
    if len(recs_json["results"]) != 0:
        return list_of_recordings(recs_json)
    return None


def list_of_recordings(recs_json: dict):
    """Goes through given recordings, parses json and returns full list of details for each recording
    Args:
        recs_json (dict): dict of all recordings for a specific course
    Returns:
        list[dict]: list of dicts containing recording info
    """
    LOGGER.debug(f"{recs_json}")
    Utils.handle_types([recs_json, {}])
    Utils.handle_res_content("results", recs_json)

    recordings_list = []
    results = recs_json["results"]
    for i in range(len(results)):
        rec_data = WEBSERVICE.get_recording_data(results[i]["id"])
        if rec_data != None:
            size = get_recording_size(rec_data, results, i)
            recordings_list.append(Utils.list_entry(results[i], size, recording_type=1))
        else:
            recordings_list.append(Utils.list_entry(results[i]))

    return recordings_list


def get_recording_size(data, results, i):
    if "mediaDownloadUrl" in data:
        return Utils.recording_storage_size(data["mediaDownloadUrl"])
    elif "storageSize" in results[i]:
        return results[i]["storageSize"]

    return Utils.recording_storage_size(data["eitStreams"][0]["streamUrl"])


def get_recordings_for_course(recs_data: list, uuid: str, course_id: str):
    """Calls methods to download recent public recordings per course, adds entry to download report.
            If private recordings exist, calls method to generate report_403.
    Args:
        recordings (list): List of recent recordings
        uuid (str): course's uuid
        course_id: course's id
    Result:
        Newly created file containing recording and chat data (if any)
        Lines in report containing information on what was downloaded
    """
    LOGGER.debug(f"Getting recordings for: {recs_data}, UUID: {uuid}, ID: {course_id}")
    Utils.handle_types([(recs_data, []), (uuid, ""), (course_id, "")])

    for rec in recs_data:
        if "msg" not in rec:
            download_recording_from_collab(rec, course_id)
            Reports.append_report_entry(uuid, rec)
        else:
            Reports.append_report_403_entry(uuid, rec)


def download_recording_from_collab(recording: dict, course_id: str):
    """Downloads recording and chat for given course ID, writes them to files
    Args:
        recording (dict): dict from parsed recording json
        course_id (str): course ID
    Result:
        Newly created files containing recording (.mp4) and chat (.csv) data (if any)
    """
    LOGGER.debug(f"Downloading from collab: {recording}, ID: {course_id}")
    Utils.handle_types([(recording, {}), (course_id, "")])
    Utils.handle_res_content("recording_id", recording)

    rec_data = WEBSERVICE.get_recording_data(recording["recording_id"])
    if rec_data != None:
        filename = Utils.return_filename(course_id, recording, ".mp4")
        chat_filename = Utils.return_filename(course_id, recording, ".csv", "Chat-")
        print(f"{filename}")
        download_stream(rec_data["extStreams"][0]["streamUrl"], f"{PATH}{filename}")
        if len(rec_data["chats"]) != 0:
            download_chat(rec_data["chats"][0]["url"], f"{PATH}{chat_filename}")


def download_stream(url: str, fname: str):
    """Download recording stream from url and write to file
    Args:
        url (str): recording url
        fname (str): file path to write recording to
    Result:
        Newly created file containing recording data (usually .mp4)
    """
    LOGGER.debug(f"Download from => {url}, Save to => {fname}")
    Utils.handle_types([(url, ""), (fname, "")])

    try:
        resp = requests_get_stream(url, True)
    except requests.exceptions.MissingSchema as e:
        LOGGER.error(str(e))
        raise requests.exceptions.MissingSchema(str(e))

    total = int(resp.headers.get("content-length", 0))
    progress_bar = tqdm(total=total, unit="iB", unit_scale=True, unit_divisor=1024)
    with open(fname, "wb") as file:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)
    progress_bar.close()


def download_chat(url: str, fname: str):
    """Creates chat file and writes recording's chat history to it
    Args:
        url (str): recording url
        fname (str): file path to write chat to
    Result:
        Newly created file containing chat data in CSV format
        Headers are : "Participant", "Message", "Time", "Message id"
    """
    LOGGER.debug(f"Download chat from => {url}, Save to => {fname}")
    Utils.handle_types([(url, ""), (fname, "")])

    try:
        chat_file = requests_get_chat(url, stream=True)
    except requests.exceptions.MissingSchema as e:
        LOGGER.error(str(e))
        raise requests.exceptions.MissingSchema(str(e))

    if chat_file.status_code == 200:
        try:
            json_info = json.loads(chat_file.text)
            header = ["Participant", "Message", "Time", "Message id"]
            try:
                Utils.save_chatfile_as_csv(fname, json_info, header)
            except OSError as oserror:
                if oserror.errno == 36:
                    LOGGER.error("Long file name")
                    raise OSError(oserror)
        except json.decoder.JSONDecodeError as e:
            LOGGER.error("Chat file is empty")
            raise ValueError("Chat file is empty")


def delete_local_downloads(downloads, unsuccessful_uploads_paths):
    for rec in downloads:
        if not rec in unsuccessful_uploads_paths:
            # print(f"FAKE -- removed locally {rec}")
            # head, tail = ntpath.split(rec)
            # os.rename(rec, head + "/_DONE_" + tail.rsplit("_", 1)[1])
            os.unlink(rec)


def delete_successful_uploads_from_collab(
    successful_uploads_sessionIds: dict, recordingIds_date_created: dict
):
    for ele in successful_uploads_sessionIds:
        for path, session_ids in ele.items():
            if len(recordingIds_date_created) > 0:
                remove_from_collab(path, recordingIds_date_created)


def remove_from_collab(path, recordingIds_date_created):
    for pair in recordingIds_date_created:
        for rec_id, date in pair.items():
            if rec_id in path:
                print(f"FAKE -- removed from Collab {rec_id}")
                LOGGER.info(f"FAKE -- removed from Collab {path}")
                # WEBSERVICE.delete_recording_from_collab(rec_id)


def requests_get_stream(url, stream=True):
    return requests.get(url, stream=stream)


def requests_get_chat(url, stream=True):
    return requests.get(url, stream=stream)
