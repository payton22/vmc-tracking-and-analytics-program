def get_query():
    return "SELECT demographics.benefit_chapter, count(demographics.benefit_chapter) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id WHERE visits.check_in_date BETWEEN '%i' AND '%o' AND visits.location IN (%l) GROUP BY demographics.benefit_chapter;"
