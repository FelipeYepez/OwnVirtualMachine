import ply.lex as lex
import ply.yacc as yacc
import pandas as pd

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
        print("   Invalid character: {", t.value[0], "} in line", 
                  t.lineno, " at position ", t.lexpos)
        t.lexer.skip(1)

    # Build the lexer
    return lex.lex()



#####################################################
# Parser
#####################################################
def PatitoParser():
    var_table = {}

    # Define CFG (Context free Grammars) from Patito Language
    def p_program(p):
        'program : PROGRAM ID SEMICOLON r body END'
        df_var_table = pd.DataFrame.from_dict(var_table, orient='index', columns=['Type'])
        df_var_table.index.name = 'Variable'
        print(df_var_table)

    def p_r(p):
        '''r : vars
             | empty'''


    def p_vars(p):
        'vars : VAR o'
    
    def p_o(p):
        'o : s p'

    def p_s(p):
        's : ID'
        var_id = p[1]
        if var_id not in var_table:
            var_table[var_id] = None
        else:
            print("Error in line", p.lineno(1), ": Variable {", var_id, "} already exists.")

    def p_p(p):
        '''p : COMA o
             | COLON type SEMICOLON q'''
        
    def p_q(p):
        '''q : empty
             | o'''
        # print("pq", var_types)


    def p_body(p):
        'body : LEFTBRACE m RIGHTBRACE'

    def p_m(p):
        '''m : statement m
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
        'condition : IF LEFTPARENTHESIS expression RIGHTPARENTHESIS body l SEMICOLON'
    
    def p_l(p):
        '''l : empty
             | ELSE body'''


    def p_expression(p):
        'expression : exp j'
    
    def p_j(p):
        '''j : empty
             | k exp'''
        
    def p_k(p):
        '''k : GREATERTHAN
             | LESSTHAN
             | NOT'''


    def p_print(p):
        'print : COUT LEFTPARENTHESIS g RIGHTPARENTHESIS SEMICOLON'
        
    def p_g(p):
        'g : h i'
    
    def p_h(p):
        '''h : expression
             | CTE_STRING'''

    def p_i(p):
        '''i : empty
             | COMA g'''


    def p_exp(p):
        'exp : term e'

    def p_e(p):
        '''e : empty
             | f term'''
    
    def p_f(p):
        '''f : ADD
             | MINUS'''


    def p_term(p):
        'term : factor c'
    
    def p_c(p):
        '''c : empty
             | d term'''
    
    def p_d(p):
        '''d : MULTIPLY
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
        var_type = p[1]
        for key in var_table:
            if var_table[key] is None:
                var_table[key] = var_type


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
        if p:
            print("    Expected token before {", p.value, "} in line", 
                  p.lineno, " at position ", p.lexpos)

    return yacc.yacc(start='program')



#####################################################
# Test Lexer
#####################################################
def test_lexer(data):
    # Create Lexer
    lexer = PatitoLexer()
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        # Print detected tokens
        # print(tok.type, " | ", tok.value)


#####################################################
# Test Parser
#####################################################
def test_parser(data):
    # Create Parser
    parser = PatitoParser()
    parser.parse(data)



#####################################################
# Test cases for the Lexer and Parser
#####################################################
def test_cases():
    with open("test_lexer_invalido.txt", "r") as file:
        data = file.read()
        print("Testing invalid lexer file...")
        test_lexer(data)
        print("\n\n")
    with open("test_lexer_valido.txt", "r") as file:
        data = file.read()
        print("Testing valid lexer file...")
        test_lexer(data)
        print("\n\n")
    with open("test_parser_invalido.txt", "r") as file:
        data = file.read()
        print("Testing invalid parser file...")
        test_parser(data)
        print("\n\n")
    with open("test_parser_valido.txt", "r") as file:
        data = file.read()
        print("Testing valid parser file...")
        test_parser(data)
        print("\n\n")

# Excecute test cases
test_cases()
