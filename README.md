# PRSTDecoder
Valeton GP-200 binary PRST file decoder and encoder

## Quick Start

Decode a preset file to readable JSON:
```bash
python3 libprst/prst_decoder.py examples/FactoryPresets200/01-B\ 50s\ Plexi.prst
```

Encode a JSON file back to binary:
```bash
python3 libprst/prst_encoder.py examples/FactoryPresets200/01-B\ 50s\ Plexi.json my_preset.prst
```

Batch decode all presets in a directory:
```bash
libprst/batch_decode.sh examples/FactoryPresets200/
```

## Documentation

- [Decoder/Encoder Usage Guide](DECODER_README.md) - How to use the tools
- [Format Patterns](docs/Format_Patterns.md) - Detailed file format analysis
- [V1 Notes](docs/V1%20Notes.md) - GP-100 XML format
- [V2 Notes](docs/V2%20Notes.md) - GP-200 binary format

## Features

- ✓ Decode .prst binary files to human-readable JSON
- ✓ Encode JSON back to .prst binary format
- ✓ Preserve preset name, BPM, effect modules, parameters
- ✓ Identify enabled/disabled effects
- ✓ Extract control and routing configuration

## Requirements

- Python 3.6+ (no external dependencies)
