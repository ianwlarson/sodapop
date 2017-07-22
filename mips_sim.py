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


class IllegalInstructionError(Exception):
    pass


class IntegerOverflow(Exception):
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
            out.h = op_str[3]
            out.args = [out.rd, out.rt, out.h]
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



    # This has been checked once, could still be wrong. Kappa
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
            return "{} ${}, ${}, {}".format(self.op, self.rd, self.rt, self.h)
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

    def __init__(self):
        self.reg = np.zeros(32, dtype=np.uint32)

        self.hi = np.uint32(0)
        self.lo = np.uint32(0)

        self.pc = np.uint32(0)
        self.epc = np.uint32(0)
        self.cause = np.uint32(0)
        self.badvaddr = np.uint32(0)
        self.status = np.uint32(0)

        self.ops = {
            "add": self._add,
            "addi": self._addi,
            "addiu": self._addiu,
            "addu": self._addu,
            "and": self._and,
            "andi": self._andi,

        }

        # TODO Do something more smarter here.
        np.seterr(over="ignore")

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

    def execute_prog(self, program):

        if type(program) is not list:
            raise ValueError()

        for i in program:
            self.ops[i.op](*self.argconv(i.args))

    def do_instr(self, i):

        if type(i) is not Instr:
            raise ValueError()

        self.ops[i.op](*self.argconv(i.args))

    def _add(self, rd, rs, rt):

        # Add two 32 bit GPRs, store in third. Traps on overflow

        temp = self.reg[rs] + self.reg[rt]

        b_temp = "{:032b}".format(temp)

        if b_temp[0] != b_temp[1]:
            raise IntegerOverflow()
        else:
            self.reg[rd] = temp

    def _addi(self, rt, rs, imm):

        # Add 16 bit signed imm to rs, then store in rt. Traps on overflow.
        temp = self.reg[rs] + np.int16(imm)

        b_temp = "{:032b}".format(temp)

        if b_temp[0] != b_temp[1]:
            raise IntegerOverflow()
        else:
            self.reg[rt] = temp

    def _addiu(self, rt, rs, imm):
        # Add 16 bit signed imm to rs, then store in rt.
        self.reg[rt] = self.reg[rs] + np.int16(imm)

    def _addu(self, rd, rs, rt):
        # Add two 32 bit GPRs, store in third.

        self.reg[rd] = self.reg[rs] + self.reg[rt]

    def _and(self, rd, rs, rt):
        # Bitwise and of two GPR, stores in a third.

        self.reg[rd] = np.bitwise_and(self.reg[rs], self.reg[rt])

    def _andi(self, rt, rs, imm):
        # Bitwise and of a GPR and an immediate value, stores in second GPR.

        self.reg[rt] = np.bitwise_and(self.reg[rs], np.uint32(imm))

    def _beq(self, rs, rt, offset):

        if self.reg[rs] == self.reg[rt]:
            self.pc += offset

