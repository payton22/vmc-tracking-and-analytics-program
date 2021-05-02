# Returns the SQL query for total visits by employment based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):

    return "SELECT demographics.employment, count(demographics.employment) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "and check_in_date <= \'" + to_time + "\' and demographics.employment is not null group by demographics.employment;"