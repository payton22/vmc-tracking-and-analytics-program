def get_query(from_time, to_time, substr):
    return "SELECT CASE cast (strftime('%w', check_in_date) AS INTEGER) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' ELSE 'Saturday' END AS Day, round(count(check_in_date)/(julianday('" + to_time\
        + "') - julianday('" + from_time \
        + "')), 2) FROM visits WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + from_time + \
           "' AND '" + to_time + "' GROUP BY strftime('%w',check_in_date);"