#!/usr/bin/env python3

import unittest
import random

import numpy as np

from mips_sim import IanMIPS, Instr, IllegalInstructionError, InstrType, CMDParse

well_formed = [
    "add $s0, $t0, $t1",
    "addi $s0, $t0, 0xfffb",    # -5 = 0xfffb
    "addiu $s0, $t0, 42",
    "addu $s0, $t0, $t1",
    "and $s0, $t0, $t1",
    "andi $s0, $t0, 63",
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
    "sllv $0, $t6, $t3",
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
            self.assertEqual(s, v.__str__())
        pass

    def test_random_ops(self):

        for i in range(1000):
            op = random.choice(IanMIPS.OPS)

            if op in IanMIPS.i_instr:
                type = InstrType.I
            elif op in IanMIPS.r_instr:
                type = InstrType.R
            elif op in IanMIPS.j_instr:
                type = InstrType.J
            elif op in IanMIPS.sp_instr:
                type = InstrType.S
            else:
                print(op)
                self.assertTrue(False)

            if type == InstrType.R:
                rs = random.randint(8, 25)
                rt = random.randint(8, 25)
                rd = random.randint(8, 25)

                while len({rt, rs, rd}) != 3:
                    rt = random.randint(8, 25)
                    rd = random.randint(8, 25)

            elif type == InstrType.I:
                rs = random.randint(8, 25)
                rt = random.randint(8, 25)

                imm = random.randint(0, 2**16 - 1)
                imm_hex = "0x{:x}".format(imm)
                imm_list = [imm, imm_hex]
                #print(imm_hex)
                s_imm = random.randint(-2 ** 15, 2 ** 15 - 1)
                s_imm_hex = "0x{:x}".format(np.uint16(s_imm))
                #print(s_imm_hex)

                while len({rt, rs}) != 2:
                    rt = random.randint(8, 25)

                if op in ["lw", "lb", "sw", "sb"]:
                    opstr = "{} ${}, {}(${})".format(op, IanMIPS.inv_reg_dict[rt], imm, IanMIPS.inv_reg_dict[rs])
                elif op == "lui":
                    opstr = "lui ${}, {}".format(IanMIPS.inv_reg_dict[rt], imm)
                elif op in ["bgez", "bgezal", "blez", "bltz", "bltzal",]:
                    opstr = "{} ${}, {}".format(op, IanMIPS.inv_reg_dict[rs], imm)
                elif op in ["beq", "bne"]:
                    # in beq and bne, rt and rs are reversed.
                    opstr = "{} ${}, ${}, {}".format(op, IanMIPS.inv_reg_dict[rs], IanMIPS.inv_reg_dict[rt], imm)
                else:
                    opstr = "{} ${}, ${}, {}".format(op, IanMIPS.inv_reg_dict[rt], IanMIPS.inv_reg_dict[rs], imm)

                #print(opstr)
            elif type == InstrType.J:
                pass
            elif type == InstrType.S:
                opstr = op
            else:
                print(type)
                self.assertTrue(False)

            pass



if __name__ == "__main__":
    random.seed()
    unittest.main()