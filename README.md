# qbiz-parser

Requires ply py module.

See insertTests.py and createTests.py for supported syntax.

returned value is a tuple containing a string and a set.  The string is the parent table name; the set contains all tables found in the query used to create/insert into the parent table, e.g. ('union_test', {'employee', 'manager', 'children'}).

Tasks:
 * Feature to read SQL from a file and feed to the compiler sequencely.
 * Interface w/ SQLAlchemy.
 * Stroage layer into any DB.
 * Generate a CSV from results.
 * Genereate AirFlow DAG from results.
