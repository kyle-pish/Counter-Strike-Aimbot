#
# S24_Brian.py  --  Simulator class for 256sim.
#
# Authors: Mark Liffiton
#          Kyle Pish
#
#   CS256
#   04/12/2024
#
from print_utils import print_val, print_mem, print_input, print_matrix

import time

# Constants for this architecture
_NUMREG = 8       # number of registers in the register file
_REGSIZE = 8      # size (in bits) of each register)
_ADDRSIZE = 8     # size (in bits) of DMEM addresses
_NUMBUTTONS = 3   # Number of buttons (binary on/off) for input
_MATRIXSIZE = 8   # width and height of the pixel matrix output


class Simulator:
    def __init__(self) -> None:
        # CPU state:
        self.imem : list[int] = [0]  # not affected by CPU reset, so only initialized here
        # Simulator state (separate from the CPU itself):
        self.bin_filename : str = ""

        # Initialize most state using .reset()
        self.reset()

    def load_bin(self, filename : str) -> None:
        """ Load machine code from a file into instruction memory.

        Parameters:
         - filename: String of a path to a file containing machine code for
                     instruction memory.  Machine code words should be written
                     in hexadecimal, separated by whitespace.
        """
        self.bin_filename = filename
        with open(filename, "r") as f:
            data = f.read()
        words = data.split()
        self.imem = [int(word, 16) for word in words]

        # Always reset on loading new code
        self.reset()

    def reset(self) -> None:
        """ Reset the CPU state to just-powered-on, with everything but IMEM cleared. """
        self.PC: int = 0
        self.regfile: list[int] = [0] * _NUMREG
        self.dmem: list[int] = [0] * 2 ** _ADDRSIZE
        self.buttons: list[int] = [0] * _NUMBUTTONS
        self.matrix: list[list[int]] = [([0] * _MATRIXSIZE) for _ in range(_MATRIXSIZE)]

    def change_buttons(self, new_buttons : str) -> None:
        """ Change the state of the simulated buttons.

        Parameters:
         - new_buttons: String containing a 0 or 1 for each button
                        e.g. "0110" for the first button not pressed, the
                        second and third pressed, and the fourth not pressed.
        """
        buttonvals = [int(c) for c in new_buttons]
        if len(buttonvals) != _NUMBUTTONS:
            raise Exception(
                f"Incorrect number of buttons.  Got {len(buttonvals)}, expected {_NUMBUTTONS}."
            )
        if max(buttonvals) > 1 or min(buttonvals) < 0:
            raise Exception("Invalid value for button.  Only allowed values are 0 and 1.")
        self.buttons = buttonvals

    def step_n(self, n: int) -> None:
        """ Simulate n cycles of the CPU (see self.step()). """
        for _ in range(n):
            self.step()

    def watch_n(self, n: int) -> None:
        """ Simulate n cycles of the CPU, as in step_n(), but watch the
            state of the CPU by printing after every 100th cycle.
        """
        for i in range(n):
            self.step()
            if i % 50 == 0:
                print("[2J[H")  # clear the screen and return to home position
                self.print()
                time.sleep(0.05)    # simulate ~1kHz clock rate

    def run_until(self, pc_breakpoint: int) -> None:
        """ Simulate until the given breakpoint is reached.

        Parameters:
         - pc_breakpoint: int of the address at which execuation should stop
        """
        # always execute at least once -- allows repeatedly running to the same instruction
        self.step()
        while self.PC != pc_breakpoint:
            self.step()

    def print(self) -> None:
        """ Print the current state of all state (memory) elements of the CPU. """
        print_val(self.PC, "PC")
        print_mem(self.imem, "IMEM", val_width=16, highlight=self.PC)
        print_mem(self.regfile, "Regfile", label_all=True)
        print_mem(self.dmem, "DMEM", limit_to_modified=True)
        print_input(self.buttons, "Input")
        print_matrix(self.matrix, "Output")

    def fetch(self) -> int:
        # Fetch the current instruction from IMEM
        return self.imem[self.PC]

    def decode(self, instruction: int) -> tuple:
        # Decode instruction
        opcode = (instruction >> 12) & 0b1111
        dest_reg = (instruction >> 9) & 0b111
        src_reg1 = (instruction >> 6) & 0b111
        src_reg2 = (instruction >> 3) & 0b111
        if opcode == 0b1011:                        
            imm = instruction & 0b111111111111    # 12-bit immediate for JAL
        else:
            imm = instruction & 0b111111111       # 9-bit immediate otherwise

        return opcode, dest_reg, src_reg1, src_reg2, imm

    def execute(self, opcode: int, dest_reg: int, src_reg1: int, src_reg2: int, imm: int) -> None:
        """ Instruction Formats
                R-Format:   Opcode(4) Dest(3) Src1(3) Src2(3)
                I-Format:   Opcode(4) Dest(3) Imm(9)
                     JAL:   Opcode(4) Imm(12)
        """

        # Ensure arithmetic operations stay within 8 bits
        mask = 0xFF

        if opcode == 0b0000:                                    # LB      (Load Byte)             R-Format        
            self.lb(dest_reg, src_reg2, mask)
        elif opcode == 0b0001:                                  # SB      (Store Byte)            R-Format
            self.sb(src_reg1, src_reg2, mask)
        elif opcode == 0b0010:                                  # ADD     (Addition)              R-Format
            self.add(dest_reg, src_reg1, src_reg2, mask)
        elif opcode == 0b0011:                                  # SUB     (Subtraction)           R-Format
            self.sub(dest_reg, src_reg1, src_reg2, mask)
        elif opcode == 0b0100:                                  # MOVE    (Move/Copy)             R-Format
            self.move(dest_reg, src_reg1, mask)
        elif opcode == 0b0101:                                  # ADDI    (Add Immediate)         I-Format
            self.addi(dest_reg, imm, mask)                            
        elif opcode == 0b0110:                                  # SETI    (Set Immediate)         I-Format
            self.seti(dest_reg, imm, mask)                            
        elif opcode == 0b0111:                                  # BEQ     (Branch if Equal)       I-Format
            self.beq(dest_reg, imm)
        elif opcode == 0b1000:                                  # BNE     (Branch if not Equal)   I-Format
            self.bne(dest_reg, imm)
        elif opcode == 0b1001:                                  # BLT     (Branch if Less Than)   I-Format
            self.blt(dest_reg, imm)
        elif opcode == 0b1010:                                  # JR      (Jump Register)         R-Format
            self.jr(src_reg1)
        elif opcode == 0b1011:                                  # JAL     (Jump and Link)         JAL
            self.jal(imm, mask)
      

    def lb(self, dest_reg: int, src_reg2: int, mask: int) -> None:                             # LB
        addr = self.regfile[src_reg2]
        if 0x80 <= addr < 0x80 + _NUMBUTTONS:
            self.regfile[dest_reg] = self.buttons[addr - 0x80]
        else:
            self.regfile[dest_reg] = self.dmem[self.regfile[src_reg2]] & mask                           # Load data from dmem address in src_reg2 --> dest_reg
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def sb(self, src_reg1: int, src_reg2: int, mask: int) -> None:                             # SB
        addr = self.regfile[src_reg2]
        data = self.regfile[src_reg1] & mask
        if addr >= 0x80:
            addr -= 0x80
            x = addr % _MATRIXSIZE
            y = addr // _MATRIXSIZE
            self.matrix[y][x] = data
        else:
            self.dmem[addr] = data                                                                  # Store data from src_reg1 --> dmem address in src_reg2
        self.PC += 1                                                                                # Increment the program counter for the next instruction
    
    def add(self, dest_reg: int, src_reg1: int, src_reg2: int, mask: int) -> None:             # ADD
        self.regfile[dest_reg] = (self.regfile[src_reg1] + self.regfile[src_reg2]) & mask           # dest_reg = src_reg1 + src_reg2
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def sub(self, dest_reg: int, src_reg1: int, src_reg2: int, mask: int) -> None:             # SUB
        self.regfile[dest_reg] = (self.regfile[src_reg1] - self.regfile[src_reg2]) & mask           # dest_reg = src_reg1 - src_reg2
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def move(self, dest_reg: int, src_reg1: int, mask: int) -> None:                           # MOVE
        self.regfile[dest_reg] = self.regfile[src_reg1] & mask                                      # Copy value from src_reg1 into dest_reg
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def addi(self, dest_reg: int, imm: int, mask: int) -> None:                                # ADDI
        self.regfile[dest_reg] = (self.regfile[dest_reg] + imm) & mask                              # dest_reg = dest_reg + imm
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def seti(self, dest_reg: int, imm: int, mask: int) -> None:                                # SETI
        self.regfile[dest_reg] = imm & mask                                                         # dest_reg = immediate
        self.PC += 1                                                                                # Increment the program counter for the next instruction

    def beq(self, dest_reg: int, imm: int) -> None:                                             # BEQ
        if imm & (1 << (9 - 1)):                                                                    # Check for sign bit
            imm = imm | ~((1 << 9) - 1)                                                             # Sign extension
        if self.regfile[dest_reg] == self.regfile[6]:                                               # dest_reg == $6 (implicit)? Branch!
            self.PC += imm                                                                          # Offset PC by immediate
        else:
            self.PC += 1                                                                            # Increment the program counter for the next instruction

    def bne(self, dest_reg: int, imm: int) -> None:                                             # BNE
        if imm & (1 << (9 - 1)):                                                                    # Check for sign bit
            imm = imm | ~((1 << 9) - 1)                                                             # Sign extension
        if self.regfile[dest_reg] != self.regfile[6]:                                               # dest_reg != $6 (implicit)? Branch!
            self.PC += imm                                                                          # Offset PC by immediate
        else:
            self.PC += 1                                                                            # Increment the program counter for the next instruction

    def blt(self, dest_reg: int, imm: int) -> None:                                             # BLT
        if imm & (1 << (9 - 1)):                                                                    # Check for sign bit
            imm = imm | ~((1 << 9) - 1)                                                             # Sign extension
        val1 = self.regfile[dest_reg]
        if val1 > 0x7f:
            val1 -= 0x100
        val2 = self.regfile[6]
        if val2 > 0x7f:
            val2 -= 0x100
        if val1 < val2:                                                                             # dest_reg < $6 (implicit)? Branch!
            self.PC += imm                                                                          # Offset PC by immediate  
        else:
            self.PC += 1                                                                            # Increment the program counter for the next instruction

    def jr(self, src_reg1: int) -> None:                                                       # JR
        self.PC = self.regfile[src_reg1]                                                            # Set PC to whatever is stored in src_reg1

    def jal(self, imm: int, mask: int) -> None:                                                # JAL
        self.regfile[7] = (self.PC + 1) & mask                                                      # Set $ra ($7) to current inst/pc
        self.PC = imm                                                                               # Set current PC = Immediate
        
    def step(self) -> None:
        ''' one CPU cycle (Fetch-Decode-Execute) '''
        # Fetch the current instruction
        instruction = self.fetch()

        # Decode the instruction into its different fields
        opcode, dest_reg, src_reg1, src_reg2, imm = self.decode(instruction)

        # Execute the instruction based on the opcode and its arguments
        self.execute(opcode, dest_reg, src_reg1, src_reg2, imm)


###
# Tips and Recommendations
###
#
# 1) Create separate methods for fetch, decode, and execute.  Then create separate
#    methods for every different instruction.  Pass the arguments for each instruction
#    into its corresponding method when it is executed.
#
# 2) You can write binary literals in Python with the 0b prefix.  E.g.,  0b01101100
#    Hexadecimal can be written with the 0x prefix.  E.g.,  0x6c
#
# 3) IMEM will contain raw binary machine code.  You will need to decode it carefully.
#    Use bitwise logical operators to mask and extract bits from a single instruction.
#    This can be used to pull separate fields out of a single binary instruction.
#
# 4) Make sure you're clear on what the following are and what they hold / how they work:
#
#      self.PC, self.imem, self.regfile, self.dmem, self.buttons, self.matrix
#
#    Mostly they're arrays.  Look at the reset() method to see how they're initialized.
#    The result of executing any instruction should be that some of these are modified.
#    Ask me for clarification if you're unsure about any of them.
#
# 5) Take it one small step at a time, and test everything you implement before moving on!
#


