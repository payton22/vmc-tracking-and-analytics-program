import csv
from datetime import datetime
from enum import Enum

time_format = '%m/%d/%y %H:%M:%S'

class Event(Enum):
    fitzgerald = 0
    pennington = 1
    event      = 2

class Visit:
    def __init__(self, arrival_time, barcode, event, is_appointment):
        self.arrival_time   = arrival_time
        self.barcode        = barcode
        self.event          = event
        self.is_appointment = is_appointment
        self.sql_args = [None]*6
    def no_departure(self):
        self.departure_time = 'NO DEPARTURE'
        self.duration = 0
    def add_departure(self, departure_time):
        self.departure_time = departure_time
        self.duration       = (datetime.strptime(departure_time, time_format) - datetime.strptime(self.arrival_time, time_format)).total_seconds() / 60
    def get_insert_statement(self):
        self.sql_args = [self.arrival_time, self.departure_time, self.duration, self.barcode, self.event, self.is_appointment]
        return 'INSERT INTO visits VALUES (' + ', '.join(['\'' + str(a) + '\'' for a in self.sql_args]) + ');'

    def __str__(self):
        return "Barcode: " + self.barcode + ' Appointment?: ' + str(self.is_appointment) + ' SignIn: ' + self.arrival_time + ' SignOut: ' + self.departure_time + ' Duration: ' + str(self.duration) + ' mins'

time_index      = 0
scan_type_index = 1
barcode_index   = 2

def format_time(raw_data):
    return list(map(lambda x: [(x[0] + ' ' + x[1]),x[2],x[3]],raw_data))

def parse_scanner_data(csvfile):
    csvreader = csv.reader(csvfile,delimiter=',')
    raw_data = []
    for row in csvreader:
        raw_data.append(row)

    raw_data = format_time(raw_data)

    visits  = []
    for i in range(0,len(raw_data)):
        parse_scan(raw_data,i,visits)

    return visits


def parse_scan(data,scan_index,visits):
    scan = data[scan_index]
    #if the scan is a wolfcard, check the previous scan to see if it is a scan in or out
    if scan[scan_type_index] == '02':
        #if it is a sign in, add a new visit to the visits list
        if data[scan_index-1][barcode_index] == 'VMCStudentSignIn':
            new_visit = Visit(scan[time_index],scan[barcode_index],Event.fitzgerald,False)
            visits.append(new_visit)
        #if it is a sign out, search the visits list for the sign in of this barcode and add
        #a departure time to it
        if data[scan_index-1][barcode_index] == 'VMCStudentSignOut' or data[scan_index-1][barcode_index] == 'VMCAppointmentSignOut':
            departure_time = scan[time_index]
            index = search_visits(visits,scan[barcode_index])
            visits[index].add_departure(departure_time)
        #if it is an appointment sign in, add a new visit to the visits list with the appointment flag tagged
        if data[scan_index-1][barcode_index] == 'VMCAppointmentSignIn':
            new_visit = Visit(scan[time_index],scan[barcode_index],Event.fitzgerald,True)
            visits.append(new_visit)
    #if the scan is not a wolfcard, check if the code is a NoIDSignIn
    if scan[barcode_index] == 'VMCNoIDSignIn':
        new_visit = Visit(scan[time_index],'NOID',Event.fitzgerald,False)
        new_visit.no_departure()
        visits.append(new_visit)


#search for the most recent visit with the associated barcode
def search_visits(visits,barcode):
    for i in range(len(visits)-1,-1,-1):
        if visits[i].barcode == barcode:
            return i
    return False
