## read_course_list(filename: str)

**Input** : filename = string path to file containing list of courses  
*Note : example of file is learn_courses.txt*  

**Positive test**  
Start : read_course_list(filename)  
Result : list[str] containing all courseId's  

*Example* :  
read_course_list(learn_courses.txt) == ['TEST-LEE', 'TESTCOURSE-LRB1C20']

**Negative test**  
Start : read_course_list(filename) *invalid path or invalid file or wrong input type*  
Result : Exception : Invalid path OR Exception : Invalid file contents OR Exception : Invalid input type  

*Example* :  

- read_course_list('invalid_path') == Exception : Invalid path
- read_course_list('path_wrong_file') == Excpetion : Invalid file contents
- read_course_list(999) == Exception : Invalid input type



## get_course_details(course_id: str)

**Input** : course_id = string for a given courseId 

**Positive test**  
Start : get_course_details(course_id)  
Result : list[dict] dictionary containing uuid and courseId for arg::course_id

*Example* :  
get_course_details(course_id) ==  [{"uuid": course_uuid, "course_id": courseId}]

**Negative test**  
Start : get_course_details(course_id)  *invalid course_id or wrong input type*  
Result : Exception : Exception : Invalid file contents OR Exception : Invalid input type  

*Example* :  

- get_course_details(course_id) ('invalid_course_id') == Exception : Invalid course id
- get_course_details(course_id) (999) == Exception : Invalid input type

