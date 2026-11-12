PACKAGE := dist/focus-unlock_0.1.0_all.deb
STAGING := dist/package
PACKAGE_FILES := focus_unlock.py focus-unlock.service README.md LICENSE debian/control

.PHONY: all package

all: package

package: $(PACKAGE)

$(PACKAGE): $(PACKAGE_FILES)
	install -d $(STAGING)/DEBIAN $(STAGING)/usr/lib/focus-unlock $(STAGING)/usr/lib/systemd/user $(STAGING)/usr/share/doc/focus-unlock
	rm -f $(STAGING)/usr/lib/focus-unlock/unlock_tracker.py
	install -m 644 debian/control $(STAGING)/DEBIAN/control
	install -m 644 focus_unlock.py $(STAGING)/usr/lib/focus-unlock/focus_unlock.py
	install -m 644 focus-unlock.service $(STAGING)/usr/lib/systemd/user/focus-unlock.service
	install -m 644 README.md $(STAGING)/usr/share/doc/focus-unlock/README.md
	install -m 644 LICENSE $(STAGING)/usr/share/doc/focus-unlock/copyright
	find $(STAGING) -type d -exec chmod 755 {} +
	dpkg-deb --root-owner-group --build $(STAGING) $@
