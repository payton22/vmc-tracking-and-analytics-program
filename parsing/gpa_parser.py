import csv

class GPAData:
    student_id = ''
    student_name = ''
    cum_gpa = ''
    term_gpa = ''
    term_credits = ''
    earned_credits = ''
    comp_percent = ''
    term = ''

    def __init__(self, row, term):
        self.student_id = row[0]
        self.student_name = row[1]
        self.cum_gpa = row[2]
        self.term_gpa = row[3]
        self.term_credits = row[4]
        self.earned_credits = row[5]
        self.comp_percent = row[6]
        self.term = term

    def get_insert_statement(self):
        insert_val_names = ['student_id','date','end_term_cumulative_gpa','end_term_term_gpa', 'end_term_attempted_credits', 'end_term_earned_credits', 'end_term_credit_completion'];
        insert_val_list = [self.student_id, self.term, self.cum_gpa, self.term_gpa, self.term_credits, self.earned_credits, self.comp_percent];
        insert_val_list = ['\"' + str(a) + '\"' for a in insert_val_list];

        return 'INSERT INTO gpa (' + ', '.join(insert_val_names) + ') VALUES (' + ', '.join(insert_val_list) + ');'

def remove_header(raw_data):
    term = ''
    for i in range(0,len(raw_data)):
        temp_str = raw_data[i][1]
        if temp_str != '':
            temp_str = temp_str.split(' ')
            if temp_str[0] == 'Term':
                temp_str = raw_data[i][1].split('(')
                term = temp_str[1].split(')')[0]
        if raw_data[i][0] == 'ID':
            return raw_data[i:],term

def parse_gpa(csvfile):
    reader = csv.reader(csvfile, delimiter=',')
    data = []
    for row in reader:
        data.append(row)
    data,term = remove_header(data)
    columns = data[0]
    data = data [1:]
    formatted = []
    for point in data:
        formatted.append(GPAData(point,term))
    return formatted

    

