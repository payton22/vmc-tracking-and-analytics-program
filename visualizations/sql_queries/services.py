# Returns the SQL query for services based on user-provided location, from date, and to date
def get_query(from_time, to_time, substr):

    return "select  services, count(*) from visits " \
           "where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' " \
            "and check_in_date <= \'" + to_time + "\' group by services;"