# Yacc example

import ply.lex as lex

KEYWORDS = ['CREATE', 'TABLE', 'SELECT', 'FROM', 'JOIN', 'AS', 'ON', 'INSERT', 'INTO', 'VALUES', 'USING',
            'WITH', 'WHERE', 'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'UNION', 'ALL','OVERWRITE','PARTITION', 'AND',
            'IS', 'OR', 'NULL']

# List of token names.   This is always required
tokens = [
   'IDENTIFIER',
   'SPECIAL',
   'NUMBER',
   'EQUAL',
   'TERMINATOR',
   'STAR',
   'COMMA',
   'RP',
   'LP',
   'LITERAL',
   'ESCAPE'
] + KEYWORDS

# Keywords special
# t_JOIN = r'JOIN'
# t_FROM = r'FROM'
# t_CREATE = r'CREATE'
# t_TABLE = r'TABLE'
# t_SELECT = r'SELECT'
# t_AS = r'AS'
# t_ON = r'ON'

# Other
t_EQUAL = r'='
# t_SPECIAL = r'(<|>|\-|\+)'
t_SPECIAL = r'[<>\-\+\[\]%]'
t_NUMBER = r'(\d+\.\d+|\d+\.|\.\+d|\d+)'
t_TERMINATOR = r';'
t_STAR = r'\*'
t_COMMA = r','
t_LP = r'\('
t_RP = r'\)'
t_LITERAL = r'\'.*\''
t_ESCAPE = r'\\\\'


def t_IDENTIFIER(t):
    r'[_a-zA-Z\']+[._a-zA-Z0-9\']*\**'
    v = t.value
    if v.upper() in KEYWORDS:
        t.type = v.upper()
    else:
        t.type = 'IDENTIFIER'
    return t

t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# import ply.lex as lex
# lexer = lex.lex()


# useless_crap : IDENTIFIER IDENTIFIER

# table_list : FROM IDENTIFIER
#            | FROM IDENTIFIER join


# join : JOIN IDENTIFIER
#        | JOIN IDENTIFIER join
#        | JOIN IDENTIFIER useless_crap2



# select : SELECT table_list
'''
precedence = (
    ('right', 'LP'),
    ('left', 'RP'),
)
'''

alias = set()
tables = set()
def add_table(p, table):
    tables.add(table)

def p_query(p):
    '''query : select TERMINATOR
             | insert TERMINATOR
             | create TERMINATOR'''
    p[0] = p[1]

# Use of IDENTIFIER instead of the non-terminal 'table' because the following 'AS'
# made the gramer ambigous -- the token following AS was expected to be a table alias,
# but in this case, it was a select.
def p_create(p):
    ''' create : parent_table AS select
               | parent_table cte LP select RP select'''
    if p[2] == 'AS':
        p[0] = (p[1], p[3])
    else:
        p[0] = (p[1], p[4])

def p_parent_table(p):
    ''' parent_table : CREATE TABLE IDENTIFIER
                     | INSERT INTO IDENTIFIER
                     | INSERT OVERWRITE TABLE IDENTIFIER
                     | INSERT OVERWRITE TABLE IDENTIFIER PARTITION LP useless_crap RP'''
    if p[3] == 'TABLE':
        p[0] = p[4]
    else:
        p[0] = p[3]

def p_cte(p):
    ' cte : WITH IDENTIFIER AS '
    pass

def p_insert(p):
    ''' insert : parent_table LP useless_crap RP select
               | parent_table LP useless_crap RP VALUES LP useless_crap RP
               | parent_table select '''
    if p[2] != '(':
        p[0] = (p[1],p[2])
    else:
        if p[5] == 'VALUES':
            p[0] = (p[1], None)
        else:
            p[0] = (p[1],p[5])

def p_select(p):
    ''' select : SELECT useless_crap FROM from_clause post_from
               | SELECT useless_crap FROM from_clause
               | select union select '''


    # For union case
    if p[2] == 'UNION':
        p[0] = p[1].union( p[3] )

    # Tests for non-union case
    else:
        p[0] = p[4]


