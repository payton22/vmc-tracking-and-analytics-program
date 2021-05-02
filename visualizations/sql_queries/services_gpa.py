# Returns the SQL query for the services vs. gpa based on user-provided location, from date, and to date
def get_query(type, from_time, to_time, substr):
    return "SELECT visits.services, round(avg(gpa." + type + "), 2) " \
           "FROM " \
           "(SELECT DISTINCT student_id FROM visits " \
           "WHERE (location = \'" + substr + "\') " \
           "AND check_in_date BETWEEN \'" + from_time + "\' AND \'" + to_time + "\') AS distinct_student_visits " \
           "LEFT JOIN gpa ON distinct_student_visits.student_id = gpa.student_id " \
           "WHERE visits.services IS NOT NULL " \
           "GROUP BY visits.services;"