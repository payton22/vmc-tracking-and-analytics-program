import sqlite3
import csv
import random
def get_students():
    conn = sqlite3.connect('vmc_tap.db')
    cur  = conn.cursor()
    cur.execute('select distinct student_id, student_name from visits')
    students = cur.fetchall()
    return students




def gen_gpa_data(filename):
    data = []
    students = get_students()
    for student in students:
        data.append(gen_gpa(student))
    csvfile = open(filename, 'a+')
    csvwriter = csv.writer(csvfile,delimiter=',')
    csvwriter.writerow(['ID','Name','End Term Cumulitive GPA', 'End Term GPA', 'End Term Attempted Credits', 'End Term Earned Credits', 'End Term % Credit Completion'])
    for point in data:
        csvwriter.writerow(point)
    csvfile.close()

def gen_gpa(student):
    student_id = student[0]
    student_name = student[1]
    cumm_gpa = (random.randint(0,20)+20)/10
    term_gpa = (random.randint(0,20)+20)/10
    term_credits = random.randint(10,18)
    earned_credits = random.randint(0,term_credits)
    comp_percent = (earned_credits/term_credits)*100
    return [student_id,student_name,cumm_gpa,term_gpa,term_credits,earned_credits,comp_percent]


