# Returns the SQL query for the total visits by nevada prepaid tuition based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.nevada_prepaid, count(demographics.nevada_prepaid) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
           "AND check_in_date <= \'" + to_time + "\' and demographics.nevada_prepaid is not null GROUP BY demographics.nevada_prepaid;"