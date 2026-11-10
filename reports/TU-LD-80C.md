# TU-LD-80C: tube, LD-80 rev C

Material E355. Tube 90 x 5 mm; gland-seat counterbore D84 H8 x 15 mm at the mouth (design variant).
FE section mesh: 6721 nodes (Q8, h = 1.00 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-210 | single | 19.0 | 19.0 | 750 / 750 | 2.36 | gland-seat counterbore: 117.6 / 27 | 3.4 | 0.40 | 3.36 |  |
| 3J-210 | two-stage | 19.0 | 5.8 | 750 / 950 | 2.36 | gland-seat counterbore: 30.0 / 27 | 0.9 | 0.40 | 3.47 | low stage raised to the chuck minimum 5.8 kN (cut needs 4.8 kN) |
| 6J-210 | single | 19.3 | 19.3 | 800 / 800 | 2.35 | gland-seat counterbore: 4.4 / 27 | 8.7 | 0.14 | 4.60 |  |
| 6J-210 | two-stage | 19.3 | 5.0 | 800 / 800 | 2.35 | gland-seat counterbore: 0.9 / 27 | 1.8 | 0.14 | 4.72 |  |
| PIE-210 | single | 20.0 | 20.0 | 750 / 750 | 2.42 | gland-seat counterbore: 23.1 / 27 | 0.6 | 0.12 | 9.61 |  |
| PIE-210 | two-stage | 20.0 | 5.8 | 750 / 800 | 2.42 | gland-seat counterbore: 5.0 / 27 | 0.1 | 0.12 | 9.72 |  |

Chosen by the trade study: **6J-210 single**. Baseline (one pressure, 3 jaws): 3J-210 single.

## Features: baseline and chosen

**baseline: 3J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| gland-seat counterbore | H8 | 84 | 17.8 | 117.6 | 27 | 3.4 | 307.9 | 1.8 | 0.80 / 1.6 | **over** |

**chosen: 6J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| gland-seat counterbore | H8 | 84 | 17.9 | 4.4 | 27 | 8.7 | 10.3 | 1.8 | 0.80 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 2.36) | met (min grip 2.35) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (19.0 / 19.0 kN) | met (19.3 / 19.3 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 750 / 750 rpm) | met (G50 800 / 800 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | NOT met (gland-seat counterbore: 117.6 / 27 um) | met (gland-seat counterbore: 4.4 / 27 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 0.80 um) | met (max Ra 0.80 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.40) | met (sigma/Re 0.14) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met with a 3-point gauge (two-point gauge blind on: gland-seat counterbore) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (3.1 kW) | met (3.1 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 6J-210 single | 7.87 | 86 % |
| 6J-210 two-stage | 7.66 | 0 % |
| PIE-210 two-stage | 5.26 | 10 % |
| PIE-210 single | 3.27 | 4 % |

Weight changes of +-10 % that flip the winner: none.
- screened out: 3J-210 single: roundness over budget: gland-seat counterbore
- screened out: 3J-210 two-stage: roundness over budget: gland-seat counterbore

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| lobed fit not detected (gland-seat counterbore) | part binds or leaks at assembly | 0.23 | 7 | 10 | 9 | 630 | two-point gauge blind to odd lobes |
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.57 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.57 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| clamp yields the section (jaw marks, permanent set) | scrap | 1.68 | 5 | 3 | 3 | 45 | visual / roundness after release |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 7.38 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.57 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.57 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 7.38 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| lobed fit not detected (gland-seat counterbore) | part binds or leaks at assembly | 6.20 | 7 | 1 | 4 | 28 | visible to the two-point gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 4.93 | 5 | 1 | 3 | 15 | visual / roundness after release |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 1.11 | 1.11 |
| specific cutting force -16 % / +18 % | 1.11 | 1.11 |
| thrust / cutting force 0.3 / 0.8 | 1.11 | 1.11 |
| tool wear factor 1.0 / 1.5 | 1.11 | 1.11 |
| top-jaw mass x0.7 / x1.3 | 1.16 | 1.06 |
| chuck minimum force 4 % / 12 % of max | 0.88 | 1.81 |

Base value 1.11.

## Program read-back (verify.py)

- fanuc: PASS; 4 cutting blocks, max 758 rpm, min grip 2.40; gland-seat counterbore 4.4 um
- sinumerik: PASS; 4 cutting blocks, max 758 rpm, min grip 2.40; gland-seat counterbore 4.4 um
