from pathlib import Path
from xanlib import load_xbf, save_xbf
import tempfile
import filecmp
import pytest

#@pytest.mark.file_test
def test_xbf_load_save_verification():
    # if not pytestconfig.getoption('file_test'):
    #     pytest.skip('Skipping file tests')

    base_path = Path('Data/')
    suffix = '.xbf'

    xbf_files = [f for f in base_path.rglob('*') if f.is_file() and f.suffix.lower() == suffix]

    for xbf_file in xbf_files:
        scene = load_xbf(xbf_file.resolve())
        with tempfile.NamedTemporaryFile(delete=True) as saved_file:
            save_xbf(scene, saved_file.name)
            assert filecmp.cmp(xbf_file, saved_file.name, shallow=False), f'Mismatch in file: {xbf_file}'
