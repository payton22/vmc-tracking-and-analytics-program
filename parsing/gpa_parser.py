import csv

class GPAData:
    student_id = ''
    student_name = ''
    cum_gpa = ''
    term_gpa = ''
    term_credits = ''
    earned_credits = ''
    comp_percent = ''

    def __init__(self, row):
        self.student_id = row[0]
        self.student_name = row[1]
        self.cum_gpa = row[2]
        self.term_gpa = row[3]
        self.term_credits = row[4]
        self.earned_credits = row[5]
        self.comp_percent = row[6]


def remove_header(raw_data):
    for i in range(0,len(raw_data)):
        if raw_data[i][0] == 'ID':
            return raw_data[i:]

def parse_gpa(csvfile):
    reader = csv.reader(csvfile, delimiter=',')
    data = []
    for row in reader:
        data.append(row)
    data = remove_header(data)
    columns = data[0]
    data = data [1:]
    formatted = []
    for point in data:
        formatted.append(GPAData(point))
    return formatted

    

