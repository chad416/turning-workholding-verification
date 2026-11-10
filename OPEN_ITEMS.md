# Open items

Everything software could close is closed (decision log in [DOSSIER.md](DOSSIER.md), section 14). These items need a paid standard, real chuck data or a turned part.

| # | Item | Why it is open | What closes it | Affects |
|---|---|---|---|---|
| W-1 | VDI 3106:2004 and EN 1550 texts | paid; the method and the safety factors are quoted from memory | buy them and compare `clamp.py` with the guideline's worked example | R-01, R-03 |
| W-2 | Chuck data for the actual lathes: maximum and minimum controllable force, jaw masses and centroid radii, rated speed | no maker or model is known; the values are catalogue orders of magnitude | the chuck maker's data sheet, or a force-measuring chuck gauge at standstill and at speed (V-3) | findings 1 and 3 |
| W-3 | Roundness of a turned thin-tube seat in three and six jaws | no part turned | DOSSIER V-1, V-2, V-4 on a roundness instrument | R-04, R-07 |
| W-4 | Jaw/part friction coefficient | assumed 0.10 (varied 0.08-0.20) | slip test V-3 | R-01 |
| W-5 | Kienzle values for C45 and E355 themselves | the open table gives only the nearest grade (E335) | a tool maker's k_c1.1 for these grades, or a dynamometer cut | force inputs (the verdicts do not depend on them, section 6) |
| W-6 | Programs on a real control | not run on a FANUC or Sinumerik control or simulator; the clamp-preset M-codes are builder-specific examples | dry run on the machine with the builder's M-codes | section 10 |
