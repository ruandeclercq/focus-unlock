#!/usr/bin/python3

from datetime import datetime
import argparse
import json
import logging
import math
import os
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table
from signal import signal, SIGINT, SIGTERM
import subprocess
import sys
import time


SHORT_DATE_FORMAT = "%Y-%m-%d"
LONG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
SUPER_LONG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def run_cmd(cmd, *f_args, **kwargs):
    '''Run a command with the shell and stderr,stdout redirected'''
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          encoding='utf-8', *f_args, **kwargs)


def text_to_state(txt):
    txt = txt.strip().lower()
    if txt in ("inactive", "not running!"):
        return "Working"
    elif txt == "active":
        return "Resting"
    logger.error(f"txt:{txt}")
    return "Unknown"


def read_state():
    out = run_cmd("gnome-screensaver-command --query")
    if out.returncode != 0:
        logger.error("Could not query the screensaver: %s", out.stdout.strip())
        return "Unknown"
    return text_to_state(out.stdout.strip().split("creensaver is ")[-1])


def wait_work(description, minutes):
    # Monotonic time keeps the timer accurate if the system clock changes.
    start_local = time.monotonic()
    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
    )
    with progress:
        task = progress.add_task(f"Working {description}(target: {get_formatted_duration(minutes*60)})", total = minutes * 60)
        state = read_state()
        while not progress.finished and state == "Working":
            elapsed = time.monotonic() - start_local
            progress.update(task, completed=int(elapsed))
            time.sleep(1)
            state = read_state()
        return progress.finished and state == "Working"


def store_work_done(work_done):
    with open("work_done.json", "w") as json_file:
        json.dump(work_done, json_file, default=str)


def load_work_done():
    if not os.path.isfile("work_done.json"):
        return {}

    with open("work_done.json") as json_file:
        return json.load(json_file)


def beep():
    # Notifications work without a terminal; the sound is controlled by GNOME.
    success = False
    try:
        result = subprocess.run(
            ["notify-send", "--app-name=Focus Unlock",
             "--hint=string:sound-name:message-new-instant",
             "Time for a break", "Get up and move around for a while."],
            capture_output=True, text=True, check=False,
        )
        if result.returncode:
            logger.error("Could not send reminder: %s", result.stderr.strip())
        else:
            success = True
    except OSError as exc:
        logger.error("Could not send reminder: %s", exc)
    if sys.stdout.isatty():
        sys.stdout.write('\a')
        sys.stdout.flush()
    return success


def get_formatted_duration(seconds):
    seconds = math.floor(seconds)
    minutes = math.floor(seconds / 60)
    hours = math.floor(minutes / 60)

    if minutes == 0:
        return f"{seconds}s"

    if hours == 0:
        return f"{minutes}m"

    minutes = minutes - hours * 60
    return f"{hours}h{minutes}m"


def show_work_done_table(work_done):
    if len(work_done) == 0:
        return

    total_seconds = 0
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    all_columns = list(work_done[0].keys())
    columns = []
    for column in all_columns:
        if any([column in result for result in work_done]):
            columns.append(column)
            table.add_column(column)
    table.add_column("duration", justify="right")
    for row in work_done:
        strings = []
        for column in columns:
            if column in row:
                strings.append(str(row[column]))
            else:
                strings.append("")
        # Display saved timestamps without changing the records in memory.
        start_time = datetime.fromisoformat(row["start"]) if isinstance(row["start"], str) else row["start"]
        stop_time = datetime.fromisoformat(row["stop"]) if isinstance(row["stop"], str) else row["stop"]
        duration = (stop_time - start_time).total_seconds()
        total_seconds += duration
        strings.append(get_formatted_duration(duration))
        table.add_row(*strings)
    strings = [""] * max(0, len(columns) - 1) + ["Total:", get_formatted_duration(total_seconds)]
    table.add_row(*strings)
    console.print(table)


def show_work_done(work_done):
    # Keep historical records, but display only the current day's sessions.
    today = datetime.now().strftime(SHORT_DATE_FORMAT)
    show_work_done_table(work_done.get(today, []))


def add_work_done(start, stop):
    now_str = datetime.now().strftime(SHORT_DATE_FORMAT)

    if now_str not in work_done.keys():
        work_done[now_str] = []
    work_done[now_str].append({"start": start.strftime(SUPER_LONG_DATE_FORMAT),\
                               "stop": stop.strftime(SUPER_LONG_DATE_FORMAT)})


def sigint_handler(signal_received, frame):
    logger.info('Stopping and saving the current work session')

    if start is not None:
        add_work_done(start, datetime.now())
        store_work_done(work_done)

    show_work_done(work_done)
    exit(0)


work_done = load_work_done()
start = None

logger = logging.getLogger("logger")
level = logging.DEBUG
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_handler.setLevel(level)
c_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s", LONG_DATE_FORMAT))
logger.addHandler(c_handler)

def main():
    global start
    signal(SIGINT, sigint_handler)
    signal(SIGTERM, sigint_handler)

    show_work_done(work_done)

    prev_state = "inactive"
    prev_time = datetime.now()
    while True:
        state = read_state()

        if state != prev_state:
            diff = datetime.now() - prev_time
            prev_state = state
            prev_time = datetime.now()

            if state == "Working":
                start = datetime.now()
                if diff.total_seconds() > 1:
                    logger.info(f"You rested {get_formatted_duration(diff.total_seconds())}")

                # Only sound a reminder after the full interval completes.
                interval_finished = wait_work("", 40)
                while interval_finished:
                    beep()
                    interval_finished = wait_work("at reduced capacity! ", 1)
                add_work_done(start, datetime.now())
                show_work_done(work_done)
                store_work_done(work_done)
                start = None
                # Process the state reached while the progress timer was running.
                prev_state = "Working"

        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remind yourself to take movement breaks.")
    parser.add_argument("--test-notification", action="store_true",
                        help="send one test reminder and exit")
    args = parser.parse_args()
    if args.test_notification:
        sys.exit(0 if beep() else 1)
    main()
