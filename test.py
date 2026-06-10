from datetime import datetime
from pathlib import Path


LOG_PATH = Path("logs/run_log.txt")


def main() -> None:
    current_time = datetime.now().astimezone().isoformat(timespec="seconds")
    log_line = f"Run time: {current_time}"

    print(log_line)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(log_line + "\n")


if __name__ == "__main__":
    main()
