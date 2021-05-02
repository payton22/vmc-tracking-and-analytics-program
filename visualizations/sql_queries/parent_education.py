# Returns the SQL query for the total visits by parent education based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):

    return "SELECT demographics.parent_education, count(demographics.parent_education) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
           "and check_in_date <= \'" + to_time + "\' and demographics.parent_education " \
                                                 "is not null group by demographics.parent_education;"