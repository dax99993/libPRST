# PRST Decoder/Encoder

Python scripts to decode and encode Valeton GP-200 .prst preset files.

## Overview

The GP-200 uses binary .prst files to store presets. These scripts convert between the binary format and human-readable JSON, making it possible to:

- Analyze preset structure
- Edit presets programmatically
- Understand the file format
- Create custom presets

## Usage

### Decoding (Binary → JSON)

Convert a single .prst file to JSON:

```bash
python3 libprst/decoder.py <input.prst> [output.json]
```

Example:
```bash
python3 libprst/decoder.py "examples/FactoryPresets200/01-B 50s Plexi.prst"
# Creates: examples/FactoryPresets200/01-B 50s Plexi.json
```

Batch decode all presets in a directory:
```bash
libprst/batch_decode.sh examples/FactoryPresets200/
```

### Encoding (JSON → Binary)

Convert a JSON file back to .prst binary:

```bash
python3 libprst/encoder.py <input.json> [output.prst]
```

Example:
```bash
python3 libprst/encoder.py "examples/FactoryPresets200/01-B 50s Plexi.json" "my_preset.prst"
```

## JSON Format

The decoded JSON contains the following structure:

```json
{
  "format": "GP-200 PRST v2",
  "header": {
    "magic": "TSRP",
    "version": 50331648,
    "product_id": "GP-2",
    "firmware_version": "00010100",
    "timestamp": 1805578016,
    "file_size": 1124
  },
  "metadata": {
    "constant": 2,
    "bpm": 88,
    "program_index": 1,
    "level": 120,
    "param4": 50,
    "param5": 0,
    "ir_or_preset": 5,
    "param7": 0
  },
  "name": "50s Plexi",
  "chain": {
    "program_index_repeat": 1,
    "module_count_info": [0, 4, 4, 4, 10],
    "order": [0, 1, 2, 3, 5, 6, 7, 8, 9, 0]
  },
  "modules": [
    {
      "index": 0,
      "slot": 0,
      "enabled": false,
      "effect_code": 25,
      "parameters": [50.0, 50.0, 55.0, 0.0, 0.0, 0.0, 0.0]
    }
    // ... more modules
  ],
  "controls": {
    "default_controls": [...],
    "assignments": [...],
    "toggles": [...]
  },
  "checksum": {
    "marker": 1168,
    "value": 13390
  }
}
```

### Fields

- **name**: Preset name (max ~60 characters)
- **metadata.bpm**: Tempo (default: 88)
- **metadata.program_index**: Bank/slot position (0-199)
- **metadata.level**: Overall volume level (0-127, default: 120)
- **metadata.ir_or_preset**: IR cabinet or effect preset ID
- **modules**: Array of up to 11 effect modules
  - **slot**: Module slot number (0-10)
  - **enabled**: Whether the module is active (true/false)
  - **effect_code**: Identifies the specific effect type
  - **parameters**: Array of floating-point effect parameters
- **controls**: Expression pedal and footswitch assignments
- **checksum**: File integrity check values

## Known Patterns

Based on analysis of factory presets:

1. **File Structure**:
   - Magic header: `TSRP` (PRST reversed)
   - Product ID: `GP-2` (GP-200 identifier, reversed)
   - Fixed file size: 1176 bytes (0x498)

2. **Module Layout**:
   - Modules identified by `0x14 0x44` marker
   - Variable spacing between modules
   - Up to 11 modules per preset
   - Each module: 64 bytes (0x40)

3. **Parameters**:
   - Stored as IEEE-754 32-bit floats (little-endian)
   - Common values: 50.0, 100.0, 120.0
   - Negative values possible (e.g., -20.0 for pan/offset)

4. **Effect Codes**:
   - Each effect has a unique code (e.g., 25, 27, 19, etc.)
   - Code determines available parameters
   - Mapping to effect names TBD (requires more testing)

## Development Status

**Working:**
- ✓ Decode .prst files to JSON
- ✓ Encode JSON back to .prst binary
- ✓ Preserve preset name, BPM, level
- ✓ Decode module structure and parameters
- ✓ Identify enabled/disabled modules

**In Progress:**
- ⚠ Round-trip encoding (some byte differences)
- ⚠ Effect code → effect name mapping
- ⚠ Parameter meaning documentation
- ⚠ Control table interpretation

**To Do:**
- ☐ Checksum validation/calculation
- ☐ Complete effect code database
- ☐ Parameter value ranges and meanings
- ☐ Expression pedal assignment details
- ☐ Footswitch configuration details
- ☐ IR cabinet file integration

## Contributing

To help map effect codes and parameters:

1. Create a preset on your GP-200
2. Save it to a .prst file
3. Decode it with this tool
4. Document what settings you used
5. Share the mapping!

## File Format Reference

See [docs/V2 Notes.md](docs/V2 Notes.md) for detailed format analysis.

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## License

See LICENSE file for details.
