#!/usr/bin/env python3

# ░░░░░░░░░░░░░░░░░░░░
# ░░░░▄▀▀▀▀▀█▀▄▄▄▄░░░░
# ░░▄▀▒▓▒▓▓▒▓▒▒▓▒▓▀▄░░
# ▄▀▒▒▓▒▓▒▒▓▒▓▒▓▓▒▒▓█░
# █▓▒▓▒▓▒▓▓▓░░░░░░▓▓█░
# █▓▓▓▓▓▒▓▒░░░░░░░░▓█░
# ▓▓▓▓▓▒░░░░░░░░░░░░█░
# ▓▓▓▓░░░░▄▄▄▄░░░▄█▄▀░
# ░▀▄▓░░▒▀▓▓▒▒░░█▓▒▒░░
# ▀▄░░░░░░░░░░░░▀▄▒▒█░
# ░▀░▀░░░░░▒▒▀▄▄▒▀▒▒█░
# ░░▀░░░░░░▒▄▄▒▄▄▄▒▒█░
# ░░░▀▄▄▒▒░░░░▀▀▒▒▄▀░░
# ░░░░░▀█▄▒▒░░░░▒▄▀░░░
# ░░░░░░░░▀▀█▄▄▄▄▀░░░░
# ░░░░░░░░░░░░░░░░░░░░

from enum import Enum, unique
import numpy as np
import re


class TODOError(Exception):
    pass


class IllegalInstructionError(Exception):
    pass


class IntegerOverflow(Exception):
    pass


class SoftwareInterrupt(Exception):
    pass


class InstrType(Enum):
    R = 0
    I = 1
    J = 2
    S = 3


class CMDParse:

    # op
    cat_0 = {
        "noop",
        "syscall",
    }

    # op $d, $s, $t
    cat_1 = {
        "add",
        "addu",
        "and",
        "or",
        "slt",
        "sltu",
        "sub",
        "subu",
        "xor",
    }

    # op $d, $t, $s
    cat_2 = {
        "sllv",
        "srlv",
    }

    # op $d, $t, h
    cat_3 = {
        "sll",
        "sra",
        "srl",
    }

    # op $t, $s, imm
    cat_4 = {
        "addi",
        "addiu",
        "andi",
        "ori",
        "slti",
        "sltiu",
        "xori",
    }

    # op $t, offset($s)
    cat_5 = {
        "lb",
        "lw",
        "sb",
        "sw"
    }

    # op $s
    cat_6 = {
        "jr"
    }

    # op target
    cat_7 = {
        "j",
        "jal",
    }

    # op $s, $t
    cat_8 = {
        "div",
        "divu",
        "mult",
        "multu",
    }

    # op $d
    cat_9 = {
        "mfhi",
        "mflo"
    }

    # op $t, imm
    cat_10 = {
        "lui"
    }

    # op $s, offset
    cat_11 = {
        "bgez",
        "bgezal",
        "bgtz",
        "blez",
        "bltz",
        "bltzal",
    }

    # op $s, $t, offset
    cat_12 = {
        "beq",
        "bne",
    }

    oplist = cat_0 | cat_1 | cat_2 | cat_3 | cat_4 | cat_5 | cat_6 | cat_7 | cat_8 | cat_9 | cat_10 | cat_11 | cat_12

    @staticmethod
    def parse_cmd(cmd):

        if type(cmd) is not str:
            raise ValueError()

        out = Instr()

        op_str = cmd.replace(',', " ")
        op_str = op_str.replace('$', " ")
        op_str = op_str.replace('(', " ")
        op_str = op_str.replace(')', " ")
        op_str = op_str.split()
        op_str = list(filter(None, op_str))

        out.op = op_str[0]

        if op_str[0] in CMDParse.cat_0:
            pass

        elif op_str[0] in CMDParse.cat_1:
            out.rd = op_str[1]
            out.rs = op_str[2]
            out.rt = op_str[3]
            out.args = [out.rd, out.rs, out.rt]

        elif op_str[0] in CMDParse.cat_2:
            out.rd = op_str[1]
            out.rt = op_str[2]
            out.rs = op_str[3]
            out.args = [out.rd, out.rt, out.rs]
        elif op_str[0] in CMDParse.cat_3:
            out.rd = op_str[1]
            out.rt = op_str[2]
            out.shamt = op_str[3]
            out.args = [out.rd, out.rt, out.shamt]

        elif op_str[0] in CMDParse.cat_4:
            out.rt = op_str[1]
            out.rs = op_str[2]
            out.imm = op_str[3]
            out.args = [out.rt, out.rs, out.imm]

        elif op_str[0] in CMDParse.cat_5:
            out.rt = op_str[1]
            out.imm = op_str[2]
            out.rs = op_str[3]
            out.args = [out.rt, out.imm, out.rs]

        elif op_str[0] in CMDParse.cat_6:
            out.rs = op_str[1]
            out.args = [out.rs]

        elif op_str[0] in CMDParse.cat_7:
            out.target = op_str[1]
            out.args = [out.target]

        elif op_str[0] in CMDParse.cat_8:
            out.rs = op_str[1]
            out.rt = op_str[2]
            out.args = [out.rs, out.rt]

        elif op_str[0] in CMDParse.cat_9:
            out.rd = op_str[1]
            out.args = [out.rd]

        elif op_str[0] in CMDParse.cat_10:
            out.rt = op_str[1]
            out.imm = op_str[2]
            out.args = [out.rt, out.imm]

        elif op_str[0] in CMDParse.cat_11:
            out.rs = op_str[1]
            out.imm = op_str[2]
            out.args = [out.rs, out.imm]

        elif op_str[0] in CMDParse.cat_12:
            out.rs = op_str[1]
            out.rt = op_str[2]
            out.imm = op_str[3]
            out.args = [out.rs, out.rt, out.imm]

        else:
            pass

        return out


