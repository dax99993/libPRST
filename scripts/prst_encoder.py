#!/usr/bin/env python3
"""
Valeton GP-200 PRST File Encoder
Converts JSON format back to binary .prst files
"""

import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict


class PRSTEncoder:
    """Encoder for Valeton GP-200 .prst preset files"""

    MAGIC = b'TSRP'  # 'PRST' reversed
    PRODUCT_ID = b'2-PG'  # 'GP-2' reversed
    PARM_MARKER = b'MRAP'  # 'PARM' reversed
    FILE_SIZE = 0x498  # 1176 bytes standard size

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.buffer = bytearray(self.FILE_SIZE)

    def encode(self) -> bytes:
        """Encode JSON data to binary .prst format"""
        self._encode_header()
        self._encode_metadata()
        self._encode_name()
        self._encode_chain()
        self._encode_modules()
        self._encode_controls()
        self._encode_checksum()

        return bytes(self.buffer)

    def _write_u32(self, offset: int, value: int):
        """Write 32-bit unsigned little-endian integer"""
        struct.pack_into('<I', self.buffer, offset, value)

    def _write_u16(self, offset: int, value: int):
        """Write 16-bit unsigned little-endian integer"""
        struct.pack_into('<H', self.buffer, offset, value)

    def _write_float(self, offset: int, value: float):
        """Write 32-bit IEEE-754 float"""
        struct.pack_into('<f', self.buffer, offset, value)

    def _encode_header(self):
        """Encode file header (0x00-0x2F)"""
        header = self.data.get('header', {})

        # Magic
        self.buffer[0:4] = self.MAGIC

        # Zero dword
        self._write_u32(0x04, 0)

        # Version
        self._write_u32(0x08, header.get('version', 3))

        # Zero dword
        self._write_u32(0x0C, 0)

        # Product ID (reversed)
        product_id = header.get('product_id', 'GP-2')
        self.buffer[0x10:0x14] = product_id.encode('ascii')[::-1]

        # Firmware version
        fw_hex = header.get('firmware_version', '00010100')
        self.buffer[0x14:0x18] = bytes.fromhex(fw_hex)

        # Timestamp
        self._write_u32(0x18, header.get('timestamp', 0x6b9eef20))

        # Constant dword
        self._write_u32(0x1C, 1)

        # File structure markers
        self._write_u32(0x20, 0x28)
        file_size = header.get('file_size', 0x464)
        self._write_u32(0x24, file_size)
        self.buffer[0x28:0x2C] = self.PARM_MARKER
        self._write_u32(0x2C, file_size)

    def _encode_metadata(self):
        """Encode metadata block (0x30-0x3F)"""
        meta = self.data.get('metadata', {})

        # Eight 16-bit values
        self._write_u16(0x30, meta.get('constant', 2))
        self._write_u16(0x32, meta.get('bpm', 120))
        self._write_u16(0x34, meta.get('program_index', 0))
        self._write_u16(0x36, meta.get('level', 120))
        self._write_u16(0x38, meta.get('param4', 50))
        self._write_u16(0x3A, meta.get('param5', 0))
        self._write_u16(0x3C, meta.get('ir_or_preset', 0))
        self._write_u16(0x3E, meta.get('param7', 0))

    def _encode_name(self):
        """Encode patch name (0x40-0x7F)"""
        name = self.data.get('name', 'Untitled')
        name_bytes = name.encode('ascii', errors='replace')[:60]  # Max 60 bytes (64 - 4 zero prefix)
        # Name starts at 0x44 (skip 4 zero bytes at 0x40)
        self.buffer[0x44:0x44+len(name_bytes)] = name_bytes
        # Rest is zero-padded (already initialized)

    def _encode_chain(self):
        """Encode module chain/order (0x80-0x9F)"""
        chain = self.data.get('chain', {})

        # Constants at 0x88
        self._write_u16(0x88, 0x0008)
        self._write_u16(0x8A, 0x0010)

        # Chain data at 0x90
        self.buffer[0x90] = chain.get('program_index_repeat', 0)

        module_count = chain.get('module_count_info', [0, 4, 4, 4, 10])
        for i, val in enumerate(module_count[:5]):
            self.buffer[0x91 + i] = val

        order = chain.get('order', list(range(10)))
        for i, val in enumerate(order[:10]):
            self.buffer[0x96 + i] = val

    def _encode_modules(self):
        """Encode module blocks (11 modules, 0x40 bytes each)"""
        modules = self.data.get('modules', [])
        base_offset = 0xA0

        for i in range(11):
            offset = base_offset + (i * 0x40)

            if i < len(modules):
                self._encode_module(offset, modules[i])
            else:
                # Empty module
                self._encode_empty_module(offset)

    def _encode_module(self, offset: int, module: Dict[str, Any]):
        """Encode a single module block"""
        # Header
        self._write_u16(offset, 0x0014)
        self._write_u16(offset + 2, 0x0044)

        # Slot and enabled flag
        self.buffer[offset + 4] = module.get('slot', 0)
        self.buffer[offset + 5] = 1 if module.get('enabled', False) else 0

        # Constant
        self._write_u16(offset + 6, 0x000F)

        # Effect code
        self._write_u32(offset + 8, module.get('effect_code', 0))

        # Parameters (up to 10 floats)
        params = module.get('parameters', [])
        for i in range(10):
            param_offset = offset + 12 + (i * 4)
            if i < len(params):
                self._write_float(param_offset, params[i])
            else:
                self._write_float(param_offset, 0.0)

    def _encode_empty_module(self, offset: int):
        """Encode an empty/disabled module block"""
        # Just write the header and zeros
        self._write_u16(offset, 0x0014)
        self._write_u16(offset + 2, 0x0044)
        self._write_u16(offset + 6, 0x000F)

    def _encode_controls(self):
        """Encode control/routing tables"""
        controls = self.data.get('controls', {})
        base = 0x3B0

        # Nine default controls
        default_controls = controls.get('default_controls', [])
        for i in range(9):
            offset = base + (i * 12)
            self._write_u16(offset, 0x000C)
            self._write_u16(offset + 2, 0x000C)

            if i < len(default_controls):
                ctrl = default_controls[i]
                self._write_u16(offset + 4, ctrl.get('id', 0))
                self._write_u32(offset + 6, 0)  # Padding
                self._write_float(offset + 8, ctrl.get('value', 100.0))
            else:
                # Default values
                self._write_u16(offset + 4, 0x00FF if i > 0 else 0x000A)
                self._write_u32(offset + 6, 0)
                self._write_float(offset + 8, 100.0)

        # Three assignments
        assignments_base = base + (9 * 12)
        assignments = controls.get('assignments', [])
        for i in range(3):
            offset = assignments_base + (i * 8)
            self._write_u16(offset, 0x0010)
            self._write_u16(offset + 2, 0x0004)

            if i < len(assignments):
                assign = assignments[i]
                self._write_u16(offset + 4, assign.get('target', 0))
                self._write_u16(offset + 6, assign.get('state', 0))
            else:
                self._write_u16(offset + 4, 0)
                self._write_u16(offset + 6, 0)

        # Four toggles
        toggles_base = assignments_base + (3 * 8)
        toggles = controls.get('toggles', [])
        for i in range(4):
            offset = toggles_base + (i * 8)
            self._write_u16(offset, 0x000F)
            self._write_u16(offset + 2, 0x0008)

            if i < len(toggles):
                toggle = toggles[i]
                self._write_u16(offset + 4, toggle.get('id', 0))
                self._write_u16(offset + 6, 0)
                self._write_u32(offset + 6, toggle.get('value', 0))
            else:
                self._write_u16(offset + 4, i)
                self._write_u16(offset + 6, 0)
                self._write_u32(offset + 6, 0)

    def _encode_checksum(self):
        """Encode checksum/trailer"""
        checksum_data = self.data.get('checksum', {})

        offset = len(self.buffer) - 8
        self._write_u32(offset, checksum_data.get('marker', 0x00000490))
        self._write_u32(offset + 4, checksum_data.get('value', 0))


def main():
    if len(sys.argv) < 2:
        print("Usage: prst_encoder.py <input.json> [output.prst]")
        print("  If output.prst is not specified, uses <input>.prst")
        sys.exit(1)

    input_path = sys.argv[1]

    # Determine output path
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = Path(input_path).with_suffix('.prst')

    try:
        # Load JSON
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Encode
        encoder = PRSTEncoder(data)
        binary_data = encoder.encode()

        # Write binary file
        with open(output_path, 'wb') as f:
            f.write(binary_data)

        print(f"✓ Encoded: {input_path}")
        print(f"  → {output_path}")
        print(f"  Preset: {data.get('name', 'Untitled')}")
        print(f"  Size: {len(binary_data)} bytes")

    except Exception as e:
        print(f"✗ Error encoding {input_path}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
