import os
from src.models import Utilities as Utils
from src.views import Logger


BASE = os.getcwd()
LOGGER = Logger.init_logger(__name__)


def get_blacklisted_courses():
    LOGGER.debug("")
    blacklisted_courses = []
    with open(f"{BASE}/data/course_blacklist.txt", "r") as f:
        blacklisted_courses = f.read().splitlines()
    LOGGER.debug(f"Blacklist: {blacklisted_courses}")
    return blacklisted_courses


def clean_downloads():
    LOGGER.debug("")
    blacklisted_courses = get_blacklisted_courses()
    downloads_list = Utils.get_downloads_list(f"{BASE}/downloads")

    to_delete = []
    for download in downloads_list:
        for course in blacklisted_courses:
            if course in download:
                to_delete.append(download)

    for blacklisted in to_delete:
        LOGGER.debug(f"Deleting {os.path.basename(blacklisted)}")
        os.unlink(blacklisted)


# TODO
def update_blacklist():
    # Input : new blacklist list
    # Write this to file
    pass


# TODO
def read_all_blacklist_emails():
    # Read emails received with "Collaborate-2-Panopto blacklist" subject
    # Body can contain "ADD <course_id>" or "REMOVE <course_id"
    # Create a new blacklist list
    # This should allow to update the blacklist
    pass
