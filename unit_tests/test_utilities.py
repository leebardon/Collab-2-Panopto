import json
from src.models.Uploads import Uploads
from typing import Type
import pytest
import unittest
import sys, re, getopt, os
import datetime as dt
from shutil import rmtree
from unittest.mock import Mock
from requests import Response
import requests

from src.models import Utilities as Utils


######################
### POSITIVE TESTS ###
######################


# === clean_long_filename ===
@pytest.mark.parametrize(
    "course_id, filename, expected",
    [
        ("course_id_1", "file_1", "file_1"),
        ("course_id_2", "file_^\\}'2", "file_2"),
        (
            "course_id_long",
            "VtfSONWwyF65bFkGe4iYtO9zIE4Q6edUkJiQS5p675IsKDjvJjJMdllSh9GrDbHjGmtRvEm5auRLHvundzlF0agvK3eH7sGtw7eHUVBn81fmovacb8IEbzF2LRkeh7MyCubGv2u4pYh40XlJmKfEpVL1CR3M1GQ1T",
            "course_id_long",
        ),
    ],
)
def test_positive_clean_long_filename(course_id, filename, expected):
    assert Utils.clean_long_filename(course_id, filename) == expected


# === create_dir_if_not_exists ===
@pytest.mark.parametrize(
    "path",
    ["./test_dir", "./test_dir/test_dir_22", "./test_dir/test_dir_33/test_dir_333",],
)
def test_positive_create_dir_if_not_exists(path):
    Utils.create_dir_if_not_exists(path)
    assert os.path.exists(path)
    rmtree("./test_dir")
    assert not os.path.exists("./test_dir")


# === calculate_time ===
@pytest.mark.parametrize(
    "secs_int, expected",
    [(1440, "00:24:00"), (9600, "02:40:00"), (24 * 60 * 60 - 1, "23:59:59")],
)
def test_positive_calculate_time(secs_int, expected):
    assert Utils.calculate_time(secs_int) == expected


# === converte_date ===
@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("1996-05-01T01:02:03.04Z", "May 01,1996"),
        ("1436-01-02T01:02:03.04Z", "Jan 02,1436"),
        ("1712-03-04T05:06:07.08Z", "Mar 04,1712"),
    ],
)
def test_positive_convert_date(date_str, expected):
    assert Utils.convert_date(date_str) == expected


# === set_search_start_date ===
@pytest.mark.parametrize("nb_weeks", [1, 10, 12])
def test_positive_set_search_start_date(nb_weeks):
    now = dt.datetime.now()
    expected_date = now - dt.timedelta(weeks=nb_weeks)
    expected_date = expected_date.strftime("%Y-%m-%d")
    assert Utils.set_search_start_date(nb_weeks) == expected_date


# === handle_response ===
def test_positive_handle_response():
    r = Mock()
    r.text = '{"text": "test_text"}'
    r.status_code = 200

    assert Utils.handle_response(r) == {"text": "test_text"}


