from genericpath import getsize
from logging import error
import pytest
import requests
from requests import Response
import os
from src.models import Downloads, WebService
import time

TEST_MP4_PATH = "unit_tests/unit_test_data/unit_test_downloads/COMP6215-32970-20-21-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1 - recording.mp4"
TEST_CSV_PATH = "unit_tests/unit_test_data/unit_test_downloads/Chat-COMP6215-32970-20-21-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1 - recording.csv"

######################
### POSITIVE TESTS ###
######################


# === get_recordings_data ===
def test_positive_get_recordings_data(monkeypatch):
    monkeypatch.setattr(
        WebService.WebService,
        "get_course_recordings_data",
        mock_webservice_get_course_recordings_data,
    )
    monkeypatch.setattr(
        WebService.WebService,
        "get_single_recording_data",
        mock_webservice_get_single_recording_data,
    )

    expected_result = [
        {
            "recording_id": "21b4e35ea2184e6abc74e4325a74e0e2",
            "recording_name": "SPARQL 1 - recording",
            "duration": 3118000,
            "storage_size": 115592014,
            "created": "2021-02-10T11:00:14.466Z",
        }
    ]

    assert (
        Downloads.get_recordings_data("test_uuid", "test_start_time") == expected_result
    )


# === list_of_recordings ===
def test_positive_list_of_recordings(monkeypatch):
    monkeypatch.setattr(
        WebService.WebService,
        "get_single_recording_data",
        mock_webservice_get_single_recording_data,
    )

    expected_result = [
        {
            "recording_id": "21b4e35ea2184e6abc74e4325a74e0e2",
            "recording_name": "SPARQL 1 - recording",
            "duration": 3118000,
            "storage_size": 115592014,
            "created": "2021-02-10T11:00:14.466Z",
        }
    ]

    mock_recs_json = mock_webservice_get_course_recordings_data()

    assert Downloads.list_of_recordings(mock_recs_json) == expected_result


# === get_recordings_for_course ===
def test_positive_get_recordings_for_course(monkeypatch):
    tmp_vid_path = "downloads/test_course_id-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1  recording.mp4"
    tmp_csv_path = "downloads/Chat-test_course_id-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1  recording.csv"

    monkeypatch.setattr(
        WebService.WebService,
        "get_course_recordings_data",
        mock_webservice_get_course_recordings_data,
    )
    monkeypatch.setattr(
        WebService.WebService,
        "get_single_recording_data",
        mock_webservice_get_single_recording_data,
    )
    monkeypatch.setattr(
        Downloads, "requests_get_stream", mock_requests_get_stream,
    )
    monkeypatch.setattr(
        Downloads, "requests_get_chat", mock_requests_get_chat,
    )

    test_recordings_data = [
        {
            "recording_id": "21b4e35ea2184e6abc74e4325a74e0e2",
            "recording_name": "SPARQL 1 - recording",
            "duration": 3118000,
            "storage_size": 115592014,
            "created": "2021-02-10T11:00:14.466Z",
        }
    ]

    Downloads.get_recordings_for_course(
        test_recordings_data, "test_uuid", "test_course_id"
    )

    assert os.path.getsize(tmp_vid_path) == os.path.getsize(TEST_MP4_PATH)
    assert os.path.getsize(tmp_csv_path) == os.path.getsize(TEST_CSV_PATH)

    os.unlink(tmp_vid_path)
    os.unlink(tmp_csv_path)


# === download_recording_from_collab ===
def test_positive_download_recording_from_collab(monkeypatch):
    tmp_vid_path = "downloads/test_course_id-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1  recording.mp4"
    tmp_csv_path = "downloads/Chat-test_course_id-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1  recording.csv"

    monkeypatch.setattr(
        WebService.WebService,
        "get_single_recording_data",
        mock_webservice_get_single_recording_data,
    )
    monkeypatch.setattr(
        Downloads, "requests_get_stream", mock_requests_get_stream,
    )
    monkeypatch.setattr(
        Downloads, "requests_get_chat", mock_requests_get_chat,
    )

    test_recording = {
        "recording_id": "21b4e35ea2184e6abc74e4325a74e0e2",
        "recording_name": "SPARQL 1 - recording",
        "duration": 3118000,
        "storage_size": 115592014,
        "created": "2021-02-10T11:00:14.466Z",
    }

    Downloads.download_recording_from_collab(test_recording, "test_course_id")

    assert os.path.getsize(tmp_vid_path) == os.path.getsize(TEST_MP4_PATH)
    assert os.path.getsize(tmp_csv_path) == os.path.getsize(TEST_CSV_PATH)

    os.unlink(tmp_csv_path)
    os.unlink(tmp_vid_path)


