#!/usr/bin/env python3
"""Split A23 board DTS sources into a core overlay and deferred subsystem overlays.

Top-level node blocks (`&label { ... };` or `/ { ... };`) whose target (or any
`&ref` inside) is a label that the khaje base DTB does not provide are moved to
a per-subsystem file (display / audio / camera). The rest stays in place.

usage: split_dts.py <dts-root> <missing-labels.txt> [--apply]
"""
import re
import sys
import os
import glob

GROUP_OF = {}
for l in ("mdss_mdp", "sde_dsi"):
    GROUP_OF[l] = "display"
for l in ("cam_cci0",):
    GROUP_OF[l] = "camera"



def resolve_conditionals(text, defined):
    """Resolve #if/#ifdef/#ifndef/#elif/#else/#endif like cpp would.

    Only simple expressions occur in the A23 sources (0, 1, defined(X), !, &&, ||).
    Macros are NOT expanded; only the conditional directives are evaluated.
    """
    def ev(expr):
        expr = re.sub(r"/\*.*?\*/", "", expr)
        expr = re.sub(r"//.*", "", expr)
        expr = re.sub(r"defined\s*\(\s*(\w+)\s*\)", lambda m: "1" if m.group(1) in defined else "0", expr)
        expr = re.sub(r"defined\s+(\w+)", lambda m: "1" if m.group(1) in defined else "0", expr)
        expr = expr.replace("&&", " and ").replace("||", " or ")
        expr = re.sub(r"!(?!=)", " not ", expr)
        if not re.fullmatch(r"[\s0-9()andort]*", expr):
            raise ValueError("unsupported #if expression: %r" % expr)
        return bool(eval(expr))

    out = []
    stack = []  # (parent_active, taken, active)
    active = True
    defined = set(defined)
    for line in text.split("\n"):
        m = re.match(r"\s*#\s*(ifdef|ifndef|if|elif|else|endif)\b(.*)", line)
        if not m:
            if active:
                dm = re.match(r"\s*#\s*define\s+(\w+)", line)
                if dm:
                    defined.add(dm.group(1))
                um = re.match(r"\s*#\s*undef\s+(\w+)", line)
                if um:
                    defined.discard(um.group(1))
                out.append(line)
            continue
        d, rest = m.group(1), m.group(2)
        if d in ("if", "ifdef", "ifndef"):
            if d == "if":
                cond = ev(rest)
            else:
                name = rest.split()[0]
                cond = (name in defined) if d == "ifdef" else (name not in defined)
            stack.append((active, cond, active and cond))
            active = active and cond
        elif d == "elif":
            pa, taken, _ = stack.pop()
            cond = (not taken) and ev(rest)
            stack.append((pa, taken or cond, pa and cond))
            active = pa and cond
        elif d == "else":
            pa, taken, _ = stack.pop()
            stack.append((pa, True, pa and not taken))
            active = pa and not taken
        else:  # endif
            pa, _, _ = stack.pop()
            active = pa
    return "\n".join(out)


def scan_blocks(text):
    """Return list of (start, end, header) for top-level `{ ... };` blocks.

    Comment/string aware. `start` is the first char of the header line, `end`
    is just after the closing `;` (or `}` when no `;` follows).
    """
    i, n = 0, len(text)
    depth = 0
    blocks = []
    hdr_start = None
    stmt_start = 0
    while i < n:
        c = text[i]
        if text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            i = j + 1
            continue
        if c == "#" and depth == 0:
            # preprocessor line (with continuations) is never part of a block
            j = i
            while True:
                k = text.find("\n", j)
                if k < 0:
                    j = n
                    break
                if text[k - 1] == "\\":
                    j = k + 1
                    continue
                j = k + 1
                break
            i = j
            stmt_start = i
            continue
        if c == "{":
            if depth == 0:
                hdr_start = stmt_start
                hdr_end = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                j = i + 1
                while j < n and text[j] in " \t":
                    j += 1
                if j < n and text[j] == ";":
                    j += 1
                header = text[hdr_start:hdr_end]
                blocks.append((hdr_start, j, header))
                stmt_start = j
                i = j
                continue
        elif c == ";" and depth == 0:
            stmt_start = i + 1
        i += 1
    return blocks


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def target_of(header):
    h = strip_comments(header).strip()
    m = re.search(r"&([A-Za-z_][A-Za-z0-9_]*)\s*$", h)
    if m:
        return m.group(1)
    return None  # root `/` or anonymous


