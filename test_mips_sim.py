#!/usr/bin/env python3

import unittest
import random

import numpy as np

from mips_sim import IanMIPS, Instr, IllegalInstructionError, CMDParse, MIPSProcessor, IntegerOverflow

well_formed = [
    "add $s0, $t0, $t1",
    "addi $s0, $t0, 0xfffb",    # -5 = 0xfffb
    "addi $s1, $t1, -5",
    "addi $s2, $t2, 26",
    "addiu $s0, $t0, 42",
    "addiu $s1, $t1, -55",
    "addiu $s2, $t2, 0x0bba",
    "addu $s0, $t0, $t1",
    "and $s0, $t0, $t1",
    "andi $s0, $t0, 63",
    "andi $s0, $t0, 0xaaaa",
    "beq $s0, $t0, 2000",
    "bgez $s0, 1000",
    "bgezal $s0, 50",
    "blez $s0, 100",
    "bltz $s0, 1001",
    "bltzal $s0, 500",
    "bne $s0, $t0, 2001",
    "div $s0, $t0",
    "divu $s0, $t0",
    "j 1000200",
    "jal 1000201",
    "jr $s4",
    "lb $s1, 50($t0)",
    "lui $s0, 5321",
    "lw $s1, 65($t0)",
    "mfhi $s0",
    "mflo $s1",
    "mult $t1, $t2",
    "multu $t1, $t2",
    "noop",
    "or $s0, $t1, $t2",
    "ori $s0, $t1, 500",
    "sb $s0, 22($s1)",
    "sll $s0, $t6, 5",
    "sllv $t0, $t6, $t3",
    "slt $s0, $t5, $t4",
    "slti $s0, $t3, -100",
    "sltiu $s0, $t3, 1000",
    "sltu $s0, $t3, $t7",
    "sra $s0, $t5, 6",
    "srl $s0, $s5, 2",
    "srlv $s0, $s1, $s2",
    "sub $s3, $s0, $s2",
    "subu $s2, $s3, $s5",
    "sw $t0, 25($s3)",
    "syscall",
    "xor $s3, $t3, $s1",
    "xori $s4, $t2, 0xFFFF"
]