# === download_stream ===
def test_positive_download_stream(monkeypatch):
    tmp_vid_path = "unit_tests/unit_test_data/unit_test_downloads/test_vid.mp4"

    monkeypatch.setattr(requests, "get", mock_requests_get_stream)
    Downloads.download_stream("test_url", tmp_vid_path)

    assert os.path.getsize(tmp_vid_path) == os.path.getsize(TEST_MP4_PATH)

    os.unlink(tmp_vid_path)


# === download_chat ===
def test_positive_download_chat(monkeypatch):
    tmp_chat_path = "unit_tests/unit_test_data/unit_test_downloads/test_chat.csv"

    monkeypatch.setattr(requests, "get", mock_requests_get_chat)
    Downloads.download_chat("test_url", tmp_chat_path)

    assert os.path.getsize(tmp_chat_path) == os.path.getsize(TEST_CSV_PATH)

    os.unlink(tmp_chat_path)


######################
### NEGATIVE TESTS ###
######################


# === get_recordings_data ===
@pytest.mark.parametrize(
    "uuid, start_time",
    [
        ("test_uuid", 123),
        (123, "test_time"),
        ({"test_key": "test_value"}, ["test_time"]),
    ],
)
def test_negative_get_recordings_data(uuid, start_time):
    with pytest.raises(TypeError):
        Downloads.get_recordings_data(uuid, start_time)


# === list_of_recordings ===
@pytest.mark.parametrize(
    "recs_json, error_type",
    [
        (123, TypeError),
        (["test_list"], TypeError),
        ({"test_key": "test_value"}, KeyError),
    ],
)
def test_negative_list_of_recordings(recs_json, error_type):
    with pytest.raises(error_type):
        Downloads.list_of_recordings(recs_json)


# === get_recordings_for_course ===
@pytest.mark.parametrize(
    "recordings_data, uuid, course_id",
    [
        (123, "test_uuid", "test_course_id"),
        (["test_list"], 123, "test_course_id"),
        (["test_list"], "test_uuid", 123),
    ],
)
def test_negative_get_recordings_for_course(recordings_data, uuid, course_id):
    with pytest.raises(TypeError):
        Downloads.get_recordings_for_course(recordings_data, uuid, course_id)


# === download_recording_from_collab ===
@pytest.mark.parametrize(
    "recording, course_id, error_type",
    [
        (123, "test_course_id", TypeError),
        ({"test_key": "test_value"}, 123, TypeError),
        ({"test_key": "test_value"}, "test_course_id", KeyError),
    ],
)
def test_negative_download_recording_from_collab(recording, course_id, error_type):
    with pytest.raises(error_type):
        Downloads.download_recording_from_collab(recording, course_id)


# === download_stream ===
@pytest.mark.parametrize(
    "url, fname",
    [
        (123, "test_fname"),
        ("test_url", 123),
        ({"test_key": "test_value"}, ["test_list"]),
    ],
)
def test_negative_download_stream(url, fname):
    with pytest.raises(TypeError):
        Downloads.download_stream(url, fname)


# === download_chat ===
@pytest.mark.parametrize(
    "url, fname",
    [
        (123, "test_fname"),
        ("test_url", 123),
        ({"test_key": "test_value"}, ["test_list"]),
    ],
)
def test_negative_download_chat(url, fname):
    with pytest.raises(TypeError):
        Downloads.download_chat(url, fname)


#############
### MOCKS ###
#############

# Mock Webservice.get_course_recordings_data
def mock_webservice_get_course_recordings_data(*args, **kwargs):
    return {
        "size": 1,
        "offset": 0,
        "limit": 1000,
        "name": "",
        "fields": "",
        "results": [
            {
                "id": "21b4e35ea2184e6abc74e4325a74e0e2",
                "name": "SPARQL 1 - recording",
                "sessionName": "SPARQL 1",
                "mediaName": "recording",
                "sessionStartTime": "2021-02-10T11:00:00.000Z",
                "duration": 3118000,
                "created": "2021-02-10T11:00:14.466Z",
                "modified": "2021-02-10T13:00:08.465Z",
                "publicLinkAllowed": True,
                "authLinkLevel": "LG",
                "lastPlayback": "2021-06-18T09:04:53.655Z",
                "playbackCount": 16,
                "lastDownload": "2021-02-10T13:01:02.366Z",
                "downloadCount": 2,
                "canDownload": False,
                "startTime": "2021-02-10T11:00:14.466Z",
                "endTime": "2021-02-10T11:52:12.466Z",
                "subtitlesEnabled": True,
                "preferredSubtitles": "USER",
                "userSubtitles": False,
                "embeddedSubtitles": False,
                "asrSubtitles": False,
                "asrStatus": "NONE",
                "status": "DONE",
                "statusUpdateTs": "2021-02-10T12:07:55.211Z",
                "storageSize": 115592014,
            }
        ],
    }