def p_union(p):
    ''' union : UNION
              | UNION ALL '''
    p[0] = 'UNION'

def p_post_from(p):
    ''' post_from : where_clause group_by_clause having_clause order_by_clause limit_clause '''
    pass


def p_where_clause(p):
    ''' where_clause : WHERE useless_crap
                     | empty '''
    pass

def p_group_by_clause(p):
    ''' group_by_clause : GROUP BY useless_crap
                        | empty '''
    pass

def p_having_clause(p):
    ''' having_clause : HAVING useless_crap
                      | empty '''
    pass

def p_order_by_clause(p):
    ''' order_by_clause : ORDER BY useless_crap
                        | empty '''
    pass

def p_limit_clause(p):
    ''' limit_clause : LIMIT useless_crap
                     | empty '''

def p_useless_crap(p):
    ''' useless_crap : single_item
                     | list_item '''
    pass
def p_sigle_item(p):
    ''' single_item :
                    | IDENTIFIER alias
                    | NUMBER alias
                    | func alias
                    | math_term alias
                    | IDENTIFIER
                    | STAR
                    | NUMBER
                    | func
                    | math_term
                    | expression
                    '''

"""
    I'm overloading a syntax that was meant for arguments to a function or a select list
    I don't know if I should do this... might be a mistake.
"""
def p_list_item(p):
    ''' list_item : single_item COMMA func alias
                  | single_item COMMA IDENTIFIER alias
                  | single_item COMMA NUMBER alias
                  | single_item COMMA STAR
                  | single_item COMMA func
                  | single_item COMMA IDENTIFIER
                  | single_item COMMA NUMBER
                  | expression AND expression
                  | expression OR expression
                  | list_item COMMA single_item
                  | list_item OR expression
                  | list_item AND expression
                  '''
    pass

def p_func(p):
    ''' func : IDENTIFIER LP something RP alias
             | LP something RP '''
    pass

def p_something(p):
    ''' something : IDENTIFIER
                  | NUMBER
                  | SPECIAL ESCAPE
                  | ESCAPE
                  | LITERAL
                  | something COMMA something
                  | math_term'''

def p_math_opperand(p):
    ''' math_opperand : IDENTIFIER
                      | NUMBER'''
def p_math_term(p):
    ''' math_term : math_opperand SPECIAL math_opperand
                  | math_opperand EQUAL math_opperand
                  | math_term STAR math_opperand
                  | math_term SPECIAL math_opperand
                  | LP math_term RP'''
    pass

# Nothing needs to be done here since we use the tables set to track
def p_from_clause(p):
    ''' from_clause : table
                    | table_list
                    | from_clause post_from'''
    p[0] = p[1]

def p_subquery(p):
    '''subquery : LP select RP'''
    p[0] = p[2]

def p_table_list(p):
    '''table_list : table join_type table ON expression
                  | table join_type table USING RP IDENTIFIER COMMA IDENTIFIER LP
                  | table_list join_type table ON expression
                  | table_list join_type table USING RP IDENTIFIER COMMA IDENTIFIER LP
                  | table_list join_type table'''

    p[0] = p[1].union(p[3])

def p_join_type(p):
    ''' join_type : JOIN
                  | IDENTIFIER JOIN 
                  | IDENTIFIER IDENTIFIER JOIN '''
    if p[1] == 'cross':
        p[0] = p[1]

#     elif p[1] in ['LEFT','RIGHT']:
#	p[0] = p[3]

def p_table(p):
    ''' table : subquery alias
              | IDENTIFIER alias
              | IDENTIFIER'''
    # If p[1] is already a set, a subquery is the input -- already a set.
    if isinstance(p[1], set):
        p[0] = p[1]
    else:
        # The IDENTIFIER case.
        p[0] = {p[1]}

def p_alias(p):
    '''alias : AS IDENTIFIER
             | IDENTIFIER'''
    pass

def p_expression(p):
    '''expression : IDENTIFIER EQUAL IDENTIFIER
                  | IDENTIFIER IS NULL
                  '''
    pass

def p_empty(p):
    ''' empty : '''
    pass

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")
    print(p)
