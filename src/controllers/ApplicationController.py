import os
from time import sleep
from src.views import Logger
from src.models import CollabWebService as Ws
from src.models import Courses, Downloads, Utilities
from src.models.Uploads import Uploads
from src.views import Reports
from src.models import Emails
from src.models import Blacklist
import time
import traceback

BASE = os.getcwd()
LOGS = Utilities.create_dir_if_not_exists(f"{BASE}/.logs")
LOGGER = Logger.init_logger(__name__)
WEBSERVICE = Ws.WebService()

THIS_YEAR = "20-21"
FAILED_UPLOADS_THIS_TIME = []


def run_application(start_time):
    try:
        # Get all "uuid: course_id" pairs
        uuid_id_pairs = get_collab_recordings(start_time)

        # Go through each course, download recordings from Collab, upload to Panopto and clean up
        missing_folders_list, failed_uploads_list = [], []
        for uuid, course_id in uuid_id_pairs.items():
            rec_ids_date_created = search_for_recordings({uuid: course_id}, start_time)
            missing_folders, failed_uploads = upload_to_panopto(
                {uuid: course_id}, rec_ids_date_created
            )
            for folder in missing_folders:
                missing_folders_list.append(folder)
            for failed in failed_uploads:
                failed_uploads_list.append(failed)

        # Send email about missing folders
        message = Emails.create_email()
        email = Emails.attach_missing_and_failed_csv(
            message, missing_folders_list, failed_uploads_list
        )
        Emails.send_info_email(email)

        LOGGER.info("Transfer complete")
        print("\n -- Completed: exiting program -- \n")

        done = True

        if done:
            sleep(1)
            os._exit(1)

    except Exception as e:
        trace_back = traceback.format_exc()
        message = Emails.create_alert_message(trace_back)
        Emails.send_alert_email(message)
        raise e


def get_collab_recordings(start_time):
    """ Obtains all courseId's from Collab
        Obtains dict of courseId: uuid pairs
        Obtains dict of courseId: uuid pairs in current academic year
        Initiates search for recordings from start_time
    Args:
        start_time (str): date in "%Y-%m-%dT%H:%M:%SZ" format 
    """
    LOGGER.debug(f"{start_time}")
    LOGGER.info(f"Searching course's for recordings from date: {start_time}")

    # NOTE the below are needed for full version, commented out for testing
    all_courses = WEBSERVICE.courses_data_from_collab()
    all_id_uuid_pairs, no_courseIds = Courses.get_id_uuid_pairs(all_courses)
    id_uuids_pairs = Courses.get_id_uuid_pairs_this_year(all_courses, THIS_YEAR)

    test_pairs = {
        "5424a081dd96497bbda1ddacd40f5312": "MATH6095-14656-20-21",
        "d70bdbdb79a448bc8af0566675a2510c": "SESM6034-39841-20-21",
        "1314a94f48d6416f931adaef6bde1da5": "COMP6215-32970-20-21",
    }

    # TODO Change this to the pair that is going to be used (prod or test)
    used_pairs = test_pairs

    # Filter out the course_ids that are blacklisted
    blacklisted_courses = Blacklist.get_blacklisted_courses()
    filtered_pairs = {}
    for uuid, course_id in used_pairs.items():
        if not course_id in blacklisted_courses:
            filtered_pairs[uuid] = course_id

    # This used to download all courses before starting to upload
    # collab_rec_ids = search_for_recordings(filtered_pairs, start_time)

    return filtered_pairs  # , collab_rec_ids


def search_for_recordings(all_courses, start_time):
    """Calls function to download recordings from Collaborate
    Args:
        course_details (list): list of course_id and uuid's 
        start_time (datetime): searches between start_time and present
    Return:
        Calls function to generate download reports
    """
    rec_ids_date_created = []
    for uuid, course_id in all_courses.items():
        LOGGER.debug(f"searching {course_id}")
        recordings_found = Downloads.search_by_uuid(uuid, start_time)

        if recordings_found is None:
            LOGGER.info(f"No recordings found for: {course_id}")
        else:
            LOGGER.info(f"Recordings found for {course_id}")
            [
                rec_ids_date_created.append(
                    {r["recording_id"]: r.get("created", "403-private")}
                )
                for r in recordings_found
            ]
            Downloads.get_recordings_for_course(recordings_found, uuid, course_id)

    Reports.generate_download_reports()

    return rec_ids_date_created


