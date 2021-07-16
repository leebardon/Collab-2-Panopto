import pytest
import os
import json
import requests
from requests import Response
from src.models import Courses, WebService

BASE = os.getcwd() + "/unit_tests/unit_test_data"


######################
### POSITIVE TESTS ###
######################


def test_get_id_uuid_pairs_returns_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert type(returned_pairs) == dict


def test_get_id_uuid_pairs_returns_list(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert type(no_course_ids) == list


def test_get_id_uuid_pairs_this_year_returns_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "20-21")
    assert type(returned_pairs) == dict


def test_returned_pairs_contains_expected_pair(monkeypatch):
    res = return_patch(monkeypatch)
    expected = {res[0]["results"][0]["id"]: res[0]["results"][0]["label"]}
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert returned_pairs | expected == returned_pairs


def test_returned_list_contains_expected_uuid(monkeypatch):
    res = return_patch(monkeypatch)
    expected = "7d97f5386ea14bd9922d099b883efe7d"
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert expected == no_course_ids[0]


def test_returned_pairs_this_year_contains_expected_pair(monkeypatch):
    res = return_patch(monkeypatch)
    expected = {"d3d97c5429094f4c97ffe48610988fb5": "GENG6099-AI-20-21"}
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "20-21")
    assert returned_pairs | expected == returned_pairs


def test_get_id_uuid_pairs_returns_correct_length_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert len(returned_pairs) == 964


def test_get_id_uuid_pairs_returns_correct_length_list(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert len(no_course_ids) == 36


def test_get_id_uuid_pairs_this_year_returns_correct_length_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "20-21")
    assert len(returned_pairs) == 1


######################
### NEGATIVE TESTS ###
######################


def test_incorrect_courses_data_from_collab(monkeypatch):
    expected_result = {"The answer is": "definitely 42"}
    res = return_patch(monkeypatch)
    assert res[0]["results"][0] != expected_result


def test_get_id_uuid_pairs_does_not_return_dict(monkeypatch):
    res = return_bad_patch(monkeypatch)
    with pytest.raises(TypeError):
        returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
        # assert type(returned_pairs) != dict


def test_get_id_uuid_pairs_does_not_returns_list(monkeypatch):
    res = return_bad_patch(monkeypatch)
    with pytest.raises(TypeError):
        returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
        # assert type(no_course_ids) != list


def test_negative_get_id_uuid_pairs_this_year_returns_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "19-20")
    assert type(returned_pairs) == dict


def test_negative_returned_pairs_contains_expected_pair(monkeypatch):
    res = return_patch(monkeypatch)
    expected = {res[0]["results"][0]["id"]: res[0]["results"][0]["label"]}
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert returned_pairs | expected == returned_pairs


def test_negative_returned_list_contains_expected_uuid(monkeypatch):
    res = return_patch(monkeypatch)
    expected = "7d97f5386ea14bd9922d099b883efe7d"
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert expected == no_course_ids[0]


def test_negative_returned_pairs_this_year_contains_expected_pair(monkeypatch):
    res = return_patch(monkeypatch)
    expected = {"d3d97c5429094f4c97ffe48610988fb5": "GENG6099-AI-20-21"}
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "20-21")
    assert returned_pairs | expected == returned_pairs


def test_negative_get_id_uuid_pairs_returns_correct_length_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert len(returned_pairs) == 964


def test_negative_get_id_uuid_pairs_returns_correct_length_list(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs, no_course_ids = Courses.get_id_uuid_pairs(res)
    assert len(no_course_ids) == 36


def test_negative_get_id_uuid_pairs_this_year_returns_correct_length_dict(monkeypatch):
    res = return_patch(monkeypatch)
    returned_pairs = Courses.get_id_uuid_pairs_this_year(res, "20-21")
    assert len(returned_pairs) == 1


########################
### HELPER FUNCTIONS ###
########################


def return_patch(monkeypatch):
    monkeypatch.setattr(
        WebService.WebService,
        "courses_data_from_collab",
        mock_webservice_courses_data_from_collab,
    )
    return WebService.WebService.courses_data_from_collab()


def return_bad_patch(monkeypatch):
    monkeypatch.setattr(
        WebService.WebService,
        "courses_data_from_collab",
        mock_negative_webservice_courses_data_from_collab,
    )
    return WebService.WebService.courses_data_from_collab()


########################
### MOCKED FUNCTIONS ###
########################


def mock_webservice_courses_data_from_collab(*args, **kwargs):
    json_obj = open(f"{BASE}/courses_test.json")
    courses = json.load(json_obj)
    json_obj.close()
    return courses


def mock_negative_webservice_courses_data_from_collab(*args, **kwargs):
    bad_json = 42
    return bad_json
