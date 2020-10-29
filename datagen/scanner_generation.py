import csv
import random

#class for a visit
class Visit:
    def __init__(self, date, arrival_time, departure_time, barcode, is_appointment):
        self.date = date
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.barcode = barcode
        self.is_appointment = is_appointment

#class for a scan
class Scan:
    def __init__(self, date, time, barcode, event_type):
        self.date = date
        self.time = time
        self.barcode = barcode
        self.event_type = event_type

#generates a random barcode that is in the correct format a2123300#######a
def gen_barcode():
    return 'a' + '2123300' + str(random.randrange(1000000,9999999)) + 'a'

#generates a random duration for a visit in minutes, from 10-120
def gen_duration():
    return random.randrange(10,120)

#generates a visit starting at a given start time
def gen_visit(date, start_time):
    arrival_time = start_time
    duration = gen_duration()
    departure_time = add_time(arrival_time,duration)
    is_appointment = False
    #20% of visitors have no barcode and therefore no departure time
    #a departure time of 99:99 is used to indicate it is invalid
    if random.random() < 0.2:
        barcode = ''
        departure_time = 9999
    else:
        #30% of wolf card visits are appointments
        if random.random() < 0.3:
            is_appointment = True
        barcode = gen_barcode()

    return Visit(date,arrival_time,departure_time, barcode, is_appointment)

#adds n minutes to a given time
def add_time(time,minutes):
    n = 100
    if minutes < 60:
        if(time+minutes)%n < 60:
            return time+minutes
        else:
            diff = 60 - (time%n)
            return time + 100 - ((time+100)%n) + (minutes-diff)
    else:
        return add_time(time+100,minutes-60)

#returns time as a string
def time_str(time):
    time_str = str(time)
    if time < 1000:
        return '0' + time_str[0] + ':' + time_str[1] + time_str[2] + ':00'
    return time_str[0] + time_str[1] + ':' + time_str[2] + time_str[3] + ':00'
        

#given a date, randomly generates visits until the day is over
def gen_visits(date):
    start_time   = 800
    end_time     = 1700
    current_time = start_time
    visits = []
    while current_time < end_time:
        #generate a random number to see if a visitor arrives
        if random.random() < 0.033:
            visits.append(gen_visit(date,current_time))
        if current_time % 100 == 59:
            current_time += 40
        current_time += 1 
    return visits

#uses a list of visits to generate a list of scans sorted in chronological order
def gen_scan_list(visits):
    scans = []
    for visit in visits:
        if visit.is_appointment:
            arrival_event = 'app_arrival'
            departure_event = 'app_departure'
        else:
            arrival_event = 'arrival'
            departure_event = 'departure'
        scans.append(Scan(visit.date, visit.arrival_time, visit.barcode, arrival_event))
        scans.append(Scan(visit.date, visit.departure_time, visit.barcode, departure_event))
    scans.sort(key = lambda x: int(x.time))
    return list(filter(lambda x: x.time < 2400,scans))

#returns the scan information in a string formatted as a csv with the relevant data
def scan_str(scan):
    if scan.event_type == 'arrival':
        temp_str = 'VMCStudentSignIn'
    elif scan.event_type == 'app_arrival':
        temp_str = 'VMCAppointmentSignIn'
    elif scan.event_type == 'departure':
        temp_str = 'VMCStudentSignOut'
    else:
        temp_str = 'VMCAppointmentSignOut'
    if scan.barcode == '':
        temp_str = 'VMCNoIDSignIn'
        return scan.date + ',' + time_str(scan.time) + ',03,' + temp_str + '\n'
    str1 = scan.date + ',' + time_str(scan.time) + ',03,' + temp_str + '\n'
    str2 = scan.date + ',' + time_str(scan.time) + ',02,' + scan.barcode + '\n'
    return str1 + str2

#generates a days worth of scans for a given date and outputs it to a file

def gen_scan_file(output_filename,date):
    visits = gen_visits(date)
    scans = gen_scan_list(visits)
    output_str = ''
    for scan in scans:
        output_str += scan_str(scan)
    text_file = open(output_filename, "a+")
    text_file.write(output_str)

