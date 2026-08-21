# libPRST

Valeton GP-200 binary PRST file codec library.

Thanks to mikeliddle for the base project and all the factory presets!

## Quick Start

- Decode a preset file to readable JSON:
- Encode a JSON file back to binary:

## Documentation

Codec for Valeton GP-200 v1.8 .prst file format

## Features

- ✓ Decode .prst binary files to human-readable JSON
- ✓ Encode JSON back to .prst binary long format
- ✓ Preserve all format metadata (except timestamp), modules, parameters.
- ✓ Supports standard and long format sizes

## Requirements
- Python 3.6+ (no external dependencies)

## TODO
- Update docs format pattern to match latest format version.
- Use data classes instead of dictionaries
- Setup project as PyPI package
- Add verbose decoding to enhance human-readability

## Example Schema

Credits to Joe Lobao for sharing his preset)

```
{
  "header": {
    "magic": "TSRP",
    "version": 100663296,
    "product_id": "GP-2",
    "firmware_version": "00010100",
    "timestamp": 0,
    "file_size": 1172
  },
  "metadata": {
    "program_index": 229,
    "bpm": 120,
    "volume": 75,
    "pan": 0,
    "category": 13,
    "fxloop_send_level": 100,
    "fxloop_return_level": 100,
    "fxloop_mode": 0,
    "name": "PRECISION DRIVE",
    "author": "Joe Lobao",
    "note": ""
  },
  "chain": {
    "program_index_repeat": 229,
    "fxloop_send_position": 5,
    "fxloop_return_position": 5,
    "order": [
      10,
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8,
      9
    ]
  },
  "modules": [
    {
      "slot": 0,
      "enabled": false,
      "effect_code": 16777217,
      "parameters": [
        50.0,
        85.0,
        88.0,
        2.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 1,
      "enabled": false,
      "effect_code": 83886081,
      "parameters": [
        50.0,
        50.0,
        50.0,
        50.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 2,
      "enabled": true,
      "effect_code": 50331676,
      "parameters": [
        6.0,
        60.0,
        63.0,
        5.0,
        50.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 3,
      "enabled": true,
      "effect_code": 117440606,
      "parameters": [
        62.0,
        61.0,
        76.0,
        57.0,
        36.0,
        67.0,
        0.0
      ]
    },
    {
      "slot": 4,
      "enabled": false,
      "effect_code": 27,
      "parameters": [
        20.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 5,
      "enabled": true,
      "effect_code": 167772192,
      "parameters": [
        1.0,
        50.0,
        30.0,
        15.0,
        60.0,
        19.0,
        20001.0
      ]
    },
    {
      "slot": 6,
      "enabled": false,
      "effect_code": 16777269,
      "parameters": [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        50.0,
        0.0
      ]
    },
    {
      "slot": 7,
      "enabled": false,
      "effect_code": 67108866,
      "parameters": [
        1.0,
        0.5,
        50.0,
        0.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 8,
      "enabled": false,
      "effect_code": 184549409,
      "parameters": [
        20.0,
        500.0,
        20.0,
        61.799999,
        100.0,
        50.0,
        0.0,
        100.0,
        50.0,
        1.0
      ]
    },
    {
      "slot": 9,
      "enabled": true,
      "effect_code": 201326595,
      "parameters": [
        50.0,
        50.0,
        50.0,
        0.0,
        0.0,
        0.0,
        0.0
      ]
    },
    {
      "slot": 10,
      "enabled": true,
      "effect_code": 100663299,
      "parameters": [
        99.36377,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0
      ]
    }
  ],
  "exps": [
    {
      "id": 0,
      "param": 0,
      "module": 10,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 0,
      "param": 1,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 0,
      "param": 2,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 1,
      "param": 0,
      "module": 255,
      "parameter": 0,
      "max_value": 0.0,
      "min_value": 0.0
    },
    {
      "id": 1,
      "param": 1,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 1,
      "param": 2,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 2,
      "param": 0,
      "module": 9,
      "parameter": 0,
      "max_value": 50.0,
      "min_value": 0.0
    },
    {
      "id": 2,
      "param": 1,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    },
    {
      "id": 2,
      "param": 2,
      "module": 255,
      "parameter": 0,
      "max_value": 100.0,
      "min_value": 0.0
    }
  ],
  "knobs": [
    {
      "id": 0,
      "module": 255,
      "param_id": 0
    },
    {
      "id": 1,
      "module": 255,
      "param_id": 0
    },
    {
      "id": 2,
      "module": 11,
      "param_id": 0
    }
  ],
  "ctrls": [
    {
      "id": 0,
      "mode": 0,
      "assigns": 256
    },
    {
      "id": 1,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 2,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 3,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 4,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 5,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 6,
      "mode": 0,
      "assigns": 0
    },
    {
      "id": 7,
      "mode": 0,
      "assigns": 0
    }
  ],
  "checksum": {
    "marker": 1216,
    "value": 3645702144
  }
}
```