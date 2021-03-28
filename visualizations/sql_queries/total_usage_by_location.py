def get_query(from_time, to_time, substr):

    return "select  location, count(*) from visits where (location = \'" + substr + "\') and check_in_date >= \'" + from_time + "\' and check_in_date <= \'" + to_time + "\' group by location;"