def upload_to_panopto(uuid_id_pairs, rec_ids_date_created):
    global FAILED_UPLOADS_THIS_TIME
    LOGGER.debug("")
    print("Getting folder IDs")
    uploader = Uploads()
    courseIds_folderIds, missing_folders_list = Utilities.get_courseId_folderId_pairs(
        uuid_id_pairs
    )

    Blacklist.clean_downloads()

    downloads_list = Utilities.get_downloads_list(f"{BASE}/downloads")
    folderId_downloads = Utilities.get_folder_download_matches(
        courseIds_folderIds, downloads_list
    )

    successful_uploads, not_on_ppto = [], []

    for folder_id, downloads in folderId_downloads.items():
        LOGGER.debug("Check if any recordings are already on Panopto")
        recs_to_upload, already_on_ppto = uploader.check_recordings_on_panopto(
            downloads, folder_id
        )

        # Do not upload those that have already failed this time
        indices = [
            recs_to_upload.index(x) if x in recs_to_upload else None
            for x in FAILED_UPLOADS_THIS_TIME
        ]
        [recs_to_upload.pop(index) if index != None else None for index in indices]

        LOGGER.debug("Uploading course recordings to Panopto folder")
        failed_uploads = uploader.upload_list_of_recordings(
            recs_to_upload, rec_ids_date_created, folder_id
        )

        # I wish we had a better solution.
        # Unfortunately it takes a little while for the session to be fully uploaded and present on ppto once recording is uploaded
        # If we check too quickly we won't see the session because it is still processing
        time.sleep(5)

        LOGGER.debug("Double checking uploaded files are discoverable on Panopto")
        (
            not_on_ppto,
            successful_uploads_sessionIds,
        ) = uploader.check_recordings_on_panopto(recs_to_upload, folder_id)
        successful_uploads.append(successful_uploads_sessionIds)

        # Just in case, remove erroneous successes
        indeces = [
            successful_uploads.index(x) if x in successful_uploads else None
            for x in failed_uploads
        ]
        for index in indeces:
            if index != None:
                successful_uploads.pop(index)

        Utilities.check_upload_results(failed_uploads, not_on_ppto)
        Downloads.delete_successful_uploads_from_collab(
            successful_uploads_sessionIds, rec_ids_date_created
        )

        [FAILED_UPLOADS_THIS_TIME.append(failed) for failed in failed_uploads]

        Downloads.delete_local_downloads(downloads, FAILED_UPLOADS_THIS_TIME)

    for ele in successful_uploads:
        print(ele)

    if len(successful_uploads) > 0:
        if len(successful_uploads[0]) > 0:
            uploader.sessions.rename_successful_uploads(successful_uploads[0])

    return missing_folders_list, not_on_ppto


def run_preview(start_date: int):
    LOGGER.info(f"Starting preview from {start_date}")

    Blacklist.clean_downloads()

    collab_uuid_courseid_pairs = get_collab_recordings(start_date)

    print("#########################")
    print("### COURSES ON COLLAB ###")
    print("#########################")
    print("┌────────────────────────────────┬──────────┐")
    print("│UUID                            │ COURSE ID│")
    print("└────────────────────────────────┴──────────┘")
    for uuid, course_id in collab_uuid_courseid_pairs.items():
        print(f"{uuid} │ {course_id}")

    print("\n")

    print("#############################")
    print("### RECORDINGS PER COURSE ###")
    print("#############################")

    for uuid, course_id in collab_uuid_courseid_pairs.items():
        recordings_found = Downloads.search_by_uuid(uuid, start_date)

        if recordings_found is None:
            print(f"\n## Recordings found for: {course_id}:\n  + <None>")
        else:
            print(f"\n## Recordings found for: {course_id}: ")
            for rec in recordings_found:
                if "msg" not in rec:
                    rec_data = WEBSERVICE.get_recording_data(rec["recording_id"])
                    if rec_data != None:
                        filename = Utilities.return_filename(course_id, rec, ".mp4")
                        print(f"  + {filename}")
                else:
                    print("  + <private recording>")

    print("\n")

    print("########################################")
    print("### CORRESPONDING FOLDERS ON PANOPTO ###")
    print("########################################")

    courseIds_folderIds, missing_folders_list = Utilities.get_courseId_folderId_pairs(
        collab_uuid_courseid_pairs
    )

    print("\n## Course IDs and their corresponding folder in Panopto:")
    for course_id, folder_id in courseIds_folderIds.items():
        print(f"  + {course_id} \t> {folder_id}")

    print("\n## Missing folders in Panopto:")
    for missing_folder_id in missing_folders_list:
        print(f"  + {missing_folder_id}")

    print("\n")

    print("#######################")
    print("### PLANNED UPLOADS ###")
    print("#######################")
    print("")

    downloads_list = Utilities.get_downloads_list(f"{BASE}/downloads")
    folderId_downloads = Utilities.get_folder_download_matches(
        courseIds_folderIds, downloads_list
    )

    if len(folderId_downloads) > 0:
        print("┌────────────────────────────┬─────────────────────────────┬─────────┐")
        print("│FILE NAME                   │COURSE ID                    │FOLDER ID│")
        print("└────────────────────────────┴─────────────────────────────┴─────────┘")

        for folder_id, downloads in folderId_downloads.items():
            # Find course_id corresponding to this folder_id
            course_id = list(courseIds_folderIds.keys())[
                list(courseIds_folderIds.values()).index(folder_id)
            ]
            for download in downloads:
                print(f"{os.path.basename(download)} > {course_id} ({folder_id})")
    else:
        print("  + <None>")