class TestOpcodes(unittest.TestCase):

    def test_well_formed(self):

        for s in well_formed:
            v = CMDParse.parse_cmd(s)
            #self.assertEqual(s, v.__str__())

    def test_encode_complete(self):

        for s in well_formed:

            iform = CMDParse.parse_cmd(s)

            try:
                bform = iform.encode()

            except NotImplementedError:
                self.assertTrue(False, "encode {} is not implemented.".format(iform.op))
            except Exception as e:
                self.assertTrue(False, "Unexpected exception encountered encoding `{}`\n{}".format(s, e))

            try:
                iform2 = Instr.decode(bform)
            except NotImplementedError:
                self.assertTrue(False, "decode {} is not implemented.".format(iform.op))
            except Exception as e:
                self.assertTrue(False, "Unexpected exception encountered decoding `{}`\n{}".format(s, e))

            self.assertEqual(iform, iform2, "error encoding and decoding {}.".format(s))

    def test_encode_jr(self):
        o = CMDParse.parse_cmd("jr $s0")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        rd = Instr.extr_rd(o_bin)
        shamt = Instr.extr_shamt(o_bin)
        funct = Instr.extr_funct(o_bin)

        self.assertEqual(op, 0)
        self.assertEqual(rs, IanMIPS.reg_dict["s0"])
        self.assertEqual(rt, 0)
        self.assertEqual(rd, 0)
        self.assertEqual(shamt, 0)
        self.assertEqual(funct, IanMIPS.funct_dict["jr"])

    def test_encode_bgez(self):
        o = CMDParse.parse_cmd("bgez $s0, 1000")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        imm = Instr.extr_imm(o_bin)

        self.assertEqual(op, 1)
        self.assertEqual(imm, 1000)
        self.assertEqual(rs, IanMIPS.reg_dict["s0"])
        self.assertEqual(rt, IanMIPS.b_instr[o.op])

    def test_encode_add(self):
        o = CMDParse.parse_cmd("add $s0, $s1, $s2")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        rd = Instr.extr_rd(o_bin)
        funct = Instr.extr_funct(o_bin)

        self.assertEqual(op, 0)
        self.assertEqual(funct, IanMIPS.funct_dict["add"])
        self.assertEqual(rd, IanMIPS.reg_dict["s0"])
        self.assertEqual(rs, IanMIPS.reg_dict["s1"])
        self.assertEqual(rt, IanMIPS.reg_dict["s2"])

    def test_encode_addi(self):
        o = CMDParse.parse_cmd("addi $s0, $t0, 22")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        imm = Instr.extr_imm(o_bin)

        self.assertEqual(op, IanMIPS.op_dict["addi"])
        self.assertEqual(rt, IanMIPS.reg_dict["s0"])
        self.assertEqual(rs, IanMIPS.reg_dict["t0"])
        self.assertEqual(imm, 22)

    def test_encode_addi_negimm(self):
        o = CMDParse.parse_cmd("addi $s0, $t0, -5")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        imm = np.int16(Instr.extr_imm(o_bin))

        self.assertEqual(op, IanMIPS.op_dict["addi"])
        self.assertEqual(rt, IanMIPS.reg_dict["s0"])
        self.assertEqual(rs, IanMIPS.reg_dict["t0"])
        self.assertEqual(imm, -5)

    def test_encode_addi_heximm(self):
        o = CMDParse.parse_cmd("addi $s0, $t0, 0xa")

        o_bin = o.encode()

        op = Instr.extr_op(o_bin)
        rs = Instr.extr_rs(o_bin)
        rt = Instr.extr_rt(o_bin)
        imm = Instr.extr_imm(o_bin)

        self.assertEqual(op, IanMIPS.op_dict["addi"])
        self.assertEqual(rt, IanMIPS.reg_dict["s0"])
        self.assertEqual(rs, IanMIPS.reg_dict["t0"])
        self.assertEqual(imm, 10)

    def test_add(self):
        p = MIPSProcessor()

        p.reg[10] = 11
        p.reg[11] = 22
        p.reg[12] = 3

        p._add(10, 11, 12)

        self.assertEqual(p.reg[10], 25)

        try:
            p.reg[11] = 2 ** 31 - 1 # INT_MAX + 1 = overflow
            p.reg[12] = 1
            p._add(10, 11, 12)
            self.assertTrue(False)
        except IntegerOverflow:
            pass

        try:
            p.reg[11] = -2 ** 31 # INT_MIN - 2 = overflow
            p.reg[12] = -2
            p._add(10, 11, 12)
            self.assertTrue(False)
        except IntegerOverflow:
            pass

        inst = CMDParse.parse_cmd("add $s3, $s4, $s5")

        p.reg[19] = 2
        p.reg[20] = 11
        p.reg[21] = 22

        p.do_instr(inst)

        self.assertEqual(p.reg[19], 33)

    def test_addi(self):

        p = MIPSProcessor()

        p.reg[10] = 5

        p._addi(11, 10, 0x5)

        self.assertEqual(p.reg[11], 10)

        try:
            p.reg[10] = 2**31 - 1
            p._addi(11, 10, 2)
            self.assertTrue(False)
        except IntegerOverflow:
            pass

        try:
            p.reg[10] = -2 ** 31
            p._addi(11, 10, -2)
            self.assertTrue(False)
        except IntegerOverflow:
            pass

        inst = CMDParse.parse_cmd("addi $s3, $s4, 0xa")

        p.reg[19] = 2
        p.reg[20] = 11

        p.do_instr(inst)

        self.assertEqual(p.reg[19], 21)

    def test_addiu(self):

        p = MIPSProcessor()

        p.reg[10] = 5

        p._addiu(11, 10, 2)

        self.assertEqual(p.reg[11], 7)

        p.reg[10] = 2**32 - 1
        p._addiu(11, 10, 2)
        self.assertEqual(p.reg[11], 1)

        p.reg[10] = 1
        p._addiu(11, 10, -2)
        self.assertEqual(p.reg[11], 2 ** 32 - 1)

    def test_addu(self):
        """ Test addu $rd, $rs, $rt """
        p = MIPSProcessor()

        p.reg[10] = 11
        p.reg[11] = 22
        p.reg[12] = 3

        p._addu(10, 11, 12)

        self.assertEqual(p.reg[10], 25)

        p.reg[11] = 2 ** 32 - 1
        p.reg[12] = 2
        p._addu(10, 11, 12)
        self.assertTrue(p.reg[10], 1)

        p.reg[11] = 0
        p.reg[12] = -1
        p._addu(10, 11, 12)
        self.assertTrue(p.reg[10], 2 ** 32 - 1)

    def test_and(self):
        """ Test and $rd, $rs, $rt """

        p = MIPSProcessor()

        for i in range(100):
            a = np.uint32(random.getrandbits(32))
            b = np.uint32(random.getrandbits(32))
            p.reg[11] = a
            p.reg[12] = b

            c = np.bitwise_and(a, b)

            p._and(10, 11, 12)

            self.assertEqual(p.reg[10], c)

    def test_andi(self):
        """ Test addi $rt, $rs, imm """

        p = MIPSProcessor()

        for i in range(100):
            imm = np.uint32(random.getrandbits(32))

            rt = random.randint(8, 23)
            rs = random.randint(8, 23)

            rsval = np.uint32(random.getrandbits(32))

            p.reg[rs] = rsval

            res = np.bitwise_and(rsval, imm)

            p._andi(rt, rs, imm)

            self.assertEqual(p.reg[rt], res)

    def test_beq(self):

        p = MIPSProcessor()

        beq_cmd = CMDParse.parse_cmd("beq $t0, $s0, 0x3")

        p.pc = 10

        p.reg[8] = 10
        p.reg[16] = 10

        p.do_instr(beq_cmd)

        self.assertEqual(p.pc, 26)

    def test_sub(self):
        p = MIPSProcessor()

        p.reg[10] = 11
        p.reg[11] = 22
        p.reg[12] = 3

        p._sub(10, 11, 12)

        self.assertEqual(p.reg[10], 19)

        try:
            p.reg[11] = 2 ** 31 - 1  # INT_MAX - -2 = overflow
            p.reg[12] = -1
            p._sub(10, 11, 12)
        except IntegerOverflow:
            pass

        try:
            p.reg[11] = -2 ** 31  # INT_MIN - 2 = overflow
            p.reg[12] = 1
            p._sub(10, 11, 12)
        except IntegerOverflow:
            pass

        inst = CMDParse.parse_cmd("sub $s3, $s4, $s5")

        p.reg[19] = 2
        p.reg[20] = 22
        p.reg[21] = 11

        p.do_instr(inst)

        self.assertEqual(p.reg[19], 11)

    def test_subu(self):
        """ Test subu $rd, $rs, $rt """
        p = MIPSProcessor()

        p.reg[10] = 11
        p.reg[11] = 22
        p.reg[12] = 3

        p._subu(10, 11, 12)

        self.assertEqual(p.reg[10], 19)

        p.reg[11] = 2 ** 32 - 1
        p.reg[12] = -1
        p._subu(10, 11, 12)
        self.assertEqual(p.reg[10], 0)

        p.reg[11] = 0
        p.reg[12] = 1
        p._subu(10, 11, 12)
        self.assertEqual(p.reg[10], 2 ** 32 - 1)

if __name__ == "__main__":
    random.seed()
    unittest.main()