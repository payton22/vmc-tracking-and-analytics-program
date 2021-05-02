# Returns the SQL query for the total visits (ind. statistic) visits by date based on user-provided location, from date, and to date
def get_query(group_by, from_time, to_time, substr):
    # No tables join -- only use the visits table
    if group_by == 'check_in_date' or group_by == 'location' or group_by == 'services':
        return "select " + group_by + ", count(" + group_by + ") from visits where (location = \'" + substr + "\') " \
                "and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' group by " + \
                group_by + ";"
    elif group_by == 'end_term_term_gpa' or group_by == 'end_term_earned_credits' or group_by == 'end_term_cumulative_gpa' \
            or group_by == 'end_term_attempted_credits' or group_by == 'end_term_credit_completion':
        return "select IFNULL(gpa." + group_by + ", ''), count(gpa." + group_by + ") from visits LEFT JOIN gpa ON visits.student_id = gpa.student_id " \
                    "where (location = \'" + substr + "\') " \
                    "and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' group by gpa." + \
               group_by + ";"
    # Else, a table join with demographics + visits is needed
    else:
        return "select IFNULL(demographics." + group_by + ", ''), count(demographics." + group_by + ") from visits LEFT JOIN demographics ON visits.student_id = demographics.student_id " \
                "where (location = \'" + substr + "\') " \
                "and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' group by demographics." + \
                group_by + ";"
