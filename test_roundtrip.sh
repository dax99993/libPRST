#!/bin/bash
# Test round-trip encoding/decoding

echo "=== Round-Trip Test ==="
echo

# Pick a test file
TEST_FILE="examples/FactoryPresets200/10-B Soaring Eagle.prst"
echo "Test file: $TEST_FILE"
echo

# Decode to JSON
echo "1. Decoding to JSON..."
python3 scripts/prst_decoder.py "$TEST_FILE"
JSON_FILE="${TEST_FILE%.prst}.json"
echo

# Encode back to binary
echo "2. Encoding back to binary..."
python3 scripts/prst_encoder.py "$JSON_FILE" "/tmp/roundtrip_test.prst"
echo

# Compare sizes
echo "3. Comparing file sizes..."
ls -lh "$TEST_FILE" "/tmp/roundtrip_test.prst" | awk '{print "  " $5 "\t" $9}'
echo

# Test decoding the new file
echo "4. Decoding the re-encoded file..."
python3 scripts/prst_decoder.py "/tmp/roundtrip_test.prst" "/tmp/roundtrip_test.json"
echo

echo "✓ Round-trip test complete!"
echo "Compare files:"
echo "  Original: $JSON_FILE"
echo "  Re-encoded: /tmp/roundtrip_test.json"
