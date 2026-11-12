PACKAGE := focus-unlock_0.1.0_all.deb
PACKAGE_FILES := focus_unlock.py focus-unlock.service README.md LICENSE debian/control debian/postinst debian/prerm Makefile

.PHONY: all package test test-notification

all: package

package: $(PACKAGE)

test:
	python3 -m unittest discover -s tests -v

test-notification:
	python3 focus_unlock.py --test-notification

$(PACKAGE): $(PACKAGE_FILES)
	@set -eu; \
	staging=$$(mktemp -d); \
	trap 'rm -rf "$$staging"' EXIT HUP INT TERM; \
	install -d "$$staging/DEBIAN" "$$staging/usr/lib/focus-unlock" "$$staging/usr/lib/systemd/user" "$$staging/usr/share/doc/focus-unlock"; \
	install -m 644 debian/control "$$staging/DEBIAN/control"; \
	install -m 755 debian/postinst "$$staging/DEBIAN/postinst"; \
	install -m 755 debian/prerm "$$staging/DEBIAN/prerm"; \
	install -m 644 focus_unlock.py "$$staging/usr/lib/focus-unlock/focus_unlock.py"; \
	install -m 644 focus-unlock.service "$$staging/usr/lib/systemd/user/focus-unlock.service"; \
	install -m 644 README.md "$$staging/usr/share/doc/focus-unlock/README.md"; \
	install -m 644 LICENSE "$$staging/usr/share/doc/focus-unlock/copyright"; \
	find "$$staging" -type d -exec chmod 755 {} +; \
	dpkg-deb --root-owner-group --build "$$staging" "$@"
