from pathlib import Path
from xanlib import load_xbf, save_xbf
import tempfile
import filecmp
import pytest

@pytest.mark.slow
@pytest.mark.parametrize('xbf_file', [f for f in Path('Data/').rglob('*') if f.is_file() and f.suffix.lower() == '.xbf'])
def test_xbf_full_roundtrip(xbf_file):

    scene = load_xbf(xbf_file.resolve())
    with tempfile.NamedTemporaryFile(delete=True) as saved_file:
        save_xbf(scene, saved_file.name)
        assert scene.error is None
        assert scene.unparsed is None
        assert filecmp.cmp(xbf_file, saved_file.name, shallow=False)
