# kaiju_tools

The kaiju-side job scripts, run wrapper and hooks, render and analysis scripts used by the zg95 annulus campaign on
kaiju (2026-11-03 to 2026-11-06), put under version control on 2026-11-06 (the Science Hub; underworld3 #948 was a
leak in np52/coarse_log_hook.py that no hub could see). Each file's first comment line (after any shebang) says what it
is and which jobs used it. Run outputs, images and the leaky hook are not included.

Paths inside the scripts are kaiju's (~/+Claude/kaiju/...). From 2026-11-06, launches run these from a pushed commit, as
the driver does.
