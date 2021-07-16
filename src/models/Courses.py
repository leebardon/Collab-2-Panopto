from src.models import CollabWebService as Ws
from src.views import Logger
from re import search

WEBSERVICE = Ws.WebService()
LOGGER = Logger.init_logger(__name__)


def get_id_uuid_pairs(courses: list):
    """Takes list of courses returned from Collab API
        extracts uuid and courseId as key:value pair
    Args:
        courses(list): Returned from Collab JWT contexts
    Returns:
        pairs(dict): All uuid:courseId pairs on Collab, as dictionary
        no_course_ids(list): uuid's with no corresponding courseId
    """
    LOGGER.info("Combining uuid & courseId as key:value pairs")
    pairs = {}
    no_course_ids = []
    for x in range(len(courses)):
        for i in range(len(courses[x]["results"])):
            try:
                pairs[courses[x]["results"][i]["id"]] = courses[x]["results"][i][
                    "label"
                ]
            except:
                no_course_ids.append(courses[x]["results"][i]["id"])
    return pairs, no_course_ids


def get_id_uuid_pairs_this_year(courses: list, this_year: str):
    """Takes list of courses returned from Collab API
        extracts uuid:courseId for currenct academic year
    Args:
        courses(list): Returned from Collab JWT contexts
        this_year(str): e.g. "21-21"
    Returns:
        pairs(dict): uuid:courseId pairs as dictionary
    """
    LOGGER.info(f"Combining uuid:courseId pairs for {this_year}")
    pairs = {}
    for x in range(len(courses)):
        for i in range(len(courses[x]["results"])):
            try:
                course_id = courses[x]["results"][i]["label"]
                if search(f"-{this_year}", course_id):
                    pairs[courses[x]["results"][i]["id"]] = courses[x]["results"][i][
                        "label"
                    ]
            except:
                continue
    return pairs