# === get_headers ===
def test_positive_get_headers():
    assert Utils.get_headers("test_bearer") == {
        "Authorization": "test_bearer",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# === clean_message ===
@pytest.mark.parametrize(
    "message", ["test_message", "test_message<.*?>"],
)
def test_positive_clean_message(message):
    assert Utils.clean_message(message) == "test_message"


# === list_entry ===
def test_positive_list_entry():
    results = {
        "id": "test_id",
        "name": "test_name",
        "duration": "test_duration",
        "created": "test_created",
    }
    size = 123

    assert Utils.list_entry(results, size, 1) == {
        "recording_id": "test_id",
        "recording_name": "test_name",
        "duration": "test_duration",
        "storage_size": 123,
        "created": "test_created",
    }

    assert Utils.list_entry(results, size) == {
        "recording_id": "test_id",
        "recording_name": "test_name",
        "msg": 403,
    }


# === recording_storage_size ===
def test_positive_recording_storage_size(monkeypatch):
    monkeypatch.setattr(requests, "get", mock_requests_get_content_length)
    assert Utils.recording_storage_size("test_url") == 123


# === return_filename ===
def test_positive_return_filename():
    assert (
        Utils.return_filename(
            "c_id",
            {"recording_id": "123", "recording_name": "name"},
            "filetype",
            "prefix",
        )
        == "prefixc_id-123-namefiletype"
    )


# === get_courseId_folderId_pairs ===
def test_positive_get_courseId_folderId_pairs(monkeypatch):
    pairs = {"1": "TEST-LEE", "2": "TESTCOURSE-LRB1C20"}

    # Create a fake function for our fake uploader
    # uploader = Mock()
    # monkeypatch.setattr(
    #     uploader, "get_folder_id_from_course_id", mock_get_folder_id_from_course_id
    # )

    # Monkeypatch Uploads init and get_folder function
    monkeypatch.setattr(Uploads, "__init__", lambda x: None)
    monkeypatch.setattr(
        Uploads, "get_folder_id_from_course_id", mock_get_folder_id_from_course_id
    )

    # Replaces save_as_json by a function that does nothing
    monkeypatch.setattr(Utils, "save_as_json", lambda x, y: None)

    assert Utils.get_courseId_folderId_pairs(pairs) == {
        "TEST-LEE": "972fc0a7-6861-44b3-b64e-ac5300a10d9a",
        "TESTCOURSE-LRB1C20": "3e79f7c5-e9f6-4e18-9481-ad5500d6b104",
    }


# === save_as_json ===
def test_positive_save_as_json(capsys):
    pairs = {
        "TEST-LEE": "972fc0a7-6861-44b3-b64e-ac5300a10d9a",
        "TESTCOURSE-LRB1C20": "3e79f7c5-e9f6-4e18-9481-ad5500d6b104",
    }
    json_dir_path = "unit_tests/unit_test_data"
    Utils.save_as_json(pairs, json_dir_path)

    with open(f"{json_dir_path}/courseId_folderId_pairs.json") as f:
        assert json.load(f) == {
            "TEST-LEE": "972fc0a7-6861-44b3-b64e-ac5300a10d9a",
            "TESTCOURSE-LRB1C20": "3e79f7c5-e9f6-4e18-9481-ad5500d6b104",
        }

    os.unlink(f"{json_dir_path}/courseId_folderId_pairs.json")


# === get_downloads_list ===
def test_positive_get_downloads_list():
    assert Utils.get_downloads_list(
        "unit_tests/unit_test_data/unit_test_downloads"
    ) == [
        "unit_tests/unit_test_data/unit_test_downloads/COMP6215-32970-20-21-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1 - recording.mp4"
    ]


# === get_folder_download_matches ===
def test_positive_get_folder_download_matches():
    courseIds_folderIds = {
        "TESTCOURSE-LRB1C20": "3e79f7c5-e9f6-4e18-9481-ad5500d6b104",
        "TEST-LEE": "972fc0a7-6861-44b3-b64e-ac5300a10d9a",
    }
    downloads_list = [
        "test/path/downloads/TESTCOURSE-LRB1C20_video.mp4",
        "test/path/downloads/TESTCOURSE-LRB1C20_video_2.mp4",
        "test/path/downloads/TEST-LEE_video.mp4",
    ]
    expected = {
        "3e79f7c5-e9f6-4e18-9481-ad5500d6b104": [
            "test/path/downloads/TESTCOURSE-LRB1C20_video.mp4",
            "test/path/downloads/TESTCOURSE-LRB1C20_video_2.mp4",
        ],
        "972fc0a7-6861-44b3-b64e-ac5300a10d9a": [
            "test/path/downloads/TEST-LEE_video.mp4"
        ],
    }

    assert (
        Utils.get_folder_download_matches(courseIds_folderIds, downloads_list)
        == expected
    )


# === logger_msg ===
def test_positive_logger_msg():
    assert Utils.logger_msg(123, "test", []) == [
        "<class 'int'>",
        "<class 'str'>",
        "<class 'list'>",
    ]


######################
### NEGATIVE TESTS ###
######################


# === clean_long_filename ==
@pytest.mark.parametrize(
    "course_id, filename", [(999, "file_1"), ("course_id_2", 999), (888, 999)]
)
def test_negative_clean_long_filename(course_id, filename):
    with pytest.raises(TypeError):
        Utils.clean_long_filename(course_id, filename)


# === create_dir_if_not_exists ===
@pytest.mark.parametrize(
    "path, error_type",
    [(999, TypeError), ("./\0", ValueError), ("///test", PermissionError),],
)
def test_negative_create_dir_if_not_exists(path, error_type):
    with pytest.raises(error_type):
        Utils.create_dir_if_not_exists(path)


def test_negative_create_dir_if_not_exists_alread_exists():
    path = "./test_dir"
    os.mkdir(path)
    assert Utils.create_dir_if_not_exists(path) == path
    os.rmdir(path)


# === calculate_time ===
@pytest.mark.parametrize("secs", ["abc", 12.5, ("value", 654)])
def test_negative_calculate_time(secs):
    with pytest.raises(TypeError):
        Utils.calculate_time(secs)


# === converte_date ===
@pytest.mark.parametrize(
    "date_in, error_type",
    [(999, TypeError), ("abc", ValueError), (["date"], TypeError)],
)
def test_negative_convert_date(date_in, error_type):
    with pytest.raises(error_type):
        Utils.convert_date(date_in)


# === set_search_start_date ===
@pytest.mark.parametrize("nb_weeks", ["1", [10], ("weeks", 12)])
def test_negative_set_search_start_date(nb_weeks):
    with pytest.raises(TypeError):
        Utils.set_search_start_date(nb_weeks)


# === handle_response ===
def test_negative_handle_response():
    r = Mock()
    r.text = '{"text": "test_text"}'

    r.status_code = 403
    assert Utils.handle_response(r) == None

    r.status_code = 404
    assert Utils.handle_response(r) == None

    r.status_code = 999
    assert Utils.handle_response(r) == None


# === get_headers ===
def test_negative_get_headers():
    with pytest.raises(TypeError):
        Utils.get_headers(123)


# === clean_message ===
def test_negative_clean_message():
    with pytest.raises(TypeError):
        Utils.clean_message(123)


# === list_entry ===
@pytest.mark.parametrize(
    "results, size, type",
    [("test", 123, 0), ({"key": "value"}, "test", 0), ({"key": "value"}, 123, "test")],
)
def test_negative_list_entry(results, size, type):
    with pytest.raises(TypeError):
        Utils.list_entry(results, size, type)


def test_negative_list_entry_keyerror():
    with pytest.raises(KeyError):
        Utils.list_entry({"key": "value"}, 123, 0)


# === recording_storage_size ===
def test_negative_recording_storage_size():
    with pytest.raises(TypeError):
        Utils.recording_storage_size(123)


# === return_filename ===
@pytest.mark.parametrize(
    "c_id, rec, filetype, prefix",
    [
        (123, {"key": "value"}, "test", "test"),
        ("test", 123, "test", "test"),
        ("test", {"key": "value"}, 123, "test"),
        ("test", {"key": "value"}, "test", 123),
    ],
)
def test_negative_return_filename(c_id, rec, filetype, prefix):
    with pytest.raises(TypeError):
        Utils.return_filename(c_id, rec, filetype, prefix)


def test_negative_return_filename_keyerror():
    with pytest.raises(KeyError):
        Utils.return_filename("test", {"key": "value"}, "test", "test")


# === get_courseId_folderId_pairs ===
def test_negative_get_courseId_folderId_pairs():
    with pytest.raises(TypeError):
        Utils.get_courseId_folderId_pairs(123)


# === save_as_json ===
@pytest.mark.parametrize(
    "courseId_folderId_pairs, json_dir_path", [(123, "test"), ({"key": "value"}, 123)],
)
def test_negative_save_as_json(courseId_folderId_pairs, json_dir_path):
    with pytest.raises(TypeError):
        Utils.save_as_json(courseId_folderId_pairs, json_dir_path)


# === get_downloads_list ===
def test_negative_get_downloads_list():
    with pytest.raises(TypeError):
        Utils.get_downloads_list(123)


# === get_folder_download_matches ===
@pytest.mark.parametrize(
    "courseIds_folderIds, downloads_list", [(123, []), ({"key": "value"}, 123)],
)
def test_negative_get_folder_download_matches(courseIds_folderIds, downloads_list):
    with pytest.raises(TypeError):
        Utils.get_folder_download_matches(courseIds_folderIds, downloads_list)


#############
### MOCKS ###
#############

# Mock requests.get content_length
def mock_requests_get_content_length(*args, **kwargs):
    resp = Response()
    resp.status_code = 200
    # resp._content = b"test_content"
    # resp.headers = {"content-length": str(len(resp.content))}
    resp.headers = {"content-length": "123"}
    return resp


def mock_get_folder_id_from_course_id(*args, **kwargs):
    if args[0] == "TEST-LEE":
        return "972fc0a7-6861-44b3-b64e-ac5300a10d9a"
    elif args[0] == "TESTCOURSE-LRB1C20":
        return "3e79f7c5-e9f6-4e18-9481-ad5500d6b104"
    else:
        return None
