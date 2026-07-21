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
    FILE_LONG_SIZE = 0x4C8 # 1224 bytes long size

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.buffer = bytearray(self.FILE_LONG_SIZE)

    def encode(self) -> bytes:
        """Encode JSON data to binary .prst format"""
        self._encode_header()
        self._encode_metadata()
        self._encode_name()
        self._encode_author()
        self._encode_note()
        self._encode_chain()
        self._encode_modules()
        self._encode_exps()
        self._encode_knobs()
        self._encode_ctrls()
        self._encode_checksum()

        return bytes(self.buffer)

    def _write_u32(self, offset: int, value: int):
        """Write 32-bit unsigned little-endian integer"""
        struct.pack_into('<I', self.buffer, offset, value)

    def _write_u16(self, offset: int, value: int):
        """Write 16-bit unsigned little-endian integer"""
        struct.pack_into('<H', self.buffer, offset, value)

    def _write_u16_big(self, offset: int, value: int):
        """Write 16-bit unsigned little-endian integer"""
        struct.pack_into('>H', self.buffer, offset, value)

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
        self._write_u32(0x08, header.get('version', 6))

        # Zero dword
        self._write_u32(0x0C, 0)

        # Product ID (reversed)
        product_id = header.get('product_id', 'GP-2')
        self.buffer[0x10:0x14] = product_id.encode('ascii')[::-1]

        # Firmware version
        fw_hex = header.get('firmware_version', '00010100')
        self.buffer[0x14:0x18] = bytes.fromhex(fw_hex)

        # Timestamp
        # self._write_u32(0x18, header.get('timestamp', 0x6b9eef20))
        self._write_u32(0x18, header.get('timestamp', 0))

        # Constant dword
        # self._write_u32(0x1C, 1)
        # self._write_u32(0x1C, 0xd8ed6f02)
        self._write_u32(0x1C, 0x026fedd8)

        # File structure markers
        self._write_u32(0x20, 0x28)
        # file_size = header.get('file_size', 0x464) # TODO: get num of ctrls to determine if standard or long filesize is used
        # self._write_u32(0x24, file_size)
        self._write_u16(0x24, self.FILE_LONG_SIZE - 52)
        self.buffer[0x28:0x2C] = self.PARM_MARKER
        self._write_u32(0x2C, self.FILE_LONG_SIZE - 52)

    def _encode_metadata(self):
        """Encode metadata block (0x30-0x3F)"""
        meta = self.data.get('metadata', {})

        # Eight 16-bit values
        self._write_u16(0x30, 0x0002)
        self._write_u16(0x32, 0x0058)
        self._write_u16(0x34, meta.get('program_index', 0))
        self._write_u16(0x36, meta.get('bpm', 120))
        self._write_u16(0x38, meta.get('volume', 50))
        self._write_u16(0x3A, meta.get('pan', 0))
        self._write_u16(0x3C, meta.get('category', 0))
        self._write_u16(0x3E, meta.get('fxloop_send_level', 0))
        self._write_u16(0x40, meta.get('fxloop_return_level', 0))
        self._write_u16(0x42, meta.get('fxloop_mode', 0))
        # self._write_u16(0x3E, meta.get('name', 0))
        # self._write_u16(0x3E, meta.get('author', 0))
        # self._write_u16(0x3E, meta.get('note', 0))

    def _encode_name(self):
        """Encode patch name (0x44-0x53)"""
        meta = self.data.get('metadata', {})
        name = meta.get('name', 'Untitled')
        name_bytes = name.encode('ascii', errors='replace')[:16]  # Max 16 characters
        self.buffer[0x44:0x44+len(name_bytes)] = name_bytes
        # Rest is zero-padded (already initialized)

    def _encode_author(self):
        """Encode patch name (0x54-0x63)"""
        meta = self.data.get('metadata', {})
        author = meta.get('author', '')
        author_bytes = author.encode('ascii', errors='replace')[:16]  # Max 16 characters
        self.buffer[0x54:0x54+len(author_bytes)] = author_bytes
        # Rest is zero-padded (already initialized)

    def _encode_note(self):
        """Encode patch name (0x64-0x81)"""
        meta = self.data.get('metadata', {})
        note = meta.get('note', '')
        note_bytes = note.encode('ascii', errors='replace')[:30]  # Max 30 characters
        self.buffer[0x54:0x54+len(note_bytes)] = note_bytes
        # Rest is zero-padded (already initialized)

    def _encode_chain(self):
        """Encode module chain/order (0x80-0x9F)"""
        meta = self.data.get('metadata', {})
        chain = self.data.get('chain', {})

        # Constants at 0x88 (header and mark)
        self._write_u16(0x8C, 0x0008)
        self._write_u16(0x8E, 0x0010)

        # Chain data at 0x90
        self.buffer[0x90] = meta.get('program_index', 0)

        self.buffer[0x92] = chain.get('fxloop_send_position', 4)
        self.buffer[0x93] = chain.get('fxloop_return_position', 4)

        order = chain.get('order', list(range(11)))
        for i, val in enumerate(order[:11]):
            self.buffer[0x94 + i] = val

    def _encode_modules(self):
        """Encode module blocks (11 modules, 72 bytes each)"""
        modules = self.data.get('modules', [])
        base_offset = 0xA0

        for i in range(11):
            offset = base_offset + (i * 72)

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
        self._write_u32(offset + 8, module.get('id', 0))

        # Parameters (up to 10 floats)
        params = module.get('parameters', [])
        for i in range(15):
            param_offset = offset + 12 + (i * 4)
            self._write_float(param_offset, params[i])

    def _encode_empty_module(self, offset: int):
        """Encode an empty/disabled module block"""
        # Just write the header and zeros
        self._write_u16(offset, 0x0014)
        self._write_u16(offset + 2, 0x0044)
        self._write_u16(offset + 6, 0x000F)

    def _encode_exps(self):
        """Encode EXP pedal"""
        base = 0x3B8

        # Nine EXP settings (3 parameters for each pedal mode)
        exps = self.data.get('exps', [])
        for i in range(9):
            offset = base + (i * 16)
            self._write_u16(offset, 0x000C)
            self._write_u16(offset + 2, 0x000C)

            if i < len(exps):
                exp = exps[i]
                self.buffer[offset + 4] = (exp['id'] << 4) | exp['parameter_id']
                self.buffer[offset + 5] = exp['module_id']
                self.buffer[offset + 6] = exp['module_parameter_id']
                self._write_float(offset + 8, exp['max_value'])
                self._write_float(offset + 12, exp['min_value'])
            else:
                # Default values
                self.buffer[offset + 4] = ((i // 3) << 4) | (i % 3)
                self.buffer[offset + 5] = 255 # OFF
                self.buffer[offset + 6] = 0
                self._write_float(offset + 8, 0)
                self._write_float(offset + 12, 0)


    def _encode_knobs(self):
        """Encode Knobs"""
        base_offset = 0x448
        # Three assignments
        knobs = self.data.get('knobs', [])
        for i in range(3):
            offset = base_offset + (i * 8)
            self._write_u16(offset, 0x0010)
            self._write_u16(offset + 2, 0x0004)

            if i < len(knobs):
                knob = knobs[i]
                self.buffer[offset + 4] = knob.get('id', 0)
                self.buffer[offset + 5] = knob.get('module_id', 0)
                self.buffer[offset + 6] = knob.get('parameter_id', 0)
            else:
                self.buffer[offset + 4] = i
                self.buffer[offset + 5] = 255 # OFF
                self.buffer[offset + 6] = 0

    def _encode_ctrls(self):
        """Encode Ctrls"""
        base_offset = 0x460
        # Eight ctrls but only four may be present
        ctrls = self.data.get('ctrls', [])
        for i in range(8):
            offset = base_offset + (i * 12)
            self._write_u16(offset, 0x000F)
            self._write_u16(offset + 2, 0x0008)

            if i < len(ctrls):
                ctrl = ctrls[i]
                self.buffer[offset + 4] = ctrl.get('id', 0)
                self.buffer[offset + 5] = ctrl.get('mode', 0)
                self._write_u16(offset + 8, ctrl.get('binds', 0))
            else:
                self.buffer[offset + 4] = i
                self.buffer[offset + 5] = 0
                self._write_u16(offset + 8, 0)

    def _encode_checksum(self):
        """Encode checksum/trailer"""
        offset = len(self.buffer) - 8
        print(offset, offset + 6)
        self._write_u16(offset, offset)
        self._write_u16_big(offset + 6, sum(self.buffer) & 0xFFFF)


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
