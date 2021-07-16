# Utilities test definition

## clean_long_filename(course_id: str, fname: str)

**Input** : course_id= string course id, fname = string filename to clean up  

**Positive test**  
Start : clean_long_filename(course_id, fname)  
Result : String of filename removed of most undesired punctuation, OR course_id if name > 160 chars  

*Example* :  

- clean_long_filename('123', 'dirty_:/"",_file_name?|') == 'dirty_file_name'
- clean_long_filename('123', 'P4wyzhn7XIEDvyaxuGYH15y6JDmocfpibnZh2PlRnIsf47UqHtQ51Qbd7MIIrED6BO2URJb2xvwuIh2b5E5YSgenrO2vSxDchAX1FqmmqFyX0JP47G0R1ya32lg87mcSflEis9wRfaMS3ax1sKysgJrN05gwBwwA160') == '123'

**Negative test**  
Start : clean_long_filename(course_id, fname) *with anything but strs for both parameters*  
Result : Exception : Invalid input  

*Example* :  
clean_long_filename(999, [357]) == Exception : Invalid input

## create_dir_if_not_exists(path: str)

**Input** : path = string path of directory to create  

**Positive test**  
Start : create_dir_if_not_exists(path)  
Result : Directory is created at specified location if it does not exist yet  

*Example* :  

- create_dir_if_not_exists('./test_dir') == Directory "test_dir" created at "./"
- create_dir_if_not_exists('./already_existing_dir') == Directory not created since it alread exists

**Negative test**  
Start : create_dir_if_not_exists(path) *with path not being a string or pointing to an invalid location*  
Result : Exception : Invalid input  

*Example* :  

- create_dir_if_not_exists(123) == Exception : Invalid input *input not a string*
- create_dir_if_not_exists('invalid path dir') == Exception : Invalid input *input not a valid path*

## parse_commandline(argv: list)

**Input** : argv = list of command line arguments without the 1st one (sys.argv[1:])

**Positive test**  
Start : parse_commandline(argv)  
Result : Either help text is printed and program exits or List containing parsed arguments [courseIds_list, uuids_list, weeks]  

*Example* :  

- parse_commandline(['-h']) ==  
"Collab.py -f \<LearnFileName_COURSE_ID.txt\> -w <numberOfWeekBehindToSearch\>"  
"Collab.py -e \<LearnFileName_COURSE_UUID\> -w <numberOfWeekBehindToSearch\>"
- parse_commandline(['-f', 'learn_courses.txt']) == ['learn_courses.txt', '', 0]
- parse_commandline(['-e', '123e4567-e89b-12d3-a456-426614174000']) == ['', '123e4567-e89b-12d3-a456-426614174000', 0]
- parse_commandline(['-w', 3]) == ['', '', 3]
- parse_commandline(['-f', 'file.txt', '-e', '123', '-w', 3]) == ['file.txt', '123', 3]

*Note : Not sure -f and -e at the same time should be possible*

**Negative test**  
Start : parse_commandline(argv) *with argv being anything but a list*  
Result : Help text is printed and program exits  

*Example* :  
parse_commandline('abc') ==  
"Collab.py -f \<LearnFileName_COURSE_ID.txt\> -w <numberOfWeekBehindToSearch\>"  
"Collab.py -e \<LearnFileName_COURSE_UUID\> -w <numberOfWeekBehindToSearch\>"


## calculate_time(secs: int)

**Input** : secs = positive int or float  

**Positive test**  
Start : calculate_time(secs)  
Result : String of seconds converted to "%H:%M:%S" format 

*Example* :  

- calculate_time(5400) == '01:30:00'
- calculate_time(5400.5) == '01:30:00' *Decimal ignored*

**Negative test**  
Start : calculate_time(secs) *secs being anything but a 0 or positive int or float*  
Result : Exception : Invalid input  

*Example* :  
calculate_time('abc') == Exception : Invalid input  

## convert_date(date: datetime)

**Input** : date = datetime object  

**Positive test**  
Start : convert_date(date)  
Result : String, date in "%b %d,%Y" format  

*Example* :  

- Current date = "2021-06-03"
- convert_date(date) == Jun 06,2021

**Negative test**  
Start : convert_date(date) *date being anything but a datetime object*  
Result : Exception : Invalid input  

*Example* :  
convert_date('abc') OR convert_date(123) == Exception : Invalid input

## set_search_start_time(weeks: int)  

**Input** : weeks = positive int or float  

**Positive test**  
Start : set_search_start_time(weeks)
Result : String corresponding to date n weeks ago. "%Y-%m-%dT%H:%M:%SZ" format  

*Example* :  

- Current date = "2021-06-03T11:06:30Z"
- set_search_start_time(2) == "2021-05-20T11:06:30Z"
- set_search_start_time(2.8) == "2021-05-20T11:06:30Z" *2.8 will be rounded down to 2*

*Note : 0 is a valid input, although useless.*  

**Negative test**
Start : set_search_start_time(weeks) *weeks being anything but a positive int or float*
Result : Exception : Invalid input  

*Example* :  

- set_search_start_time('abc') OR set_search_start_time(-6) == Exception : Invalid input

## search_from(params: list)  

**Input** : params = [courseIds_list, uuids_list, weeks] *weeks is the only one useful here* 

**Positive test**  
Start : search_from(["", "", weeks]) *weeks can be 0, positive int or float*  
Result : String corresponding to date n weeks ago. "%Y-%m-%dT%H:%M:%SZ" format 

*Example* :  

- Current date = "2021-06-03T11:06:30Z"
- search_from(["", "", 2]) == "2021-05-20T11:06:30Z"
- search_from(["", "", 2.8]) == "2021-05-20T11:06:30Z" *2.8 will be rounded down to 2*

**Negative test**
Start : search_from(["", "", weeks]) *weeks being anything but a positive int or float*
Result : Exception : Invalid input  

*Example* :  

- search_from(["", "", 'abc']) OR search_from(["", "", -6]) == Exception : Invalid input
