import csv
import random
import datetime
from copy import deepcopy
class Data:
    student_name = ''
    student_email = ''
    student_id = ''
    classification = ''
    major = ''
    services = ''
    location = ''
    check_in_date = ''
    check_in_time = ''
    check_out_date = ''
    check_out_time = ''
    check_in_duration = ''
    staff_name = ''
    staff_id = ''
    staff_email = ''
    tags = ''
    def toList(self):
        return [self.student_name,self.student_email, self.student_id, self.tags, self.classification, self.major, self.services, self.location, self.check_in_date, self.check_in_time, self.check_out_date, self.check_out_time, self.check_in_duration, self.staff_name, self.staff_id, self.staff_email]
    def __lt__(self,other):
        return self.check_in_time < other.check_in_time
    def __str__(self):
        div = '\",\"'
        return '\"'+self.student_name+div+self.student_email+div+self.student_id+div+self.student_alt_id+div+self.tags+div+self.classification+div+self.major+div+self.assigned_staff+div+self.care_unit+div+self.services+div+self.course_name+div+self.course_number+div+self.location+div+self.check_in_date+div+self.check_in_time+div+self.check_out_date+div+self.check_out_time+div+self.check_in_duration+div+self.staff_name+div+self.staff_id+div+self.staff_email+'\"'

def gen_new_name(name_list):
    new_name = random.choice(names) + ', ' + random.choice(names)
    if new_name in name_list:
        gen_new_name(name_list)
    else:
        return new_name

def gen_student_id():
    return str(random.randint(1000000000,9999999999))

def gen_string(a,b):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = random.randint(a,b)
    ret = ''
    for _ in range(length):
        ret  = ret + random.choice(characters)
    return ret

def get_first_last(name):
    l = name.split(', ')
    return l[1], l[0]

def gen_email(name):
    first,last = get_first_last(name)
    return first + last + '@nevada.unr.edu'

def gen_classification():
    return random.choice(classifications)

def gen_major():
    return random.choice(majors)

def gen_service():
    services = ['Veteran Services_VMC_VISIT', 'Veteran Services_VMC_Other', 'Veteran Services_FSSB_Current Student_Personal Support', 'Veteran Services_FSSB_Current Student_UNR Academic Q', 'Veteran Services_FSSB_Current Student_VA Benefits', 'Veteran Services_FSSB_New Student', 'Veteran Services_FSSB_Other']
    return random.choice(services)

def gen_location():
    locations = ['Veteran Services_VMC', 'Veteran Services_Fitzgerald', 'Event']
    return random.choice(locations)

def gen_time(date):
    hours = random.randint(8,17)
    minutes = random.randint(0,59)
    return date + datetime.timedelta(hours=hours,minutes=minutes)

def gen_visit(student,date):
    visit = deepcopy(student)
    
    check_in  = gen_time(date)
    check_in_duration  = random.randint(0,120)
    check_out = check_in + datetime.timedelta(minutes=check_in_duration)

    visit.check_in_date = date.strftime('%m/%d/%y')
    visit.check_out_date = date.strftime('%m/%d/%y')
    visit.check_in_time = check_in.strftime('%I:%M %p')
    visit.check_out_time = check_out.strftime('%I:%M %p')
    visit.check_in_duration = str(check_in_duration)
    visit.location = gen_location()
    visit.staff_name = gen_staff()
    visit.staff_id = gen_student_id()
    visit.staff_email = gen_email(visit.staff_name)
    visit.services = gen_service()
    return visit

def gen_staff_list():
    names = []
    for _ in range(10):
        names.append(gen_new_name(names))
    return names

def gen_staff():
    return random.choice(staff_list)

def gen_tags():
    ret = ''
    n = random.randint(0,3)
    for _ in range(n):
        ret = ret + random.choice(tags) + ','
    if n == 0:
        return ''
    else:
        return ret + random.choice(tags)


def gen_student(name):
    student = Data()
    student.student_name = name
    student.student_email = gen_email(name)
    student.student_id = gen_student_id()
    student.classification = gen_classification()
    student.major = gen_major()
    student.tags = gen_tags()
    return student

def gen_header(d1,d2):
    start_date = d1.strftime('%m/%d/%Y')
    end_date = d2.strftime('%m/%d/%Y')
    report_date = d2.strftime('%m/%d/%Y %I:%M %p')
    return ["University of Nevada, Reno", "Check-Ins", start_date + ' to ' + end_date, report_date, "John Pratt"]

names = open('datagen/names.txt').read().splitlines()
classifications = ['Senior (2020 Fall)', 'Freshman (2020 Fall)', 'Sophomore (2020 Fall)', 'Junior (2020 Fall)']
majors = ['Computer Sci and Engr BSCSE', 'Accounting', 'Accounting & IS', 'Agricultural Science', 'Anthropology', 'Art', 'Art History', 'Atmospheric Science', 'Biochemistry and Molecular Biology', 'Biomedical Engineering', 'Biotechnology', 'Business', 'Chemical Engineering', 'Chemistry', 'Civil and Environmental Engineering', 'Criminal Justice', 'Economics', 'Elementary Education', 'Electrical Engineering', 'Geography', 'Marketing', 'Mechanical Engineering', 'Music', 'Nursing' , 'Nutrition', 'Physics', 'Social Work', 'Spanish', 'Theatre']
staff_list = gen_staff_list() 

tags = []
for _ in range(40):
    tags.append(gen_string(4,16))


def gen_data(start):
    visits = []
    student_names = []
    for _ in range(60):
        student_names.append(gen_new_name(student_names))
    students = []
    for name in student_names:
        students.append(gen_student(name))
    
    for new_day in (start + datetime.timedelta(days=n) for n in range(30)):
        gen_visits(students,new_day,visits)
    return visits

def gen_visits(students,date,visits):
    for student in students:
        if random.randint(0,100) < 80:
            visits.append(gen_visit(student,date))

def gen_report(filename,date):
    date = datetime.datetime.strptime(date,'%m/%d/%Y')
    visits = gen_data(date)
    header = gen_header(date,date+datetime.timedelta(days=30))
    titles = ["Student Name", "Student E-mail", "Student ID", "Tags", "Classification", "Major", "Services", "Location", "Check In Date", "Check In Time", "Check Out Date", "Check Out Time", "Checked In Duration (In Min)", "Staff Name",  "Staff ID", "Staff E-mail"]
    csvfile = open(filename, 'a+')
    csvwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
    csvwriter.writerow(header)
    csvwriter.writerow("\n")
    csvwriter.writerow(titles)
    for visit in visits:
        csvwriter.writerow(visit.toList())
    csvfile.close()

d = datetime.datetime.strptime('1/4/2021','%m/%d/%Y')
student = gen_student(gen_new_name([]))
visit = gen_visit(student,d)