# Mock Webservice.get_single_recording_data
def mock_webservice_get_single_recording_data(*args, **kwargs):
    return {
        "status": 3,
        "streams": {
            "WEB": "https://ultra-eu-prod-sms.collab.cloudflare.blackboardcdn.com/content/ded64fdc-d30d-5c1f-8061-068b80bac01d/21/06/17/11/ded64fdc-d30d-5c1f-8061-068b80bac01d_1_210617T115059150Z.mp4?X-Blackboard-Expiration=1624052031681&X-Blackboard-Signature=hRdJlM7s2mlnSR50QZNBvosUfEHvLLGKmGGqfsHOeuw%3D&X-Blackboard-Client-Id=void&Expires=1624052031&Signature=aTFX-9aGCP1NTLBYu7U9Q0bN6WO78cLiML0Czw8fKudrvNeGKTnsLy6-9c5Xb0MTKfhjQpSXxMAdjz30xyXlY7OzvmYsxBcDl95GVtKg3tWkvTqGnPE2ZoAdsvdAEUk~nCN5eLjbaOt83Rbe8OCO4jmYDQiBKfLL-L5FG82lZ8rULCNnYfrUvG4iNkvzp8XKsE7HwaFQtZ6fPG1cRSTVcIcuJpxNJJe7H8jkLlONXqmlaeWrmzgrvARjZVIcs7HIdnNNHT37h9tl5S8yBLRYhLEnrg0Hv2~h7wmDCkVT9UIXDU-HuT52ma-z66eCLOpiO-Ou6dRDmUgr8ccyIoH9lg__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA"
        },
        "extStreams": [
            {
                "streamUrl": "https://ultra-eu-prod-sms.collab.cloudflare.blackboardcdn.com/content/ded64fdc-d30d-5c1f-8061-068b80bac01d/21/06/17/11/ded64fdc-d30d-5c1f-8061-068b80bac01d_1_210617T115059150Z.mp4?X-Blackboard-Expiration=1624052031681&X-Blackboard-Signature=hRdJlM7s2mlnSR50QZNBvosUfEHvLLGKmGGqfsHOeuw%3D&X-Blackboard-Client-Id=void&Expires=1624052031&Signature=aTFX-9aGCP1NTLBYu7U9Q0bN6WO78cLiML0Czw8fKudrvNeGKTnsLy6-9c5Xb0MTKfhjQpSXxMAdjz30xyXlY7OzvmYsxBcDl95GVtKg3tWkvTqGnPE2ZoAdsvdAEUk~nCN5eLjbaOt83Rbe8OCO4jmYDQiBKfLL-L5FG82lZ8rULCNnYfrUvG4iNkvzp8XKsE7HwaFQtZ6fPG1cRSTVcIcuJpxNJJe7H8jkLlONXqmlaeWrmzgrvARjZVIcs7HIdnNNHT37h9tl5S8yBLRYhLEnrg0Hv2~h7wmDCkVT9UIXDU-HuT52ma-z66eCLOpiO-Ou6dRDmUgr8ccyIoH9lg__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA",
                "contentType": "video/mp4",
                "flavorCode": 1,
            }
        ],
        "cookies": "https://d1os9znak2uyeg.cloudfront.net/v1/cookies/eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjYxNjI0MDEwODc5LCJjb250YWluZXIiOiJJVFhTTVNDb250YWluZXIiLCJwYXRoIjoiY29udGVudC9kZWQ2NGZkYy1kMzBkLTVjMWYtODA2MS0wNjhiODBiYWMwMWQqIiwic2l0ZSI6IkNjcklUWFByb2QiLCJwcm90b2NvbCI6IkhUVFBTIiwiZXhwaXJhdGlvbiI6IjE2MjQwNTIwMzE2NzAifQ.8Hz5nUrFMVWRJ4TxBbcLLPQWtMZ_Mf4wQQMAYYdB-Kw?Expires=1624052031&Signature=dybu8ZTcJBRueNKZlnfwOcauUFrXWN4AA-7GYvtnHw8dHDrL7qPMNbS08BoqKtmRalxcOcAjmttZ13J4keyPpqSlwr6wA7wDqIopGMGGmYt~g9j9gyl9nAStJhDOXGbAVgwqvyluONAuXt9aIboVRyp~9cycyz97IWJdZSBMVRf1Iic40hNMkM4r1Izxojh6CnNoAxvfLFMXC3R7d75kYiDV6JzwfwZQgOurlgve~9JoJxtrgn97qVBJviXVcVGVyRtbOwmobtttxUyYNjpx5VqBdif1WbuS1HIF~oI31rEmfEZbMJLP-CjEa~MdtStgdjzNaJtIFihT4hHlF4rX4g__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA",
        "subtitlesInDownload": True,
        "aspectRatio": "16:9",
        "subtitles": [],
        "chats": [
            {
                "url": "https://ultra-eu-prod-sms.collab.cloudflare.blackboardcdn.com/content/ded64fdc-d30d-5c1f-8061-068b80bac01d/21/02/10/13/ded64fdc-d30d-5c1f-8061-068b80bac01d_210210T130016064Z_chat.json?X-Blackboard-Expiration=1624052031684&X-Blackboard-Signature=j04E0kwb1yOt%2FaCnb5a9w1L23PgBsovKSLxkno2QFto%3D&X-Blackboard-Client-Id=void&Expires=1624052031&Signature=U03~GGkRFbsOkZ720XZ42JpZ2PHCrFHsAmwPVKil2tYVx518Zf1dsKr1g6fZl1aeIRQjYRvw98nfZlRKBYKSh6hHN6qFUeK1f8ZOcW7ytTAKCuczKI9lGucJ11AUBzUzmVhXF0X0uiwLmaDsTpOUeFmZ~fntmxWwRr6yMjLeBxn7l6EWHWUbJ9oQvumfW-F8SnbU0CCK4UE5zwDzb-q~IFhjvdw4QyAr3G8w0K3tej2GERaE2w8Rz3GDTMocUleJ8im3mOiv1FXJKLQirlsorkO81QEQvRueUc7oUFe7DEPtqtpU2UFXiRXeRXPWPCizuFXAGg5NNjBNpOGPK3uGBA__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA"
            }
        ],
        "uuid": "ded64fdc-d30d-5c1f-8061-068b80bac01d",
        "sessionInstanceUUID": "808b5683-55a3-4b8d-a890-91e6c9ed0da9",
        "profanityFilterEnabled": False,
        "name": "SPARQL 1 - recording",
        "duration": 3118000,
        "created": "2021-02-10T11:00:14.466Z",
    }


