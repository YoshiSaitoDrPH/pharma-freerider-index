"""Renumber bracketed citations [n] in paper/manuscript.md in order of first appearance and reorder the reference list.
Also prints word counts for the VIH title page. Usage: python src/renumber_refs.py"""
import re, pathlib
p = pathlib.Path(__file__).resolve().parents[1] / "paper" / "manuscript.md"
s = p.read_text()
body, refs = s.split("# References\n")
refmap = {int(n): t for n, t in re.findall(r"^(\d+)\. (.*)$", refs, flags=re.M)}
def expand(tok):
    out = []
    for part in tok.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1))
        else: out.append(int(part))
    return out
order = []
for m in re.finditer(r"\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]", body):
    for n in expand(m.group(1)):
        if n not in order: order.append(n)
uncited = [n for n in refmap if n not in order]
new = {old: i + 1 for i, old in enumerate(order)}
def compress(nums):
    nums = sorted(set(nums)); groups = []; start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1: prev = n
        else: groups.append((start, prev)); start = prev = n
    groups.append((start, prev))
    return ",".join(f"{a}-{b}" if b - a >= 2 else (f"{a},{b}" if b != a else f"{a}") for a, b in groups)
body2 = re.sub(r"\[(\d+(?:-\d+)?(?:,\s*\d+(?:-\d+)?)*)\]", lambda m: "[" + compress([new[n] for n in expand(m.group(1))]) + "]", body)
reflist = "\n".join(f"{new[old]}. {refmap[old]}" for old in order)
p.write_text(body2 + "# References\n\n" + reflist + "\n")
main = body2.split("# Introduction")[1].split("# Declaration of generative AI")[0]
wc = lambda t: len(re.findall(r"\S+", re.sub(r"\[[\d,\- ]+\]", "", t)))
print(f"references: {len(order)} (uncited dropped: {uncited})")
print(f"main text words: {wc(main)}")
for sec in ["Introduction", "Methods", "Results", "Discussion", "Conclusions"]:
    print(f"  {sec}: {wc(body2.split('# ' + sec)[1].split(chr(10) + '# ')[0])}")
abstract = body2.split("# Abstract")[1].split("**Keywords")[0]
abs_words = len(re.findall(r"\S+", re.sub(r"\*\*[^*]+\*\*", "", abstract)))
print(f"abstract words: {abs_words}")
hl = body2.split("# Highlights")[1].split("# Introduction")[0]
hl_words = len(re.findall(r"\S+", hl.replace("- ", "")))
print(f"highlights words: {hl_words}")
