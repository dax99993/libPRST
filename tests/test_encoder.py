from pathlib import Path
from libprst.encoder import PRSTEncoder
from libprst.decoder import PRSTDecoder
import os


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

    # remove temp file
    os.remove(filepath_temp)

    # Header differs in file_size
    assert preset['metadata'] == preset2['metadata']
    assert preset['chain'] == preset2['chain']
    assert preset['exps'] == preset2['exps']
    assert preset['knobs'] == preset2['knobs']
    assert preset['ctrls'] == preset2['ctrls'][:4] # only first 4 ctrls match as long format has 8 and short only 4
    # Checksum differs as long format has more ctrls, thus checksum differs


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

    # remove temp file
    os.remove(filepath_temp)

    # Header might be different due to timestamp (in this case both are zero)
    assert preset['header'] == preset2['header']
    assert preset['metadata'] == preset2['metadata']
    assert preset['chain'] == preset2['chain']
    assert preset['exps'] == preset2['exps']
    assert preset['knobs'] == preset2['knobs']
    assert preset['ctrls'] == preset2['ctrls']
    # Check sum might be different due to timestamp
    # assert preset['checksum'] == preset2['checksum']
