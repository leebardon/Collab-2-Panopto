## create_collab_download_report(report: list[list])

**Input** : report = List containing lists of recording data [[(str)c_uuid, (str)recording_id, (str)recording_name, (int)duration, (int)storage_size, (str)created], [...]]  

**Positive test**  
Start : create_collab_download_report(report)  
Result : "./reports/Collab_Download_Report.csv" file created and filled in with the correct report data and printed string : "Report: Collab_Download_Report.csv created!"  

*Example* :  

create_collab_download_report([['123_uuid', '456_recording_id', 'testvid 2 - recording_1', 119000, 13837851, '2021-05-19T17:11:45.331Z']]) ==  

1. CSV file created with data :  
Course ID/UUID,Recording ID,Recording Name,Duration,Storage Size (MB),Created Date  
123_uuid,456_recording_id,testvid 2 - recording_1,00:01:59,13.84,"May 19,2021"
2. Print "Report: Collab_Download_Report.csv created!"

*Note : This should be able to process a list of lists, so multiple recording data are written to the same report file*

**Negative test**  
Start : create_collab_download_report(report) *with report being anything but a list of lists*  
Result : Exception : Invalid input  

*Example* :  

- create_collab_download_report(['', '', '', 0, 0, '']) == Exception : Invalid input *Not a list of lists*
- create_collab_download_report([['', 0]]) == Exception : Invalid input *Lists don't have expected length*

## create_collab_download_403_report(report: list[list]):

**Input** : report = List containing lists of private 403 recording data [[(str)c_uuid, (str)recording_id, (str)recording_name, (str)details], [...]]  

**Positive test**  
Start : create_collab_download_403_report(report)  
Result : "./reports/Collab_Download_Report_403.csv" file created and filled in with the correct report data and printed string : "Report: Collab_Download_Report_403.csv created!"  

*Example* :  

create_collab_download_403_report([['123_uuid', '456_recording_id', 'testvid 2 - recording_1', 'test_details']]) ==  

1. CSV file created with data :  
Course ID/UUID,Recording ID,Recording Name,Details 
123_uuid,456_recording_id,testvid 2 - recording_1,test_details
2. Print "Report: Collab_Download_Report_403.csv created!"

**Negative test**  
Start : create_collab_download_403_report(report) *with report being anything but a list of lists*  
Result : Exception : Invalid input  

*Example* :  

- create_collab_download_403_report(['', '', '', '']) == Exception : Invalid input *Not a list of lists*
- create_collab_download_403_report([['', 0]]) == Exception : Invalid input *Lists don't have expected length*