class IanMIPS:

    # TODO Check this to make sure it is correct.
    op_dict = {
        "add":      0b000000,
        "addi":     0b001000,
        "addiu":    0b001001,
        "addu":     0b000000,
        "and":      0b000000,
        "andi":     0b001100,
        "beq":      0b000100,
        "bgez":     0b000001,
        "bgezal":   0b000001,
        "bgtz":     0b000111,
        "blez":     0b000110,
        "bltz":     0b000001,
        "bltzal":   0b000001,
        "bne":      0b000101,
        "div":      0b000000,
        "divu":     0b000000,
        "j":        0b000010,
        "jal":      0b000011,
        "jr":       0b000000,
        "lb":       0b100000,
        "lui":      0b001111,
        "lw":       0b100011,
        "mfhi":     0b000000,
        "mflo":     0b000000,
        "mult":     0b000000,
        "multu":    0b000000,
        "noop":     0b000000,
        "or":       0b000000,
        "ori":      0b001101,
        "sb":       0b101000,
        "sll":      0b000000,
        "sllv":     0b000000,
        "slt":      0b000000,
        "slti":     0b001010,
        "sltiu":    0b001011,
        "sltu":     0b000000,
        "sra":      0b000000,
        "srl":      0b000000,
        "srlv":     0b000000,
        "sub":      0b000000,
        "subu":     0b000000,
        "sw":       0b101011,
        "syscall":  0b000000,
        "xor":      0b000000,
        "xori":     0b001110,
    }

    OPS = list(op_dict.keys())

    funct_dict = {
        "add":      0b100000,
        "addu":     0b100001,
        "and":      0b100100,
        "div":      0b011010,
        "divu":     0b011011,
        "jr":       0b001000,
        "mfhi":     0b010000,
        "mflo":     0b010010,
        "mult":     0b011000,
        "multu":    0b011001,
        "or":       0b100101,
        "sll":      0b000000,
        "sllv":     0b000100,
        "slt":      0b101010,
        "sltu":     0b101011,
        "sra":      0b000011,
        "srl":      0b000010,
        "srlv":     0b000110,
        "sub":      0b100010,
        "subu":     0b100011,
        "syscall":  0b001100,
        "xor":      0b100110,
    }

    inv_op_dict = {v: k for k, v in op_dict.items()}
    inv_funct_dict = {v: k for k, v in funct_dict.items()}

    r_instr = {
        "add", "addu", "and", "div", "divu", "mfhi", "mflo", "mult", "multu", "or", "sll", "sllv", "slt", "sltu",
        "sra", "srl", "srlv", "sub", "subu", "xor"
    }

    i_instr = {
        "addi", "addiu", "andi", "beq", "bgez", "bgezal", "bgtz", "blez", "bltz", "bltzal", "bne",
        "lb", "lui", "lw", "ori", "sb", "slti", "sltiu", "sw", "xori",
    }

    j_instr = {
        "j", "jal", "jr"
    }

    sp_instr = {
        "noop",
        "syscall",
    }

    b_instr = {
        "bgez":     0b00001,    # $at
        "bgezal":   0b10001,    # $s1
        "bltz":     0b00000,    # $zero
        "bltzal":   0b10000,
    }

    inv_b_instr = {v: k for k, v in b_instr.items()}

    reg_dict = {
        "zero": 0,
        "at": 1,
        "v0": 2,
        "v1": 3,
        "a0": 4,
        "a1": 5,
        "a2": 6,
        "a3": 7,
        "t0": 8,
        "t1": 9,
        "t2": 10,
        "t3": 11,
        "t4": 12,
        "t5": 13,
        "t6": 14,
        "t7": 15,
        "s0": 16,
        "s1": 17,
        "s2": 18,
        "s3": 19,
        "s4": 20,
        "s5": 21,
        "s6": 22,
        "s7": 23,
        "t8": 24,
        "t9": 25,
        "k0": 26,
        "k1": 27,
        "gp": 28,
        "sp": 29,
        "fp": 30,
        "ra": 31,
    }

    inv_reg_dict = {v: k for k, v in reg_dict.items()}

    pass


