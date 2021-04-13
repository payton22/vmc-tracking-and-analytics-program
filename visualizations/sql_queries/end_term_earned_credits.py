def get_query(from_time, to_time, substr):

    return "SELECT gpa.end_term_earned_credits, count(gpa.end_term_earned_credits) FROM visits LEFT JOIN gpa ON visits.student_id = gpa.student_id where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' and gpa.end_term_earned_credits is not null group by gpa.end_term_earned_credits;"