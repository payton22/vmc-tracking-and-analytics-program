# Returns the SQL query for break in attendance vs. gpa by date based on user-provided location, from date, and to date
def get_query(type, from_time, to_time, substr):
    return "SELECT demographics.break_in_attendance, round(avg(gpa." + type + "), 2) " \
           "FROM " \
           "(SELECT DISTINCT student_id FROM visits " \
           "WHERE (location = \'" + substr + "\') " \
           "AND check_in_date BETWEEN \'" + from_time + "\' AND \'" + to_time + "\') AS distinct_student_visits " \
           "LEFT JOIN demographics ON distinct_student_visits.student_id = demographics.student_id " \
           "LEFT JOIN gpa ON distinct_student_visits.student_id = gpa.student_id " \
           "WHERE demographics.break_in_attendance IS NOT NULL " \
           "GROUP BY demographics.break_in_attendance;"