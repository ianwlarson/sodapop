#!/usr/bin/env python3

from enum import Enum, unique
import numpy as np


class IllegalInstructionError(Exception):
    pass


class IanMIPS:

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

    funct_dict = {
        "noop": 0b000000,
        "srl":  0b000010,
        "sra":  0b000011,
        "sllv": 0b000100,
        "srlv": 0b000110,
        "jr":   0b001000,
        "syscall": 0b001100,
        "mfhi": 0b010000,
        "mflo": 0b010010,
        "mult": 0b011000,
        "div":  0b011010,
        "divu": 0b011011,
        "add":  0b100000,
        "addu": 0b100001,
        "sub":  0b100010,
        "subu": 0b100011,
        "and":  0b100100,
        "or":   0b100101,
        "xor":  0b100110,
        "slt":  0b101010,
        "sltu": 0b101011,


    }

    inv_op_dict = {v: k for k, v in op_dict.items()}
    inv_funct_dict = {v: k for k, v in funct_dict.items()}

    r_instr = {0, "add", "addu", "and"}

    b_instr = {
        "bgez": 0b00001,    # $at
        "bgezal": 0b10001,  # $s1
        "blez": 0b00000,    # $zero
        "bltz": 0b00000,    # $zero
        "bltzal": 0b10000,
    }

    i_instr = {"addi", "addiu", "andi", "beq", "bgez", "bgezal", "bgtz", "blez", "bne", "xori"}

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
    def encode_r_instr(op, rd, rs, rt, shamt = 0, funct = 0):
        tmp_arr = np.zeros(6, dtype=np.uint32)

        out = np.uint32(0)

        tmp_arr[0] = np.left_shift(IanMIPS.op_dict[op], 26)
        #print(np.binary_repr(tmp_arr[0], width=32))
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

    def __init__(self, instr):

        #print("instr = ", np.binary_repr(instr, width=32))

        self.op = self.extr_op(instr)
        self.rs = self.extr_rs(instr)
        self.rt = self.extr_rt(instr)

        if self.op in IanMIPS.r_instr:
            self.rd = self.extr_rd(instr)
            self.shamt = self.extr_shamt(instr)
            self.funct = self.extr_funct(instr)
            pass
        elif self.op in IanMIPS.i_instr:
            self.imm = self.extr_imm(instr)
            pass
        else:
            pass

        if self.op not in IanMIPS.op_dict.values():
            raise IllegalInstructionError()

    def __str__(self):
        if self.op in IanMIPS.r_instr:
            if self.op == 0:

                try:
                    l_op = IanMIPS.inv_funct_dict[self.funct]
                except KeyError:
                    raise IllegalInstructionError()

            else:
                l_op = IanMIPS.inv_op_dict[self.op]

            l_rd = IanMIPS.inv_reg_dict[self.rd]
            l_rs = IanMIPS.inv_reg_dict[self.rs]
            l_rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, ${}, ${}".format(l_op, l_rd, l_rs, l_rt)
        elif self.op in IanMIPS.i_instr:
            l_op = IanMIPS.inv_op_dict[self.op]
            l_rs = IanMIPS.inv_reg_dict[self.rs]
            l_rt = IanMIPS.inv_reg_dict[self.rt]
            return "{} ${}, {}(${})".format(l_op, l_rt, self.imm, l_rs)
        else:
            raise IllegalInstructionError()

    pass


class Processor:

    def __init__(self):
        self.reg = np.zeros(32, dtype=np.uint32)

    def do_instr(self, instr):

        if type(instr) is not Instr:
            instr = Instr(instr)



        pass

    pass

kappa = Instr.encode_r_instr("add", "t0", "s2", "t0", funct=32)

inv_kappa = Instr(kappa)

print("add $t0, $s2, $t0 => {} => {}".format(np.binary_repr(kappa,32), inv_kappa))

kappa = Instr.encode_i_instr("lw", "t0", "s3", 32)

inv_kappa = Instr(kappa)

print("lw $t0, 32($s3) => {} => {}".format(np.binary_repr(kappa,32), inv_kappa))

kappa = Instr.encode_r_instr("xor", "t0", "s2", "t0")

inv_kappa = Instr(kappa)

print("xor $t0, $s2, $t0 => {} => {}".format(np.binary_repr(kappa,32), inv_kappa))