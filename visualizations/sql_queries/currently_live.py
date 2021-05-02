# Returns the SQL query for the total visits grouped by currently live based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):

    return "SELECT demographics.currently_live, count(demographics.currently_live) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "and check_in_date <= \'" + to_time + "\' and demographics.currently_live " \
                                                  "is not null group by demographics.currently_live;"