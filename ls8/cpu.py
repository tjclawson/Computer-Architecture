"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.ir = 0
        self.mar = 0
        self.mdr = 0
        # L Less-than: during a CMP, set to 1 if registerA is less than registerB, zero otherwise.
        # G Greater-than: during a CMP, set to 1 if registerA is greater than registerB, zero otherwise.
        # E Equal: during a CMP, set to 1 if registerA is equal to registerB, zero otherwise.
        #         0b00000LGE
        self.fl = 0b00000000

        # Init branch table for opcodes
        self.optable = {0b00000001: self.handle_hlt,
                        0b10000010: self.handle_ldi,
                        0b01000111: self.handle_prn,
                        0b10100010: self.handle_mul,
                        0b01000101: self.handle_push,
                        0b01000110: self.handle_pop,
                        0b01010000: self.handle_call,
                        0b00010001: self.handle_ret,
                        0b10100000: self.handle_add,
                        0b10100111: self.handle_cmp,
                        0b01010100: self.handle_jmp,
                        0b01010101: self.handle_jeq,
                        0b01010110: self.handle_jne}

        # Init stack pointer in register
        self.reg[7] = 0xf4

    def load(self):
        """Load a program into memory."""

        address = 0

        program = []

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            with open(filename) as f:
                for line in f:

                    # Ignore comments
                    comment_split = line.split("#")

                    # Strip out whitespace
                    opstring = comment_split[0].strip()

                    # Ignore blank lines
                    if opstring == '':
                        continue

                    # Convert opstring to base 2 int
                    opcode = int(opstring, 2)
                    program.append(opcode)

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def get_arg_count(self):
        return int(self.ir >> 6)

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_hlt(self, operand_a, operand_b):
        self.pc += 1
        sys.exit()

    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def handle_prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def handle_mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def handle_add(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def handle_and(self, operand_a, operand_b):
        self.alu("AND", operand_a, operand_b)

    def handle_or(self, operand_a, operand_b):
        self.alu("OR", operand_a, operand_b)

    def handle_xor(self, operand_a, operand_b):
        self.alu("XOR", operand_a, operand_b)

    def handle_not(self, operand_a, operand_b):
        self.alu("NOT", operand_a, operand_b)

    def handle_shl(self, operand_a, operand_b):
        self.alu("SHL", operand_a, operand_b)

    def handle_shr(self, operand_a, operand_b):
        self.alu("SHR", operand_a, operand_b)

    def handle_mod(self, operand_a, operand_b):
        self.alu("MOD", operand_a, operand_b)

    def handle_push(self, operand_a, operand_b):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.reg[operand_a]

    def handle_pop(self, operand_a, operand_b):
        self.reg[operand_a] = self.ram[self.reg[7]]
        self.reg[7] += 1

    def handle_call(self, operand_a, operand_b):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.pc + 2
        self.pc = self.reg[operand_a]

    def handle_ret(self, operand_a, operand_b):
        self.handle_pop(operand_a, operand_b)
        self.pc = self.reg[operand_a]

    def handle_cmp(self, operand_a, operand_b):
        if self.reg[operand_a] == self.reg[operand_b]:
            self.fl = 1
            # self.fl = ((1 << 0) | self.fl)
        elif self.reg[operand_a] < self.reg[operand_b]:
            self.fl = 2
            # self.fl = ((1 << 1) | self.fl)
        elif self.reg[operand_a] > self.reg[operand_b]:
            self.fl = 4
            # self.fl = ((1 << 2) | self.fl)

    def handle_jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def handle_jeq(self, operand_a, operand_b):
        if self.fl == 1:
            self.handle_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def handle_jne(self, operand_a, operand_b):
        if self.fl != 1:
            self.handle_jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            self.ir = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            self.optable[self.ir](operand_a, operand_b)

            # Bitwise shift to check if 4th bit of opcode is 0 i.e. not a PC mutator,
            if (self.ir >> 4) % 2 == 0:
                self.pc += self.get_arg_count() + 1
