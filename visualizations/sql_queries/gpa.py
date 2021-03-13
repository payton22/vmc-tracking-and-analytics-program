def get_query():
    return "select major, count(major) from demographics GROUP BY major;"
