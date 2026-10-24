#!/bin/sh
# ==============================================================================
# A.T.L.A.S — backup container entrypoint
# ==============================================================================
# Two modes, selected via ATLAS_MODE:
#   ATLAS_MODE=schedule  (default)  run as a long-lived cron loop
#   ATLAS_MODE=backup    run one backup now and exit
#   ATLAS_MODE=restore   run `restore.py` with ATLAS_RESTORE_ARGS and exit
# ==============================================================================
set -eu

MODE="${ATLAS_MODE:-schedule}"

case "$MODE" in
    backup)
        echo "[entrypoint] running one-shot backup"
        exec python /app/backup.py "$@"
        ;;

    restore)
        echo "[entrypoint] running one-shot restore"
        # shellcheck disable=SC2086
        exec python /app/restore.py ${ATLAS_RESTORE_ARGS:-latest} "$@"
        ;;

    schedule|"")
        # Schedule mode: hand the cron string to a tiny Python helper that
        # computes the next fire time and sleeps until then. We avoid relying
        # on host cron (not installed in slim images) and avoid GNU-isms in
        # shell date math.
        SCHEDULE="${ATLAS_BACKUP_SCHEDULE:-0 2 * * *}"
        echo "[entrypoint] schedule mode: '${SCHEDULE}' (UTC)"

        while true; do
            sleep_for=$(python - "$SCHEDULE" <<'PY'
import sys, time, datetime as dt

def parse_field(f, cur, lo, hi):
    if f == "*":
        return set(range(lo, hi + 1))
    out = set()
    for part in f.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            lo2 = lo if base == "*" else int(base)
            out |= set(range(lo2, hi + 1, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            out |= set(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    return out & set(range(lo, hi + 1))

fields = sys.argv[1].split()
while len(fields) < 5:
    fields.append("*")
minutes = parse_field(fields[0], None, 0, 59)
hours   = parse_field(fields[1], None, 0, 23)
doms    = parse_field(fields[2], None, 1, 31)
months  = parse_field(fields[3], None, 1, 12)
# POSIX dow: 0-6 (0=Sunday). Convert Python weekday (0=Mon..6=Sun) to that.
dows_in = parse_field(fields[4], None, 0, 6)

now = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
# Walk forward up to 366 days.
for i in range(0, 366 * 24 * 60):
    t = now + dt.timedelta(minutes=i)
    py_dow = t.weekday()              # 0=Mon..6=Sun
    posix_dow = (py_dow + 1) % 7      # 0=Sunday..6=Saturday
    if (t.minute in minutes and t.hour in hours and t.day in doms
            and t.month in months and posix_dow in dows_in):
        delta = (t - dt.datetime.now(dt.timezone.utc)).total_seconds()
        print(int(max(delta, 0)))
        sys.exit(0)
print(3600)
PY
)
            echo "[entrypoint] next backup in ${sleep_for}s"
            sleep "$sleep_for" || exit 0
            echo "[entrypoint] $(date -u +%FT%TZ) firing scheduled backup"
            python /app/backup.py || echo "[entrypoint] backup FAILED (exit $?) - will retry next cycle"
        done
        ;;

    *)
        echo "[entrypoint] unknown ATLAS_MODE='$MODE' (expected: schedule|backup|restore)" >&2
        exit 2
        ;;
esac
