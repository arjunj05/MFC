import re
import math
import dataclasses

from pathlib import Path


import common
import tests.test as test

from common import MFCException


@dataclasses.dataclass(repr=False)
class PackEntry:
    filepath: str
    doubles:  list

    def __repr__(self) -> str:
        return f"{self.filepath} {' '.join([ str(d) for d in self.doubles ])}"


@dataclasses.dataclass
class Pack:
    entries: list

    def save(self, filepath: str):
        common.file_write(filepath, '\n'.join([ str(e) for e in self.entries ]))


def load(filepath: str) -> Pack:
    entries: list = []

    for line in common.file_read(filepath).splitlines():
        if common.isspace(line):
            continue

        arr = line.split(' ')

        entries.append(PackEntry(
            filepath=arr[0],
            doubles=[ float(d) for d in arr[1:] ]
        ))

    return Pack(entries)


def generate(case: test.Case) -> Pack:
    entries = []

    case_dir = case.get_dirpath()
    D_dir    = f"{case_dir}/D/"

    for filepath in list(Path(D_dir).rglob("*.dat")):
        short_filepath = str(filepath).replace(f'{case_dir}/', '')

        data_content = common.file_read(filepath)
        
        # 2 or more (contiguous) spaces
        pattern = r"([ ]{2,})"
        
        numbers_str = re.sub(pattern, " ", data_content.replace('\n', '')).strip()
        
        doubles: list = [ float(e) for e in numbers_str.split(' ') ] 

        entries.append(PackEntry(short_filepath,doubles))

    return Pack(entries)


def check_tolerance(uuid: str, candidate: Pack, golden: Pack, tol: float) -> None:
    # Compare entry-count
    if len(candidate.entries) != len(golden.entries):
        raise MFCException(f"tests/{uuid}: Line count didn't match.")
    
    # For every entry in the golden's pack
    for gIndex, gEntry in enumerate(golden.entries):
        # Find the corresponding entry in the candidate's pack
        cIndex, cEntry = common.find(lambda i, e: e.filepath == gEntry.filepath, candidate.entries)

        if cIndex == None:
            raise MFCException(f"tests/{uuid}: No reference of {gEntry.filepath} in the candidate's pack.")
        
        filepath: str = gEntry.filepath

        # Compare variable-count
        if len(gEntry.doubles) != len(cEntry.doubles):
            raise MFCException(f"tests/{uuid}: Variable count didn't match for {filepath}.")

        # Check if each variable is within tolerance
        for valIndex, (gVal, cVal) in enumerate(zip(gEntry.doubles, cEntry.doubles)):
            if not math.isclose(gVal, cVal, rel_tol=tol, abs_tol=tol):
                raise MFCException(f"""\
tests/{uuid}: Variable n°{valIndex+1} (1-indexed) in {filepath} is not within tolerance ({tol}):
  - Candidate: {cVal}
  - Golden:    {gVal}
""")
