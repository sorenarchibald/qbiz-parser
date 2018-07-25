# qbiz-parser

Requires ply py module be installed for python.

I have defined the lexical analyzer and gramer in sql_yacc.py
To use create your own application, you must include these three statments:

from sql_yacc import * # to import all symbols defined.
import ply.lex as lex
lexer = lex.lex()
import ply.yacc as yacc
parser = yacc.yacc()
result = parser.parse(statement)


See insertTests.py and createTests.py for supported syntax.

returned value is a tuple containing a string and a set.  The string is the parent table name; the set contains all tables found in the query used to create/insert into the parent table, e.g. ('union_test', {'employee', 'manager', 'children'}).

Tasks:
 * Feature to read SQL from a file and feed to the compiler sequencely.
 * Interface w/ SQLAlchemy.
 * Stroage layer into any DB.
 * Generate a CSV from results.
 * Genereate AirFlow DAG from results.

## Fauzia's questions

1. What are terminal and non-terminal tokens and how are they identified.
    * Eg: 
     * Query1) SELECT * from table1 Where t1=t2 : SELECT terminal here?
     * Query2) CREATE TABLE table2 AS SELECT * from table1 where t1=t2 : SELECT not terminal here?
    * How to distinguish between them.
1. Slide 4 has the below lines:
```
   query : parent_table AS select
   p[0] = (p[1], p[3])--What is p[0] here?
   
   parent_table : CREATE TABLE IDENTIFIER
   p[0] = p[3] --Not sure about this too. What will be p[3] the select query table within the create table?
```

## Soren's Answers
1. Terminals are really the same as tokens.  When talking about parsing, the objects are described as tokens, but in the context of a grammar, a different terminology is used.  Terminals are single tokens, such as FROM, WHERE and SELECT; non-terminals are a sequence of tokens, such as IDENTIFIER COMMA IDENTIFIER COMMA IDENTIFIER or just IDENTIFIER, this example could represent the variable length list of column names, in a select statement.  Compilers use a finite state machine; a grammar can be represented as a network of states (nodes) -- maybe look at the illustrations on Wikipedia.  Terminals are flags that signal the end of a series of non-terminals -- such as the variable length of a column list in the select-clause, or variable length of a table list in the from-clause, or variable length of boolean terms in the where-clause.  Non-terminals can be recursive, such as column_list : IDENTIFIER | column_list COMMA IDENTIFIER.  Read the previous statement as column_list is a IDENTIFIER or a column_list followed by a column_list then a COMMA then a IDENTIFIER.

Now to your examples.  Terminals and non-terminals are part of a grammar and we could use many different grammars to describe a SQL queries (let's not get distracted here) but let's say I choose to define the following grammar to describe SQL:

```
query : SELECT column_list FROM table_list WHERE boolean_list SEMI_COLON
         | SELECT column_list FROM table_list SEMI_COLON
```

In the above, all lower case words are non-terminals; all upper-case words are terminals.  I define two possible syntax rules for a query -- one with a where-clause and one without.   Reading from left to right, if the compiler doesn't find a SELECT as the first token, it will throw a syntax error.  Provided the SQL is well formed, as the compiler processes the table_list, it's on the lookout for either a WHERE or a SEMI_COLON, which will flag the end of the list and begin a new state and a new set of rules or terminate.  Given your SQL statements and the grammar I've defined, SELECT is a TERMINAL in both statements.

1. With each grammar rule, there is an action associated with it.  The equation, or a more complicated series of statements, describe how to process the series of tokens.  The p[0] is the result; the other p-values are positional indices.  Imagine the series of tokens as a list.  Grammar rules are going to delete some number of elements and replace them with a new element -- know as a reduce operation (action).  Using the second SQL statement, my list (in python) would look like:
```
['CREATE', 'TABLE', 'table2', 'AS', 'SELECT', '*', 'from', 'table1', 'where', 't1=t2']
```
You must think of these elements as objects, with types and values.  The CREATE element is of type CREATE and has a value of CREATE  -- yes, it's redundant -- but the table2 element is of type IDENTIFIER and has value table2.  If my grammar and action are defined as:
```
parent_table : CREATE TABLE IDENTIFIER
p[0] = p[3]
```
While processing the list from left-to-right, the compiler recognizes the first three elements in the list match the rule and so reduces the list by following the action defined -- replace these three objects with a new one and set its value to the value of the third object.  The list now becomes:
```
[parent_table, 'AS', 'SELECT', '*', 'from', 'table1', 'where', 't1=t2']
```
Here, parent_table is an object of type parent_table and has a value of table2.  The action says take the value of the third element in the list and assign it as the value of the object parent_type. But the parent_type rule isn't the top rule.  The top rule looks something like:
```
statement : parent_table AS select
 p[0] = (p[1], p[3])
```
After all the other grammar rules for select are applied, I'll be left with a list which looks like this:
```
[parent_table, AS, select]
```
Again, these  are objects, with types [parent_table, AS, select] with values ['table2', 'AS', 'table1'].  The action says this construct is reduced to a tuple, (p[1], p[3]) which evaluates to ('table2', 'table1').  Since this is the end of my statement, this value is returned by the compiler.  I actually use sets to maintain the table_list so we don't get duplicates, so values returned by the compiler will really look like ('table2', {'table1'}).    

In summary, I had a class in compilers but it has been a very long time since graduate school.  Consequently, I had to relearn the subject in addition to how this python module works, which resulted in some trial-and-error and a grammar that I know can be improved and simplified, given that all we want a few choice elements.  But, it's working now, for the cases I've tested.  The grammar can be improved at a later date, perhaps as we need to fix it to support more cases.  I actually think the compiler will need to be rewritten to not only return a tuple of parent-child tables, but the associated SQL statements that AirFlow will need as well.  Maybe the children should not be returned as a set, but as dictionary, where the key is the child table and the value is a list of SQL statements.
