# TU-HD-160B: tube, HD-160 rev B

Material E355. Tube 182.5 x 11.25 mm; gland-seat counterbore D166 H8 x 20 mm at the mouth (design variant).
FE section mesh: 4612 nodes (Q8, h = 2.00 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-315 | single | 21.2 | 21.2 | 350 / 350 | 2.34 | gland-seat counterbore: 67.0 / 32 | 5.5 | 0.13 | 4.42 |  |
| 3J-315 | two-stage | 21.2 | 9.6 | 350 / 700 | 2.34 | gland-seat counterbore: 27.5 / 32 | 2.3 | 0.13 | 4.48 | low stage raised to the chuck minimum 9.6 kN (cut needs 4.9 kN) |
| 6J-315 | single | 21.4 | 21.4 | 350 / 350 | 2.35 | gland-seat counterbore: 3.8 / 32 | 7.6 | 0.04 | 5.67 |  |
| 6J-315 | two-stage | 21.4 | 8.0 | 350 / 600 | 2.35 | gland-seat counterbore: 1.2 / 32 | 2.5 | 0.04 | 5.73 | low stage raised to the chuck minimum 8.0 kN (cut needs 5.0 kN) |
| PIE-315 | single | 22.2 | 22.2 | 350 / 350 | 2.40 | gland-seat counterbore: 13.2 / 32 | 1.0 | 0.04 | 10.67 |  |
| PIE-315 | two-stage | 22.2 | 9.6 | 350 / 550 | 2.40 | gland-seat counterbore: 4.9 / 32 | 0.4 | 0.04 | 10.73 | low stage raised to the chuck minimum 9.6 kN (cut needs 5.9 kN) |

Chosen by the trade study: **6J-315 single**. Baseline (one pressure, 3 jaws): 3J-315 single.

## Features: baseline and chosen

**baseline: 3J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| gland-seat counterbore | H8 | 166 | 20.1 | 67.0 | 32 | 5.5 | 175.2 | 0.4 | 0.80 / 1.6 | **over** |

**chosen: 6J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| gland-seat counterbore | H8 | 166 | 20.2 | 3.8 | 32 | 7.6 | 8.9 | 0.4 | 0.80 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 2.34) | met (min grip 2.35) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (21.2 / 21.2 kN) | met (21.4 / 21.4 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 350 / 350 rpm) | met (G50 350 / 350 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | NOT met (gland-seat counterbore: 67.0 / 32 um) | met (gland-seat counterbore: 3.8 / 32 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 0.80 um) | met (max Ra 0.80 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.13) | met (sigma/Re 0.04) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met with a 3-point gauge (two-point gauge blind on: gland-seat counterbore) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (3.6 kW) | met (3.6 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 6J-315 single | 7.20 | 27 % |
| 6J-315 two-stage | 7.02 | 0 % |
| 3J-315 two-stage | 6.83 | 63 % |
| PIE-315 single | 5.40 | 10 % |
| PIE-315 two-stage | 5.25 | 0 % |

Weight changes of +-10 % that flip the winner: none.
- screened out: 3J-315 single: roundness over budget: gland-seat counterbore

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| lobed fit not detected (gland-seat counterbore) | part binds or leaks at assembly | 0.47 | 7 | 10 | 9 | 630 | two-point gauge blind to odd lobes |
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.56 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.56 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 39.89 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 5.24 | 5 | 1 | 3 | 15 | visual / roundness after release |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.57 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.57 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 39.89 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| lobed fit not detected (gland-seat counterbore) | part binds or leaks at assembly | 8.33 | 7 | 1 | 4 | 28 | visible to the two-point gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 17.33 | 5 | 1 | 3 | 15 | visual / roundness after release |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 0.87 | 0.87 |
| specific cutting force -16 % / +18 % | 0.87 | 0.87 |
| thrust / cutting force 0.3 / 0.8 | 0.87 | 0.87 |
| tool wear factor 1.0 / 1.5 | 0.87 | 0.87 |
| top-jaw mass x0.7 / x1.3 | 0.90 | 0.85 |
| chuck minimum force 4 % / 12 % of max | 0.37 | 1.38 |

Base value 0.87.

## Program read-back (verify.py)

- fanuc: PASS; 4 cutting blocks, max 350 rpm, min grip 2.35; gland-seat counterbore 3.8 um
- sinumerik: PASS; 4 cutting blocks, max 350 rpm, min grip 2.35; gland-seat counterbore 3.8 um
