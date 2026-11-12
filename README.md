# Focus Unlock

Focus Unlock is a small reminder to take movement breaks during long stretches at the computer. I built it during the 2020 COVID lockdown, when I noticed I was working too many hours without getting up. Inspired by the Pomodoro technique, I wanted a nudge to stop, move my body, and return to work refreshed.

The script watches the GNOME screensaver state. After 40 continuous minutes with the screen unlocked, it sends a desktop notification every minute until the screensaver becomes active or the screen is locked. Locking the screen ends the work session; the next unlock starts a fresh 40-minute timer. It also saves work sessions to `work_done.json` in the current directory and displays today's session durations. Earlier sessions remain in the file.

## Run it

On a Linux desktop with GNOME, install Python 3, `gnome-screensaver-command`, `notify-send` (usually provided by the `libnotify` package), and the Python package `rich`. Then run:

```sh
python3 -m pip install rich
python3 focus_unlock.py
```

Leave the script running in a terminal and press Ctrl+C to stop it. Reminders request a notification sound and also ring the terminal bell when run interactively. Sound depends on your GNOME notification settings and audio volume; the notification remains visible even when sounds are disabled. The screensaver command must report the state of your desktop session; if it cannot, the script logs an error and waits until it can read the state.

## Debian package

On Debian or Ubuntu, install `make` and `dpkg-dev`, then run `make package` to build `focus-unlock_0.1.0_all.deb`. Install it on your GNOME desktop with:

```sh
sudo apt install ./focus-unlock_0.1.0_all.deb
systemctl --user status focus-unlock.service
```

The package installs the Python and GNOME dependencies and enables the service for all users. It starts the service in running graphical sessions and when a graphical session begins. The service runs in a GNOME session that activates `graphical-session.target` and stores sessions in `~/.local/state/focus-unlock/work_done.json` (or under `$XDG_STATE_HOME` if set). Check it with `systemctl --user status focus-unlock.service` and `journalctl --user -u focus-unlock.service`. Stop it and prevent automatic startup for your user with `systemctl --user mask --now focus-unlock.service`; use `systemctl --user unmask focus-unlock.service` to allow it again.

To check notifications and sound before waiting 40 minutes, run:

```sh
make test-notification
```

This calls the same reminder used by the tracker. Run `make test` for the automated tests. Run it in your graphical desktop session; after installing the Debian package, use `python3 /usr/lib/focus-unlock/focus_unlock.py --test-notification`. A successful command means the notification was submitted, so check visually and listen to confirm it appeared and sounded. If you see the notification but hear no sound, check GNOME's notification sound settings and system volume. A desktop may ignore the requested sound. The service requires access to your graphical session and its session bus; check the journal if the screensaver query or notification fails.