def main():
    root = sys.argv[1]
    missing = set(open(sys.argv[2]).read().split())
    apply_ = "--apply" in sys.argv
    files = sorted(
        glob.glob(os.path.join(root, "*.dts"))
        + glob.glob(os.path.join(root, "*.dtsi"))
        + glob.glob(os.path.join(root, "a23", "*.dts"))
        + glob.glob(os.path.join(root, "a23", "*.dtsi"))
    )
    files = [f for f in files if "-mm-" not in os.path.basename(f)]
    raw = {f: open(f, errors="replace").read() for f in files}
    defined = set()  # nothing predefined: no CONFIG_* are set for DT builds
    data = {}
    for f in files:
        t = resolve_conditionals(raw[f], defined)
        data[f] = (t, scan_blocks(t))

    deferred = {}  # (file, idx) -> group
    defined = {}   # label -> group, for labels defined inside deferred blocks
    group_of = dict(GROUP_OF)

    def grp_for(label):
        return group_of.get(label, "audio")

    def block_labels(text):
        body = strip_comments(text)
        return set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:\s*[A-Za-z_@/]", body))

    changed = True
    deps = set(missing)
    while changed:
        changed = False
        for f, (t, bl) in data.items():
            for idx, (s, e, h) in enumerate(bl):
                if (f, idx) in deferred:
                    continue
                body = t[s:e]
                tgt = target_of(h)
                refs = set(re.findall(r"&([A-Za-z_][A-Za-z0-9_]*)", strip_comments(body)))
                hit = None
                if tgt in deps:
                    hit = tgt
                else:
                    inner = (refs & deps) - ({tgt} if tgt else set())
                    if inner:
                        hit = sorted(inner)[0]
                if hit is None:
                    continue
                g = grp_for(hit)
                deferred[(f, idx)] = g
                changed = True
                for lab in block_labels(body):
                    deps.add(lab)
                    group_of.setdefault(lab, g)

    # report
    summary = {}
    for (f, idx), g in sorted(deferred.items()):
        t, bl = data[f]
        s, e, h = bl[idx]
        tgt = target_of(h) or "/"
        summary.setdefault(g, []).append((os.path.relpath(f, root), tgt, t[s:e].count("\n") + 1))
    for g, items in summary.items():
        print(f"== {g}: {len(items)} blocks, {sum(i[2] for i in items)} lines")
        for rel, tgt, n in items:
            print(f"   {rel:60s} &{tgt:32s} {n:5d} lines")

    if not apply_:
        return
    outs = {}
    for f, (t, bl) in data.items():
        cut = []
        for idx, (s, e, h) in enumerate(bl):
            g = deferred.get((f, idx))
            if g:
                outs.setdefault(g, []).append(
                    f"/* from {os.path.relpath(f, root)} */\n" + t[s:e].strip("\n") + "\n"
                )
                cut.append((s, e))
        if cut:
            new = t
            for s, e in sorted(cut, reverse=True):
                new = new[:s] + new[e:]
            open(f, "w").write(new)
    for g, parts in outs.items():
        path = os.path.join(root, "a23", f"khaje-sec-a23-mm-{g}.dtsi")
        with open(path, "w") as fh:
            fh.write(
                "// SPDX-License-Identifier: GPL-2.0\n"
                f"/*\n * Galaxy A23 4G: {g} nodes carried over from 4.19.\n"
                " * These target labels that the khaje base DTB (CLO 5.15) does not\n"
                " * define; they are provided by the separate Qualcomm display/audio/\n"
                " * camera devicetree repos. Built as their own dtbo, not merged into the\n"
                " * core DTB.\n */\n\n"
            )
            fh.write("\n".join(parts))
        print("wrote", path)


if __name__ == "__main__":
    main()
