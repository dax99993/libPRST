from dataclasses import dataclass
from typing import List

@dataclass
class Header:
    magic: str
    version: int
    product_id: str
    firmware_version: str # or int
    timestamp: int
    file_size: int

@dataclass
class Metadata:
    constant: int #
    bpm: int
    program_index: int
    level: int
    param4: int
    param5: int
    ir_or_preset: int
    param7: int
    name: str
    author: str
    note: str
    category: int # or a custom type when i know what each value means

@dataclass
class Chain:
    loop_in: int
    loop_out: int

    order: List[int]

@dataclass
class Module:
    id: int

@dataclass
class ExpModule:
    id: int

@dataclass
class Knob:
    id: int

@dataclass
class Ctrl:
    id: int

@dataclass
class Preset:
    header: Header
    metadata: Metadata
    chain: Chain
    modules: List[Module]
    exps: List[ExpModule]
    knobs: List[Knob]
    ctrls: List[Ctrl]
    checksum: int
