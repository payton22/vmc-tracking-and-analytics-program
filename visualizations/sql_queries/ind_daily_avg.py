def get_query(group_by, from_time, to_time, substr):
    # No tables join -- only use the visits talbe
    if group_by == 'total_usage_by_location':
        return "SELECT location, round(count(*)/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits  WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' GROUP BY location;"
    elif group_by == 'usage_by_date':
        return "SELECT check_in_date, round(count(*)/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits  WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' GROUP BY check_in_date;"
    elif group_by == 'services':
        return "SELECT services, round(count(*)/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits  WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' GROUP BY services;"
    elif group_by == 'end_term_term_gpa' or group_by == 'end_term_earned_credits' or group_by == 'end_term_cumulative_gpa' or group_by == 'end_term_attempted_credits' or group_by == 'end_term_credit_completion':
        return "SELECT gpa." + group_by + ", round(count(gpa." + group_by + ")/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits LEFT JOIN gpa ON visits.student_id = gpa.student_id WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' and gpa." + group_by + " is not null GROUP BY gpa." + group_by + "; "
    else:
        return "SELECT demographics." + group_by + ", round(count(demographics." + group_by + ")/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' and demographics." + group_by + " is not null GROUP BY demographics." + group_by + "; "
