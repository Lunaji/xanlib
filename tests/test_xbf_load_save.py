from pathlib import Path
from xanlib import load_xbf, save_xbf
import tempfile
import filecmp
import pytest

#@pytest.mark.file_test
@pytest.mark.parametrize('xbf_file', [f for f in Path('Data/').rglob('*') if f.is_file() and f.suffix.lower() == '.xbf'])
def test_xbf_load_save_verification(xbf_file):
    # if not pytestconfig.getoption('file_test'):
    #     pytest.skip('Skipping file tests')
    scene = load_xbf(xbf_file.resolve())
    with tempfile.NamedTemporaryFile(delete=True) as saved_file:
        save_xbf(scene, saved_file.name)
        assert filecmp.cmp(xbf_file, saved_file.name, shallow=False)
