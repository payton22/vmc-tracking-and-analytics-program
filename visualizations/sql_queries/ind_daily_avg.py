def get_query(group_by, from_time, to_time, substr):
    # No tables join -- only use the visits talbe

    return "SELECT demographics." + group_by + ", round(count(demographics." + group_by + ")/(julianday('" + to_time + "') - julianday('" + from_time + "')), 2) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id WHERE (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' AND check_in_date <= \'" + to_time + "\' and demographics." + group_by + "is not null GROUP BY demographics." + group_by + ";"
