from logger import LogManager


def test_log_manager_does_not_duplicate_handlers(tmp_path):
    first_logger = LogManager(tmp_path)
    second_logger = LogManager(tmp_path)

    first_logger.log_info("started")
    second_logger.log_info("ready")

    lines = (tmp_path / "error.log").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0].endswith("INFO - started")
    assert lines[1].endswith("INFO - ready")
