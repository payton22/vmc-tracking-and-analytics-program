def get_query(from_time, to_time, substr):

    return "SELECT IFNULL(demographics.break_in_attendance, ''), count(demographics.break_in_attendance) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' group by demographics.break_in_attendance;"