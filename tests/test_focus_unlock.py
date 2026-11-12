import io
import unittest
from datetime import datetime, timedelta
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

import focus_unlock as tracker


class TrackerTests(unittest.TestCase):
    def test_screen_state_and_query_failure(self):
        for output, expected in [("The screensaver is inactive\n", "Working"),
                                 ("The screensaver is active\n", "Resting")]:
            with self.subTest(output=output), patch.object(
                tracker, "run_cmd", return_value=SimpleNamespace(returncode=0, stdout=output)
            ):
                self.assertEqual(tracker.read_state(), expected)
        with patch.object(tracker, "run_cmd", return_value=SimpleNamespace(
            returncode=1, stdout="The screensaver is inactive"
        )), self.assertLogs(tracker.logger, level="ERROR"):
            self.assertEqual(tracker.read_state(), "Unknown")

    def test_table_does_not_mutate_saved_timestamps(self):
        sessions = [{"start": "2020-01-01 10:00:00", "stop": "2020-01-01 10:40:00"}]
        with redirect_stdout(io.StringIO()):
            tracker.show_work_done_table(sessions)
            tracker.show_work_done_table(sessions)
        self.assertEqual(sessions[0]["start"], "2020-01-01 10:00:00")

    def test_show_work_done_only_displays_today(self):
        today = datetime.now().date()
        today_sessions = [{"start": "today"}]
        sessions = {today.isoformat(): today_sessions,
                    (today - timedelta(days=1)).isoformat(): [{"start": "yesterday"}]}
        with patch.object(tracker, "show_work_done_table") as show_table:
            tracker.show_work_done(sessions)
            show_table.assert_called_once_with(today_sessions)
            show_table.reset_mock()
            tracker.show_work_done({(today - timedelta(days=1)).isoformat(): []})
            show_table.assert_called_once_with([])

    def test_background_reminder_requests_notification_sound(self):
        with patch.object(tracker.sys, "stdout") as stdout, patch.object(
            tracker.subprocess, "run", return_value=SimpleNamespace(returncode=0)
        ) as run:
            stdout.isatty.return_value = False
            self.assertTrue(tracker.beep())
            command = run.call_args.args[0]
            self.assertEqual(command[0], "notify-send")
            self.assertIn("--hint=string:sound-name:message-new-instant", command)
            stdout.write.assert_not_called()

    def test_notification_failure_is_logged(self):
        with patch.object(tracker.sys, "stdout") as stdout, patch.object(
            tracker.subprocess, "run", side_effect=FileNotFoundError("notify-send")
        ), self.assertLogs(tracker.logger, level="ERROR"):
            stdout.isatty.return_value = False
            self.assertFalse(tracker.beep())


if __name__ == "__main__":
    unittest.main()
