from Scanner_Parser_Patito import PatitoLexer, PatitoParser

#####################################################
# Test Lexer
#####################################################
def test_lexer(data, print_tokens=False):
    # Create Lexer
    lexer = PatitoLexer()
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        if print_tokens:
            # Print detected tokens
            div = '.' * (20 - len(tok.type))
            print(tok.type, div, tok.value)


#####################################################
# Test Parser
#####################################################
def test_parser(data):
    # Create Parser
    parser = PatitoParser(True, quads = [], var_table= {}, cte_table={})
    # Parse input
    try:
        parser.parse(data)
    except Exception as e:
        print('Parsing error: ', e)


#####################################################
# Test cases for the Lexer and Parser
#####################################################
def test_cases():
    with open('test_lexer_invalido.txt', 'r') as file:
        data = file.read()
        print('Testing invalid lexer file...')
        test_lexer(data)
        print('\n\n')
    with open('test_lexer_valido.txt', 'r') as file:
        data = file.read()
        print('Testing valid lexer file...')
        test_lexer(data, print_tokens=True)
        print('\n\n')
    with open('test_parser_invalido.txt', 'r') as file:
        data = file.read()
        print('Testing invalid parser file...')
        test_parser(data)
        print('\n\n')
    with open('test_parser_valido.txt', 'r') as file:
        data = file.read()
        print('Testing valid parser file...')
        test_parser(data)
        print('\n\n')
    with open('test_quadruples.txt', 'r') as file:
        data = file.read()
        print('Testing quadruples file...')
        test_parser(data)
        print('\n\n')
    with open('test_elseif.txt', 'r') as file:
        data = file.read()
        print('Testing ELSEIF file...')
        test_parser(data)
        print('\n\n')

# Excecute test cases
test_cases()