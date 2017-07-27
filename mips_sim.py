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


@unique
class MIPSI(Enum):
    ADD = 0
    ADDI = 1
    ADDIU = 2
    ADDU = 3
    AND = 4
    ANDI = 5
    BEQ = 6
    BGEZ = 7
    BGEZAL = 8
    BGTZ = 9
    BLEZ = 10
    BLTZ = 11
    BLTZAL = 12
    BNE = 13
    DIV = 14
    DIVU = 15
    J = 16
    JAL = 17
    JR = 18
    LB = 19
    LUI = 20
    LW = 21
    MFHI = 22
    MFLO = 23
    MULT = 24
    MULTU = 25
    NOOP = 26
    OR = 27
    ORI = 28
    SB = 29
    SLL = 30
    SLLV = 31
    SLT = 32
    SLTI = 33
    SLTIU = 34
    SLTU = 35
    SRA = 36
    SRL = 37
    SRLV = 38
    SUB = 39
    SUBU = 40
    SW = 41
    SYSCALL = 42
    XOR = 43
    XORI = 44

op_enum = {
    "add":      MIPSI.ADD,
    "addi":     MIPSI.ADDI,
    "addiu":    MIPSI.ADDIU,
    "addu":     MIPSI.ADDU,
    "and":      MIPSI.AND,
    "andi":     MIPSI.ANDI,
    "beq":      MIPSI.BEQ,
    "bgez":     MIPSI.BGEZ,
    "bgezal":   MIPSI.BGEZAL,
    "bgtz":     MIPSI.BGTZ,
    "blez":     MIPSI.BLEZ,
    "bltz":     MIPSI.BLTZ,
    "bltzal":   MIPSI.BLTZAL,
    "bne":      MIPSI.BNE,
    "div":      MIPSI.DIV,
    "divu":     MIPSI.DIVU,
    "j":        MIPSI.J,
    "jal":      MIPSI.JAL,
    "jr":       MIPSI.JR,
    "lb":       MIPSI.LB,
    "lui":      MIPSI.LUI,
    "lw":       MIPSI.LW,
    "mfhi":     MIPSI.MFHI,
    "mflo":     MIPSI.MFLO,
    "mult":     MIPSI.MULT,
    "multu":    MIPSI.MULTU,
    "noop":     MIPSI.NOOP,
    "or":       MIPSI.OR,
    "ori":      MIPSI.ORI,
    "sb":       MIPSI.SB,
    "sll":      MIPSI.SLL,
    "sllv":     MIPSI.SLLV,
    "slt":      MIPSI.SLT,
    "slti":     MIPSI.SLTI,
    "sltiu":    MIPSI.SLTIU,
    "sltu":     MIPSI.SLTU,
    "sra":      MIPSI.SRA,
    "srl":      MIPSI.SRL,
    "srlv":     MIPSI.SRLV,
    "sub":      MIPSI.SUB,
    "subu":     MIPSI.SUBU,
    "sw":       MIPSI.SW,
    "syscall":  MIPSI.SYSCALL,
    "xor":      MIPSI.XOR,
    "xori":     MIPSI.XORI,
}

# Sanity check
for k, v in op_enum.items():
    assert(v.name.lower() == k)


class IllegalInstructionError(Exception):
    pass


class IntegerOverflow(Exception):
    pass


