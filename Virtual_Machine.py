class Virtual_Machine:
    def __init__(self, quads, var_table, cte_table):
        self.quadruples = quads
        self.var_table = var_table
        self.cte_table = cte_table
        # Define memory starts used by Parser
        self.mem_cte_int = 0
        self.mem_cte_float = 1000
        self.mem_cte_string = 2000
        self.mem_int = 3000
        self.mem_float = 4000
        self.mem_bool = 5000
        self.mem_limit = 6000
        self.start_cte_int = 0
        self.start_cte_float = 0
        self.start_cte_string = 0
        self.start_int = len(self.cte_table)
        self.start_float = self.start_int
        self.start_bool = self.start_int
        self.end = self.start_int
        self.allocate_memory()
        self.save_cte()
    
    def allocate_memory(self):
        for cte in self.cte_table:
            memory_dir = self.cte_table[cte]['memory_dir']
            if memory_dir < self.mem_cte_float:
                self.start_cte_float += 1
            elif memory_dir < self.mem_cte_string:
                self.start_cte_string += 1
        self.start_cte_string += self.start_cte_float

        for var in self.var_table:
            memory_dir = self.var_table[var]['memory_dir']
            if self.mem_int <= memory_dir < self.mem_float:
                self.start_float = max(self.start_float, memory_dir)
            elif self.mem_float <= memory_dir < self.mem_bool:
                self.start_bool = max(self.start_bool, memory_dir)
            elif self.mem_bool <= memory_dir < self.mem_limit:
                self.end = max(self.end, memory_dir)

        for quad in self.quadruples:
            operator, l_operand_mem, r_operand_mem, memory_dir = quad
            if memory_dir != None:
                if self.mem_int <= memory_dir < self.mem_float:
                    self.start_float = max(self.start_float, memory_dir)
                elif self.mem_float <= memory_dir < self.mem_bool:
                    self.start_bool = max(self.start_bool, memory_dir)
                elif self.mem_bool <= memory_dir < self.mem_limit:
                    self.end = max(self.end, memory_dir)

        if self.start_float > self.start_int:
            self.start_float = self.start_float - self.mem_int + self.start_int + 1
        if self.start_bool > self.start_int:
            self.start_bool = self.start_bool - self.mem_float + self.start_float + 1
        else:
            self.start_bool = self.start_float
        if self.end > self.start_int:
            self.end = self.end - self.mem_bool + self.start_bool + 1
        else:
            self.end = self.start_bool

        self.memory = [None] * self.end 



    def get_memory_dir(self, memory_dir):
        if memory_dir == None:
            return memory_dir
        m_dir = 0
        if memory_dir < self.mem_cte_float:
            m_dir = self.start_cte_int + (memory_dir - self.mem_cte_int)
        elif memory_dir < self.mem_cte_string:
            m_dir = self.start_cte_float + (memory_dir - self.mem_cte_float)
        elif memory_dir < self.mem_int:
            m_dir = self.start_cte_string + (memory_dir - self.mem_cte_string)
        elif memory_dir < self.mem_float:
            m_dir = self.start_int + (memory_dir - self.mem_int)
        elif memory_dir < self.mem_bool:
            m_dir = self.start_float + (memory_dir - self.mem_float)
        elif memory_dir < self.mem_limit:
            m_dir = self.start_bool + (memory_dir - self.mem_bool)
        else:
            print("ERROR: Stack Overflow")
        return m_dir


    def save_to_memory(self, memory_dir, value):
        m_dir = self.get_memory_dir(memory_dir)
        self.memory[m_dir] = value


    def save_cte(self):
        for cte in self.cte_table:
            memory_dir = self.cte_table[cte]['memory_dir']
            self.save_to_memory(memory_dir, cte)


    def execute(self):
        pc = 0
        while pc < len(self.quadruples):
            quad = self.quadruples[pc]
            operator, l_operand_mem, r_operand_mem, result_mem = quad
            l_operand_mem = self.get_memory_dir(l_operand_mem)
            r_operand_mem = self.get_memory_dir(r_operand_mem)

            if operator == '+':
                value = self.memory[l_operand_mem] + self.memory[r_operand_mem]
                self.save_to_memory(result_mem, value)
            elif operator == '-':
                if l_operand_mem == None:
                    value = self.memory[r_operand_mem] * -1
                    self.save_to_memory(result_mem, value)
                else:
                    value = self.memory[l_operand_mem] - self.memory[r_operand_mem]
                    self.save_to_memory(result_mem, value)
            elif operator == '*':
                value = self.memory[l_operand_mem] * self.memory[r_operand_mem]
                self.save_to_memory(result_mem, value)
            elif operator == '/':
                value = self.memory[l_operand_mem] / self.memory[r_operand_mem]
                self.save_to_memory(result_mem, value)
            elif operator == '>':
                if self.memory[l_operand_mem] > self.memory[r_operand_mem]:
                    self.save_to_memory(result_mem, True)
                else:
                    self.save_to_memory(result_mem, False)
            elif operator == '<':
                if self.memory[l_operand_mem] < self.memory[r_operand_mem]:
                    self.save_to_memory(result_mem, True)
                else:
                    self.save_to_memory(result_mem, False)
            elif operator == '!=':
                if self.memory[l_operand_mem] != self.memory[r_operand_mem]:
                    self.save_to_memory(result_mem, True)
                else:
                    self.save_to_memory(result_mem, False)
            elif operator == '=':
                value = self.memory[l_operand_mem]
                self.save_to_memory(result_mem, value)
            elif operator == 'Goto':
                pc = result_mem
                continue
            elif operator == 'GotoF':
                if not self.memory[l_operand_mem]:
                    pc = result_mem
                    continue
            elif operator == 'GotoT':
                if self.memory[l_operand_mem]:
                    pc = result_mem
                    continue
            elif operator == 'print':
                if l_operand_mem == None:
                    print()
                else:
                    print(self.memory[l_operand_mem], end='')
            else:
                print("ERROR operator", operator, "not recognized")
            pc += 1


    def print_memory(self):
        for i in range(len(self.memory)):
            print(f"Memory[{i}] = {self.memory[i]}")

    # def debug(self):
    #     print(self.cte_table)
    #     print()
    #     print(self.var_table)
    #     print()
    #     print(self.quadruples)