class Instr:

    @staticmethod
    def encode_r_instr(op, rd = "zero", rs = "zero", rt = "zero", shamt = 0, funct = 0):
        tmp_arr = np.zeros(6, dtype=np.uint32)

        out = np.uint32(0)

        if type(op) is str:
            tmp_arr[0] = np.left_shift(IanMIPS.op_dict[op], 26)
        else:
            tmp_arr[0] = np.left_shift(op, 26)

        tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[rs], 21)
        #print(np.binary_repr(tmp_arr[1], width=32))
        tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[rt], 16)
        #print(np.binary_repr(tmp_arr[2], width=32))
        tmp_arr[3] = np.left_shift(IanMIPS.reg_dict[rd], 11)
        #print(np.binary_repr(tmp_arr[3], width=32))
        tmp_arr[4] = np.left_shift(shamt, 6)
        #print(np.binary_repr(tmp_arr[4], width=32))
        if tmp_arr[0] == 0:
            tmp_arr[5] = IanMIPS.funct_dict[op]
        else:
            tmp_arr[5] = funct
        #print(np.binary_repr(tmp_arr[5], width=32))

        for i in range(6):
            out = np.bitwise_or(out, tmp_arr[i])

        #print(np.binary_repr(out, width=32))

        return out

    @staticmethod
    def encode_i_instr(op, rt, rs, imm):
        tmp_arr = np.zeros(4, dtype=np.uint32)

        out = np.uint32(0)

        tmp_arr[0] = np.left_shift(IanMIPS.op_dict[op], 26)
        # print(np.binary_repr(tmp_arr[0], width=32))
        tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[rs], 21)
        # print(np.binary_repr(tmp_arr[1], width=32))
        tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[rt], 16)

        tmp_arr[3] = imm

        for i in range(4):
            out = np.bitwise_or(out, tmp_arr[i])

        return out

    @staticmethod
    def extr_rd(instr):
        mask = np.uint32(0b11111)
        out = np.right_shift(instr, 11)
        out = np.bitwise_and(out, mask)

        return out

    @staticmethod
    def extr_rt(instr):
        mask = np.uint32(0b11111)
        out = np.right_shift(instr, 16)
        out = np.bitwise_and(out, mask)

        return out

    @staticmethod
    def extr_rs(instr):
        mask = np.uint32(0b11111)
        out = np.right_shift(instr, 21)
        out = np.bitwise_and(out, mask)

        return out

    @staticmethod
    def extr_op(instr):
        mask = np.uint32(0b111111)
        out = np.right_shift(instr, 26)
        out = np.bitwise_and(out, mask)

        return out

    @staticmethod
    def extr_funct(instr):
        mask = np.uint32(0b111111)
        out = np.bitwise_and(instr, mask)

        return out

    @staticmethod
    def extr_shamt(instr):
        mask = np.uint32(0b11111)
        out = np.right_shift(instr, 6)
        out = np.bitwise_and(out, mask)

        return out

    @staticmethod
    def extr_imm(instr):
        mask = np.uint32(0b1111111111111111)
        out = np.bitwise_and(instr, mask)

        return out

    def __init__(self):
        self.op = ""
        self.funct = ""
        self.rs = ""
        self.rt = ""
        self.rd = ""
        self.shamt = ""
        self.target = ""
        self.imm = ""
        self.offset = ""
        pass

    @staticmethod
    def conv_imm(imm):
        try:
            return int(imm)
        except ValueError:
            return int(imm, 16)


    def encode(self):

        #  0 -  1 -  2 -  3 -   4   -   5
        # op - rs - rt - rd - shamt - funct
        # op - rs - rt - imm
        # op - rs - target

        tmp_arr = np.zeros(6, dtype=np.uint32)
        out = np.uint32(0)

        if self.op == "noop":
            return out

        tmp_arr[0] = np.left_shift(IanMIPS.op_dict[self.op], 26)

        if IanMIPS.op_dict[self.op] == 0:
            tmp_arr[5] = IanMIPS.funct_dict[self.op]
            if self.op == "jr":
                tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
                tmp_arr[2] = 0
                tmp_arr[3] = 0
                tmp_arr[4] = 0
            elif self.op in ["sll", "srl", "sra"]:
                tmp_arr[1] = 0
                tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[self.rt], 16)
                tmp_arr[3] = np.left_shift(IanMIPS.reg_dict[self.rd], 11)
                tmp_arr[4] = np.left_shift(self.conv_imm(self.shamt), 6)
            elif self.op in ["mflo", "mfhi"]:
                tmp_arr[1] = 0
                tmp_arr[2] = 0
                tmp_arr[3] = np.left_shift(IanMIPS.reg_dict[self.rd], 11)
            elif self.op in ["mult", "multu", "div", "divu"]:
                tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
                tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[self.rt], 16)
            elif self.op == "syscall":
                pass
            else:
                tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
                tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[self.rt], 16)
                tmp_arr[3] = np.left_shift(IanMIPS.reg_dict[self.rd], 11)

        elif IanMIPS.op_dict[self.op] == 1:
            tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
            tmp_arr[2] = np.left_shift(IanMIPS.b_instr[self.op], 16)
            tmp_arr[3] = self.conv_imm(self.imm)
        else:
            # op - rs - rt - imm
            if self.op in ["addi", "addiu", "andi", "beq", "bne", "lb", "lw", "ori", "sb", "slti", "sltiu", "sw", "xori"]:
                tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
                tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[self.rt], 16)
                tmp_arr[3] = self.conv_imm(self.imm)
            elif self.op in ["blez"]:
                tmp_arr[1] = np.left_shift(IanMIPS.reg_dict[self.rs], 21)
                tmp_arr[2] = 0
                tmp_arr[3] = self.conv_imm(self.imm)
            elif self.op in ["j", "jal"]:
                tmp_arr[1] = self.conv_imm(self.target)
            elif self.op in ["lui"]:
                tmp_arr[1] = 0
                tmp_arr[2] = np.left_shift(IanMIPS.reg_dict[self.rt], 16)
                tmp_arr[3] = self.conv_imm(self.imm)
            else:
                raise NotImplementedError()

        for e in tmp_arr:
            out = np.bitwise_or(out, e)

        return out

    def decode(self, word):
        pass

    def init_from_word(self, instr):

        #print("instr = ", np.binary_repr(instr, width=32))

        if type(instr) is not np.uint32:
            raise ValueError()

        if instr == 0:
            self.op_str = "noop"
            self.op = 0
            return

        self.op = self.extr_op(instr)
        if self.op == 0:
            # syscall or arithmetic operations
            self.funct = self.extr_funct(instr)
            self.op_str = IanMIPS.inv_funct_dict[self.funct]
        elif self.op == 1:
            # bgez, bgezal, bltz, bltzal

            self.rt = self.extr_rt(instr)
            self.op_str = IanMIPS.inv_b_instr[self.rt]

        else:
            self.op_str = IanMIPS.inv_op_dict[self.op]

        self.rs = self.extr_rs(instr)
        self.rt = self.extr_rt(instr)

        if self.op_str in IanMIPS.r_instr:
            self.rd = self.extr_rd(instr)
            self.shamt = self.extr_shamt(instr)
            pass
        elif self.op_str in IanMIPS.i_instr:
            self.imm = self.extr_imm(instr)
            pass
        else:
            pass

        if self.op not in IanMIPS.op_dict.values():
            raise IllegalInstructionError()

    def __str__(self):
        if self.op in CMDParse.cat_0:
            return self.op
        elif self.op in CMDParse.cat_1:
            return "{} ${}, ${}, ${}".format(self.op, self.rd, self.rs, self.rt)
        elif self.op in CMDParse.cat_2:
            return "{} ${}, ${}, ${}".format(self.op, self.rd, self.rt, self.rs)
        elif self.op in CMDParse.cat_3:
            return "{} ${}, ${}, {}".format(self.op, self.rd, self.rt, self.shamt)
        elif self.op in CMDParse.cat_4:
            # hex_imm = np.uint16(self.imm)

            return "{} ${}, ${}, {}".format(self.op, self.rt, self.rs, self.imm)
        elif self.op in CMDParse.cat_5:
            return "{} ${}, {}(${})".format(self.op, self.rt, self.imm, self.rs)
        elif self.op in CMDParse.cat_6:
            return "{} ${}".format(self.op, self.rs)
        elif self.op in CMDParse.cat_7:
            # TODO target and imm hex immediate values etc
            return "{} {}".format(self.op, self.target)
        elif self.op in CMDParse.cat_8:
            return "{} ${}, ${}".format(self.op, self.rs, self.rt)
        elif self.op in CMDParse.cat_9:
            return "{} ${}".format(self.op, self.rd)
        elif self.op in CMDParse.cat_10:
            return "{} ${}, {}".format(self.op, self.rt, self.imm)
        elif self.op in CMDParse.cat_11:
            return "{} ${}, {}".format(self.op, self.rs, self.imm)
        elif self.op in CMDParse.cat_12:
            return "{} ${}, ${}, {}".format(self.op, self.rs, self.rt, self.imm)
        else:
            print("How did this happen? FUCK", self.op)
            raise IllegalInstructionError()

    def __eq__(self, other):
        if self.op != other.op:
            return False

        try:
            if hasattr(self, "rs"):
                if self.rs != other.rs:
                    return False

            if hasattr(self, "rt"):
                if self.rt != other.rt:
                    return False

            if hasattr(self, "rd"):
                if self.rd != other.rd:
                    return False

            if hasattr(self, "imm"):
                # TODO convert to unsigned before checking.
                if self.imm != other.imm:
                    return False

            if hasattr(self, "offset"):
                # TODO convert before checking
                if self.offset != other.offset:
                    return False

            if hasattr(self, "target"):
                # TODO This should be in hex?
                if self.target != other.target:
                    return False
        except AttributeError:
            return False

        return True


