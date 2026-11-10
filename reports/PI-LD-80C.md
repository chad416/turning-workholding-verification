# PI-LD-80C: piston, LD-80 rev C

Material C45. Finished OD 79.7, bore 51, length 50 mm from hollow bar 85 x 40, gripped on the bar behind the part.
FE section mesh: 1408 nodes (Q8, h = 1.83 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-210 | single | 28.5 | 28.5 | 1450 / 1450 | 2.65 | bore: 1.5 / 15 | 0.2 | 0.22 | 8.57 |  |
| 3J-210 | two-stage | 28.5 | 22.6 | 1450 / 550 | 2.29 | bore: 1.3 / 15 | 0.2 | 0.22 | 9.77 |  |
| 6J-210 | single | 29.5 | 29.5 | 1450 / 1450 | 2.70 | bore: 0.1 / 15 | 0.2 | 0.14 | 9.82 |  |
| 6J-210 | two-stage | 29.5 | 22.7 | 1450 / 550 | 2.30 | bore: 0.1 / 15 | 0.2 | 0.14 | 11.02 |  |
| PIE-210 | single | 32.3 | 32.3 | 1500 / 1500 | 2.79 | bore: 0.3 / 15 | 0.0 | 0.07 | 14.82 |  |
| PIE-210 | two-stage | 32.3 | 23.1 | 1500 / 550 | 2.31 | bore: 0.3 / 15 | 0.0 | 0.07 | 16.02 |  |

Chosen by the trade study: **3J-210 single**. Baseline (one pressure, 3 jaws): 3J-210 single.

## Features: baseline and chosen

**baseline: 3J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | - | 79.7 | 26.4 | 1.2 | - | 0.3 | 3.1 | 0.3 | 1.43 / 3.2 | ok |
| bore | H7 | 51 | 25.2 | 1.5 | 15 | 0.2 | 3.9 | 0.4 | 0.80 / 1.6 | ok |
| guide band groove (front) | h8 | 75 | 27.9 | 0.0 | 23 | 0.0 | 0.1 | 0.0 | 1.18 / 1.6 | ok |
| piston seal groove | h9 | 62 | 27.7 | 0.6 | 37 | 0.0 | 1.6 | 0.0 | 1.18 / 1.6 | ok |
| guide band groove (rear) | h8 | 75 | 27.9 | 1.4 | 23 | 0.2 | 3.7 | 0.0 | 1.18 / 1.6 | ok |

**chosen: 3J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | - | 79.7 | 26.4 | 1.2 | - | 0.3 | 3.1 | 0.3 | 1.43 / 3.2 | ok |
| bore | H7 | 51 | 25.2 | 1.5 | 15 | 0.2 | 3.9 | 0.4 | 0.80 / 1.6 | ok |
| guide band groove (front) | h8 | 75 | 27.9 | 0.0 | 23 | 0.0 | 0.1 | 0.0 | 1.18 / 1.6 | ok |
| piston seal groove | h9 | 62 | 27.7 | 0.6 | 37 | 0.0 | 1.6 | 0.0 | 1.18 / 1.6 | ok |
| guide band groove (rear) | h8 | 75 | 27.9 | 1.4 | 23 | 0.2 | 3.7 | 0.0 | 1.18 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 2.65) | met (min grip 2.65) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (28.5 / 28.5 kN) | met (28.5 / 28.5 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 1450 / 1450 rpm) | met (G50 1450 / 1450 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | met (bore: 1.5 / 15 um) | met (bore: 1.5 / 15 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 1.43 um) | met (max Ra 1.43 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.22) | met (sigma/Re 0.22) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met (lobing small or visible) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (3.9 kW) | met (3.9 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 3J-210 single | 9.56 | 99 % |
| 3J-210 two-stage | 8.68 | 0 % |
| 6J-210 single | 7.73 | 0 % |
| 6J-210 two-stage | 6.97 | 0 % |
| PIE-210 single | 6.33 | 1 % |
| PIE-210 two-stage | 5.52 | 0 % |

Weight changes of +-10 % that flip the winner: none.

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.76 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (bore) | part binds or leaks at assembly | 9.92 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 1.76 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 19.50 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 3.03 | 5 | 1 | 3 | 15 | visual / roundness after release |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.76 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (bore) | part binds or leaks at assembly | 9.92 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 1.76 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 19.50 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 3.03 | 5 | 1 | 3 | 15 | visual / roundness after release |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 0.11 | 0.04 |
| specific cutting force -16 % / +18 % | 0.07 | 0.10 |
| thrust / cutting force 0.3 / 0.8 | 0.09 | 0.09 |
| tool wear factor 1.0 / 1.5 | 0.07 | 0.10 |
| top-jaw mass x0.7 / x1.3 | 0.09 | 0.09 |
| chuck minimum force 4 % / 12 % of max | 0.09 | 0.09 |

Base value 0.09.

## Program read-back (verify.py)

- fanuc: PASS; 25 cutting blocks, max 1345 rpm, min grip 2.89; OD 1.2 um, bore 1.5 um, guide band groove (front) 0.0 um, piston seal groove 0.6 um, guide band groove (rear) 1.4 um
- sinumerik: PASS; 25 cutting blocks, max 1345 rpm, min grip 2.89; OD 1.2 um, bore 1.5 um, guide band groove (front) 0.0 um, piston seal groove 0.6 um, guide band groove (rear) 1.4 um
