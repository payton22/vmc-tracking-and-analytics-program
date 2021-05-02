# Returns the SQL query for total visits by year based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):
    return "SELECT SUBSTR(check_in_date,1,4), COUNT(check_in_date) FROM visits " \
           "WHERE (location = '" + substr + "') and check_in_date BETWEEN '" + from_time + "' " \
            "AND '" + to_time + "' GROUP BY SUBSTR(check_in_date,1,4);"