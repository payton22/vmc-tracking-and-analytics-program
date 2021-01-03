'''
import sqlite3
conn = sqlite3.connect('vmc_tap.db');

# Execute the query
conn.execute("DROP TABLE IF EXISTS test;");
conn.execute("CREATE TABLE test (col1 INTEGER);");
conn.execute("INSERT INTO test VALUES (1);");
conn.execute("INSERT INTO test VALUES (2);");
conn.execute("INSERT INTO test VALUES (3);");
result = conn.execute("SELECT * FROM test;");
conn.execute("DROP TABLE test;");

for r in result:
    print(r);
'''