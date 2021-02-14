import csv
from datetime import datetime


class Data:
    student_name = ''
    student_email = ''
    student_id = ''
    #student_alt_id = ''
    classification = ''
    major = ''
    #assigned_staff = ''
    #care_unit = ''
    services = ''
    #course_name = ''
    #course_number = ''
    location = ''
    check_in_date = ''
    check_in_time = ''
    check_out_date = ''
    check_out_time = ''
    duration = ''
    #staff_name = ''
    #staff_id = ''
    #staff_email = ''

    def get_insert_statement(self):
        insert_val_list = [self.student_name, self.student_email, self.student_id, self.services, self.location,
        datetime.strptime(self.check_in_date, '%m/%d/%y').strftime('%Y-%m-%d'), self.check_in_time,
        datetime.strptime(self.check_out_date, '%m/%d/%y').strftime('%Y-%m-%d'), self.check_out_time, self.duration]
        input_val_string = ''
        for i in insert_val_list:
            input_val_string = input_val_string + '\'' + i + '\','
        input_val_string = input_val_string[:-1]
        return 'insert into visits values (' + input_val_string + ');'


class Tag:
    student_id = ''
    tag = ''
    date = ''


def raw_data(csvfile):
    reader = csv.reader(csvfile, delimiter=',')
    data = []
    for row in reader:
        data.append(row)
    return data

def parse_report(csvfile):
    data = raw_data(csvfile)
    formatted = []
    tags = []
    staff = []
    titles = data[2]
    data = data[3:]
    for point in data:
        if point:
            formatted.append(format_data(titles, point))
            format_tag(titles, point, tags)
    return formatted, tags

def format_tag(titles, raw, tags):
    tag_list = raw[titles.index('Tags')].split(',')
    student_id = raw[titles.index('Student ID')]
    if not tag_list[0]:
        return
    for tag in tag_list:
        new_tag = Tag()
        new_tag.student_id = student_id
        new_tag.tag = tag
        tags.append(new_tag)

def format_data(titles, raw):
    if not raw:
        return
    data = Data()
    data.student_name = raw[titles.index('Student Name')]
    data.student_email = raw[titles.index('Student E-mail')]
    data.student_id = raw[titles.index('Student ID')]
    data.classification = raw[titles.index('Classification')]
    data.major = raw[titles.index('Major')]
    data.services = raw[titles.index('Services')]
    data.location = raw[titles.index('Location')]
    data.check_in_date = raw[titles.index('Check In Date')]
    data.check_in_time = raw[titles.index('Check In Time')]
    data.check_out_date = raw[titles.index('Check Out Date')]
    data.check_out_time = raw[titles.index('Check Out Time')]
    data.duration = raw[titles.index('Checked In Duration (In Min)')]
    data.staff_name = raw[titles.index('Staff Name')]
    data.staff_id = raw[titles.index('Staff ID')]
    data.staff_email = raw[titles.index('Staff E-mail')]
    return data
