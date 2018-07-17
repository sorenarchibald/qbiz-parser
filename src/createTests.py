
createTest1 = "CREATE TABLE temp_employee AS SELECT * FROM employee;"
createTest2 = "CREATE TABLE temp_employee AS SELECT * FROM employee e join manager m on m.id = e.manager_id;"
createTest3 = """
CREATE TABLE pivot_scores
WITH some_alias AS (
        select a.*, b.scores,
            substr(b.scores,((c.id-1)
            *3)
            +1, 2) as score
        from person a  join tests b on a.id = b.name_id cross join seq c
)
SELECT * FROM some_alias;
"""

createTest4 = """CREATE TABLE salary_by_manager
                 AS SELECT  m.name, sum(e.salary) as net_pay
                 FROM employee e join
                      manager m on m.id = e.manager_id
                 WHERE e.active = 1
                 group by m.name_id
                 order by net_pay; """

createTest5 = """ CREATE TABLE union_test
                 AS SELECT  m.name
                 FROM employee e join
                      manager m on m.id = e.manager_id
                 WHERE e.active = 1
                 UNION
                 select name from children
                 group by name;"""

# Build the parser
from sql_yacc import *

import ply.lex as lex
lexer = lex.lex()

import ply.yacc as yacc
parser = yacc.yacc()

dval = False
result = parser.parse(createTest1, debug=dval)
assert result == ('temp_employee', {'employee'})
tables.clear()
print("Pass 1")

result = parser.parse(createTest2, debug=dval)
assert result == ('temp_employee', {'employee','manager'})
tables.clear()
print("Pass 2")

result = parser.parse(createTest3, debug=dval)
assert result == ('pivot_scores', {'person','tests','seq'})
tables.clear()
print("Pass 3")

result = parser.parse(createTest4, debug=dval)
assert result == ('salary_by_manager', {'employee','manager'})
tables.clear()
print("Pass 4")

result = parser.parse(createTest5, debug=dval)
assert result == ('union_test', {'employee','manager', 'children'})
tables.clear()
print("Pass 5")

print("Pass all")
