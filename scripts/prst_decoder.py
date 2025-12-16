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

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = self.filepath.read_bytes()

    def decode(self) -> Dict[str, Any]:
        """Decode the entire .prst file"""
        if len(self.data) < self.FILE_SIZE:
            raise ValueError(f"File too small: {len(self.data)} bytes, expected {self.FILE_SIZE}")

        result = {
            "format": "GP-200 PRST v2",
            "header": self._decode_header(),
            "metadata": self._decode_metadata(),
            "name": self._decode_name(),
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

    def _read_float(self, offset: int) -> float:
        """Read 32-bit IEEE-754 float"""
        return struct.unpack('<f', self.data[offset:offset+4])[0]

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
        """Decode metadata block (0x30-0x3F)"""
        # Eight 16-bit values
        vals = [self._read_u16(0x30 + i*2) for i in range(8)]

        return {
            "constant": vals[0],  # Always 0x0002
            "bpm": vals[1],       # e.g., 0x58 = 88 BPM
            "program_index": vals[2],  # Bank/slot position
            "level": vals[3],     # e.g., 0x78 = 120
            "param4": vals[4],    # e.g., 0x32 = 50
            "param5": vals[5],    # Usually 0
            "ir_or_preset": vals[6],  # Varies: IR or effect chain preset
            "param7": vals[7]     # Usually 0
        }

    def _decode_name(self) -> str:
        """Decode patch name (0x40-0x7F)"""
        # Name starts at 0x44 (skip 4 zero bytes)
        name_bytes = self.data[0x44:0x80]
        # Find null terminator
        null_pos = name_bytes.find(b'\x00')
        if null_pos >= 0:
            name_bytes = name_bytes[:null_pos]
        return name_bytes.decode('ascii', errors='replace').strip()

    def _decode_chain(self) -> Dict[str, Any]:
        """Decode module chain/order (0x80-0x9F)"""
        # Last 2 bytes before chain data are constant: 0x0800 0x1000
        chain_start = 0x90
        chain_bytes = self.data[chain_start:chain_start+16]

        return {
            "program_index_repeat": chain_bytes[0],
            "module_count_info": list(chain_bytes[1:6]),
            "order": list(chain_bytes[6:])
        }

    def _decode_modules(self) -> List[Dict[str, Any]]:
        """Decode module blocks - scan for 0x1400 0x4400 markers"""
        modules = []

        # Search for module markers from 0xA0 to 0x3B0 (start of control tables)
        offset = 0xA0
        while offset < 0x3B0:
            # Look for module header
            if offset + 4 <= len(self.data):
                header = self._read_u16(offset)
                marker = self._read_u16(offset + 2)

                if header == 0x0014 and marker == 0x0044:
                    # Found a module
                    slot = self.data[offset + 4]
                    module = self._decode_module(offset, slot)
                    modules.append(module)
                    offset += 0x40  # Modules are 0x40 bytes
                    continue

            offset += 1  # Move to next byte

        # Sort by slot number
        modules.sort(key=lambda m: m['slot'])

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
        for i in range(10):
            param_offset = offset + 12 + (i * 4)
            value = self._read_float(param_offset)
            if value != 0.0 or i < 7:  # Include first 7 even if zero
                params.append(round(value, 6))

        return {
            "index": index,
            "slot": slot,
            "enabled": bool(enabled),
            "effect_code": effect_code,
            "parameters": params
        }

    def _decode_controls(self) -> Dict[str, Any]:
        """Decode control/routing tables (starts ~0x3B0)"""
        base = 0x3B0

        # Nine 0C00 0C00 records
        default_controls = []
        for i in range(9):
            offset = base + (i * 12)
            header = self._read_u16(offset)
            if header != 0x000C:
                break

            ctrl_id = self._read_u16(offset + 4)
            value = self._read_float(offset + 8)
            default_controls.append({
                "id": ctrl_id,
                "value": round(value, 2)
            })

        # Three 1000 0400 records (footswitch/expression assignments?)
        assignments_base = base + (9 * 12)
        assignments = []
        for i in range(3):
            offset = assignments_base + (i * 8)
            header = self._read_u16(offset)
            if header != 0x0010:
                break

            target = self._read_u16(offset + 4)
            state = self._read_u16(offset + 6)
            assignments.append({
                "target": target,
                "state": state
            })

        # Four 0F00 0800 records (toggle states?)
        toggles_base = assignments_base + (3 * 8)
        toggles = []
        for i in range(4):
            offset = toggles_base + (i * 8)
            header = self._read_u16(offset)
            if header != 0x000F:
                break

            toggle_id = self._read_u16(offset + 4)
            value = self._read_u32(offset + 6)
            toggles.append({
                "id": toggle_id,
                "value": value
            })

        return {
            "default_controls": default_controls,
            "assignments": assignments,
            "toggles": toggles
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
