import sys
import os

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import comments


def test_add_and_list_comments(tmp_path):
    db = tmp_path / "c.db"
    comments.add_comment(db, "img1", "a")
    comments.add_comment(db, "img1", "b")
    rows = comments.list_comments(db, "img1")
    assert len(rows) == 2
    assert rows[0]["text"] == "a"


def test_update_comment(tmp_path):
    db = tmp_path / "c.db"
    comments.add_comment(db, "img", "old")
    cid = comments.list_comments(db)[0]["id"]
    comments.update_comment(db, cid, "new")
    row = comments.list_comments(db)[0]
    assert row["text"] == "new"
