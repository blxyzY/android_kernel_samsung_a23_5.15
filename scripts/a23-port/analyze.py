#!/usr/bin/env python3
"""Map A23 (4.19) hardware requirements to what exists in the 5.15 (A05s) tree.

usage: analyze.py <k419_src> <k515_src> <outdir>

Produces:
  missing-configs.txt   CONFIG_ symbols enabled in a23_eur_open_defconfig whose
                        Kconfig symbol does not exist in the 5.15 tree
  present-configs.txt   same, but symbols that DO exist in 5.15
  dts-compat-map.md     compatible strings used by the A23 DTS, with whether a
                        matching driver exists in 5.15 and where the 4.19 one is
"""
import os
import re
import sys
from collections import defaultdict

k419, k515, outdir = sys.argv[1:4]
os.makedirs(outdir, exist_ok=True)

CONFIG_RE = re.compile(r'^\s*(?:menu)?config\s+([A-Z0-9_]+)\s*$', re.M)


def kconfig_symbols(root):
    syms = set()
    for dp, dn, fn in os.walk(root):
        if '/.git' in dp:
            continue
        for f in fn:
            if f.startswith('Kconfig'):
                try:
                    with open(os.path.join(dp, f), errors='replace') as fh:
                        syms.update(CONFIG_RE.findall(fh.read()))
                except OSError:
                    pass
    return syms


def parse_defconfig(path):
    on = {}
    with open(path, errors='replace') as fh:
        for line in fh:
            m = re.match(r'^CONFIG_([A-Z0-9_]+)=(.*)$', line.strip())
            if m:
                on[m.group(1)] = m.group(2)
    return on


syms419 = kconfig_symbols(k419)
syms515 = kconfig_symbols(k515)
a23 = parse_defconfig(os.path.join(k419, 'arch/arm64/configs/a23_eur_open_defconfig'))

missing, present = [], []
for name, val in sorted(a23.items()):
    if val in ('n',):
        continue
    # only symbols that are defined by some Kconfig in 4.19 (skip compiler
    # detected / generated ones that have no config entry)
    if name not in syms419:
        continue
    (present if name in syms515 else missing).append((name, val))

with open(os.path.join(outdir, 'missing-configs.txt'), 'w') as fh:
    fh.write('# Enabled in a23_eur_open_defconfig (4.19) but no Kconfig symbol in the 5.15 tree.\n')
    fh.write('# Each of these is a driver/feature that must be ported or replaced.\n')
    for n, v in missing:
        fh.write('CONFIG_%s=%s\n' % (n, v))
with open(os.path.join(outdir, 'present-configs.txt'), 'w') as fh:
    fh.write('# Enabled in a23_eur_open_defconfig (4.19) and defined in the 5.15 tree.\n')
    for n, v in present:
        fh.write('CONFIG_%s=%s\n' % (n, v))

# ---------------------------------------------------------------- DTS part
dts_root = os.path.join(k419, 'arch/arm64/boot/dts')
search_dirs = [dts_root, os.path.join(dts_root, 'samsung'),
               os.path.join(dts_root, 'samsung/a23'),
               os.path.join(dts_root, 'samsung/a23/a23'),
               os.path.join(dts_root, 'vendor'),
               os.path.join(dts_root, 'vendor/qcom'),
               os.path.join(k419, 'include')]
INC_RE = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.M)


def resolve(inc, cur_dir):
    for base in [cur_dir] + search_dirs:
        p = os.path.join(base, inc)
        if os.path.isfile(p):
            return p
    return None


def collect(entry):
    seen, stack = set(), [entry]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        if not p.endswith(('.dts', '.dtsi')):
            continue
        with open(p, errors='replace') as fh:
            txt = fh.read()
        for inc in INC_RE.findall(txt):
            r = resolve(inc, os.path.dirname(p))
            if r:
                stack.append(r)
    return seen


entry = os.path.join(dts_root, 'samsung/a23/a23/a23_eur_open_w00_r08.dts')
files = sorted(f for f in collect(entry) if f.endswith(('.dts', '.dtsi')))

COMPAT_RE = re.compile(r'compatible\s*=\s*([^;]+);', re.S)
STR_RE = re.compile(r'"([^"]+)"')
compat_users = defaultdict(set)
for f in files:
    with open(f, errors='replace') as fh:
        txt = fh.read()
    for m in COMPAT_RE.finditer(txt):
        for s in STR_RE.findall(m.group(1)):
            compat_users[s].add(os.path.relpath(f, dts_root))

# index driver string literals in both trees
LIT_RE = re.compile(r'"([a-zA-Z0-9_-]+,[a-zA-Z0-9_.,+-]+)"')


def index_drivers(root):
    idx = defaultdict(set)
    for sub in ('drivers', 'sound', 'techpack', 'net', 'kernel', 'arch/arm64'):
        base = os.path.join(root, sub)
        for dp, dn, fn in os.walk(base):
            for f in fn:
                if f.endswith('.c'):
                    p = os.path.join(dp, f)
                    try:
                        with open(p, errors='replace') as fh:
                            for s in set(LIT_RE.findall(fh.read())):
                                idx[s].add(os.path.relpath(p, root))
                    except OSError:
                        pass
    return idx


idx419 = index_drivers(k419)
idx515 = index_drivers(k515)

rows_missing, rows_present, rows_unknown = [], [], []
for c in sorted(compat_users):
    in419 = sorted(idx419.get(c, []))
    in515 = sorted(idx515.get(c, []))
    users = sorted(compat_users[c])
    if in515:
        rows_present.append((c, in515[0], in419[0] if in419 else '-'))
    elif in419:
        rows_missing.append((c, in419[0], users[0]))
    else:
        rows_unknown.append((c, users[0]))

with open(os.path.join(outdir, 'dts-compat-map.md'), 'w') as fh:
    fh.write('# A23 DTS compatible -> driver map\n\n')
    fh.write('Source DTS: `samsung/a23/a23/a23_eur_open_w00_r08.dts` (4.19) with all includes resolved '
             '(%d dts/dtsi files).\n\n' % len(files))
    fh.write('- %d compatible strings total\n' % len(compat_users))
    fh.write('- %d already have a matching driver in the 5.15 tree\n' % len(rows_present))
    fh.write('- %d have a driver only in 4.19 (must be ported)\n' % len(rows_missing))
    fh.write('- %d not found as a literal in any .c file of either tree (generic/binding-only or '
             'matched another way)\n\n' % len(rows_unknown))
    fh.write('## Driver exists only in 4.19 (port needed)\n\n')
    fh.write('| compatible | 4.19 driver | first used in |\n|---|---|---|\n')
    for c, d, u in rows_missing:
        fh.write('| `%s` | `%s` | `%s` |\n' % (c, d, u))
    fh.write('\n## Not found in any driver source\n\n')
    fh.write('| compatible | first used in |\n|---|---|\n')
    for c, u in rows_unknown:
        fh.write('| `%s` | `%s` |\n' % (c, u))
    fh.write('\n## Already present in 5.15\n\n')
    fh.write('| compatible | 5.15 driver |\n|---|---|\n')
    for c, d5, _ in rows_present:
        fh.write('| `%s` | `%s` |\n' % (c, d5))

print('config: %d present in 5.15, %d missing' % (len(present), len(missing)))
print('dts files: %d, compatibles: %d (present %d / only-4.19 %d / unknown %d)' %
      (len(files), len(compat_users), len(rows_present), len(rows_missing), len(rows_unknown)))