class MIPSProcessor:

    def errcall(self, errstr, errflag):
        if errstr == "overflow":
            self.set_over()

    def set_over(self):
        self.over = True

    def __init__(self):
        self.reg = np.zeros(32, dtype=np.uint32)

        self.hi = np.uint32(0)
        self.lo = np.uint32(0)

        self.pc = np.uint32(0)
        self.instr_c = 0
        self.epc = np.uint32(0)
        self.cause = np.uint32(0)
        self.badvaddr = np.uint32(0)
        self.status = np.uint32(0)

        self.ir = np.uint32(0)

        self.mem = np.empty(1000000, dtype='uint8')

        self.over = False

        self.ops = {
            "add": self._add,
            "addi": self._addi,
            "addiu": self._addiu,
            "addu": self._addu,
            "and": self._and,
            "andi": self._andi,
            "beq": self._beq,
            "sub": self._sub,
            "subu": self._subu,
            "syscall": self._syscall,

        }

        # TODO Do something more smarter here.
        np.seterr(over="call")
        np.seterrcall(self.errcall)

    def argconv(self, args):

        out = []
        for a in args:
            try:
                out.append(IanMIPS.reg_dict[a])
                continue
            except KeyError:
                pass

            try:
                out.append(int(a))
            except ValueError:
                out.append(int(a, 16))

        return out

    def load_program(self, start_addr, program):

        self.mem[start_addr:start_addr + len(program)] = program

    def execute_prog(self, program):

        raise TODOError()

        if type(program) is not list:
            raise ValueError()

        self.pc = 0
        self.instr_c = 0

        while True:
            try:
                instr = program[self.pc]
                self.pc += 1
                self.instr_c += 1
                self.ops[instr.op](*self.argconv(instr.args))
            except IndexError:
                break

    def fetch(self):

        self.ir = np.uint32(self.mem[self.pc:self.pc + 4].view('uint32')[0])

    def decode(self):

        instr = Instr()

        l_op = Instr.extr_op(self.ir)
        instr.bin = self.ir

        if l_op == 0:
            if self.ir == 0:
                instr.op = "noop"
            else:
                l_func = Instr.extr_funct(self.ir)
                instr.op = IanMIPS.inv_funct_dict[l_func]
        elif l_op == 1:
            l_rt = Instr.extr_rt(self.ir)
            instr.op = IanMIPS.inv_b_instr[l_rt]
        else:
            instr.op = IanMIPS.inv_op_dict[l_op]


        raise TODOError()

    def do_instr(self, i):

        if type(i) is not Instr:
            raise ValueError()

        self.ops[i.op](*self.argconv(i.args))

    def _add(self, rd, rs, rt):
        # Add two 32 bit GPRs, store in third. Traps on overflow.
        exp = int(self.reg[rs]) + int(self.reg[rt])
        act = np.int32(self.reg[rs]) + np.int32(self.reg[rt])

        if self.over:
            self.over = False
            raise IntegerOverflow()

        self.reg[rd] = act

    def _addi(self, rt, rs, imm):
        # Add 16 bit signed imm to rs, then store in rt. Traps on overflow.
        temp = np.int32(self.reg[rs]) + np.int16(imm)

        if self.over:
            self.over = False
            raise IntegerOverflow()

        self.reg[rt] = temp

    def _addiu(self, rt, rs, imm):
        # Add 16 bit signed imm to rs, then store in rt.
        self.reg[rt] = self.reg[rs] + np.uint32(imm)

    def _addu(self, rd, rs, rt):
        # Add two 32 bit GPRs, store in third.

        self.reg[rd] = np.uint32(self.reg[rs]) + np.uint32(self.reg[rt])

    def _and(self, rd, rs, rt):
        # Bitwise and of two GPR, stores in a third.

        self.reg[rd] = np.bitwise_and(self.reg[rs], self.reg[rt])

    def _andi(self, rt, rs, imm):
        # Bitwise and of a GPR and an immediate value, stores in second GPR.

        self.reg[rt] = np.bitwise_and(self.reg[rs], np.uint32(imm))

    def _beq(self, rs, rt, offset):

        if offset < 0:
            offset -= 1

        if self.reg[rs] == self.reg[rt]:
            self.pc += offset

    def _bgez(self, rs, offset):

        if offset < 0:
            offset -= 1

        if self.reg[rs] >= 0:
            self.pc += offset

    def _bgezal(self, rs, offset):
        # Branch greater than or equal to zero and link

        if offset < 0:
            offset -= 1

        if self.reg[rs] >= 0:
            self.reg[31] = self.pc + 1
            self.pc += offset

        self.pc += 4

    def _bgtz(self, rs, offset):
        # Branch greater than zero

        if offset < 0:
            offset -= 1

        if self.reg[rs] > 0:
            self.pc += offset

    def _blez(self, rs, offset):
        # Branch less than or equal to zero
        if offset < 0:
            offset -= 1

        if self.reg[rs] <= 0:
            self.pc += offset

    def _bltz(self, rs, offset):
        # Branch less than zero
        if offset < 0:
            offset -= 1

        if self.reg[rs] < 0:
            self.pc += offset

    def _bltzal(self, rs, offset):
        # Branch less than zero and link
        if offset < 0:
            offset -= 1

        if self.reg[rs] < 0:
            self.reg[31] = self.pc + 1
            self.pc += offset

    def _bne(self, rs, rt, offset):
        if offset < 0:
            offset -= 1

        if self.reg[rs] != self.reg[rt]:
            self.pc += offset

    def _div(self, rs, rt):
        a = np.int32(self.reg[rs])
        b = np.int32(self.reg[rt])
        self.lo = a / b
        self.hi = a % b

    def _divu(self, rs, rt):
        a = np.uint32(self.reg[rs])
        b = np.uint32(self.reg[rt])
        self.lo = a / b
        self.hi = a % b

    def _j(self):
        raise TODOError()

    def _jal(self):
        raise TODOError()

    def _jr(self):
        raise TODOError()

    def _lb(self):
        raise TODOError()

    def _lui(self):
        raise TODOError()

    def _lw(self, rt, offset, rs):
        # c = np.uint32(*a[start:start + 4].view('uint32'))

        start = rt + offset*4

        self.reg[rt] = np.uint32(self.mem[start:start + 4].view('uint32')[0])

        self.pc += 4

    def _mfhi(self):
        raise TODOError()

    def _mflo(self):
        raise TODOError()

    def mult(self):
        raise TODOError()

    def multu(self):
        raise TODOError()

    def noop(self):

        self.pc += 4

    def _or(self):
        raise TODOError()

    def _ori(self):
        raise TODOError()

    def _sb(self):
        raise TODOError()

    def _sll(self):
        raise TODOError()

    def _sllv(self):
        raise TODOError()

    def _slt(self):
        raise TODOError()

    def _slti(self):
        raise TODOError()

    def _sltiu(self):
        raise TODOError()

    def _sltu(self):
        raise TODOError()

    def _sra(self):
        raise TODOError()

    def _srl(self):
        raise TODOError()

    def _srlv(self):
        raise TODOError()

    def _sub(self, rd, rs, rt):
        # Subtact two 32 bit GPRs, store in third. Traps on overflow
        a = np.int32(self.reg[rs])
        b = np.int32(self.reg[rt])
        c = a - b

        if self.over:
            self.over = False
            raise IntegerOverflow()

        self.reg[rd] = c

        self.pc += 4

    def _subu(self, rd, rs, rt):
        # Subtact two 32 bit GPRs, store in third. Does not trap on overflow
        self.reg[rd] = self.reg[rs] - self.reg[rt]

        self.pc += 4

    def _sw(self, rt, offset, rs):
        #a[start:start + 4] = np.uint32([c]).view('uint8')
        start = self.reg[rs] + offset*4
        self.mem[start:start + 4] = np.uint32([self.reg[rt]]).view('uint8')

        self.pc += 4

    def _syscall(self):
        raise SoftwareInterrupt()

    def _xor(self):
        raise TODOError()

    def _xori(self):
        raise TODOError()


# Static checks to ensure everything is correct.
assert(all([op in IanMIPS.op_dict.keys() for op in CMDParse.oplist]))

assert(len(IanMIPS.funct_dict.values()) == len(set(IanMIPS.funct_dict.values())))

for k, v in IanMIPS.op_dict.items():
    if v == 0:
        if k == "noop" or k == "syscall":
            continue

        assert(k in IanMIPS.funct_dict.keys())


for k, v in IanMIPS.op_dict.items():
    if v == 1:
        assert(k in IanMIPS.b_instr.keys())