# Workholding for turned hydraulic-cylinder parts: grip, speed limit and squeeze

**Systems engineering dossier.** Structure after C. S. Wasson, *System Engineering Analysis, Design, and Development*, 2nd ed. (Wiley, 2016); page numbers are the book's printed pages, the same principles that were read and cited in the companion project [hydraulic-cylinder-design-verification](https://github.com/chad416/hydraulic-cylinder-design-verification) ("project 13"). All engineering numbers come from `python -m clampform report` (reports in `reports/`, programs in `reports/nc/`, figures in `docs/img/`). Every number is tagged **[S]** sourced, **[D]** derived by this project's models, or **[A]** assumed. Section 12 lists the assumptions; section 13 lists every source and how far it was checked.

Author: Chander Vinayak Sharma, 10 Nov 2026. Status: analysis and simulation only. No part was turned and no program was run on a lathe.

---

## 0. The question and the answer

**Question.** Project 13 verified two cylinder designs and project 07 (the [CNC part-family generator](https://github.com/chad416/cnc-part-family-generator)) wrote and geometrically verified the lathe programs for their glands and pistons. Neither knows the chuck. A CNC programmer has to decide **how hard to clamp, how fast the spindle may turn, and whether the squeeze leaves the toleranced diameters round** — and the answer differs between a gland made from bar and the thin tube of the same cylinder. **For each turned part of the two cylinders (tube mouth, gland, piston), which chuck and clamping scheme hold the part safely at the programmed speed and keep every fit inside its tolerance after release, and what must the lathe program contain?**

**Answer.** The three things a generic program header leaves to chance (one chuck pressure, `G50 S3500`, a three-jaw chuck) each fail on a different part, and the deciding parameter is never the cutting force itself:

1. **Speed limit: the large chuck lets go.** Project 07's programs start every tool with `G50 S3500` and face the solid bar to X0 under G96, so the spindle reaches 3500 rpm at the end of every facing cut [D, from the program text]. For the HD-160 gland and piston (bar D165, 315 mm chuck with soft top jaws), the static force their own heaviest cut needs is **50.6 kN** (VDI 3106 method) [D], while the jaws' centrifugal force at 3500 rpm is **106.6 kN** [D]: the grip is gone (**-56 kN**) before the cut ends. The soft jaws are **1.33 ×** heavier (sum of m·r) than the chuck's speed rating assumes [D]. The derived limit is **1950 rpm**. On the 210 mm chuck (LD-80 parts) the same header is safe: **16.4 kN** remain at 3500 rpm and the allowed speed is 3664 rpm [D]. Every program written here carries its own G50 / LIMS per stage.
2. **Squeeze: the thin tube comes out three-lobed, and a micrometer cannot see it.** Turning a toleranced seat at the mouth of the LD-80 tube (90 × 5 mm, counterbore D84 H8) in a three-jaw chuck at the single pressure the roughing cut needs (19 kN) leaves **117.6 µm** of roundness error after release against a budget of **27 µm** (half the H8 band) [D]. A two-point gauge sees only **3.4 µm** of it, because a three-lobed shape has a constant two-point size; a 108° vee shows it amplified 2.6 × [D].
3. **Two-stage clamping is the textbook fix, and it is not enough on the thin tube: the chuck's minimum force decides.** Dropping to the low preset for the finishing cut would need only **4.8 kN**, but the chuck cannot be set below **5.8 kN** (8 % of its maximum [A]), which still leaves **30.0 µm** > 27 µm [D]. None of the cutting-force inputs moves this verdict (sensitivity, section 6), only the chuck minimum and the jaw mass do. **The deciding parameter is the number and arc of the jaw contacts**: a six-jaw compensating chuck gives **4.4 µm** at the same single pressure (0.9 µm with two stages) and pie jaws 23.1 µm (5.0 µm with two stages) [D].
4. **The same physics says the bar-made glands and pistons need nothing special.** Gripped on the bar behind the part, the clamp deformation does not reach the toleranced surfaces: the worst feature uses at most **25 %** of its roundness budget with a plain three-jaw chuck at one pressure [D]. The jaws reach far along a thin tube but only a few millimetres into a thick ring (section 7, figure `jaw_reach.png`).
5. **The HD-160 tube (182.5 × 11.25 mm) sits on the boundary**: three jaws at one pressure **67.0 µm** against **32 µm**; with two stages **27.5 µm**, inside but again set by the chuck minimum (9.6 kN, while the cut needs 4.9 kN) [D]. Here the trade study is not robust: the six-jaw chuck wins the weighted sum, three jaws with two stages win most random weight sets (section 6).

The project writes the lathe programs (FANUC and Sinumerik) for the chosen workholding of every part, and **reads each program back** (`verify.py`): it re-simulates the material from the G-code text, recomputes chip, Kienzle force, actual spindle speed, centrifugal loss and grip for every cutting block, and checks the preset switching, the dwells at the groove bottoms and the roundness after release. All 12 programs pass. During development the read-back found one real planner error: entering a groove to finish its bottom is a full-width plunge, which the planner had costed as a light side pass (decision D-07).

---

## 1. Need, problem space and concept of operations (Wasson ch. 4-6)

**Problem statement** (Principle 4.15, p. 91). A make-to-order cylinder shop turns glands, pistons and tube ends in single pieces and small batches. Programs are written per order, often from a part-family template. The template fixes the geometry, but the workholding (jaw type, chuck pressure, spindle-speed limit) is left to the set-up person, and a header such as `G50 S3500` is copied into every program. Two consequences are invisible until they hurt: a part that is released by the jaws at speed, and a fit that measures right with a micrometer and still does not assemble.

**Stakeholders and needs** (Principle 4.12, p. 89):

| Stakeholder | Need |
|---|---|
| Cylinder design (project 13) | fits (H8/f7 gland in the honed bore, H9 seal grooves, h9 piston grooves) as specified; clearances that the buckling analysis relied on |
| CNC programmer | a program per part with the right speed limit and clamping instructions, without trial runs |
| Machine operator | safe spindle speeds; a set-up sheet that says which jaws and which pressures |
| Quality | an inspection method that sees the error the process makes |
| Assembly | glands that slide into the tube; seal grooves that give the specified squeeze |
| Production planning | cycle time per part, set-up time per batch |

**Use cases** (Principles 5.12-5.23, pp. 120-122):

| UC | Outcome | Trigger | Main scenario | When it goes wrong | Covered by |
|---|---|---|---|---|---|
| UC-1 | Hold the part during roughing | program starts | jaws grip, every cut is transferred by friction | part slips or is thrown at speed | `clamp.py`, rule W1 |
| UC-2 | Finish a fit round | finishing cut | the squeeze during the cut is small enough | lobed fit after release | `harmfe.py`, `form.py`, rule W7 |
| UC-3 | Face to the centre | G96 facing | speed rises to the G50 limit | grip lost to centrifugal force | `audit07.py`, rule W1/W2 |
| UC-4 | Change pressure between stages | rough → finish | spindle stops, preset switches, dwell, restart | pressure drops while turning | rule W3 |
| UC-5 | Finish a groove bottom | grooving | plunge, dwell, side pass, dwell | thin wall springs back, bottom oversize | rule W4 |
| UC-6 | Inspect the fit | part released | gauge reading inside tolerance means the part fits | two-point gauge blind to 3 lobes | `form.py` gauges, R-07 |

**Concept of operations** (Principle 6.6, p. 139). The part rows come from project 13's verified designs (`data/parts.json`, single information source, Principle 27.4, p. 579). `clampform` plans the operations, computes for each one the cutting force (Kienzle), the clamping force it needs (VDI 3106 method), the spindle speed under G96 and the centrifugal loss, and evaluates six workholding strategies (three chucks × one or two pressures). The squeeze is computed by a Fourier-harmonic axisymmetric finite-element model of the part's real section at the moment each surface is finished. A trade study picks the strategy, the program is written for it, and the read-back verifier checks the program text against the same physics.

---

## 2. Phases, modes and states (Wasson ch. 7)

Phases (Section 7.3, p. 150), modes (Principle 7.4, p. 157) and states (Principles 7.3, 7.8, 7.9, pp. 156-166) of the part on the lathe. Each one that loads the part becomes a load case.

| Kind | Name | What it does to the part | Load case |
|---|---|---|---|
| phase | set-up | jaws bored or changed, presets set | chuck data, set-up time |
| phase | roughing | large torque | high preset, grip at speed |
| phase | finishing | small torque; the surface takes the shape of the squeezed section | low preset, roundness after release |
| phase | inspection | released part | two-point / vee / roundness gauges |
| mode | G96 constant surface speed | speed rises as the diameter falls | centrifugal loss at the G50 limit |
| mode | G97 constant speed | drilling | torque at fixed speed |
| mode | clamp preset high / low | static force | grip and squeeze |
| dynamic state | spindle at speed | jaws fly outwards, grip falls | F_c = Σ m r ω² |
| dynamic state | spindle stopped | full static force | stress in the gripped section |
| dynamic state | groove plunge at depth | thin wall deflected by the feed force | spring-back, dwell |

**Prohibited actions** (Principle 7.10, p. 169), enforced by the read-back verifier: switching the clamp preset while the spindle turns (W3); G96 without a speed limit (W2); a groove plunge to depth without a dwell of at least two revolutions (W4).

---

## 3. Requirements (Wasson ch. 19-22)

Each requirement follows Principle 22.5 (p. 449) and names its verification method (Principle 22.4, p. 448; methods after Principle 13.10, p. 280). Sources are standards, the seal maker's installation tables, or derived needs (Section 21.4, p. 436).

| ID | Requirement | Source | Method |
|---|---|---|---|
| R-01 | Every cut shall leave a grip µ (F_set − F_c(n)) / F_transfer ≥ S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method [S, not re-checked] | A; T (slip test) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data [A] | I |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating practice [S, not re-checked] | A; I |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the least-squares circle) | ISO 14405-1 envelope requirement on fits; machined at mid-tolerance, a lobe amplitude a gives MCC = two-point size + 2a, so 2a ≤ IT/2 [D] | A; T |
| R-05 | Seal and guide groove bottoms Ra ≤ 1.6 µm, other turned surfaces Ra ≤ 3.2 µm | seal maker's catalogue, Table V "groove surface Ra < 1.6 µm" [S, checked]; 3.2 µm project choice [A] | A; T |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule (no jaw marks, no permanent set) [A] | A |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 roundness; derived from UC-6 [D] | I |
| R-08 | Cutting power shall not exceed the spindle power | machine data [A] | A |

Tolerances: gland OD f7 in the honed H8 bore (clearance fit, assumed practice) [A]; rod-seal groove H9 and piston-seal groove h9 [S, checked in the seal maker's installation tables]; guide-ring groove H8/h8 and wiper groove H11 [A, from memory]; ISO 286-1 IT values [S, from memory, cross-checked against the standard tolerance unit in a test].

**Specification issue found** (Principle 19.4, p. 400). R-04 is not written on drawings as "roundness ≤ IT/2"; it follows from the envelope requirement (Ⓔ) that a fit needs. Without Ⓔ, ISO 8015's independency principle lets a three-lobed seat pass inspection with any two-point gauge. The derived requirement R-07 exists for that reason: the drawing of a thin-walled fit must carry Ⓔ or a roundness tolerance, and the inspection plan must use a gauge that sees three lobes.

---

## 4. Architecture and interfaces (Wasson ch. 26-27)

**Physical architecture** (Principle 26.5, p. 551) of the workholding system:

```
clamping cylinder (preset pressure, M61 / M62) ─ draw bar ─ chuck body ─ base jaws ─ top jaws (soft / pie / 6-jaw)
                                                                                       │ friction µ, contact arc
                                                                         part section (bar remnant / tube wall)
spindle (G96 / G97, G50 / LIMS limit) ─ centrifugal force on the jaws ──────────────────┘
tool (insert, nose radius, feed) ─ cutting force (Kienzle) ─ torque and radial force on the part
```

**Interfaces** (Principles 27.1, p. 575; 27.6, p. 583; owner after Principle 27.3, p. 577):

| ID | Interface | Across it | Owner | Becomes |
|---|---|---|---|---|
| IF-1 | jaw ↔ part | radial force, friction, contact arc | process planning | R-01, R-04, R-06 |
| IF-2 | program ↔ control | G50 / LIMS, G96 S, M61 / M62, G4 | CNC programmer | R-03, rules W2-W4 |
| IF-3 | control ↔ chuck clamping cylinder | preset pressure → static force | machine builder | R-02, chuck minimum |
| IF-4 | tool ↔ part | cutting force, feed, nose radius | CNC programmer | Kienzle, R-05 |
| IF-5 | design ↔ manufacturing | fits, roughness, envelope Ⓔ | design (project 13) | R-04, R-05, R-07 |
| IF-6 | part ↔ inspection | gauge type and its sensitivity to lobes | quality | R-07 |
| IF-7 | project 07 programs ↔ this project | program text (G50, G96 facing, G71 depth and feed) | project 07 | speed-limit audit |

The verifier makes IF-2 testable: it only reads the program text, so a program edited at the machine can be re-checked.

---

## 5. Budgets and margins (Wasson ch. 31)

A safety margin accommodates "variations and uncertainty" in a measure of performance (Section 31.2, p. 667); every capability needs one (Principle 31.1, p. 667).

| Margin | Value | Basis |
|---|---|---|
| cutting-force safety on the transferred force | S_z = 1.5 | VDI 3106 [S, not re-checked] |
| static clamping-force safety | S_sp = 1.5 on (F_spz + F_c) | VDI 3106 [S, not re-checked] |
| friction jaw/part | µ = 0.10 | smooth soft jaws on machined steel [A], varied 0.08-0.20 |
| tool wear on the cutting force | K_wear = 1.3 | between new and the 1.5 the source quotes [S/A] |
| roundness | RONt ≤ IT/2 | derived from the envelope requirement (R-04) [D] |
| finishing feed | Ra ≤ 0.8 × requirement | project margin [A]; the feed is solved for it with the ploughing term |
| clamping stress | σ ≤ Re / 1.5 | project rule [A] |

**Roundness budget, apportioned** (Principle 31.4, p. 668), H8 seat D84 on the LD-80 tube (54 µm band): the half band (27 µm) is the allowance for the lobe shape that two-point gauging cannot see; the other half is the size scatter the machine and the gauge are allowed. The tool-load deflection (1.8 µm, section 7) is a size error and goes into the second half.

**Force budget, three jaws on the LD-80 tube:** the finish cut needs 4.8 kN static (VDI); the chuck minimum is 5.8 kN; at 5.8 kN the squeeze during the cut is 5.8 kN minus 0.1 kN centrifugal, and the lobe is 30.0 µm. The cut's own need would give about 25 µm: inside the budget. The 1 kN between them is what decides.

---

## 6. Analysis of alternatives (Wasson ch. 32)

Method after Wasson Fig. 32.7 (p. 690): criteria and weights, linear 0-10 utilities, viable candidates only (p. 683: a candidate that fails a must requirement is screened out), scoring, ranking, and sensitivity: every weight ±10 % (Wasson's definition, p. 682) and 2000 random weight sets. Scores are **model** (computed) or **judgement** (reason written next to it in `clampform/aoa.py`, Principle 32.5, p. 697).

| Criterion | Weight | Kind |
|---|---|---|
| roundness margin (1 − RONt / budget, worst feature) | 0.30 | model |
| cycle time per part, set-up spread over a batch of 4 | 0.25 | model |
| grip margin at speed | 0.10 | model |
| changeover for high-mix work (pie jaws are bored per diameter) | 0.20 | judgement |
| investment (6-jaw chuck about 2.5 × a 3-jaw; pie set 1.2 ×; two-stage needs a programmable valve) | 0.15 | judgement |

| Part | Screened out (not viable) | Winner | Robustness |
|---|---|---|---|
| TU-LD-80C | 3J-210 single, 3J-210 two-stage | 6J-210 single (7.87) | wins 86 % of random weight sets; ±10 % flips: none |
| TU-HD-160B | 3J-315 single | 6J-315 single (7.20) | wins 27 % of random weight sets; ±10 % flips: none; **not robust**: 3J-315 two-stage wins 63 % of random weight sets |
| GL-LD-80C | none | 3J-210 single (9.33) | wins 100 % of random weight sets; ±10 % flips: none |
| GL-HD-160B | none | 3J-315 single (9.24) | wins 99 % of random weight sets; ±10 % flips: none |
| PI-LD-80C | none | 3J-210 single (9.56) | wins 99 % of random weight sets; ±10 % flips: none |
| PI-HD-160B | none | 3J-315 single (9.80) | wins 100 % of random weight sets; ±10 % flips: none |

**Sensitivity of the deciding verdict** (three jaws, two stages, worst RONt / budget; `docs/img/TU-LD-80C_sensitivity.png`). On the LD-80 tube the ratio is **1.11** and stays 1.11 for jaw friction 0.08-0.20, specific cutting force −16 %/+18 %, thrust ratio 0.3-0.8 and tool wear 1.0-1.5 [D]: the low preset is pinned at the chuck minimum, so the cut does not set the squeeze. Only the chuck minimum (0.88 at 4 % of the maximum force, 1.81 at 12 %) and the jaw mass (1.16 / 1.06 for ×0.7 / ×1.3) move it. That is the evidence for finding 3: buying a chuck with a lower controllable minimum force, or more contact points, decides the outcome; better cutting data does not.

---

## 7. Modelling and simulation (Wasson ch. 33)

"All models are wrong but some are useful" (Principle 33.5, p. 718). The fidelity of each model is stated (Principle 33.1, p. 706) and each is **verified** against an independent result in `tests/`. None is **validated** against a measured part yet; section 9 is the plan to do that.

| Model | Fidelity | Verified against (test) | Not modelled |
|---|---|---|---|
| squeeze: Fourier-harmonic axisymmetric FE (`harmfe.py`) | 8-node quadrilaterals in the (r, z) section, circumferential harmonics k = 0, n, 2n ... 48 for n jaws, jaw arc load as a Fourier series, linear elastic | thin-ring theory for 2, 3 and 6 jaws and pie jaws (0.5 %; 1.5 % at k = 6 where shear and thickness enter); Roark's two-point ring coefficient (π² − 8)/(4π) = 0.1488; Lamé bore displacement under external pressure (1 %); Fourier series rebuilds the jaw pressure | contact stiffness and local indentation under the jaw; friction between jaw and part (the jaws are force-controlled); material removal during the cut (the section is taken at the finishing stage) |
| released profile and metrics (`form.py`) | profile = clamped deformation mirrored; LS circle, two-point size range, MCC/MIC, vee-block kinematics | two-point gauge reads zero for odd lobes and 2 × RONt for an oval; vee sensitivity 1 − cos(kβ)/cos β (2.62 for 3 lobes in 108°, 2.0 for 5 lobes in 60°, 3.0 for 3 lobes in 120°) | form error from machine spindle run-out |
| cutting force (`cutting.py`) | Kienzle k_c1.1, m_c with rake, speed, wear and process factors; mean chip thickness over the engaged nose; Colwell equivalent edge for the force direction | closed form for a sharp nose and large depth; passive force dominating at a_p < r | built-up edge, tool-specific force ratios |
| surface roughness | arc profile Ra = f²/(18√3 r) plus Brammertz ploughing term (h_min = 2 µm [A]) | closed form | vibration, tool wear |
| clamping (`clamp.py`) | VDI 3106 form; jaw centrifugal force from masses and centroid radii | hand calculation; speed limit is the inverse of the force requirement | jaw elasticity, chuck friction hysteresis |
| tool-load deflection | same harmonic FE, grip zone held, radial patch load, k = 0-24 | (consistency with the clamp model; part of the size budget only) | dynamic response, chatter |
| program read-back (`verify.py`) | text parser with modal state; material as outer/inner radius per 0.05 mm | finishing forces from the text agree with the planner within 2 %; deliberate edits are caught (W1-W4) | canned cycles (the programs use explicit moves) |

**Two model-based findings only the simulation could give:**

1. **How far the jaws reach** (`docs/img/jaw_reach.png`). Along the bore, the lobing per 10 kN at the jaw edge and its decay away from the jaws: on the 5 mm LD-80 tube 49.6 µm per 10 kN at the jaw edge, 21.8 µm 25 mm away and still 7.9 µm 50 mm away; on the 11.25 mm HD-160 tube 24.0 µm at the edge, 15.9 µm at 25 mm and 10.0 µm at 50 mm (the thicker, larger tube decays more slowly); in the LD-80 gland bar work the bore at the part is at most 2.0 µm per 10 kN and 0.7 µm 25 mm from the jaws. A thin shell carries the three-lobe (k = 3) deformation a long way (semi-membrane behaviour), a thick ring does not. This is why the same chuck is harmless for bar work and decisive at a tube mouth.
2. **Where the gauge is blind.** For the three-jaw chuck the released profile is dominated by k = 3 with a little k = 6. A two-point measurement of a pure k = 3 lobe reads exactly zero; the small k = 6 content is all it sees (3.4 µm of 117.6 µm on the LD-80 tube). A vee of 108° reads 2.62 × RONt, a 90° vee 2.0 ×; a 60° vee is right for five lobes, not three (`docs/img/gauge_sensitivity.png`).

---

## 8. Reliability and FMEA (Wasson ch. 34)

RPN = S × O × D (Wasson eq. 34.41, p. 765). Occurrence is read from the computed margin with a fixed rule (`clampform/fmea.py`, same rule shape as project 13), so the ranking moves with the strategy. Severity and detection are judgement per row. LD-80 tube, three jaws at one pressure (baseline):

| Failure mode | Margin | O | RPN |
|---|---|---|---|
| lobed fit not detected (two-point gauge blind) | 0.23 | 10 | 630 |
| part thrown at speed (centrifugal loss of grip) | 1.57 | 3 | 240 |
| part slips under the cutting torque | 1.57 | 3 | 54 |
| clamp yields the section | 1.68 | 3 | 45 |
| groove / seat off size (wall deflects under the tool) | 7.4 | 1 | 36 |

With the chosen six-jaw chuck the lobing row falls to O = 1 and D = 4 (RPN 28): it is then visible to the two-point gauge because it is no longer an odd lobe, and it is small. The top row becomes "part thrown at speed" with severity 10. Detection there is 8 because nothing on the machine shows a falling grip; only the calculation in the program (R-03) or a slip test (V-3) does. For the HD-160 bar parts this row is the one the project 07 header fails outright (finding 1).

The strength-stress view (Principle 34.21, p. 752) is applied to the gripped section: σ/Re = 0.40 for the three-jaw grip on the LD-80 tube at 19 kN, inside the 1/1.5 rule. Wear-out (Principle 34.20, p. 751) enters through the jaws: soft jaws bored to the grip diameter lose contact arc as they wear, which moves a pie jaw towards a three-point grip; V-6 re-measures it.

---

## 9. Verification and validation (Wasson ch. 13 and 28)

Verification asks "did we build it right?" and validation "did we build the right thing?" (Principles 13.3 and 13.4, p. 275). One test verifies as many requirements as practical (Principle 28.3, p. 608); the gauges are calibrated (Principle 28.9, p. 618); every pass limit is a number the analysis relied on, so passing also validates the model.

| Step | Test | Pass limit | Validates |
|---|---|---|---|
| V-1 | turn the LD-80 tube seat with three jaws at 19 kN and at 5.8 kN, release, measure on a roundness instrument (ISO 12181, LS circle, 1-50 UPR filter) | RONt within ±25 % of 117.6 / 30.0 µm; harmonic k = 3 dominant | the harmonic FE and the "mirror" assumption |
| V-2 | measure the same parts with a two-point bore gauge and a 108° three-point gauge | two-point range < 10 % of RONt; three-point reading 2.6 × RONt ± 20 % | the gauge kinematics; R-07 |
| V-3 | slip test: marked part, increasing torque at standstill and at 1000 / 2000 rpm, with a force-measuring chuck gauge | measured static force within ±10 % of the preset; loss at speed within ±20 % of Σ m r ω² | the centrifugal model and µ |
| V-4 | six-jaw chuck, same part, same force | RONt ≤ 27 µm | the chosen strategy (R-04) |
| V-5 | groove bottoms with and without the 2-revolution dwell, measured with an internal groove gauge | difference within ±50 % of the computed deflection | tool-load model, rule W4 |
| V-6 | jaw contact pattern (marking paste) on worn soft / pie jaws | contact arc ≥ the modelled one | contact assumption |

Integration is incremental (Principle 28.1, p. 605): static force first (V-3 at standstill), then speed, then form; a failure is isolated by the step it appears in (Principle 28.2, p. 606).

**Program verification.** Every program in `reports/nc/` is read back by `python -m clampform verify` in CI. The rules W1-W7 are listed in `clampform/verify.py`. The tests prove the verifier catches each rule's violation when the program is deliberately edited (preset switched while turning, dwell removed, G50 removed, low preset below the cut's need).

---

## 10. The lathe programs

`reports/nc/<part>.nc` (FANUC) and `.mpf` (Sinumerik) for the chosen strategy of each part. What the workholding analysis adds to the program, compared with project 07's output for the same parts:

- a set-up block in the header: chuck and jaw type, grip diameter and axial range, the two preset forces in kN;
- `M61` / `M62` (builder-specific example codes for two pressure presets) with spindle stop and a 2 s dwell around the switch;
- `G50 S` / `LIMS=` per stage from the grip-at-speed requirement, not the machine maximum;
- finishing feeds solved from the Ra requirement with the ploughing term (e.g. OD finish 0.12 mm/rev, groove side passes 0.075 mm/rev with the 0.2 mm corner radius);
- a dwell of two revolutions at every groove bottom (`G4 X` seconds for FANUC, `G4 S2` revolutions for Sinumerik).

The programs use explicit G0/G1 moves (no canned cycles) so the read-back sees every cut. They were not run on a control or a simulator.

---

## 11. Results summary

| part | baseline worst RONt / budget | chosen | chosen worst RONt / budget | G50 rough / finish | programs |
|---|---|---|---|---|---|
| TU-LD-80C | 4.36 | 6J-210 single | 0.16 | 800 / 800 | PASS |
| TU-HD-160B | 2.13 | 6J-315 single | 0.12 | 350 / 350 | PASS |
| GL-LD-80C | 0.25 | 3J-210 single | 0.25 | 800 / 800 | PASS |
| GL-HD-160B | 0.11 | 3J-315 single | 0.11 | 350 / 350 | PASS |
| PI-LD-80C | 0.10 | 3J-210 single | 0.10 | 1450 / 1450 | PASS |
| PI-HD-160B | 0.05 | 3J-315 single | 0.05 | 1000 / 1000 | PASS |

Speed-limit audit of project 07's programs: `reports/SUMMARY.md`.

---

## 12. Limits and assumptions

- **No part was turned.** The roundness numbers are model results; V-1 to V-6 would validate them.
- **Chuck data are assumed** catalogue orders of magnitude (`data/machine.json`): maximum and minimum force, jaw masses and centroid radii, rated speeds. The minimum controllable force (8 % of maximum) decides finding 3; section 6 varies it.
- **Jaws are modelled as force-controlled arc loads** on the gripped surface. Rigid jaws that also constrain the part between cuts, jaw indentation and friction in the contact are not modelled.
- **The section at finishing is taken as the final geometry** (for the usual sequence, the OD of bar parts is finished on the section with the stock bore). Material removal during the finishing cut and residual stresses from earlier cuts are not modelled.
- **Kienzle values for C45 and E355** are those of the nearest tabulated steel (E335) in a secondary source; the verdicts were shown not to depend on them.
- **VDI 3106 and EN 1550** were not available; their method (S_z, S_sp, the 1/3 rating rule) is quoted from memory.
- **The gland-seat counterbore in the tube** is a design variant, not part of project 13's design; it stands for any toleranced turned diameter near the mouth of a thin tube.
- **Chatter is not modelled.** Thin walls also chatter; that would need the dynamic stiffness and is left out rather than guessed.

---

## 13. References and how far each was checked

| # | Source | Used for | Status |
|---|---|---|---|
| W | C. S. Wasson, *System Engineering Analysis, Design, and Development*, 2nd ed., Wiley 2016 | dossier structure; cited principles | checked in project 13 (chapters 4-7, 13, 19-22, 26-28, 31-34); the same principles are cited here |
| S1 | de.wikipedia, "Spezifische Schnittkraft" (fetched 10 Nov 2026): k_c1.1 / m_c table (S275JR 1780/0.17, E335 2110/0.17, 42CrMo4 2500/0.26) and correction factors, citing H. Tschätsch, *Praxis der Zerspantechnik*, 10th ed., 2011, p. 18 | cutting force | checked (page read); the cited book itself not opened |
| S2 | Trelleborg Sealing Solutions, *Hydraulic Seals - Linear: Rod Seals*, Edition January 2011: Turcon Stepseal 2K, Table XII (groove D1 H9, rod f8/h9) | rod-seal groove tolerance | checked (catalogue PDF, table read) |
| S3 | Trelleborg Sealing Solutions, *Hydraulic Seals - Linear: Piston Seals*, Edition January 2011: Table V surface roughness (groove surface Ra < 1.6 µm); Turcon Glyd Ring Table X (bore H9, groove d1 h9) | R-05, piston groove tolerance | checked (catalogue PDF, tables read) |
| S4 | VDI 3106:2004 *Determination of permissible speed of lathe chucks (jaw chucks)* | clamping-force method, S_z, S_sp, centrifugal force | NOT available; method quoted from memory |
| S5 | EN 1550 *Machine tools safety - Safety requirements for the design and construction of work holding chucks* | speed-rating rule (1/3 of the force left at n_max) | NOT available; quoted from memory |
| S6 | ISO 286-1 *ISO code system for tolerances on linear sizes* | IT values, deviation f | from memory; test against the standard tolerance unit i = 0.45 D^(1/3) + 0.001 D |
| S7 | ISO 14405-1 (envelope requirement), ISO 8015 (independency principle), ISO 12181 (roundness) | R-04, R-07 | from memory, not re-checked |
| S8 | O. C. Zienkiewicz, R. L. Taylor, J. Z. Zhu, *The Finite Element Method*, vol. 1 (semi-analytical / harmonic axisymmetric elements); R. D. Cook et al., *Concepts and Applications of FEA*, 4th ed. | harmonic FE formulation | not re-checked; tests against ring theory, Roark and Lamé |
| S9 | W. C. Young, R. G. Budynas, *Roark's Formulas for Stress and Strain*, ch. 9 (rings) | two-point ring coefficient 0.1488 | from memory; test reproduces (π² − 8)/(4π) exactly from the Fourier series |
| S10 | Brammertz (1961), minimum chip thickness correction of the kinematic roughness | Ra with ploughing | from secondary sources; h_min assumed |
| S11 | D. J. Whitehouse, *Handbook of Surface and Nanometrology* (vee-block roundness measurement) | vee sensitivity, 3 lobes in 108° | not re-checked; the formula is derived in `form.py` and checked by a test |
| S12 | project 13 reports (`reports/HD-160.md`, `reports/LD-80.md`): gland and piston rows, tube sizes | part data | checked (copied) |
| S13 | project 07 programs for the same parts (copies in `data/p07/`) | speed-limit audit | checked (read by `audit07.py`) |

---

## 14. Decision log

| # | Decision | Alternatives considered | Evidence |
|---|---|---|---|
| D-01 | Fourier-harmonic axisymmetric FE for the squeeze | thin-ring formula; full 3-D FE | ring formula ignores the section shape and the axial reach; the harmonic FE is exact for a body of revolution and solves in seconds; agrees with ring theory to 0.5 % |
| D-02 | Roundness budget = IT/2 (R-04) | no form requirement (ISO 8015 independency) | a fit needs Ⓔ; with mid-tolerance machining 2a ≤ IT/2 is the envelope condition |
| D-03 | The squeeze during a cut is F_set − F_c(n), not F_set | use the static preset | the centrifugal loss relieves the squeeze; using F_set would overstate the lobing |
| D-04 | Every program carries its own G50 / LIMS per stage | one machine-wide limit | the HD-160 audit: the machine maximum releases the part (finding 1) |
| D-05 | Thin tube: six-jaw chuck at one pressure | three jaws two-stage; pie jaws; six jaws two-stage | LD-80: three jaws fail R-04 even at the chuck minimum; pie jaws pass but cost a bored jaw set per diameter; a second stage adds nothing the six jaws need (section 6). HD-160: three jaws two-stage is viable (0.87 of budget) and wins most random weight sets, so a lathe that already has a programmable two-stage valve can keep three jaws for this tube |
| D-06 | Bar-made glands and pistons: keep the three-jaw chuck | six-jaw, pie | the clamp does not reach the toleranced surfaces (section 7) |
| D-07 | Groove finish costed as entry plunge + side pass (heavier governs) | side pass only | the read-back found the full-width entry plunge needs more grip than the low preset gave |
| D-08 | Finishing feed solved from Ra with the ploughing term | tool library feed | the library feed gave Ra 1.77 µm on a 1.6 µm groove with the ploughing term |
| D-09 | Chatter left out | a single-mode stability lobe with assumed damping | without measured damping the limit would be a guess; stated in section 12 |
