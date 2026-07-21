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
    program_index: int
    bpm: int
    volume: int
    pan: int
    category: int # or a custom type when i know what each value means
    fxloop_send_level: int
    fxloop_return_level: int
    fxloop_mode: int
    name: str
    author: str
    note: str

@dataclass
class Chain:
    fxloop_send_position: int
    fxloop_return_position: int
    order: List[int]

@dataclass
class EffectModule:
    slot: int
    id: int
    enabled: bool
    parameters: List[float]

@dataclass
class Exp:
    id: int
    parameter_id: int
    module_id: int
    module_parameter_id: int
    max_value: float # When lifted
    min_value: float # When pressed

@dataclass
class Knob:
    id: int
    module_id: int
    parameter_id: int

@dataclass
class Ctrl:
    id: int
    mode: int
    binds: List[int]
    # binds: int

@dataclass
class Preset:
    header: Header
    metadata: Metadata
    chain: Chain
    modules: List[EffectModule]
    exps: List[Exp]
    knobs: List[Knob]
    ctrls: List[Ctrl]
    checksum: int
