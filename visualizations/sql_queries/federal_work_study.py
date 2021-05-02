# Returns the SQL query for the total visits by federal work study based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT demographics.federal_work_study, count(demographics.federal_work_study) " \
           "FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
           "WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
        "AND check_in_date <= \'" + to_time + "\' and demographics.federal_work_study " \
                                              "is not null GROUP BY demographics.federal_work_study;"