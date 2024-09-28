from pathlib import Path
from xanlib import load_xbf, save_xbf
import tempfile
import filecmp
import pytest
import json


@pytest.fixture(scope='session')
def expected_errors():
    with open('tests/test_data/expected_errors.json', 'r') as f:
        return json.load(f)

@pytest.mark.slow
@pytest.mark.parametrize('xbf_file', [f for f in Path('Data/').rglob('*') if f.is_file() and f.suffix.lower() == '.xbf'])
def test_xbf_full_roundtrip(xbf_file, expected_errors):

    scene = load_xbf(xbf_file.resolve())
    with tempfile.NamedTemporaryFile(delete=True) as saved_file:
        save_xbf(scene, saved_file.name)
        assert filecmp.cmp(xbf_file, saved_file.name, shallow=False)

        filename_without_root = '/'.join(xbf_file.parts[1:])
        if filename_without_root in expected_errors:
            pytest.xfail(f'File {xbf_file} expected to have error')

        assert scene.error is None
        assert scene.unparsed is None
