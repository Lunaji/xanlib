from pathlib import Path
from xanlib import load_xbf, save_xbf
import filecmp
import pytest

@pytest.mark.slow
@pytest.mark.parametrize('xbf_file', [f for f in Path('Data/').rglob('*') if f.is_file() and f.suffix.lower() == '.xbf'])
def test_xbf_full_roundtrip(xbf_file, tmp_path):
    scene = load_xbf(xbf_file.resolve())
    temp_file = tmp_path / xbf_file
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    save_xbf(scene, temp_file)
    assert filecmp.cmp(xbf_file, temp_file, shallow=False)
    assert scene.error is None
    assert scene.unparsed is None
