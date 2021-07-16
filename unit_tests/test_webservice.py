import pytest
import requests
import base64

# import json
# from cachetools import TTLCache
# import Config as Conf
# from src.controllers import AuthController as Auth
import unittest

"""
Testing API services in this scenario is notoriously tricky, due to the interface between 
e.g. our own code, and Blackboard's code. As such, we'll start elsewhere and return to this.

"""


TEST_COURSE_PATH = "/learn/api/public/v1/courses/courseId:Test-Lee"
TEST_AUTH_PATH = "/learn/api/public/v1/oauth2/token"


class BasicLearnAPITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.key = "6c828253-28e1-4c17-90e2-c9d08f653b85"
        self.secret = "YRJXRSgNuTTM3hAS7kNfRZ4IiuXFuZib"
        self.domain = "blackboard.soton.ac.uk"
        self.cache = None

    def tearDown(self) -> None:
        pass


# class TestGetFromLearnAPI(BasicLearnAPITestCase):

#     def payload(self):
#         credential = "Basic " + str(
#             base64.b64encode((f"{self.key}:{self.secret}").encode("utf-8")), encoding="utf-8"
#         )
#         headers = {
#             "Authorization": credential,
#             "Content-Type": "application/x-www-form-urlencoded",
#         }
#         body = "grant_type=client_credentials"
#         return headers, body


#     def test_set_token_should_create_token(self) -> None:
#         base_url = "https://" + self.learn_domain + self.course_path
#         headers, body = payload(self)
#         r = requests.get(base_url, headers=credential)

#     def test_get_token_should_return_token(self) -> None:
#         pass


#     def test_get_request_should_return_200_status_code(self) -> None:
#         pass
