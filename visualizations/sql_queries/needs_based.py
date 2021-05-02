# Returns the SQL query for the total visits by needs-based grants based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.needs_based, count(demographics.needs_based) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "AND check_in_date <= \'" + to_time + "\' and demographics.needs_based " \
                                                  "is not null GROUP BY demographics.needs_based;"