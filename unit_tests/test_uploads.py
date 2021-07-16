from src.models.Uploads import Uploads

# TODO THESE ARE TEMPORARY AND SHOULD BE CHANGED ENTIRELY FOR THE PROPER TESTS

u = Uploads()
try:
    print(u.get_folder_id_from_course_id("COMP6215-32970-20-21"))
except ValueError as e:
    print(e)
except IndexError as e:
    print(e)

try:
    print(u.get_folder_id_from_course_id("ELEC"))
except ValueError as e:
    print(e)
except IndexError as e:
    print(e)

try:
    print(u.get_folder_id_from_course_id("ELEC3204-32989-16-17"))
except ValueError as e:
    print(e)
except IndexError as e:
    print(e)
