def get_query(group_by, from_time, to_time, substr):
    # No tables join -- only use the visits talbe
    if group_by == 'check_in_date' or group_by == 'location' or group_by == 'services':
        return "SELECT " + group_by + ", ROUND(COUNT(" + group_by + ") / (strftime('%m','" + to_time\
           + "') - strftime('%m', '" + from_time \
           + "')), 2) FROM visits WHERE check_in_date BETWEEN '" + from_time +\
           "' AND '" + to_time + "' GROUP BY " + group_by + ";"
        # Else, a table join with demographics + visits is needed
    else:
        return "SELECT IFNULL(demographics." + group_by + ", ''), ROUND(COUNT(demographics." + group_by + ") / (strftime('%m','" + to_time \
               + "') - strftime('%m', '" + from_time \
               + "')), 2) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id WHERE check_in_date BETWEEN '" + from_time + \
               "' AND '" + to_time + "' GROUP BY demographics." + group_by + ";"
