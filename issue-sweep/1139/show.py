import json, sys
for line in open(sys.argv[1]):
    r = json.loads(line)
    if "fixture_error" in r or "process_exit" in r:
        print(f"{r['case']:24s} !! {r}"); continue
    s = f"{r['case']:24s} add={r['add'][:150]}"
    if r["add"] == "accepted":
        s += f" | fn={r['stored_fn']} c={r['stored_components']} | solve={r['solve'][:120]}"
        if r["solve"] == "ran":
            s += f" reason={r['snes_reason']} its={r['snes_its']}/{r['ksp_its']} u={r['u_hash']} p={r.get('p_hash','-')} bnd={r['on_boundary']} err={r['max_err']}"
    print(s)
