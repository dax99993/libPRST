# GP-200 PRST Format Analysis - Detailed Patterns

## Summary of Identified Patterns

After analyzing 99 factory preset files, here are the confirmed patterns in the binary .prst format.

## File Structure

```
Offset    Size    Description
------    ----    -----------
0x000     4       Magic: 'TSRP' (PRST reversed)
0x004     4       Zero padding
0x008     4       Version: 0x00000003 (little-endian = 50331648)
0x00C     4       Zero padding
0x010     4       Product ID: '2-PG' (GP-2 reversed)
0x014     4       Firmware version: 0x00010100
0x018     4       Timestamp: 0x6b9eef20 (1805578016)
0x01C     4       Constant: 0x00000001
0x020     4       Constant: 0x00000028 (40)
0x024     4       File size reference: 0x00000464 (1124)
0x028     4       Marker: 'MRAP' (PARM reversed)
0x02C     4       File size reference: 0x00000464 (repeated)
0x030     16      Metadata block (8 x 16-bit values)
0x040     4       Zero padding
0x044     60      Preset name (ASCII, null-terminated)
0x080     8       Chain header
0x088     2       Constant: 0x0008
0x08A     2       Constant: 0x0010
0x08C     4       Unknown
0x090     16      Chain configuration
0x0A0     ~784    Module blocks (variable, up to 11 modules)
0x3B0     108     Default controls (9 x 12 bytes)
0x41C     24      Assignments (3 x 8 bytes)
0x434     32      Toggles (4 x 8 bytes)
0x454     8       Checksum/trailer
```

## Metadata Block (0x30-0x3F)

Eight 16-bit little-endian values:

| Offset | Field         | Description                           | Common Values |
|--------|---------------|---------------------------------------|---------------|
| 0x30   | constant      | Always 0x0002                         | 2             |
| 0x32   | bpm           | Beats per minute                      | 88, 120       |
| 0x34   | program_index | Bank/slot (0-199)                     | 0-99          |
| 0x36   | level         | Overall volume                        | 120 (0x78)    |
| 0x38   | param4        | Unknown parameter                     | 50 (0x32)     |
| 0x3A   | param5        | Usually 0                             | 0             |
| 0x3C   | ir_or_preset  | IR cabinet or effect chain preset     | 0-10          |
| 0x3E   | param7        | Usually 0                             | 0             |

## Preset Name (0x44-0x7F)

- Starts at 0x44 (after 4 zero bytes at 0x40)
- Maximum ~60 characters ASCII
- Null-terminated
- Zero-padded to fill remaining space

Examples:

- "50s Plexi"
- "Soaring Eagle"
- "I Was a Bass Am"

## Chain Configuration (0x90-0x9F)

16 bytes encoding module order and configuration:

| Offset | Description              |
|--------|--------------------------|
| 0x90   | program_index (repeated) |
| 0x91   | Module count info byte 0 |
| 0x92   | Module count info byte 1 |
| 0x93   | Module count info byte 2 |
| 0x94   | Module count info byte 3 |
| 0x95   | Module count info byte 4 |
| 0x96-9F| Module order array       |

## Module Blocks

Each module block:

- Identified by marker: `0x14 0x00 0x44 0x00`
- Size: 64 bytes (0x40)
- Variable spacing between modules (use marker to locate)
- Up to 11 modules per preset

### Module Structure

```
Offset  Size  Description
------  ----  -----------
+0      2     Header: 0x0014
+2      2     Marker: 0x0044
+4      1     Slot number (0-10)
+5      1     Enabled flag (0=disabled, 1=enabled)
+6      2     Constant: 0x000F
+8      4     Effect code (identifies effect type)
+12     40    Parameters (up to 10 x 32-bit floats)
```

### Effect Codes (Partial List)

Observed effect codes from factory presets:

| Code | Possible Effect        | Occurrences |
|------|------------------------|-------------|
| 0    | Empty/No effect        | Common      |
| 3    | Unknown effect         | Multiple    |
| 5    | Unknown effect         | Multiple    |
| 8    | Unknown effect         | Multiple    |
| 9    | Unknown effect         | Multiple    |
| 19   | Unknown effect         | Multiple    |
| 25   | Unknown effect         | Multiple    |
| 27   | Unknown effect         | Multiple    |

*Note: Effect code mapping requires testing with known presets*

### Parameters

- Stored as IEEE-754 32-bit little-endian floats
- Up to 10 parameters per module
- Commonly observed values:
  - `50.0` (0x42480000)
  - `100.0` (0x42C80000)
  - `120.0` (0x42F00000)
  - `0.0` (0x00000000)
  - Negative values: `-20.0` (0xC1A00000)

## Control Tables (0x3B0-0x453)

### Default Controls (9 records x 12 bytes)

Each record:

```
+0  2    Header: 0x000C
+2  2    Marker: 0x000C
+4  2    Control ID
+6  2    Padding (zero)
+8  4    Float value (usually 100.0)
```

Common control IDs:

- `0x000A` (first record)
- `0x01FF`, `0x02FF` (following records)
- `0x1001`, `0x11FF`, `0x12FF`
- `0x20FF`, `0x21FF`, `0x22FF`

### Assignments (3 records x 8 bytes)

Each record:

```
+0  2    Header: 0x0010
+2  2    Marker: 0x0004
+4  2    Target
+6  2    State
```

Observed patterns:

- First: `0x0000/0x0000` or `0x0102/0x0200`
- Second: `0x0109/0x0000` or similar
- Third: `0x020B/0x0000` (common)

*Likely expression pedal or footswitch assignments*

### Toggles (4 records x 8 bytes)

Each record:

```
+0  2    Header: 0x000F
+2  2    Marker: 0x0008
+4  2    Toggle ID (0-3)
+6  2    Padding
+8  4    Value (varies per preset)
```

*Possibly footswitch states or scene toggles*

## Checksum/Trailer (0x454-0x45B)

Last 8 bytes:

```
+0  4    Marker: 0x00000490 (1168)
+4  4    Checksum value (varies per file)
```

Checksum values observed:

- `0x00004E34` (01-B 50s Plexi)
- `0x00004375` (10-B Soaring Eagle)
- `0x0000D74C` (25-D I Was a Bass Am)

*Algorithm unknown - likely CRC-32 or similar*

## Common Patterns Across All Files

1. **Fixed Header**: First 48 bytes identical across all factory presets
   - Same magic, version, product ID, firmware version
   - Same timestamp (likely factory build date)

2. **BPM**: Most factory presets use 88 BPM (0x58)

3. **Level**: Most use level 120 (0x78)

4. **Module Spacing**: Variable gaps between modules filled with zeros
   - Not strictly 0x40-byte intervals
   - Must search for 0x1400 0x4400 markers

5. **Zero Padding**: Large areas of zero bytes between structures
   - Used for alignment and future expansion

## Unknown/To Be Determined

- [ ] Exact meaning of chain configuration bytes
- [ ] Complete effect code to effect name mapping
- [ ] Parameter ranges and meanings for each effect
- [ ] Checksum calculation algorithm
- [ ] IR file references and integration
- [ ] MIDI/expression pedal assignment details
- [ ] Meaning of metadata fields param4, param5, param7
- [ ] Toggle and assignment interpretation

## Testing Recommendations

To fully understand the format:

1. Create presets with known settings
2. Change one parameter at a time
3. Save and decode
4. Compare with reference presets
5. Document the differences

Focus areas:

- Effect selection (to map codes)
- Parameter adjustments (to understand ranges)
- Expression pedal assignments
- Footswitch configurations
- IR cabinet selection
