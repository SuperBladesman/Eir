import os
import shutil
from pathlib import Path

import pytest

os.environ.setdefault('MPLBACKEND', 'Agg')

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples'


@pytest.fixture
def examples(tmp_path):
    """A scratch copy of examples/, so no test writes into the repository."""
    d = tmp_path / 'examples'
    shutil.copytree(EXAMPLES, d)
    return d
