#!/usr/bin/env python3
import sys
import ply.lex as lex

KEYWORDS = ['hql']

# List of token names.   This is always required
tokens = [
   'EQUAL',
   'COMMA',
   'RP',
   'LP',
   'TRIPPLE',
   'IDENTIFIER',
   'SPECIAL',
   'MACRO',
   'TERMINATOR'
] + KEYWORDS

# Other
t_EQUAL = r'='
t_COMMA = r','
t_LP = r'\('
t_RP = r'\)'
t_TRIPPLE = r'(\'\'\'|\"\"\")'
t_SPECIAL = r'[%()\[\]\#^0-9$*-./\\<>@:]'
t_MACRO  = r'({{|}})'
t_TERMINATOR = r';'


def t_IDENTIFIER(t):
    r'[_a-zA-Z]+[._a-zA-Z0-9]*\**'
    v = t.value
    if v in KEYWORDS:
        t.type = v
    else:
        t.type = 'IDENTIFIER'
    return t

t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0], file=sys.stderr)
    t.lexer.skip(1)

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

lexer = lex.lex()


# parser = yacc.yacc()


inp =  sys.stdin.read()
lexer.input( inp )

def p_hql(p):
    '''hql : HQL EQUAL TRIPLE token_series TRIPLE'''
    p[0] = p[4]

def p_token_series(p):
    '''token_series : token_series IDENTIFIER
                    | IDENTIFIER'''
    if isinstance(p[1], list):
        p[0] = p[1].append(p[2])
    else:
        p[0] = list(p[1])

# import ply.yacc as yacc
# parser = yacc.yacc()
# print( parser.parse(inp) )

