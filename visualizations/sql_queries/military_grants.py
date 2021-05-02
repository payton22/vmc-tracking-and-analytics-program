# Returns the SQL query for the total visits by military grants based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.military_grants, count(demographics.military_grants) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "AND check_in_date <= \'" + to_time + "\' and demographics.military_grants " \
                                                  "is not null GROUP BY demographics.military_grants;"