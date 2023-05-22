import ply.lex as lex
import ply.yacc as yacc

# List of reserved words used by 'Patito' language
reserved = {
    'program' : 'PROGRAM',
    'end' : 'END',
    'var' : 'VAR',
    'int' : 'INT',
    'float' : 'FLOAT',
    'cout' : 'COUT',
    'if' : 'IF',
    'else' : 'ELSE',
    'do' : 'DO',
    'while' : 'WHILE',
}

# Tokens from 'Patito' language to be used for the lexer
# This tokens are also used by yacc to identify terminals
tokens = [
    'ID',
    'CTE_STRING',
    'CTE_INT',
    'CTE_FLOAT',
    'LEFTPARENTHESIS',
    'RIGHTPARENTHESIS',
    'LEFTBRACE',
    'RIGHTBRACE',
    'COLON',
    'COMA',
    'SEMICOLON',
    'EQUAL',
    'ADD',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'GREATERTHAN',
    'LESSTHAN',
    'NOT',
] + list(reserved.values())


#####################################################
# Lexer
#####################################################
def PatitoLexer():
    # Specify tokens by writing their regular expression
    t_LEFTPARENTHESIS = r'\('
    t_RIGHTPARENTHESIS = r'\)'
    t_LEFTBRACE = r'\{'
    t_RIGHTBRACE = r'\}'
    t_COLON = r'\:'
    t_COMA = r'\,'
    t_SEMICOLON = r'\;'
    t_EQUAL = r'\='
    t_ADD = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_GREATERTHAN = r'\>'
    t_LESSTHAN = r'\<'
    t_NOT = r'\!\='

    # Regular expression for tokens with action code needed
    def t_ID(t):
        r'[a-zA-Z][a-zA-Z0-9]*'
        t.type = reserved.get(t.value,'ID')    # Check for reserved words
        return t


    def t_CTE_STRING(t):
        # r'\"[a-zA-Z0-9]*\"'
        r'\".*?\"'
        # Delete " "
        t.value = t.value[1:-1]
        return t


    def t_CTE_FLOAT(t):
        r'[0-9]+\.[0-9]+'
        t.value = float(t.value)
        return t


    def t_CTE_INT(t):
        r'[0-9]+'
        t.value = int(t.value)
        return t


    # Rule to track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Ignore spaces and tabs
    t_ignore  = ' \t'

    # Lexer error handling rule
    def t_error(t):
        print("   Invalid character: ", t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    return lex.lex()



#####################################################
# Parser
#####################################################
def PatitoParser():
    # Define CFG (Context free Grammars) from Patito Language
    def p_program(p):
        '''program : PROGRAM ID SEMICOLON r body END
        r       : vars
                | empty'''


    def p_vars(p):
        '''vars : VAR o
        o    : ID p
        p    : COMA o
                | COLON type SEMICOLON q
        q    : empty
                | o'''


    def p_body(p):
        '''body : LEFTBRACE m RIGHTBRACE
        m    : statement m
                | empty'''


    def p_statement(p):
        '''statement : assign
                    | condition
                    | cycle
                    | print'''


    def p_assign(p):
        'assign : ID EQUAL expression SEMICOLON'


    def p_cycle(p):
        'cycle : DO body WHILE LEFTPARENTHESIS expression RIGHTPARENTHESIS SEMICOLON'


    def p_condition(p):
        '''condition : IF LEFTPARENTHESIS expression RIGHTPARENTHESIS body l SEMICOLON
        l         : empty
                    | ELSE body'''


    def p_expression(p):
        '''expression : exp j
        j          : empty
                    | k exp
        k          : GREATERTHAN
                    | LESSTHAN
                    | NOT'''


    def p_print(p):
        '''print : COUT LEFTPARENTHESIS g RIGHTPARENTHESIS SEMICOLON
        g     : h i
        h     : expression
                | CTE_STRING
        i     : empty
                | COMA g'''


    def p_exp(p):
        '''exp : term e
        e   : empty
            | f term
        f   : ADD
            | MINUS'''


    def p_term(p):
        '''term : factor c
        c    : empty
                | d term
        d    : MULTIPLY
                | DIVIDE'''


    def p_factor(p):
        '''factor : LEFTPARENTHESIS expression RIGHTPARENTHESIS
                | a b
        a      : empty
                | ADD
                | MINUS
        b      : ID
                | cte'''


    def p_type(p):
        '''type : INT
                | FLOAT'''


    def p_cte(p):
        '''cte : CTE_INT
            | CTE_FLOAT'''


    # Define the p_empty rule that does nothing
    def p_empty(p):
        'empty :'
        pass


    # Error rule for syntax errors
    def p_error(p):
        print("  Syntax error in input")

    return yacc.yacc(start='program')



#####################################################
# Test Lexer
#####################################################
def test_lexer(lexer, data):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        # print(tok.type, tok.value)


#####################################################
# Test Parser
#####################################################
def test_parser(parser, data):
    parser.parse(data)


# Create Lexer and Parser
lexer = PatitoLexer()
parser = PatitoParser()

def test_cases():
    with open("test_lexer_invalido.txt", "r") as file:
        data = file.read()
        print("Testing incorrect lexer...")
        test_lexer(lexer, data)
        print("\n\n")
    with open("test_lexer_valido.txt", "r") as file:
        data = file.read()
        print("Testing correct lexer...")
        test_lexer(lexer, data)
        print("\n\n")
    with open("test_parser_valido.txt", "r") as file:
        data = file.read()
        print("Testing correct parser...")
        test_parser(parser, data)
        print("\n\n")
    with open("test_parser_invalido.txt", "r") as file:
        data = file.read()
        print("Testing incorrect parser...")
        test_parser(parser, data)
        print("\n\n")


test_cases()
