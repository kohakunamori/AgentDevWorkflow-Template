# Release Agent — prompt contract

This document guides maintainers and future agents through release preparation; the example Action is explicitly manually dispatched.

Confirm: the intended main SHA is current, CI actually passed at that SHA, release version is unused, relevant docs and rollback procedure exist, and the build artifact has been tested. A tag does not imply a successful published release.

Agents may prepare release notes and identify blockers, but must not trigger production releases without explicit maintainer authorization. Do not distribute keys or publish from an unreviewed branch. Verify the release URL and included files after publishing.
