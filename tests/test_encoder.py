from pathlib import Path

from libprst.prst_decoder import PRSTDecoder
import os

from libprst.prst_encoder import PRSTEncoder


def test_decoder_binary_long(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')

    binary_preset = Path(filepath).read_bytes()

    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    encoder = PRSTEncoder(preset)
    encoded_preset = encoder.encode()

    base = 0x10
    offset = 16
    print(binary_preset[base:base+offset])
    print(encoded_preset[base:base+offset])

    assert binary_preset == encoded_preset

def test_decoder_long_reencoded(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    filepath_temp = os.path.join(rootdir, 'examples', 'FactoryPresets200', 'temp.prst')

    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    encoder = PRSTEncoder(preset)
    encoded_preset = encoder.encode()

    with open(filepath_temp, 'wb') as f:
        f.write(encoded_preset)

    decoder2 = PRSTDecoder(filepath_temp)
    preset2 = decoder2.decode()

    assert preset == preset2

def test_decoder_standard_reencoded(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '01-C Clean FUZZ.prst')
    filepath_temp = os.path.join(rootdir, 'examples', 'FactoryPresets200', 'temp.prst')

    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    encoder = PRSTEncoder(preset)
    encoded_preset = encoder.encode()

    with open(filepath_temp, 'wb') as f:
        f.write(encoded_preset)

    decoder2 = PRSTDecoder(filepath_temp)
    preset2 = decoder2.decode()

    # Header differs in file_size
    assert preset['metadata'] == preset2['metadata']
    assert preset['chain'] == preset2['chain']
    assert preset['exps'] == preset2['exps']
    assert preset['knobs'] == preset2['knobs']
    assert preset['ctrls'] == preset2['ctrls'][:4] # only first 4 ctrls match as long format has 8 and short only 4
    # Checksum differs as long format has more ctrls, thus checksum differs


