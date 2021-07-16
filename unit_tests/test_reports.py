import pytest
import os

from src.views import Reports

BASE = os.getcwd() + "/unit_tests/unit_test_data"

recording_data = {
    "recording_id": "19ceeea8cb984bd79a6d...967af9db12",
    "recording_name": "testvid 2 - public_2",
    "duration": 119000,
    "storage_size": 13837851,
    "created": "2021-05-19T17:11:45.331Z",
}
uuid = "f61d43526fe343039f0a8334d1dd0af2"


# NOTE tests not implemented because currently unsure if reporting will be kept
# TODO possibly implement tests for logging processes

######################
### POSITIVE TESTS ###
######################


def test_report_entry_returns_correct_data():
    pass


def test_report_403_entry_returns_correct_data():
    pass


def test_append_report_entry_appends_correct_data():
    pass


def test_append_report_403_entry_appends_correct_data():
    pass


def test_generate_reports_generates_correct_report():
    pass


def test_create_collab_download_report():
    pass


def test_create_collab_403_download_report():
    pass


######################
### NEGATIVE TESTS ###
######################


########################
### HELPER FUNCTIONS ###
########################
