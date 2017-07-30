#!/usr/bin/env python3

from mips_sim import CMDParse, Instr, MIPSR, MIPSI, IllegalInstructionError
import os.path
import argparse
import re
import sys

debug = False


def dprint(s):
    if debug:
        print(s)


def is_valid_file(filename):
    if not os.path.exists(filename):
        return False

    try:
        # Default is open for reading.
        with open(filename):
            pass

        return True
    except IOError:
        return False


def remove_comments(file):

    out = []
    comment = re.compile(";.*$")

    for l in file:
        out.append(comment.sub("", l.strip()))

    return list(filter(None, out))


def attempt_assemble(filename):

    with open(filename) as ifile:
        in_file = ifile.readlines()

    # 1st pass
    in_file = remove_comments(in_file)

    out_file_name = os.path.splitext(filename)[0] + ".bin"

    with open(out_file_name, 'wb') as ofile:
        print(in_file)

        label = re.compile('(.+):$')
        label_dict = {}
        label_less_prog = []
        prog = []

        # 2nd pass
        for l in in_file:

            m = label.match(l)
            if m:
                print("Found label: {}".format(m.group(1)))
                label_dict[m.group(1)] = len(label_less_prog)
                continue

            label_less_prog.append(l)

        # 3rd pass
        for i in range(len(label_less_prog)):
            l = label_less_prog[i]

            for k, v in label_dict.items():
                if k in l.split():
                    rel_jmp = int(v) - i - 1
                    l = l.replace(k, "{}".format(rel_jmp))

            prog.append(l)

        for p in prog:
            ofile.write(CMDParse.parse_cmd(p).bin)

        pass

    pass

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='My barebones MIPS assembler',
                                     description='')
    parser.add_argument(dest='files', type=str, nargs='*',
                        help="Files")
    parser.add_argument('-d', '--debug', action='store_true', dest='debug', default=False,
                        help='Debug mode.')

    args = parser.parse_args()

    if len(args.files) > 1:
        parser.error("Currently more than one assembly file is unsupported.")

    for f in args.files:
        if not is_valid_file(f):
            parser.error("{} cannot be opened.".format(f))

        attempt_assemble(f)

    print("Kappa")
