import requests
import pprint

base_url = 'http://127.0.0.1:8000/api/'

# retrieve all courses
print(f'....All Subjects......')
r = requests.get(f"{base_url}subjects/")
courses = r.json()
courses = pprint.pformat(courses, indent=2)
print(courses)
