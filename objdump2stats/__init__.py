import argparse
import json
import logging
import string
import subprocess
import sys


class StdinLineReader:
    ARGS = None

    def __init__(self):
        self._process = None

    def __start(self):
        if self._process is None:
            self._process = subprocess.Popen(
                self.ARGS, stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )

    def __call__(self, symbol):
        self.__start()
        self._process.stdin.write(symbol.encode() + b"\n")
        self._process.stdin.flush()
        return self._process.stdout.readline().decode().strip()


class RustFiltDemangler(StdinLineReader):
    ARGS = ["rustfilt"]


class CppFiltDemangler(StdinLineReader):
    ARGS = ["c++filt"]


def cxxfilt_demangler(symbol):
    import cxxfilt

    return cxxfilt.demangle(symbol)


DEMANGLER = {
    "c++filt": CppFiltDemangler(),
    "cxxfilt": cxxfilt_demangler,
    "rustfilt": RustFiltDemangler(),
}


def parse_objdump(infile, logger, demangle=None):
    current_section = "<unknown>"
    current_symbol = None
    stats = {"symbols": {}}

    for line in infile:
        words = line.strip().split()
        if (
            len(words) >= 4
            and words[0] == "Disassembly"
            and words[1] == "of"
            and words[2] == "section"
            and words[3][-1] == ":"
        ):
            current_section = words[3][:-1]
        elif len(words) >= 1 and words[1].startswith("<") and words[-1].endswith(">:"):
            address = words[0]
            symbol = " ".join(words[1:])[1:-2]
            if demangle:
                symbol = DEMANGLER[demangle](symbol)
            current_symbol = current_section + "/" + symbol
            if current_symbol in stats["symbols"]:
                logger.warning(
                    'Found duplicated symbol "{}", statistics will be grouped together.'.format(
                        current_symbol
                    )
                )
            else:
                stats["symbols"][current_symbol] = {
                    "instructions": {},
                    "section": current_section,
                }
        elif current_symbol and len(words) > 4:
            idx = 2
            while (
                idx < len(words)
                and len(words[idx]) == 2
                and words[idx][0] in string.hexdigits
                and words[idx][1] in string.hexdigits
            ):
                idx += 1
            if idx < len(words):
                instruction = words[idx]
                instruction_set = stats["symbols"][current_symbol]["instructions"]
                instruction_set[instruction] = instruction_set.get(instruction, 0) + 1

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Compute statistics from objdump disassembly output"
    )
    parser.add_argument("-s", "--sort", action="store_true")
    parser.add_argument(
        "infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin
    )
    parser.add_argument(
        "-o", "--outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    parser.add_argument(
        "-l", "--logfile", nargs="?", type=argparse.FileType("w"), default=sys.stderr
    )
    parser.add_argument("--demangle", type=str, choices=DEMANGLER.keys())

    args = parser.parse_args()
    logging.basicConfig(stream=args.logfile)
    stats = parse_objdump(
        args.infile, logging.getLogger("objdump2stats"), args.demangle
    )
    json.dump(stats, args.outfile, sort_keys=args.sort)


if __name__ == "__main__":
    main()
