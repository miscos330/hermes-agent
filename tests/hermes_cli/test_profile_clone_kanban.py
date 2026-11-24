"""``hermes profile create --clone-all`` leaves the shared kanban boards at the default root.

Boards are read only from the default root (``kanban_db.kanban_home``), so a copy inside the clone
is a stale snapshot that nothing reads (#159604).
"""

from __future__ import annotations

from pathlib import Path

from hermes_cli import profiles

_BOARD = ("kanban.db", "kanban.db-wal", "kanban.db-shm", "kanban.db.init.lock", "kanban.db.dispatch.lock",
          "kanban/current", "kanban/boards/ops/kanban.db", "kanban/boards/ops/workspaces/t1/notes.md")


def test_clone_all_from_default_does_not_copy_the_kanban_boards(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    home = tmp_path / ".hermes"
    monkeypatch.setenv("HERMES_HOME", str(home))
    monkeypatch.setattr(profiles, "_maybe_register_gateway_service", lambda name: None)
    for rel in ("config.yaml", "SOUL.md", *_BOARD):
        path = home / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rel, encoding="utf-8")

    clone = profiles.create_profile("clone", clone_from="default", clone_all=True, no_alias=True)

    assert (clone / "SOUL.md").read_text(encoding="utf-8") == "SOUL.md"
    copied = [rel for rel in (*_BOARD, "kanban") if (clone / rel).exists()]
    assert copied == []
    assert all((home / rel).read_text(encoding="utf-8") == rel for rel in _BOARD)