class SoftwareInterrupt(Exception):
    pass


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
            out.rd = IanMIPS.reg_dict[op_str[1]]
            out.rs = IanMIPS.reg_dict[op_str[2]]
            out.rt = IanMIPS.reg_dict[op_str[3]]
            out.args = [out.rd, out.rs, out.rt]

        elif op_str[0] in CMDParse.cat_2:
            out.rd = IanMIPS.reg_dict[op_str[1]]
            out.rt = IanMIPS.reg_dict[op_str[2]]
            out.rs = IanMIPS.reg_dict[op_str[3]]
            out.args = [out.rd, out.rt, out.rs]

        elif op_str[0] in CMDParse.cat_3:
            out.rd = IanMIPS.reg_dict[op_str[1]]
            out.rt = IanMIPS.reg_dict[op_str[2]]
            out.shamt = Instr.conv_shamt(op_str[3])
            out.args = [out.rd, out.rt, out.shamt]

        elif op_str[0] in CMDParse.cat_4:
            out.rt = IanMIPS.reg_dict[op_str[1]]
            out.rs = IanMIPS.reg_dict[op_str[2]]
            out.imm = Instr.conv_imm(op_str[3])
            out.args = [out.rt, out.rs, out.imm]

        elif op_str[0] in CMDParse.cat_5:
            out.rt = IanMIPS.reg_dict[op_str[1]]
            out.imm = Instr.conv_imm(op_str[2])
            out.rs = IanMIPS.reg_dict[op_str[3]]
            out.args = [out.rt, out.imm, out.rs]

        elif op_str[0] in CMDParse.cat_6:
            out.rs = IanMIPS.reg_dict[op_str[1]]
            out.args = [out.rs]

        elif op_str[0] in CMDParse.cat_7:
            out.target = Instr.conv_target(op_str[1])
            out.args = [out.target]

        elif op_str[0] in CMDParse.cat_8:
            out.rs = IanMIPS.reg_dict[op_str[1]]
            out.rt = IanMIPS.reg_dict[op_str[2]]
            out.args = [out.rs, out.rt]

        elif op_str[0] in CMDParse.cat_9:
            out.rd = IanMIPS.reg_dict[op_str[1]]
            out.args = [out.rd]

        elif op_str[0] in CMDParse.cat_10:
            out.rt = IanMIPS.reg_dict[op_str[1]]
            out.imm = Instr.conv_imm(op_str[2])
            out.args = [out.rt, out.imm]

        elif op_str[0] in CMDParse.cat_11:
            out.rs = IanMIPS.reg_dict[op_str[1]]
            out.imm = Instr.conv_imm(op_str[2])
            out.args = [out.rs, out.imm]

        elif op_str[0] in CMDParse.cat_12:
            out.rs = IanMIPS.reg_dict[op_str[1]]
            out.rt = IanMIPS.reg_dict[op_str[2]]
            out.imm = Instr.conv_imm(op_str[3])
            out.args = [out.rs, out.rt, out.imm]

        else:
            pass

        out.bin = out.encode()

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

    # if op == 1, rt must equal one of these
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

    def gen_args(self):
        if self.op in CMDParse.cat_0:
            pass

        elif self.op in CMDParse.cat_1:
            self.args = [self.rd, self.rs, self.rt]

        elif self.op in CMDParse.cat_2:
            self.args = [self.rd, self.rt, self.rs]

        elif self.op in CMDParse.cat_3:
            self.args = [self.rd, self.rt, self.shamt]

        elif self.op in CMDParse.cat_4:
            self.args = [self.rt, self.rs, self.imm]

        elif self.op in CMDParse.cat_5:
            self.args = [self.rt, self.imm, self.rs]

        elif self.op in CMDParse.cat_6:
            self.args = [self.rs]

        elif self.op in CMDParse.cat_7:
            self.args = [self.target]

        elif self.op in CMDParse.cat_8:
            self.args = [self.rs, self.rt]

        elif self.op in CMDParse.cat_9:
            self.args = [self.rd]

        elif self.op in CMDParse.cat_10:
            self.args = [self.rt, self.imm]

        elif self.op in CMDParse.cat_11:
            self.args = [self.rs, self.imm]

        elif self.op in CMDParse.cat_12:
            self.args = [self.rs, self.rt, self.imm]

        else:
            raise IllegalInstructionError()

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

    @staticmethod
    def extr_target(instr):
        mask = np.uint32(0b11111111111111111111111111)
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
        self.imm = np.uint16(0)
        self.offset = ""
        self.args = []
        self.bin = np.uint32(0)
        pass

    @staticmethod
    def conv_imm(imm):
        try:
            return np.uint16(int(imm))
        except ValueError:
            return np.uint16(int(imm, 16))

    @staticmethod
    def conv_shamt(shamt):
        try:
            return np.bitwise_and(np.uint8(int(shamt)), 0b11111)
        except ValueError:
            return np.bitwise_and(np.uint8(int(shamt, 16)), 0b11111)

    @staticmethod
    def conv_target(target):
        try:
            return np.bitwise_and(np.uint32(int(target)), 0b11111111111111111111111111)
        except ValueError:
            return np.bitwise_and(np.uint32(int(target, 16)), 0b11111111111111111111111111)

    @staticmethod
    def decode(word):

        #  0 -  1 -  2 -  3 -   4   -   5
        # op - rs - rt - rd - shamt - funct
        # op - rs - rt - imm
        # op - rs - target

        instr = Instr()
        instr.bin = word

        if word == 0:
            instr.op = "noop"
            return instr

        op = Instr.extr_op(word)

        if op == 0:
            instr.funct = Instr.extr_funct(word)
            instr.op = IanMIPS.inv_funct_dict[instr.funct]
        elif op == 1:
            instr.rt = Instr.extr_rt(word)
            instr.op = IanMIPS.inv_b_instr[instr.rt]
        else:
            instr.op = IanMIPS.inv_op_dict[op]

        if op == 0:
            instr.funct = Instr.extr_funct(word)
            if instr.op == "jr":
                instr.rs = Instr.extr_rs(word)
            elif instr.op in ["sll", "srl", "sra"]:
                instr.rt = Instr.extr_rt(word)
                instr.rd = Instr.extr_rd(word)
                instr.shamt = Instr.extr_shamt(word)
            elif instr.op in ["mflo", "mfhi"]:
                instr.rd = Instr.extr_rd(word)
            elif instr.op in ["mult", "multu", "div", "divu"]:
                instr.rs = Instr.extr_rs(word)
                instr.rt = Instr.extr_rt(word)
            elif instr.op == "syscall":
                pass
            else:
                instr.rs = Instr.extr_rs(word)
                instr.rt = Instr.extr_rt(word)
                instr.rd = Instr.extr_rd(word)

        elif op == 1:
            instr.rs = Instr.extr_rs(word)
            instr.rt = Instr.extr_rt(word)
            instr.imm = Instr.extr_imm(word)
        else:
            # op - rs - rt - imm
            if instr.op in ["addi", "addiu", "andi", "beq", "bne", "lb", "lw", "ori", "sb", "slti", "sltiu", "sw", "xori"]:
                instr.rs = Instr.extr_rs(word)
                instr.rt = Instr.extr_rt(word)
                instr.imm = Instr.extr_imm(word)
            elif instr.op in ["blez"]:
                instr.rs = Instr.extr_rs(word)
                instr.imm = Instr.extr_imm(word)
            elif instr.op in ["j", "jal"]:
                instr.target = Instr.extr_target(word)
            elif instr.op in ["lui"]:
                instr.rt = Instr.extr_rt(word)
                instr.imm = Instr.extr_imm(word)
            else:
                raise NotImplementedError()

        # TODO Rewrite this so it doesn't need to pass into parse_cmd again.

        instr.gen_args()

        return instr

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
                tmp_arr[1] = np.left_shift(self.rs, 21)
                tmp_arr[2] = 0
                tmp_arr[3] = 0
                tmp_arr[4] = 0
            elif self.op in ["sll", "srl", "sra"]:
                tmp_arr[1] = 0
                tmp_arr[2] = np.left_shift(self.rt, 16)
                tmp_arr[3] = np.left_shift(self.rd, 11)
                tmp_arr[4] = np.left_shift(self.shamt, 6)
            elif self.op in ["mflo", "mfhi"]:
                tmp_arr[1] = 0
                tmp_arr[2] = 0
                tmp_arr[3] = np.left_shift(self.rd, 11)
            elif self.op in ["mult", "multu", "div", "divu"]:
                tmp_arr[1] = np.left_shift(self.rs, 21)
                tmp_arr[2] = np.left_shift(self.rt, 16)
            elif self.op == "syscall":
                pass
            else:
                tmp_arr[1] = np.left_shift(self.rs, 21)
                tmp_arr[2] = np.left_shift(self.rt, 16)
                tmp_arr[3] = np.left_shift(self.rd, 11)

        elif IanMIPS.op_dict[self.op] == 1:
            tmp_arr[1] = np.left_shift(self.rs, 21)
            tmp_arr[2] = np.left_shift(IanMIPS.b_instr[self.op], 16)
            tmp_arr[3] = self.imm
        else:
            # op - rs - rt - imm
            if self.op in ["addi", "addiu", "andi", "beq", "bne", "lb", "lw", "ori", "sb", "slti", "sltiu", "sw", "xori"]:
                tmp_arr[1] = np.left_shift(self.rs, 21)
                tmp_arr[2] = np.left_shift(self.rt, 16)
                tmp_arr[3] = self.imm
            elif self.op in ["blez"]:
                tmp_arr[1] = np.left_shift(self.rs, 21)
                tmp_arr[2] = 0
                tmp_arr[3] = self.imm
            elif self.op in ["j", "jal"]:
                tmp_arr[1] = self.target
            elif self.op in ["lui"]:
                tmp_arr[1] = 0
                tmp_arr[2] = np.left_shift(self.rt, 16)
                tmp_arr[3] = self.imm
            else:
                raise NotImplementedError()

        for e in tmp_arr:
            out = np.bitwise_or(out, e)

        return out

    def __str__(self):
        if self.op in CMDParse.cat_0:
            return self.op
        elif self.op in CMDParse.cat_1:
            rd = IanMIPS.inv_reg_dict[self.rd]
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}, ${}".format(self.op, rd, rs, rt)
        elif self.op in CMDParse.cat_2:
            rd = IanMIPS.inv_reg_dict[self.rd]
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}, ${}".format(self.op, rd, rt, rs)
        elif self.op in CMDParse.cat_3:
            rd = IanMIPS.inv_reg_dict[self.rd]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}, {}".format(self.op, rd, rt, self.shamt)
        elif self.op in CMDParse.cat_4:
            # hex_imm = np.uint16(self.imm)
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]

            return "{} ${}, ${}, {}".format(self.op, rt, rs, self.imm)
        elif self.op in CMDParse.cat_5:
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, {}(${})".format(self.op, rt, self.imm, rs)

        elif self.op in CMDParse.cat_6:
            rs = IanMIPS.inv_reg_dict[self.rs]
            return "{} ${}".format(self.op, rs)

        elif self.op in CMDParse.cat_7:
            return "{} {:x}".format(self.op, self.target)

        elif self.op in CMDParse.cat_8:
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}".format(self.op, rs, rt)

        elif self.op in CMDParse.cat_9:
            rd = IanMIPS.inv_reg_dict[self.rd]
            return "{} ${}".format(self.op, rd)

        elif self.op in CMDParse.cat_10:
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, {}".format(self.op, rt, self.imm)

        elif self.op in CMDParse.cat_11:
            rs = IanMIPS.inv_reg_dict[self.rs]
            return "{} ${}, {}".format(self.op, rs, self.imm)

        elif self.op in CMDParse.cat_12:
            rs = IanMIPS.inv_reg_dict[self.rs]
            rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}, {}".format(self.op, rs, rt, self.imm)

        else:
            print("How did this happen? FUCK", self.op)
            raise IllegalInstructionError()

    def __eq__(self, other):

        return self.bin == other.bin


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
            name.lower(): getattr(self, "_{}".format(name.lower())) for name, _ in MIPSI.__members__.items()
        }

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

        if type(program) is not np.ndarray:
            raise ValueError()
        elif type(program[0]) is not np.uint8:
            raise ValueError()

        try:
            self.mem[start_addr:start_addr + len(program)] = program
        except IndexError:
            raise MemoryError()

    def execute_prog(self, start_point):

        raise NotImplementedError()

    def fetch(self):

        self.ir = np.uint32(self.mem[self.pc:self.pc + 4].view('uint32')[0])

    def decode(self):

        instr = Instr.decode(self.ir)

    def do_instr(self, i):

        if type(i) is not Instr:
            raise ValueError()

        self.ops[i.op](*self.argconv(i.args))

    def _add(self, rd, rs, rt):
        # Add two 32 bit GPRs, store in third. Traps on overflow.
        self.pc += 4
        res = np.int32(self.reg[rs]) + np.int32(self.reg[rt])

        if self.over:
            self.over = False
            raise IntegerOverflow()

        self.reg[rd] = res

    def _addi(self, rt, rs, imm):
        # Add 16 bit signed imm to rs, then store in rt. Traps on overflow.
        self.pc += 4
        res = np.int32(self.reg[rs]) + np.int16(imm)

        if self.over:
            self.over = False
            raise IntegerOverflow()

        self.reg[rt] = res

    def _addiu(self, rt, rs, imm):
        # Add 16 bit signed imm to rs, then store in rt.
        self.pc += 4
        self.reg[rt] = self.reg[rs] + np.int16(imm)

    def _addu(self, rd, rs, rt):
        # Add two 32 bit GPRs, store in third.
        self.pc += 4
        self.reg[rd] = self.reg[rs] + self.reg[rt]

    def _and(self, rd, rs, rt):
        # Bitwise and of two GPR, stores in a third.
        self.pc += 4
        self.reg[rd] = np.bitwise_and(self.reg[rs], self.reg[rt])

    def _andi(self, rt, rs, imm):
        # Bitwise and of a GPR and an immediate value, stores in second GPR.
        self.pc += 4
        self.reg[rt] = np.bitwise_and(self.reg[rs], np.uint32(imm))

    def _beq(self, rs, rt, offset):
        # Branch if two specified GPRs are equal.
        self.pc += 4

        if self.reg[rs] == self.reg[rt]:
            self.pc += offset * 4

    def _bgez(self, rs, offset):
        # Branch on greater than or equal to 0.
        self.pc += 4

        if self.reg[rs] >= 0:
            self.pc += offset * 4

    def _bgezal(self, rs, offset):
        # Branch greater than or equal to zero and link
        self.pc += 4

        if self.reg[rs] >= 0:
            self.reg[31] = self.pc
            self.pc += offset * 4

    def _bgtz(self, rs, offset):
        # Branch greater than zero
        self.pc += 4

        if self.reg[rs] > 0:
            self.pc += offset * 4

    def _blez(self, rs, offset):
        # Branch less than or equal to zero
        self.pc += 4

        if self.reg[rs] <= 0:
            self.pc += offset * 4

    def _bltz(self, rs, offset):
        # Branch less than zero
        self.pc += 4

        if self.reg[rs] < 0:
            self.pc += offset * 4

    def _bltzal(self, rs, offset):
        # Branch less than zero and link
        self.pc += 4
        if self.reg[rs] < 0:
            self.reg[31] = self.pc
            self.pc += offset * 4

    def _bne(self, rs, rt, offset):
        # Branch if the contents of two GPRs are not equal
        self.pc += 4

        if self.reg[rs] != self.reg[rt]:
            self.pc += offset * 4

    def _div(self, rs, rt):
        self.pc += 4
        a = np.int32(self.reg[rs])
        b = np.int32(self.reg[rt])
        self.lo = a / b
        self.hi = a % b

    def _divu(self, rs, rt):
        self.pc += 4
        a = np.uint32(self.reg[rs])
        b = np.uint32(self.reg[rt])
        self.lo = a / b
        self.hi = a % b

    def _j(self, target):
        self.pc = np.bitwise_or(np.bitwise_and(0xf0000000, self.pc), target * 4)

    def _jal(self, target):
        self.reg[31] = self.pc + 8
        self.pc = np.bitwise_or(np.bitwise_and(0xf0000000, self.pc), target * 4)

    def _jr(self, rs):
        self.pc = self.reg[rs]

    def _lb(self, rt, offset, rs):

        start = rs + offset * 4

        self.reg[rt] = self.mem[start]

    def _lui(self, rt, imm):

        self.reg[rt] = np.left_shift(imm, 16)

    def _lw(self, rt, offset, rs):
        # c = np.uint32(*a[start:start + 4].view('uint32'))

        start = rs + offset*4

        self.reg[rt] = np.uint32(self.mem[start:start + 4].view('uint32')[0])

        self.pc += 4

    def _mfhi(self, rd):
        self.pc += 4
        self.reg[rd] = self.hi

    def _mflo(self, rd):
        self.pc += 4
        self.reg[rd] = self.lo

    def _mult(self, rs, rt):
        self.pc += 4
        res = np.int64(np.int32(self.reg[rs])) * np.int64(np.int32(self.reg[rt]))
        self.hi = np.right_shift(res, 32)
        self.lo = np.bitwise_and(res, 0xffffffff)

    def _multu(self, rs, rt):
        self.pc += 4
        res = np.uint64(self.reg[rs]) * np.uint64(self.reg[rt])
        self.hi = np.right_shift(res, 32)
        self.lo = np.bitwise_and(res, 0xffffffff)

    def _noop(self):

        self.pc += 4

    def _or(self, rd, rs, rt):
        self.pc += 4

        self.reg[rd] = np.bitwise_or(self.reg[rs], self.reg[rt])

    def _ori(self, rt, rs, imm):
        self.pc += 4

        self.reg[rt] = np.bitwise_or(self.reg[rs], imm)

    def _sb(self, rt, offset, rs):

        start = self.reg[rs] + offset * 4

        self.mem[start] = np.uint8(np.bitwise_and(0xff, self.reg[rt]))

        self.pc += 4

    def _sll(self, rd, rt, shamt):
        self.pc += 4

        self.reg[rd] = np.left_shift(self.reg[rt], shamt)

    def _sllv(self, rd, rt, rs):
        self.pc += 4

        self.reg[rd] = np.left_shift(self.reg[rt], self.reg[rs])


    def _slt(self, rd, rs, rt):
        self.pc += 4

        if np.int32(self.reg[rs]) < np.int32(self.reg[rt]):
            self.reg[rd] = 1
        else:
            self.reg[rd] = 0

    def _slti(self, rt, rs, imm):
        self.pc += 4

        if np.int32(self.reg[rs]) < np.int32(imm):
            self.reg[rt] = 1
        else:
            self.reg[rt] = 0

    def _sltiu(self, rt, rs, imm):
        self.pc += 4

        if self.reg[rs] < np.int16(imm):
            self.reg[rt] = 1
        else:
            self.reg[rt] = 0

    def _sltu(self, rd, rs, rt):
        self.pc += 4

        if self.reg[rs] < self.reg[rt]:
            self.reg[rd] = 1
        else:
            self.reg[rd] = 0

    def _sra(self, rd, rt, shamt):
        self.pc += 4

        self.reg[rd] = np.right_shift(np.int32(self.reg[rt]), shamt)


    def _srl(self, rd, rt, shamt):
        self.pc += 4

        self.reg[rd] = np.right_shift(self.reg[rt], shamt)

    def _srlv(self, rd, rs, rt):
        self.pc += 4

        self.reg[rd] = np.right_shift(self.reg[rt], self.reg[rs])

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
        self.pc += 4
        raise SoftwareInterrupt()

    def _xor(self, rd, rs, rt):
        self.pc += 4
        self.reg[rd] = np.bitwise_xor(self.reg[rs], self.reg[rt])

    def _xori(self, rt, rs, imm):
        self.pc += 4
        self.reg[rt] = np.bitwise_xor(self.reg[rs], imm)


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