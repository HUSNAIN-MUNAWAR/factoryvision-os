from pathlib import Path
import os,pytest
@pytest.fixture
def tmp_root(tmp_path:Path): return tmp_path
