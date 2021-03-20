def get_query():
    return "SELECT IFNULL(demographics.benefit_chapter, ''), count(demographics.benefit_chapter) FROM visits LEFT JOIN demographics ON visits.student_id = demographics.student_id GROUP BY demographics.benefit_chapter;"
