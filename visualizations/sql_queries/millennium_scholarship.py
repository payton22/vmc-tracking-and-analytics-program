# Returns the SQL query for the total visits by millennium scholarship based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.millennium_scholarship, count(demographics.millennium_scholarship) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
         "AND check_in_date <= \'" + to_time + "\' and demographics.millennium_scholarship " \
                                               "is not null GROUP BY demographics.millennium_scholarship;"