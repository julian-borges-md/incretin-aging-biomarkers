#!/usr/bin/env python3
"""Chain manager: supervises the screening chains and restarts stale or stopped jobs.

Purpose
  The screening chains (work/screen_chain*.sh, gitignored, resumable) run the local reviewers one
  record at a time on the GPU. A chain can stop (a transient Ollama error exhausts the retries of
  a step), die (the shell is killed, the machine sleeps) or go stale (a request hangs inside the
  Ollama runner while the Python step waits on it, up to the 600 s HTTP timeout per attempt). The
  manager watches the chains named on its command line and intervenes on evidence, in an
  escalation ladder, writing every observation that led to an action, and the action, to a log.

States, one per chain
  not_launched   no log file: the chain was never started; left alone
  waiting        the chain shell is alive and has printed no start line (it waits on an earlier chain)
  between_steps  the chain shell is alive, started, and no step process exists at this instant
  running        a step process (python3 -I src/...) is alive under the chain shell, progress is recent
  stale          a step process is alive but nothing has progressed for --stale-minutes
  stopped        the log ends with CHAIN STOPPED and no chain shell is alive
  dead           the log has a start line, no completion line, and no chain shell is alive
  complete       the log ends with "<chain> complete"
  attention      an action budget is spent: the manager stops acting on that chain and notifies

Escalation, each action subject to a sliding six hour budget (BUDGET below)
  stale, first time for a step   terminate the Ollama runner (llama-server): the in flight request
                                 fails at once and the step's own retry (six attempts, backoff) goes on
  stale again after the grace    terminate the step process; the chain prints CHAIN STOPPED and exits;
                                 the chain is relaunched (every step skips the records already done)
  stopped or dead                relaunch the chain
  Ollama API unreachable on      quit and reopen the Ollama app (which owns the server)
  three consecutive checks

Progress signal
  The newest modification time among the supervised chain logs and the decision and adjudication
  CSVs in search/screening: every screened record appends a row, so progress is measured on the
  artefacts, never inferred from a process being alive.

Safety switch
  A file work/MANAGER_PAUSE makes the manager observe and report without acting. Stop the manager
  (or create that file) before stopping a chain on purpose; otherwise the manager relaunches it.

Files
  search/screening/manager.log          append only log of observations and actions
  search/screening/manager_status.json  state of every supervised chain, rewritten each cycle

Usage
  python3 -I src/chain_manager.py status chain3c chain4 chain3d
  python3 -I src/chain_manager.py run [--interval 120] [--stale-minutes 12] [--grace-minutes 8]
                                      [--once] [--no-notify] chain3c chain4 chain3d
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "work")
OUTDIR = os.path.join(ROOT, "search", "screening")
LOG = os.path.join(OUTDIR, "manager.log")
STATUS = os.path.join(OUTDIR, "manager_status.json")
PAUSE = os.path.join(WORK, "MANAGER_PAUSE")
OLLAMA_VERSION = "http://127.0.0.1:11434/api/version"
WINDOW = 6 * 3600
BUDGET = {"relaunch": 4, "kill_runner": 6, "kill_step": 3, "restart_ollama": 2}
RUNNER_NAMES = ("llama-server", "ollama_llama_server", "ollama-runner")
OLLAMA_FAILURES_BEFORE_RESTART = 3
HEARTBEAT_EVERY = 10  # cycles


def now():
    return time.time()


def stamp(t=None):
    t = now() if t is None else t
    return datetime.fromtimestamp(t).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def fmt_dur(seconds):
    if seconds is None:
        return "-"
    seconds = int(seconds)
    h, m = divmod(seconds // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{seconds % 60:02d}s"


def log(msg):
    line = f"{stamp()} {msg}"
    print(line, flush=True)
    os.makedirs(OUTDIR, exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


def notify(enabled, title, text):
    if not enabled:
        return
    text = text.replace('"', "'")[:200]
    try:
        subprocess.run(["osascript", "-e", f'display notification "{text}" with title "{title}"'],
                       timeout=10, capture_output=True)
    except Exception as e:  # a failed notification never stops the manager
        log(f"notification failed: {e!r}")


# ----- observation -----------------------------------------------------------------------------

def ps_table():
    out = subprocess.run(["ps", "-axwwo", "pid=,ppid=,etime=,command="],
                         capture_output=True, text=True, timeout=20).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        try:
            rows.append(dict(pid=int(parts[0]), ppid=int(parts[1]), etime=parts[2], cmd=parts[3]))
        except ValueError:
            continue
    return rows


def etime_seconds(s):
    days = 0
    if "-" in s:
        d, s = s.split("-", 1)
        days = int(d)
    parts = [int(p) for p in s.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return days * 86400 + parts[0] * 3600 + parts[1] * 60 + parts[2]


def chain_shells(rows, name):
    target = f"work/screen_{name}.sh"
    found = []
    for r in rows:
        w = r["cmd"].split()
        if len(w) >= 2 and os.path.basename(w[0]) in ("zsh", "bash", "sh") and w[1].endswith(target):
            found.append(r)
    return found


def step_procs(rows, shell_pid):
    return [r for r in rows
            if r["ppid"] == shell_pid and "src/" in r["cmd"] and "ython" in r["cmd"].split()[0]]


def step_label(cmd):
    return cmd.split(" -I ", 1)[1] if " -I " in cmd else cmd


def runner_procs(rows):
    return [r for r in rows if os.path.basename(r["cmd"].split()[0]) in RUNNER_NAMES]


def log_state(name):
    """Last marker in the chain log: complete | stopped | started | empty | no_log, and the last line."""
    path = os.path.join(OUTDIR, f"{name}.log")
    if not os.path.exists(path):
        return "no_log", ""
    state, last = "empty", ""
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.rstrip("\n")
            if not s.strip():
                continue
            last = s
            if s.startswith(f"{name} complete "):
                state = "complete"
            elif s.startswith("CHAIN STOPPED"):
                state = "stopped"
            elif s.startswith(f"{name} start ") or s.startswith("== "):
                state = "started"
    return state, last


def last_progress(names):
    paths = [os.path.join(OUTDIR, f"{n}.log") for n in names]
    for fn in os.listdir(OUTDIR):
        if fn.endswith(".csv") and ("decisions" in fn or "adjudication" in fn):
            paths.append(os.path.join(OUTDIR, fn))
    best, which = 0.0, ""
    for p in paths:
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m > best:
            best, which = m, os.path.basename(p)
    return best, which


def ollama_ok():
    try:
        with urllib.request.urlopen(OLLAMA_VERSION, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def classify(name, rows, t_prog, stale_minutes):
    shells = chain_shells(rows, name)
    lstate, last = log_state(name)
    info = dict(chain=name, log_state=lstate, last_line=last[:120], shell_pid=None,
                step=None, step_pid=None, since_s=None, step_since_s=None, note="")
    if shells:
        sh = shells[0]
        info["shell_pid"] = sh["pid"]
        info["since_s"] = etime_seconds(sh["etime"])
        steps = step_procs(rows, sh["pid"])
        if steps:
            st = steps[0]
            info["step"] = step_label(st["cmd"])
            info["step_pid"] = st["pid"]
            info["step_since_s"] = etime_seconds(st["etime"])
            age_min = (now() - t_prog) / 60 if t_prog else 1e9
            info["state"] = "stale" if age_min >= stale_minutes else "running"
        else:
            info["state"] = "between_steps" if lstate == "started" else "waiting"
        if len(shells) > 1:
            info["note"] = f"{len(shells)} shells alive for this chain"
    elif lstate == "complete":
        info["state"] = "complete"
    elif lstate == "no_log":
        info["state"] = "not_launched"
    elif lstate == "stopped":
        info["state"] = "stopped"
    else:
        info["state"] = "dead"
    return info


# ----- actions ---------------------------------------------------------------------------------

def spent(events, action, chain=None):
    cutoff = now() - WINDOW
    return sum(1 for e in events if e["t"] >= cutoff and e["action"] == action
               and (chain is None or e.get("chain") == chain))


def record(status, action, chain, detail, enabled):
    status["events"].append(dict(t=now(), at=stamp(), action=action, chain=chain, detail=detail))
    status["events"] = status["events"][-300:]
    log(f"ACTION {action} chain={chain} :: {detail}")
    notify(enabled, "FTRL chain manager", f"{action} {chain or ''}: {detail}")


def attention(status, name, why, opts):
    att = status.setdefault("attention", {})
    if att.get(name) != why:
        att[name] = why
        record(status, "attention", name, why, opts.notify)


def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def terminate(pid, wait=15):
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return "already gone"
    except PermissionError as e:
        return f"not permitted: {e}"
    for _ in range(wait * 5):
        time.sleep(0.2)
        if not alive(pid):
            return "terminated"
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return "terminated"
    time.sleep(1)
    return "killed" if not alive(pid) else "still alive"


def relaunch(name, reason):
    script = os.path.join(WORK, f"screen_{name}.sh")
    if not os.path.exists(script):
        return None
    logpath = os.path.join(OUTDIR, f"{name}.log")
    with open(logpath, "a") as fh:
        fh.write(f"== manager relaunch {stamp()} :: {reason}\n")
    try:
        with open(logpath, "ab") as fh:
            p = subprocess.Popen(["zsh", script], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=fh,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    except Exception as e:
        log(f"  relaunch of {name} failed: {e!r}")
        return None
    return p.pid


def restart_ollama():
    subprocess.run(["osascript", "-e", 'quit app "Ollama"'], timeout=20, capture_output=True)
    deadline = now() + 25
    while now() < deadline and any("Ollama.app/Contents/MacOS/Ollama" in r["cmd"] for r in ps_table()):
        time.sleep(1)
    for r in ps_table():
        base = os.path.basename(r["cmd"].split()[0])
        if r["cmd"].endswith("ollama serve") or base in RUNNER_NAMES:
            log(f"  ollama process {r['pid']} ({base}): {terminate(r['pid'], wait=5)}")
    subprocess.run(["open", "-a", "Ollama"], timeout=20, capture_output=True)
    deadline = now() + 60
    while now() < deadline:
        if ollama_ok():
            return True
        time.sleep(2)
    return ollama_ok()


def handle_relaunch(name, status, opts, reason):
    if spent(status["events"], "relaunch", name) >= BUDGET["relaunch"]:
        attention(status, name, f"relaunch budget ({BUDGET['relaunch']} per 6 h) spent; last reason: {reason}", opts)
        return
    pid = relaunch(name, reason)
    if pid is None:
        attention(status, name, "chain script missing or the relaunch failed (see manager.log)", opts)
        return
    record(status, "relaunch", name, f"{reason} -> new shell pid {pid}", opts.notify)


def handle_stale(name, info, status, opts, t_prog):
    ev = status["events"]
    st = status.setdefault("stale", {}).setdefault(name, {})
    idle_min = round((now() - t_prog) / 60) if t_prog else None
    if st.get("step_pid") != info["step_pid"]:
        st.clear()
        st.update(step_pid=info["step_pid"], first_seen=now(), runner_killed_at=None)
        log(f"STALE chain={name} step='{info['step']}' pid={info['step_pid']} "
            f"no progress for {idle_min} min (last progress {stamp(t_prog) if t_prog else 'never'})")
    if st.get("runner_killed_at") is None:
        if spent(ev, "kill_runner") >= BUDGET["kill_runner"]:
            attention(status, name, f"kill_runner budget ({BUDGET['kill_runner']} per 6 h) spent", opts)
            return
        runners = runner_procs(ps_table())
        record(status, "kill_runner", name,
               f"no progress for {idle_min} min at step '{info['step']}'; runner pids {[r['pid'] for r in runners]}",
               opts.notify)
        for r in runners:
            log(f"  runner {r['pid']}: {terminate(r['pid'], wait=10)}")
        st["runner_killed_at"] = now()
        return
    if t_prog and t_prog > st["runner_killed_at"]:
        st.clear()  # the step progressed after the runner kill; start the ladder again if it stalls
        return
    if now() - st["runner_killed_at"] < opts.grace_minutes * 60:
        return
    if spent(ev, "kill_step", name) >= BUDGET["kill_step"]:
        attention(status, name, f"kill_step budget ({BUDGET['kill_step']} per 6 h) spent", opts)
        return
    record(status, "kill_step", name,
           f"still no progress {round((now() - st['runner_killed_at']) / 60)} min after the runner kill; "
           f"terminating step '{info['step']}' pid {info['step_pid']}", opts.notify)
    log(f"  step {info['step_pid']}: {terminate(info['step_pid'], wait=15)}")
    deadline = now() + 30
    while now() < deadline and alive(info["shell_pid"]):
        time.sleep(0.2)
    if alive(info["shell_pid"]):
        log(f"  shell {info['shell_pid']} still alive: {terminate(info['shell_pid'], wait=5)}")
    st.clear()
    handle_relaunch(name, status, opts, reason="step terminated by the manager after a stale period")


# ----- cycle -----------------------------------------------------------------------------------

def load_status():
    try:
        with open(STATUS) as fh:
            s = json.load(fh)
    except Exception:
        s = {}
    s.setdefault("events", [])
    s.setdefault("attention", {})
    s.setdefault("stale", {})
    s.setdefault("ollama", {})
    return s


def write_status(status):
    tmp = STATUS + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(status, fh, indent=1, default=str)
    os.replace(tmp, STATUS)


def cycle(names, opts, status, act):
    rows = ps_table()
    t_prog, which = last_progress(names)
    ok = ollama_ok()
    oll = status["ollama"]
    oll["reachable"] = ok
    oll["consecutive_failures"] = 0 if ok else oll.get("consecutive_failures", 0) + 1
    oll["runners"] = [dict(pid=r["pid"], etime=r["etime"]) for r in runner_procs(rows)]
    previous = {k: v.get("state") for k, v in status.get("chains", {}).items()}
    chains = {}
    for name in names:
        info = classify(name, rows, t_prog, opts.stale_minutes)
        info["relaunches_6h"] = spent(status["events"], "relaunch", name)
        if status["attention"].get(name) and info["state"] not in ("complete", "running"):
            info["state"] = "attention"
            info["note"] = status["attention"][name]
        chains[name] = info
    status["chains"] = chains
    status["progress"] = dict(last=stamp(t_prog) if t_prog else None, file=which,
                              age_min=round((now() - t_prog) / 60, 1) if t_prog else None)
    status["paused"] = os.path.exists(PAUSE)
    status["updated"] = stamp()
    for name, info in chains.items():
        if previous.get(name) != info["state"] and act:
            log(f"state chain={name} {previous.get(name) or '?'} -> {info['state']}"
                + (f" step='{info['step']}'" if info["step"] else ""))
    if act and status["paused"]:
        if not status.get("pause_logged"):
            log(f"paused by {PAUSE}: observing only")
            status["pause_logged"] = True
        act = False
    elif act:
        status["pause_logged"] = False
    try:
        if act:
            act_on(chains, status, opts, t_prog, ok)
    finally:
        write_status(status)  # budgets and events persist even when an action raises
    return status


def act_on(chains, status, opts, t_prog, ok):
    oll = status["ollama"]
    running = [c["chain"] for c in chains.values() if c["state"] in ("running", "stale")]
    if len(running) > 1:
        detail = "+".join(sorted(running))
        recent = [e for e in status["events"] if e["action"] == "concurrent_steps"
                  and e["detail"] == detail and e["t"] > now() - 3600]
        if not recent:
            record(status, "concurrent_steps", None, detail, opts.notify)
    for name, info in chains.items():
        if info["state"] == "stale":
            handle_stale(name, info, status, opts, t_prog)
        elif info["state"] in ("stopped", "dead"):
            handle_relaunch(name, status, opts, reason=f"{info['state']}: {info['last_line']}")
    if not ok and oll["consecutive_failures"] >= OLLAMA_FAILURES_BEFORE_RESTART:
        if spent(status["events"], "restart_ollama") >= BUDGET["restart_ollama"]:
            attention(status, "ollama", f"restart_ollama budget ({BUDGET['restart_ollama']} per 6 h) spent", opts)
        else:
            record(status, "restart_ollama", None,
                   f"API unreachable on {oll['consecutive_failures']} consecutive checks", opts.notify)
            try:
                back = restart_ollama()
            except Exception as e:
                log(f"  ollama restart failed: {e!r}")
                back = False
            log(f"  ollama reachable after restart: {back}")
            if back:
                oll["consecutive_failures"] = 0


def print_status(status):
    p = status["progress"]
    o = status["ollama"]
    print(f"manager status at {status['updated']}  paused={status['paused']}  "
          f"last progress {p['last']} ({p['file']}, {p['age_min']} min ago)  "
          f"ollama reachable={o['reachable']} runners={len(o['runners'])}")
    print(f"{'chain':9} {'state':14} {'shell':>6} {'step':58} {'for':>8} {'relaunch':>8}  note")
    for name, c in status["chains"].items():
        for_s = c.get("step_since_s") if c.get("step") else c.get("since_s")
        print(f"{name:9} {c['state']:14} {str(c.get('shell_pid') or '-'):>6} "
              f"{(c.get('step') or c.get('last_line') or '-')[:58]:58} {fmt_dur(for_s):>8} "
              f"{c['relaunches_6h']:>8}  {c.get('note', '')}")
    recent = [e for e in status["events"] if e["t"] > now() - WINDOW]
    if recent:
        print(f"actions in the last 6 h: {len(recent)}")
        for e in recent[-8:]:
            print(f"  {e['at']}  {e['action']:16} {e.get('chain') or '-':9} {e['detail'][:100]}")


def chain_names(args):
    """Chains from the command line plus, re read every cycle, the names in --chains-file
    (one per line, # comments), so chains can be added while the manager runs."""
    names = list(args.chains)
    if args.chains_file and os.path.exists(args.chains_file):
        with open(args.chains_file) as fh:
            for line in fh:
                s = line.split("#", 1)[0].strip()
                if s and s not in names:
                    names.append(s)
    return names


def main(argv):
    ap = argparse.ArgumentParser(description="supervise the screening chains")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("status", "run"):
        p = sub.add_parser(c)
        p.add_argument("chains", nargs="*", help="chain names, e.g. chain3c (work/screen_chain3c.sh)")
        p.add_argument("--chains-file", default=None, help="file with one chain name per line, re read every cycle")
        p.add_argument("--stale-minutes", type=float, default=12)
        p.add_argument("--grace-minutes", type=float, default=8)
        p.add_argument("--interval", type=float, default=120)
        p.add_argument("--once", action="store_true")
        p.add_argument("--no-notify", action="store_true")
    args = ap.parse_args(argv)
    args.notify = not args.no_notify
    if not chain_names(args):
        ap.error("name at least one chain, or give --chains-file")
    status = load_status()
    if args.cmd == "status":
        print_status(cycle(chain_names(args), args, status, act=False))
        return
    status["attention"] = {}  # a manager start is a human reset of the attention flags
    log(f"manager start pid={os.getpid()} chains={chain_names(args)} chains_file={args.chains_file} "
        f"interval={args.interval:g}s stale={args.stale_minutes:g}min grace={args.grace_minutes:g}min "
        f"python={sys.executable}")
    n = 0
    while True:
        try:
            cycle(chain_names(args), args, status, act=True)
            n += 1
            if n % HEARTBEAT_EVERY == 0:
                summary = ", ".join(f"{k}={v['state']}" for k, v in status["chains"].items())
                log(f"heartbeat {summary}; progress {status['progress']['age_min']} min ago")
        except Exception as e:
            log(f"cycle error: {e!r}")
        if args.once:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main(sys.argv[1:])
