
## list_recordings(recordings: dict)

**Input** : recordings = dict recordings data
*Note : a test JSON is available at the end of this file*

**Positive test**  
Start : list_recordings(recordings)  
Result : list[dict] containing useful data for all available recordings  

*Example* :  

- list_recordings(public_recordings) == [{'recording_id': str, 'recording_name': str, 'duration': int, 'storage_size': int, 'created': '%Y-%m-%dT%H:%M:%S.%fZ'}, {...}]
- list_recordings(private_recordings) == [{'recording_id': str, 'recording_name': str, 'msg': 403}, {...}]

**Negative test**  
Start : list_recordings(recordings) *recordings either being an incorrect dict or not a dict*  
Result : Exception : Incorrect fields in dict OR Exception : Invalid input type  

*Example* :  

- list_recordings(incorrect_recordings) == Exception : Incorrect fields in dict
- list_recordings(999) == Exception Invalid input type

## recording_storage_size(url: str)
*LEFT PARTIALLY FILLED UNTIL WE HAVE A URL TO TEST IT WITH* 
**Input** : url = string url of recording or chat   

**Positive test**  
Start : recording_storage_size(url)  
Result : int size of recording given in url  

*Example* :  
recording_storage_size(url) == ??? *NEED TEST URL HEREE*

**Negative test**  
Start : recording_storage_size(url) *with invalid url or not string*  
Result : Exception : Invalid url OR Invalid input type  

*Example* :  

- recording_storage_size(invalid_url) == Exception : Invalid url
- recording_storage_size(999) == Exception : Invalid input type

## download_recording(url: str, fname: str)

**Input** : url = string url to recording, fname = str file path to save recording to "_.mp4"  
*Note : test recording url given at end of this file*  

**Positive test**  
Start : download_recording(url, fname)  
Result : file.mp4 created at specified path with recording data inside  

*Example* :  
download_recording(url, './downloads/recording.mp4') == recording.mp4 created in /downloads containing recording data

**Negative test**  
Start : download_recording(url, fname) *url could be invalid, or input types could be wrong*  
Result : Exception : Invalid url OR Invalid input type  

*Example* :  

- download_recording(invalid_url, './downloads/recording.mp4') == Exception Invalid url
- download_recording(999, 888) == Exception Invalid input type

## download_chat(url: str, fname: str)

**Input** : url = string url to chat, fname = str file path to save chat to "_.csv"  
*Note : test chat url given at end of this file*  

**Positive test**  
Start : download_chat(url, fname)  
Result : file.csv created at specified path with chat data inside  

*Example* :  
download_chat(url, './downloads/chat.csv') == chat.csv created in /downloads containing chat data

**Negative test**  
Start : download_chat(url, fname) *url could be invalid, or input types could be wrong*  
Result : Exception : Invalid url OR Invalid input type  

*Example* :  

- download_chat(invalid_url, './downloads/chat.csv') == Exception Invalid url
- download_chat(999, 888) == Exception Invalid input type

## download_recording_from_id(recording: dict, course_id: str)

**Input** : recording = dict {'recording_id': str, 'recording_name': str, 'duration': int, 'storage_size': int, 'created': '%Y-%m-%dT%H:%M:%S.%fZ'}, course_id = str  

**Positive test**  
Start : download_recording_from_id(recording, course_id)  
Result : recording files created in ./downloads/  
*Note : if recording contains chat, a .csv file will also be created with chat data*

*Example* :  
download_recording_from_id(recording, '123') == file created at './downloads/123-recording_id-recording_name.mp4'

**Negative test**  
Start : download_recording_from_id(recording, course_id) *with recording containing the wrong information or not being a dict, and course_id not being a string*  
Result : Exception : Invalid input  

*Example* :  

- download_recording_from_id({'wrong': 'info'}, '123') == Exception : Invalid input (missing required fields in dict) *recording doesn't have the right info*
- download_recording_from_id('abc', 999) == Exception : Invalid input type *wrong input types*

---

