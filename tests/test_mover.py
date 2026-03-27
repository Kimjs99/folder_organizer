import pytest
from pathlib import Path
from organizer.mover import move_file, get_unique_path, is_hidden_or_system

def test_is_hidden_or_system():
    assert is_hidden_or_system(Path(".DS_Store")) is True
    assert is_hidden_or_system(Path("thumbs.db")) is True
    assert is_hidden_or_system(Path(".localized")) is True
    assert is_hidden_or_system(Path("test.alias")) is True
    assert is_hidden_or_system(Path(".hidden")) is True
    
    assert is_hidden_or_system(Path("normal.txt")) is False
    assert is_hidden_or_system(Path("document.pdf")) is False

def test_get_unique_path(tmp_path):
    dest_path = tmp_path / "file.txt"
    dest_path.touch()
    
    unique1 = get_unique_path(dest_path)
    assert unique1.name == "file_1.txt"
    
    unique1.touch()
    
    unique2 = get_unique_path(dest_path)
    assert unique2.name == "file_2.txt"

def test_move_file(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    
    src = src_dir / "test.txt"
    src.write_text("hello")
    
    success, msg, new_path = move_file(src, dest_dir, dry_run=False)
    
    assert success is True
    assert msg == "success"
    assert new_path is not None
    assert new_path.exists()
    assert not src.exists()
    assert new_path.read_text() == "hello"

def test_move_file_dry_run(tmp_path):
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    
    src = src_dir / "test.txt"
    src.write_text("hello")
    
    success, msg, new_path = move_file(src, dest_dir, dry_run=True)
    
    assert success is True
    assert msg == "dry-run"
    assert src.exists() # Source should still exist
    assert not new_path.exists() # Target shouldn't be created
