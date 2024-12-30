import json

# Load the courses data
with open('courses.json', 'r') as f:
    courses = json.load(f)

# Load the course details data
with open('course_details.json', 'r') as f:
    course_details = json.load(f)

# Create a dictionary for quick lookup of URLs by title
course_url_dict = {course['title']: course['url'] for course in courses}

# Update the course details with URLs
for detail in course_details:
    title = detail.get('title')
    if title in course_url_dict:
        detail['url'] = course_url_dict[title]

# Save the updated course details back to the file
with open('course_details.json', 'w') as f:
    json.dump(course_details, f, indent=4)

print("Course details updated with URLs.")