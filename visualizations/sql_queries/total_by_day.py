# Returns the SQL query for the total visits by day based on user-provided location, from date, and to date
# Referenced StackOverflow https://stackoverflow.com/questions/4319302/format-date-as-day-of-week
# Last visited 3/12/2021
def get_query(from_time, to_time, substr):
    return "SELECT CASE cast (strftime('%w', check_in_date) AS INTEGER) " \
           "WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' " \
           "WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' " \
           "ELSE 'Saturday' END AS Day, count(check_in_date) FROM visits " \
           "WHERE (location = '" + substr + "') and check_in_date " \
                                            "BETWEEN '" + from_time + "' AND '" + to_time + "' " \
                                            "GROUP BY strftime('%w',check_in_date);"