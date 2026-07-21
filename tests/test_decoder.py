from libprst.models import Header
from libprst.prst_decoder import PRSTDecoder
import os

def test_decoder_header_long(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    header = preset['header']
    assert header["magic"] == "TSRP"
    assert header["version"] == int.from_bytes([6,0,0,0], byteorder='big', signed=False)
    assert header["firmware_version"] == '00010100'
    assert header["timestamp"] == 0
    assert header["file_size"] == 1224 - 52

def test_decoder_header_standard(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '01-B 50s Plexi.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    header = preset['header']
    assert header["magic"] == "TSRP"
    assert header["version"] == int.from_bytes([3,0,0,0], byteorder='big', signed=False)
    assert header["firmware_version"] == '00010100'
    assert header["timestamp"] == 1805578016
    assert header["file_size"] == 1176 - 52

def test_decoder_metadata_long(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    metadata = preset['metadata']
    print(metadata)
    assert metadata["program_index"] == (58 - 1) * 4 + 1 # index of bank 58 slot B
    assert metadata['name'] == "PRECISION DRIVE"
    assert metadata['author'] == "Joe Lobao"
    assert metadata['note'] == ""
    assert metadata['category'] == 13

def test_decoder_metadata_standard(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '01-C Clean FUZZ.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    metadata = preset['metadata']
    print(metadata)
    assert metadata["program_index"] == (1 - 1) * 4 + 2  # index of bank 1 slot C
    assert metadata['name'] == "Clean FUZZ"
    assert metadata['author'] == ""
    assert metadata['note'] == ""
    assert metadata['category'] == 7

def test_decoder_chain_long(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    chain = preset['chain']
    print(chain)
    assert chain["fxloop_return_position"] == 5
    assert chain['fxloop_send_position'] == 5
    assert chain['order'] == [10,0,1,2,3,4,5,6,7,8,9]


def test_decoder_chain_standard(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '01-C Clean FUZZ.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    chain = preset['chain']
    print(chain)
    assert chain["fxloop_return_position"] == 4
    assert chain['fxloop_send_position'] == 4
    assert chain['order'] == [4,10,0,1,2,3,5,6,7,8,9]

def test_decoder_exps_long(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    exps = preset['exps']
    print(exps)
    assert exps[0]['id'] == 0

def test_decoder_exps_standard(pytestconfig):
    rootdir = pytestconfig.rootdir
    filepath = os.path.join(rootdir, 'examples', 'FactoryPresets200', '58-B PRECISION DRIVE.prst')
    decoder = PRSTDecoder(filepath)
    preset = decoder.decode()

    exps = preset['exps']
    print(exps)
    assert exps[0]['id'] == 0
    assert exps[4]['id'] == 1
