# Focus Unlock

Focus Unlock is a small reminder to take movement breaks during long stretches at the computer. I built it during the 2020 COVID lockdown, when I noticed I was working too many hours without getting up. Inspired by the Pomodoro technique, I wanted a nudge to stop, move my body, and return to work refreshed.

The script watches the GNOME screensaver state. After 40 continuous minutes with the screen unlocked, it sounds a terminal bell every minute until the screensaver becomes active or the screen is locked. Locking the screen ends the work session; the next unlock starts a fresh 40-minute timer. It also saves work sessions to `work_done.json` in the current directory and displays their durations.

## Run it

On a Linux desktop with GNOME, install Python 3, `gnome-screensaver-command`, and the Python package `rich`. Then run:

```sh
python3 -m pip install rich
python3 unlock_tracker.py
```

Leave the script running in a terminal and press Ctrl+C to stop it. The reminder uses the terminal bell, so its sound depends on your terminal and system settings. The screensaver command must report the state of your desktop session; if it cannot, the script logs an error and waits until it can read the state.
