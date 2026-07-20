#!/usr/bin/env python3
"""
Valeton GP-200 PRST File Decoder
Converts binary .prst files to human-readable JSON format
"""

import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List


class PRSTDecoder:
    """Decoder for Valeton GP-200 .prst preset files"""

    MAGIC = b'TSRP'  # 'PRST' reversed
    PRODUCT_ID = b'2-PG'  # 'GP-2' reversed
    PARM_MARKER = b'MRAP'  # 'PARM' reversed
    FILE_SIZE = 0x498  # 1176 bytes standard size
    FILE_LONG_SIZE = 0x4C8 # 1224 bytes long size

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = self.filepath.read_bytes()

    def decode(self) -> Dict[str, Any]:
        """Decode the entire .prst file"""
        if len(self.data) != self.FILE_SIZE and len(self.data) != self.FILE_LONG_SIZE:
            raise ValueError(f"File size incorrect: {len(self.data)} bytes, expected {self.FILE_SIZE} or {self.FILE_LONG_SIZE}")

        print(len(self.data))

        result = {
            "header": self._decode_header(),
            "metadata": self._decode_metadata(),
            "name": self._decode_name(),
            "author": self._decode_author(),
            "note": self._decode_note(),
            "chain": self._decode_chain(),
            "modules": self._decode_modules(),
            "controls": self._decode_controls(),
            "checksum": self._decode_checksum()
        }

        return result

    def _read_u32(self, offset: int) -> int:
        """Read 32-bit unsigned little-endian integer"""
        return struct.unpack('<I', self.data[offset:offset+4])[0]

    def _read_u16(self, offset: int) -> int:
        """Read 16-bit unsigned little-endian integer"""
        return struct.unpack('<H', self.data[offset:offset+2])[0]

    def _read_u8(self, offset: int) -> int:
        """Read 8-bit unsigned integer"""
        return self.data[offset]

    def _read_float(self, offset: int) -> float:
        """Read 32-bit IEEE-754 float"""
        return struct.unpack('<f', self.data[offset:offset+4])[0]

    @staticmethod
    def _decode_ascii(str_bytes: bytes) -> str:
        """Read ASCII-encoded string"""
        # Find null terminator
        null_pos = str_bytes.find(b'\x00')
        if null_pos >= 0:
            str_bytes = str_bytes[:null_pos]
        return str_bytes.decode('ascii', errors='replace').strip()

    def _decode_header(self) -> Dict[str, Any]:
        """Decode file header (0x00-0x2F)"""
        magic = self.data[0:4]
        if magic != self.MAGIC:
            raise ValueError(f"Invalid magic: {magic}, expected {self.MAGIC}")

        version = self._read_u32(0x08)
        product_id = self.data[0x10:0x14][::-1].decode('ascii')  # Reverse bytes
        fw_version = self.data[0x14:0x18].hex()
        timestamp = self._read_u32(0x18)
        file_size = self._read_u32(0x24)

        return {
            "magic": magic.decode('ascii'),
            "version": version,
            "product_id": product_id,
            "firmware_version": fw_version,
            "timestamp": timestamp,
            "file_size": file_size
        }

    def _decode_metadata(self) -> Dict[str, Any]:
        """Decode metadata block (0x30-0x43)"""
        offset = 0x30
        # Verify header
        header = self._read_u16(offset)
        if header != 0x0002:
            raise ValueError(f"Invalid module header at {offset:#x}: {header:#x}")

        marker = self._read_u16(offset + 2)
        if marker != 0x0058:
            raise ValueError(f"Invalid module marker at {offset+2:#x}: {marker:#x}")

        # Eight 16-bit values
        vals = [self._read_u16(offset + 4 + i*2) for i in range(8)]

        return {
            "program_index": vals[0],  # Bank/slot position
            "bpm": vals[1],     # e.g., 0x78 = 120
            "volume": vals[2],    # e.g., 0x32 = 50
            "pan": vals[3],    # Usually 0
            "category": vals[4],  # Varies: IR or effect chain preset
            # FX Loop params
            "send_level": vals[5],     #
            "return_level": vals[6],  #
            "mode": vals[7],  # 0 -> parallel ; 1 -> series
        }

    def _decode_name(self) -> str:
        """Decode patch name (0x44-0x53)"""
        name_bytes = self.data[0x44:0x54]
        return self._decode_ascii(name_bytes)

    def _decode_author(self) -> str:
        """Decode patch author (0x54-0x64)"""
        author_bytes = self.data[0x54:0x64]
        return self._decode_ascii(author_bytes)

    def _decode_note(self) -> str:
        """Decode patch note (0x64-0x81)"""
        note_bytes = self.data[0x64:0x82]
        return self._decode_ascii(note_bytes)

    def _decode_chain(self) -> Dict[str, Any]:
        """Decode module chain/order (0x82-0x9F)"""
        # Last 2 bytes before chain data are constant: 0x0800 0x1000
        chain_start = 0x90
        chain_bytes = self.data[chain_start:chain_start+16]

        return {
            "program_index_repeat": chain_bytes[0],
            # chain_bytes[1], # Zero byte separator
            "send_position": chain_bytes[2],
            "return_position": chain_bytes[3],
            "order": list(chain_bytes[4:15])
            # chain_bytes[15] # Zero byte separator
        }

    def _decode_modules(self) -> List[Dict[str, Any]]:
        """Decode module blocks - scan for 0x1400 0x4400 markers"""
        modules = []

        # Search for module markers from 0xA0 to 0x3B7 (start of control tables)
        base_offset = 0xA0
        for i in range(11):
            offset = base_offset + (i * 72)
            # print(f"Effect Module Offset: {offset:04X}")
            module = self._decode_module(offset, i)
            modules.append(module)
            # print(module)

        # Sort by slot number
        # modules.sort(key=lambda m: m['slot'])

        return modules

    def _decode_module(self, offset: int, index: int) -> Dict[str, Any]:
        """Decode a single module block"""
        # Verify header
        header = self._read_u16(offset)
        if header != 0x0014:
            raise ValueError(f"Invalid module header at {offset:#x}: {header:#x}")

        marker = self._read_u16(offset + 2)
        if marker != 0x0044:
            raise ValueError(f"Invalid module marker at {offset:#x}: {marker:#x}")

        # Slot and enabled flag
        slot = self.data[offset + 4]
        enabled = self.data[offset + 5]

        # Effect code
        effect_code = self._read_u32(offset + 8)

        # Parameters (up to 10 floats starting at offset + 12)
        params = []
        for i in range(15):
            param_offset = offset + 12 + (i * 4)
            value = self._read_float(param_offset)
            if value != 0.0 or i < 7:  # Include first 7 even if zero
                params.append(round(value, 6))
            # print(f"Effect Module Param Offset: {param_offset:04X}")

        return {
            "index": index,
            "slot": slot,
            "enabled": bool(enabled),
            "effect_code": effect_code,
            "parameters": params
        }

    def _decode_controls(self) -> Dict[str, Any]:
        """Decode control/routing tables (starts 0x3B8)"""
        base_offset = 0x3B8

        # Nine EXP records each 16 bytes
        default_exps = []
        for i in range(9):
            offset = base_offset + (i * 16)
            header = self._read_u16(offset)
            marker = self._read_u16(offset + 2)
            if header != 0x000C and marker != 0x000C:
                break

            exp_id = (self._read_u8(offset + 4) >> 4) & 0x0F
            exp_param_id = self._read_u8(offset + 4) & 0x0F

            default_exps.append({
                "id": exp_id,
                "param": exp_param_id,
                "module": self._read_u8(offset + 5),
                "parameter": self._read_u8(offset + 6),
                "max_value": self._read_float(offset + 8),
                "min_value": self._read_float(offset + 12),
            })

            # print(default_exps)

        # Three Knob records each 8 bytes
        knobs_base = base_offset + (9 * 16)
        knobs = []
        for i in range(3):
            offset = knobs_base + (i * 8)
            header = self._read_u16(offset)
            marker = self._read_u16(offset + 2)
            if header != 0x0010 and marker != 0x0004:
                break

            id = self._read_u8(offset + 4)
            module = self._read_u8(offset + 5)
            param_id = self._read_u8(offset + 6)
            knobs.append({
                "id": id,
                "module": module,
                "param_id": param_id,
            })

        # Four or Eight Ctrl records each 12 bytes
        ctrls_base = knobs_base + (3 * 8)
        ctrls = []
        num_ctrls = 4 if len(self.data) == self.FILE_SIZE else 8
        # print("Num of controls: ", num_ctrls)

        for i in range(num_ctrls):
            offset = ctrls_base + (i * 12)
            header = self._read_u16(offset)
            marker = self._read_u16(offset + 2)
            if header != 0x000F and marker != 0x0008:
                break

            ctrl_id = self._read_u8(offset + 4)
            mode = self._read_u8(offset + 5)
            assigns = self._read_u16(offset + 8) # Effect slot as bit flag
            # print(f"Assigns {assigns:03X}")

            ctrls.append({
                "id": ctrl_id,
                "mode": mode,
                "assigns": assigns,
            })

        return {
            "exps": default_exps,
            "knobs": knobs,
            "ctrls": ctrls
        }

    def _decode_checksum(self) -> Dict[str, Any]:
        """Decode checksum/trailer"""
        # Last 8 bytes
        offset = len(self.data) - 8
        marker = self._read_u32(offset)
        checksum = self._read_u32(offset + 4)

        return {
            "marker": marker,
            "value": checksum
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: prst_decoder.py <input.prst> [output.json]")
        print("  If output.json is not specified, uses <input>.json")
        sys.exit(1)

    input_path = sys.argv[1]

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = Path(input_path).with_suffix('.json')

    try:
        decoder = PRSTDecoder(input_path)
        result = decoder.decode()

        # Write JSON with nice formatting
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"✓ Decoded: {input_path}")
        print(f"  → {output_path}")
        print(f"  Preset: {result['name']}")
        print(f"  BPM: {result['metadata']['bpm']}")
        print(f"  Modules: {len([m for m in result['modules'] if m['enabled']])} enabled")

    except Exception as e:
        print(f"✗ Error decoding {input_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
