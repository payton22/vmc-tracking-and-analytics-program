# Returns the SQL query for the total visits by pell grant based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.pell_grant, count(demographics.pell_grant) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "AND check_in_date <= \'" + to_time + "\' and demographics.pell_grant " \
                                                  "is not null GROUP BY demographics.pell_grant;"