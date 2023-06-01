from Scanner_Parser_Patito import PatitoParser, PatitoLexer
from Virtual_Machine import Virtual_Machine

files = ['main_VM.txt', 'test_elseif.txt']

while len(files) > 0:
    quads = []
    var_table = {}
    cte_table = {}
    lexer = PatitoLexer()
    parser = PatitoParser(quads=quads, var_table=var_table, cte_table=cte_table)
    
    f = files.pop()
    with open(f, 'r') as file:
            data = file.read()
            # Parse input
            try:
                parser.parse(data)

            except Exception as e:
                print('Parsing error: ', e)

    # Create a virtual machine and execute the quadruples
    try:
        vm = Virtual_Machine(quads, var_table, cte_table)
        vm.execute()
        # Print the memory after execution
        # vm.print_memory()
    except Exception as e:
        print('Error runing program on Virtual Machine', e)

