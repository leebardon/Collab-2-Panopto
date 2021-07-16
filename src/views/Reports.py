from src.models import Utilities as Utils
from prettytable import PrettyTable
from src.views import Logger

LOGGER = Logger.init_logger(__name__)
REPORT = []
REPORT_403 = []

# TODO Make sure we have a list of lists : https://stackoverflow.com/a/56427043
# TODO Check our lists have the expected size at very least. Maybe also data types for expected values


def create_download_report(report: list[list], report_403):
    """Creates tabular output report detailing Collaborate downloads per session.
        Reports number of downloads in logs. 
    Args:
        report (list[list]): raw data from each downloaded recording 
    """
    LOGGER.info(f"Downloaded {len(report)} recordings from Collaborate.")
    LOGGER.info(f"Found {len(report_403)} private recordings that were not downloaded.")

    Utils.create_dir_if_not_exists("./reports")
    filename = "./reports/collab_download_report.txt"

    table = PrettyTable(
        [
            "Course UUID",
            "Collab Recording ID",
            "Recording Name",
            "Duration",
            "Storage Size (MB)",
            "Created Date",
        ]
    )
    for i in range(len(report)):
        entry = report[i]
        table.add_row(
            [
                entry[0],
                entry[1],
                entry[2],
                Utils.calculate_time(int(entry[3] / 1000)),
                str(round(float(entry[4]) / 1000000, 2)),
                Utils.convert_date(entry[5]),
            ]
        )
    try:
        with open(filename, "w") as f:
            f.write(table.get_string())
            LOGGER.info(f"Download report created.")
    except:
        LOGGER.info(f"Unable to create download report.")


def create_download_403_report(report: list[list]):
    """Creates download report for "403" private recordings
    Args:
        report (list[list]): raw data from each downloaded recording
    """
    filename = "./reports/private_recordings_403.txt"

    table = PrettyTable(["Course UUID", "Recording ID", "Recording Name", "Details",])
    for i in range(len(report)):
        entry = report[i]
        table.add_row(
            [entry[0], entry[1], entry[2], entry[3],]
        )
    try:
        with open(filename, "w") as f:
            f.write(table.get_string())
    except:
        assert TypeError


def append_report_entry(uuid, recording_data):
    REPORT.append(report_entry(uuid, recording_data))


def append_report_403_entry(uuid, recording_data):
    REPORT_403.append(report_403_entry(uuid, recording_data))


def report_entry(uuid, recording_data):
    """[summary] Creates entry for recording download report, for given course.
    Args:
        uuid (str): Course uuid
        recording_data (dict): Data for a given recording
    Returns:
        [array]: A entry for the recording download report, with details for a particular uuid.
    """
    return [
        uuid,
        recording_data["recording_id"],
        recording_data["recording_name"],
        recording_data["duration"],
        recording_data["storage_size"],
        recording_data["created"],
    ]


def report_403_entry(uuid, recording_data):
    return [
        uuid,
        recording_data["recording_id"],
        recording_data["recording_name"],
        "403 - private recording",
    ]


def generate_download_reports():
    create_download_report(REPORT, REPORT_403) if len(REPORT) > 0 else LOGGER.info(
        "No new public recordings found."
    )
    create_download_403_report(REPORT_403) if len(REPORT_403) > 0 else LOGGER.info(
        "No new private recordings found."
    )