# Mock requests.get stream
def mock_requests_get_stream(*args, **kwargs):
    stream = open(
        "unit_tests/unit_test_data/unit_test_downloads/COMP6215-32970-20-21-21b4e35ea2184e6abc74e4325a74e0e2-SPARQL 1 - recording.mp4",
        "rb",
    )
    resp = Response()
    resp.status_code = 200
    resp._content = stream.read()
    resp.headers = {"content-length": str(len(resp.content))}
    stream.close()
    return resp


# Mock requests.get chat
def mock_requests_get_chat(*args, **kwargs):
    resp = Response()
    resp.status_code = 200
    resp._content = b'[{"id":1827763572,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:07:23.709Z","relativeEventTime":"00:07:09","body":"<p>If we can query the columns of subject, predicate and object, do we need to query the graph column directly?</p>","groupName":""},{"id":1827987945,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:21:10.961Z","relativeEventTime":"00:20:56","body":"<p>Do we use floats and doubles in our queries?</p>","groupName":""},{"id":1828007146,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:22:28.585Z","relativeEventTime":"00:22:14","body":"<p>yes</p>","groupName":""},{"id":1828343321,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:45:43.001Z","relativeEventTime":"00:45:28","body":"<p>I would appreciate it if there is anyway you can provide us with practical tutorials that we can follow and apply to fully understand the concepts introduced in this lecture.</p>","groupName":""},{"id":1828393882,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:49:34.513Z","relativeEventTime":"00:49:20","body":"<p>and are these examples up to date? Do we need to worry if some of them are outdated?</p>","groupName":""},{"id":1828395981,"groupID":0,"userName":"Mr Adam Putland","targetType":"everyone","eventTime":"2021-02-10T11:49:44.333Z","relativeEventTime":"00:49:29","body":"<p>I think dbpedia has a sparql endpoint you can play around with aswell</p>","groupName":""},{"id":1828409661,"groupID":0,"userName":"MISS Panpan Wu","targetType":"everyone","eventTime":"2021-02-10T11:50:46.427Z","relativeEventTime":"00:50:31","body":"<p>Could you please use cursor or pen to indicate the codes or something important you are explaining?</p><p>It\'s a bit difficult to follow without highlighting.</p>","groupName":""},{"id":1828425679,"groupID":0,"userName":"Mr Abdullah Alsherefi","targetType":"everyone","eventTime":"2021-02-10T11:52:00.710Z","relativeEventTime":"00:51:46","body":"<p>I appreciate it. Thanks.</p>","groupName":""}]'
    return resp
