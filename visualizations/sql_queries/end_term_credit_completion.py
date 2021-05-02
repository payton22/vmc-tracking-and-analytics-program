# Returns the SQL query for the total visits by end term completed credits based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):

    return "SELECT gpa.end_term_credit_completion, count(gpa.end_term_credit_completion) " \
           "FROM visits LEFT JOIN gpa ON visits.student_id = gpa.student_id " \
           "where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "and check_in_date <= \'" + to_time + "\' and gpa.end_term_credit_completion " \
            "is not null group by gpa.end_term_credit_completion;"