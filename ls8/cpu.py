"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010


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

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

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
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def get_arg_count(self):
        return int(format(self.ir, '#010b')[2:4], 2)

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

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            self.ir = self.ram[self.pc]
            operand_a = self.ram[self.pc + 1]
            operand_b = self.ram[self.pc + 2]

            if self.ir == HLT:
                running = False

            elif self.ir == LDI:
                self.reg[operand_a] = operand_b
                self.pc += self.get_arg_count()

            elif self.ir == PRN:
                print(self.reg[operand_a])
                self.pc += self.get_arg_count()

            elif self.ir == MUL:
                self.reg[operand_a] *= self.reg[operand_b]
                print(self.reg[operand_a])

            self.pc += 1