*Test recording URL* : 'https://ultra-eu-prod-sms.collab.cloudflare.blackboardcdn.com/content/a29738ff-095b-5c1f-819c-06c9d61e3447/21/05/20/13/a29738ff-095b-5c1f-819c-06c9d61e3447_1_210520T131700331Z.mp4?X-Blackboard-Expiration=1622846967140&X-Blackboard-Signature=S1K2fwgv%2BUwwr8UhOUVcM8%2Fbu9pXJe21esjLY38O0b4%3D&X-Blackboard-Client-Id=void&Expires=1622846967&Signature=MFgW6x9ZO0kIsNcm-bCik12HWMWbLritghcKpD3-NOdr8BLwieLCcRAUjr5PHrPanikFv4Tph6EJPlzwCLuD8sNMptXDm2uiauVgYJ90oSpVqqXetGAQHE~Dlf5l-JRa00awjmAQ1pRLYNVR74KsuL3ID76vPkknIiiAH6Mq2okyJwMAmT8E3yieJf~osMB4Wj5WKxOtTUnp5OAT3xY5Tk0DixZtsEGydLe4NmPdqOUYAqvZMRa1N36P129p8dVs0lzV1e9sJbynpK2nRGvl1XzdUBq8dlRH~Q7lTahDxfP00Z2j4RzmHvxUUBUiyIXZczWv5JpoeedlxW4PIATXLg__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA'  

*Test chat URL* : 'https://ultra-eu-prod-sms.collab.cloudflare.blackboardcdn.com/content/96397440-c366-5c1f-95b1-06d214184507/21/06/03/15/96397440-c366-5c1f-95b1-06d214184507_210603T152401259Z_chat.json?X-Blackboard-Expiration=1622838207863&X-Blackboard-Signature=Ze865gdBhePF4mO5tTwZJairf7pMr7EAh3R951P0z%2BI%3D&X-Blackboard-Client-Id=void&Expires=1622838207&Signature=VnHCUp7FeHuIeMNTEa8UsB3bd1QdWmohowwXbGmRdMmKNh1lUGI6ynafoXoqoqxEar57SUn9tiUxu8X7UT1lOJMx6EQR8D4HgSGHuvaxcTYEwtn34etlfouKjy-iwJ9-sEPMm8OtyVZJVtx0kmMJAb9Bf-CiAlDRq2pa0~q~fXZoCuVcbwdrGXuMBGgYqIcLf3ZRwFPb9OIpiYASRY6yRluYfLSUbk9dfQ4FyfoIIuJ0TSZUed1Jr0TqNmMbWbLIsf2M1~FqddScRk8bbdue0LTmB7qNfFg28O31NicWy8Wc6b6OtkWA4w4gSCLg74kaEK6BjG2xHaCJUQfhK3Y05Q__&Key-Pair-Id=APKAIOBDBIMXUOQOBYVA'

*Test public recording with chat JSON* : {"size": 1, "offset": 0, "limit": 1000, "name": "", "fields": "", "results": [{"id": "19ceeea8cb984bd79a6d0f967af9db12", "name": "testvid 2 - public_2", "sessionName": "testvid 2", "mediaName": "public_2", "sessionStartTime": "2021-05-19T17:10:00.000Z", "duration": 119000, "created": "2021-05-19T17:11:45.331Z", "modified": "2021-06-03T15:22:27.784Z", "publicLinkAllowed": true, "authLinkLevel": "LG", "lastPlayback": "2021-06-04T11:08:03.677Z", "playbackCount": 350, "downloadCount": 0, "canDownload": false, "startTime": "2021-05-19T17:11:45.331Z", "endTime": "2021-05-19T17:13:44.331Z", "subtitlesEnabled": true, "preferredSubtitles": "USER", "userSubtitles": false, "embeddedSubtitles": false, "asrSubtitles": false, "asrStatus": "NONE", "status": "DONE", "statusUpdateTs": "2021-05-19T17:16:43.220Z", "storageSize": 13837851}]}

*Test private recording JSON* : {"size": 1, "offset": 0, "limit": 1000, "name": "", "fields": "", "results": [{"id": "86d4fedc892141b0b46eaf996cf3979d", "name": "testvid 2 - private_1", "sessionName": "testvid 2", "mediaName": "private_1", "sessionStartTime": "2021-05-19T16:00:00.000Z", "duration": 55000, "created": "2021-05-19T16:01:27.998Z", "modified": "2021-06-03T15:22:12.636Z", "publicLinkAllowed": false, "authLinkLevel": "LG", "lastPlayback": "2021-06-03T14:48:06.854Z", "playbackCount": 281, "downloadCount": 0, "canDownload": false, "startTime": "2021-05-19T16:01:27.998Z", "endTime": "2021-05-19T16:02:22.998Z", "subtitlesEnabled": true, "preferredSubtitles": "USER", "userSubtitles": false, "embeddedSubtitles": false, "asrSubtitles": false, "asrStatus": "NONE", "status": "DONE", "statusUpdateTs": "2021-05-19T16:05:07.064Z", "storageSize": 5632264}]}
