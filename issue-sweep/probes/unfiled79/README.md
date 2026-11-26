# UNFILED 79: does the usage-metrics post block mesh construction?

## What development does (fbef72fa, also the newest development here)
There is ONE post per process, at import:
- `underworld3/__init__.py` starts `utilities._utils.postHog` on a daemon thread, on rank 0 only,
  unless `UW_NO_USAGE_METRICS` is set;
- `postHog` calls `requests.post(..., timeout=10)` and prints "PostHog telemetry failed" on an
  error.
Nothing in the mesh constructor posts, nothing is collective, and the thread is a daemon, so exit
does not wait for it.

## Measured on the laptop (macOS, serial; `net79.py`)
The network was blocked by pointing `HTTPS_PROXY`/`HTTP_PROXY` at a non-routable address
(10.255.255.1:9), so the connect waits out the 10 s timeout.

| | import | three meshes (h 0.2 / 0.1 / 0.05) | whole process | thread at exit |
|---|---|---|---|---|
| blocked | 3.71 s | 0.23 / 0.07 / 0.07 s | 4.9 s | still waiting |
| blocked, `UW_NO_USAGE_METRICS=1` | 3.14 s | 0.13 / 0.06 / 0.06 s | 4.2 s | none |
| open | 3.01 s | 0.13 / 0.07 / 0.06 s | 4.0 s | running |

There is no per-mesh wait here. The first build is about 0.1 s slower while the thread imports and
connects, and the process exits without waiting for the thread.

## For the machine where the wait was seen
Run `net79.py` there with the real blocked network, three ways: plain, with
`UW_NO_USAGE_METRICS=1`, and under `py-spy dump --pid` during a slow build if one shows. The
`NET` line gives import time, per-mesh times, and the threads alive at the end. A per-mesh wait
with metrics on and none with it off would point to a mechanism this laptop cannot show (for
example the resolver holding the interpreter on that system's libc). The dump would name it.
