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
        # r'\'[a-zA-Z0-9]*\''
        r'\".*?\"'
        # Delete ' '
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
        print('   Invalid character: ', t.value[0], ' in line', 
                  t.lineno, ' at position ', t.lexpos)
        t.lexer.skip(1)

    # Build the lexer
    return lex.lex()



#####################################################
# Parser
#####################################################
def PatitoParser(print_intermediate_code = False, quads = [], var_table = {}, cte_table = {}):
    # Define start of memory for each type
    cont_cte_int = 0
    cont_cte_float = 1000
    cont_cte_string = 2000
    cont_int = 3000
    cont_float = 4000
    cont_bool = 5000
    # Create dictionaries to store memory location and type of each constant and variable
    
    # Helper to detect change of sign
    change_symbol = False
    # Stack operators, operands and jumps to perform intermediate code quadriples
    stack_operands = [] # A, B
    stack_operators = [] # + -
    stack_jumps = []
    cont_quads = 0
    
    # Semantic rules between types operators
    semantics = {
            ('int', 'int', '+'): 'int',
            ('int', 'int', '-'): 'int',
            ('int', 'int', '*'): 'int',
            ('int', 'int', '/'): 'float',
            ('int', 'int', '>'): 'bool',
            ('int', 'int', '<'): 'bool',
            ('int', 'int', '!='): 'bool',
            ('int', 'float', '+'): 'float',
            ('int', 'float', '-'): 'float',
            ('int', 'float', '*'): 'float',
            ('int', 'float', '/'): 'float',
            ('int', 'float', '>'): 'bool',
            ('int', 'float', '<'): 'bool',
            ('int', 'float', '!='): 'bool',
            ('float', 'int', '+'): 'float',
            ('float', 'int', '-'): 'float',
            ('float', 'int', '*'): 'float',
            ('float', 'int', '/'): 'float',
            ('float', 'int', '>'): 'bool',
            ('float', 'int', '<'): 'bool',
            ('float', 'int', '!='): 'bool',
            ('float', 'float', '+'): 'float',
            ('float', 'float', '-'): 'float',
            ('float', 'float', '*'): 'float',
            ('float', 'float', '/'): 'float',
            ('float', 'float', '>'): 'bool',
            ('float', 'float', '<'): 'bool',
            ('float', 'float', '!='): 'bool'
        }
    
    # Helper function to add quadriple to queue of intermediate code
    def save_quad(quad, res_type):
        nonlocal quads, stack_operands, cont_quads
        quads.append(quad)
        cont_quads += 1
        # if there are no more follow-up operations to perform with generated quad
        if res_type != None:
            memory_dir = quad[3]
            stack_operands.append((memory_dir, res_type))


    # Helper function to build quadriple from operations
    def create_quad():
        r_operand_mem, r_type = stack_operands.pop()
        l_operand_mem, l_type = stack_operands.pop()
        operator = stack_operators.pop()
        # if valid operation between types
        if (r_type, l_type, operator) in semantics:
            res_type = semantics[(r_type, l_type, operator)]
            if res_type == 'int':
                nonlocal cont_int
                quad = (operator, l_operand_mem, r_operand_mem, cont_int)
                save_quad(quad, res_type)
                cont_int += 1
            elif res_type == 'float':
                nonlocal cont_float
                quad = (operator, l_operand_mem, r_operand_mem, cont_float)
                save_quad(quad, res_type)
                cont_float += 1
            elif res_type == 'bool':
                nonlocal cont_bool
                quad = (operator, l_operand_mem, r_operand_mem, cont_bool)
                save_quad(quad, res_type)
                cont_bool += 1
        else:
            raise yacc.YaccError('Type mismatch.')


    # Define CFG (Context free Grammars) from Patito Language
    # Actions to perform when all the file is parsed
    def p_program(p):
        'program : PROGRAM ID SEMICOLON r body END'
        # Detect error if pending operation or quadriple
        if (len(stack_operands) > 0 or 
            len(stack_operators) > 0 or
            len(stack_jumps) > 0):
            raise yacc.YaccError('Pending quadruples')
        if print_intermediate_code:
            # Print variables tables
            df_var_table = pd.DataFrame.from_dict(var_table, orient='index')
            df_var_table.index.name = 'Variable'
            if len(df_var_table) > 0:
                print('-- VARIABLES TABLE --')
                print(df_var_table, '\n')
            # Print constants table
            df_cte_table = pd.DataFrame.from_dict(cte_table, orient='index')
            df_cte_table.index.name = 'Constant'
            if len(df_cte_table) > 0:
                print('-- CONSTANTS TABLE --')
                print(df_cte_table, '\n')
            # Print queue of quadriples, intermediate code
            print('-- QUADRUPLES GENERATED --')
            i = 0
            while len(quads) > 0:
                print(i, quads.pop(0))
                i += 1

    def p_r(p):
        '''r : vars
             | empty'''

    # Declare variables
    def p_vars(p):
        'vars : VAR o'
    
    def p_o(p):
        'o : s p'

    def p_s(p):
        's : ID'
        # Create variable or detect it is duplicated if exists
        var_id = p[1]
        if var_id not in var_table:
            var_table[var_id] = {
                'type': None,
                'memory_dir': None
            }
        else:
            print('ERROR in line', p.lineno(1), ': Variable {', var_id, '} already exists.')

    def p_p(p):
        '''p : COMA o
             | COLON type SEMICOLON q'''
        
    def p_q(p):
        '''q : empty
             | o'''


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


    # Create quadriple of variable assignation
    def p_assign(p):
        'assign : id_assign equal_assign expression SEMICOLON'
        if (len(stack_operators) > 0 and 
            stack_operators[-1] == '='):
            r_operand_mem, r_type = stack_operands.pop()
            l_operand_mem, l_type = stack_operands.pop()
            operator = stack_operators.pop()
            # Detect if Type mismatch on assignation
            if l_type != r_type:
                # TODO si operator es '=' se debe asignar resultado a direccion de memoria de operador derecho
                print('Trying to assign type', r_type, 'to type', l_type, 'in line', p.lineno(2))
            else:
                quad = (operator, r_operand_mem, None, l_operand_mem)
                save_quad(quad, None)
        else:
            raise yacc.YaccError('Unexpected error trying to assign value to variable')

    # Check if variable was decleared and add it to operands
    def p_id_assign(p):
        'id_assign : ID'
        var_id = p[1]
        if var_id not in var_table:
            raise yacc.YaccError(f'Variable {var_id}, was not declared.')
        else:
            memory_dir = var_table[var_id]['memory_dir']
            var_type = var_table[var_id]['type']
            stack_operands.append((memory_dir, var_type))

    # Add equal operator to detect assignation
    def p_equal_assign(p):
        'equal_assign : EQUAL'
        operator = p[1]
        stack_operators.append(operator)


    def p_cycle(p):
        'cycle : do_cycle body WHILE l_par_cycle expression r_par_cycle SEMICOLON'

    # Mark start of cycle
    def p_do_cycle(p):
        'do_cycle : DO'
        stack_jumps.append(cont_quads)
    
    # Separate cycle inner operations from the others
    def p_l_par_cycle(p):
        'l_par_cycle : LEFTPARENTHESIS'
        # start limiting inner operations with '(' in stack
        operator = p[1]
        stack_operators.append(operator)

    # Completed inner operations from cycle expression
    def p_r_par_cycle(p):
        'r_par_cycle : RIGHTPARENTHESIS'
        # remove '(' from operators stack
        operator = stack_operators.pop()
        if operator != '(':
            raise yacc.YaccError('Unexpected error with Parenthesis encountered')
        else:
            operand_mem, operand_type = stack_operands.pop()
            # Check condition is of type 'bool'
            if operand_type != 'bool':
                raise yacc.YaccError('Type mismatch in Do While statement.')
            # Add quadriple of Jump to start of cycle if condition is true
            else:
                jump = stack_jumps.pop()
                quad = ('GotoT', operand_mem, None, jump)
                save_quad(quad, None)

    # End of If or Else
    def p_condition(p):
        'condition : IF left_par_condition expression right_par_condition body l SEMICOLON'
        # FILL end of If / else condition
        fill_quad_jump = stack_jumps.pop()        
        op, l_mem, r_mem, jump = quads[fill_quad_jump]
        if jump == None:
            quads[fill_quad_jump] = (op, l_mem, r_mem, cont_quads)
        else:
            raise yacc.YaccError('Unexpected error in condition IF.')

    def p_left_par_condition(p):
        'left_par_condition : LEFTPARENTHESIS'
        # start limiting inner operations with '(' in stack
        operator = p[1]
        stack_operators.append(operator)

    # Boolean condition, if false jump and skip
    def p_right_par_condition(p):
        'right_par_condition : RIGHTPARENTHESIS'
        # remove '(' from operators stack
        operator = stack_operators.pop()
        if operator != '(':
            raise yacc.YaccError('Unexpected error with Parenthesis encountered')
        else:
            operand_mem, operand_type = stack_operands.pop()
            if operand_type != 'bool':
                raise yacc.YaccError('Type mismatch condition IF.')
            # Unfilled quadriple waiting to know where to jump if false
            else:
                quad = ('GotoF', operand_mem, None, None)
                save_quad(quad, None)
                stack_jumps.append(cont_quads-1)
    
    def p_l(p):
        '''l : empty
             | else_condition body'''
    
    # Quadriple to Jump to end of condition if expression was true
    def p_else_condition(p):
        'else_condition : ELSE'
        quad = ('Goto', None, None, None)
        save_quad(quad, None)
        fill_quad_jump = stack_jumps.pop()
        stack_jumps.append(cont_quads-1)
        op, l_mem, r_mem, jump = quads[fill_quad_jump]
        if jump == None:
            quads[fill_quad_jump] = (op, l_mem, r_mem, cont_quads)
        else:
            raise yacc.YaccError('Unexpected error in condition ELSE.')


    def p_expression(p):
        'expression : exp j'
    
    def p_j(p):
        '''j : empty
             | k exp'''

    def p_k(p):
        '''k : GREATERTHAN
             | LESSTHAN
             | NOT'''
        operator = p[1]
        stack_operators.append(operator)


    def p_print(p):
        'print : cout_print LEFTPARENTHESIS g RIGHTPARENTHESIS semicolon_print'

    # Limit to print operations
    def p_cout_print(p):
        'cout_print : COUT'
        stack_operators.append(p[1])
        
    def p_g(p):
        'g : h i'
    
    # Generate quadriple to print string saving it to constants
    def p_h(p):
        '''h : expression_print
             | CTE_STRING'''
        # If string
        if p[1] != None:
            if (len(stack_operators) > 0 and 
            stack_operators[-1] == 'cout'):
                cte_string = p[1]
                # Save string in constant table
                if cte_string not in cte_table:
                    nonlocal cont_cte_string
                    cte_table[cte_string] = {
                        'type': 'string',
                        'memory_dir': cont_cte_string
                    }
                    cont_cte_string += 1
                # Get constant's memory direction and save print quadriple
                memory_dir = cte_table[cte_string]['memory_dir']
                quad = ('print', memory_dir, None, None)
                save_quad(quad, None)
            else:
                raise yacc.YaccError('Unexpected error in COUT.')

    # Generate quadriple to print expression
    def p_expression_print(p):
        'expression_print : expression'
        if (len(stack_operators) > 0 and 
            stack_operators[-1] == 'cout'):
            operand_mem, operand_type = stack_operands.pop()
            quad = ('print', operand_mem, None, None)
            save_quad(quad, None)
        else:
            raise yacc.YaccError('Unexpected error in COUT.')

    def p_i(p):
        '''i : empty
             | COMA g'''

    # End of print, break line quadriple
    def p_semicolon_print(p):
        'semicolon_print : SEMICOLON'
        # remove 'cout' from operators stack
        operator = stack_operators.pop()
        if operator != 'cout':
            raise yacc.YaccError('Unexpected error in COUT.')
        else:
            quad = ('print', None, None, None)
            save_quad(quad, None)

    # Create quadriples of booleans
    def p_exp(p):
        'exp : term e'
        if (len(stack_operators) > 0 and 
            (stack_operators[-1] == '>' or
             stack_operators[-1] == '<' or 
             stack_operators[-1] == '!=')):
            create_quad()

    def p_e(p):
        '''e : empty
             | f exp'''

    # Add operators to stack
    def p_f(p):
        '''f : ADD
             | MINUS'''
        operator = p[1]
        stack_operators.append(operator)

    # Create quadriples of adding or substracting
    def p_term(p):
        'term : factor c'
        if (len(stack_operators) > 0 and 
            (stack_operators[-1] == '+' or 
             stack_operators[-1] == '-')):
            create_quad()
    
    def p_c(p):
        '''c : empty
             | d term'''

    # Add operators to stack
    def p_d(p):
        '''d : MULTIPLY
             | DIVIDE'''
        operator = p[1]
        stack_operators.append(operator)

    # Create quadriples of multiplying or dividing
    def p_factor(p):
        '''factor : left_par_factor expression right_par_factor
                  | a b'''
        if (len(stack_operators) > 0 and 
            (stack_operators[-1] == '*' or 
             stack_operators[-1] == '/')):
            create_quad()

    def p_left_par_factor(p):
        'left_par_factor : LEFTPARENTHESIS'
        # start limiting inner operations with '(' in stack
        operator = p[1]
        stack_operators.append(operator)

    def p_right_par_factor(p):
        'right_par_factor : RIGHTPARENTHESIS'
        # remove '(' from operators stack
        operator = stack_operators.pop()
        if operator != '(':
            raise yacc.YaccError('Unexpected error with Parenthesis encountered')

    # Detect change of symbol of constant or variable
    def p_a(p):
        '''a : empty
             | ADD
             | MINUS'''
        if p[1] == '-':
            nonlocal change_symbol
            change_symbol = True
    
    # Check if variable was declared, and add it's memory location to operands stack with type
    def p_b(p):
        '''b : ID
             | cte'''
        if p[1] != None:
            var_id = p[1]
            if var_id not in var_table:
                raise yacc.YaccError(f'Variable {var_id}, was not declared.')
            else:
                # Get variable's memory direction and type
                memory_dir = var_table[var_id]['memory_dir']
                var_type = var_table[var_id]['type']
                # if variable is set to negative perform previuos quad
                nonlocal change_symbol
                if change_symbol:
                    change_symbol = False
                    if var_type == 'int':
                        nonlocal cont_int
                        quad = ('-', None, memory_dir, cont_int)
                        memory_dir = cont_int
                        save_quad(quad, None)
                        cont_int += 1
                    elif var_type == 'float':
                        nonlocal cont_float
                        quad = ('-', None, memory_dir, cont_float)
                        memory_dir = cont_float
                        save_quad(quad, None)
                        cont_float += 1
                    elif var_type == 'bool':
                        raise yacc.YaccError('Cannot set negative value to bool')
                # Add variables's memory reference to operands stack
                stack_operands.append((memory_dir, var_type))


    # Set type of variables when decleared and assign space in memory
    def p_type(p):
        '''type : INT
                | FLOAT'''
        var_type = p[1]
        nonlocal cont_int, cont_float
        for key in var_table:
            if var_table[key]['type'] is None:
                var_table[key]['type'] = var_type
                if var_type == 'int':
                    var_table[key]['memory_dir'] = cont_int
                    cont_int += 1
                elif var_type == 'float':
                    var_table[key]['memory_dir'] = cont_float
                    cont_float += 1


    # Create and add constants to operands stack
    def p_cte(p):
        '''cte : CTE_INT
            | CTE_FLOAT'''
        cte = p[1]
        # Save constant in constant table
        if cte not in cte_table:
            nonlocal cont_cte_int, cont_cte_float
            if isinstance(cte, int):
                cte_table[cte] = {
                    'type': 'int',
                    'memory_dir': cont_cte_int
                }
                cont_cte_int += 1
            elif isinstance(cte, float):
                cte_table[cte] = {
                    'type': 'float',
                    'memory_dir': cont_cte_float
                }
                cont_cte_float += 1
            else:
                raise yacc.YaccError(f'Constant {cte}, is not int or float.')
        # Get constant's memory direction and type
        memory_dir = cte_table[cte]['memory_dir']
        cte_type = cte_table[cte]['type']
        # if constant is set to negative perform previuos quad
        nonlocal change_symbol
        if change_symbol:
            change_symbol = False
            if cte_type == 'int':
                nonlocal cont_int
                quad = ('-', None, memory_dir, cont_int)
                memory_dir = cont_int
                save_quad(quad, None)
                cont_int += 1
            elif cte_type == 'float':
                nonlocal cont_float
                quad = ('-', None, memory_dir, cont_float)
                memory_dir = cont_float
                save_quad(quad, None)
                cont_float += 1
        # Add constant's memory reference to operands stack
        stack_operands.append((memory_dir, cte_type))


    # Define the p_empty rule that does nothing
    def p_empty(p):
        'empty :'
        pass


    # Error rule for syntax errors
    def p_error(p):
        print('  Syntax error in input')
        if p:
            print('    Expected token before {', p.value, '} in line', 
                  p.lineno, ' at position ', p.lexpos)

    return yacc.yacc(start='program')
