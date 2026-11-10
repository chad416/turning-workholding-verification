# PI-HD-160B: piston, HD-160 rev B

Material C45. Finished OD 159.7, bore 75, length 80 mm from hollow bar 165 x 60, gripped on the bar behind the part.
FE section mesh: 4267 nodes (Q8, h = 2.00 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-315 | single | 36.3 | 36.3 | 1000 / 1000 | 3.03 | bore: 0.7 / 15 | 0.1 | 0.12 | 21.13 |  |
| 3J-315 | two-stage | 36.3 | 23.9 | 1000 / 300 | 2.31 | bore: 0.6 / 15 | 0.1 | 0.12 | 24.40 |  |
| 6J-315 | single | 37.2 | 37.2 | 1000 / 1000 | 3.08 | guide band groove (rear): 0.2 / 32 | 0.4 | 0.08 | 22.38 |  |
| 6J-315 | two-stage | 37.2 | 23.9 | 1000 / 300 | 2.32 | guide band groove (rear): 0.1 / 32 | 0.2 | 0.08 | 25.65 |  |
| PIE-315 | single | 43.2 | 43.2 | 1000 / 1000 | 3.37 | bore: 0.2 / 15 | 0.0 | 0.03 | 27.38 |  |
| PIE-315 | two-stage | 43.2 | 24.4 | 1000 / 250 | 2.34 | bore: 0.1 / 15 | 0.0 | 0.03 | 31.97 |  |

Chosen by the trade study: **3J-315 single**. Baseline (one pressure, 3 jaws): 3J-315 single.

## Features: baseline and chosen

**baseline: 3J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | - | 159.7 | 34.1 | 1.1 | - | 0.5 | 2.8 | 0.1 | 1.43 / 3.2 | ok |
| bore | H7 | 75 | 30.0 | 0.7 | 15 | 0.1 | 2.0 | 0.1 | 0.80 / 1.6 | ok |
| guide band groove (front) | h8 | 152.5 | 35.7 | 0.1 | 32 | 0.0 | 0.2 | 0.0 | 1.18 / 1.6 | ok |
| piston seal groove | h9 | 133 | 35.6 | 0.3 | 50 | 0.0 | 0.7 | 0.0 | 1.18 / 1.6 | ok |
| guide band groove (rear) | h8 | 152.5 | 35.7 | 1.0 | 32 | 0.3 | 2.6 | 0.0 | 1.18 / 1.6 | ok |

**chosen: 3J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | - | 159.7 | 34.1 | 1.1 | - | 0.5 | 2.8 | 0.1 | 1.43 / 3.2 | ok |
| bore | H7 | 75 | 30.0 | 0.7 | 15 | 0.1 | 2.0 | 0.1 | 0.80 / 1.6 | ok |
| guide band groove (front) | h8 | 152.5 | 35.7 | 0.1 | 32 | 0.0 | 0.2 | 0.0 | 1.18 / 1.6 | ok |
| piston seal groove | h9 | 133 | 35.6 | 0.3 | 50 | 0.0 | 0.7 | 0.0 | 1.18 / 1.6 | ok |
| guide band groove (rear) | h8 | 152.5 | 35.7 | 1.0 | 32 | 0.3 | 2.6 | 0.0 | 1.18 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 3.03) | met (min grip 3.03) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (36.3 / 36.3 kN) | met (36.3 / 36.3 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 1000 / 1000 rpm) | met (G50 1000 / 1000 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | met (bore: 0.7 / 15 um) | met (bore: 0.7 / 15 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 1.43 um) | met (max Ra 1.43 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.12) | met (sigma/Re 0.12) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met (lobing small or visible) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (3.9 kW) | met (3.9 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 3J-315 single | 9.80 | 100 % |
| 3J-315 two-stage | 8.65 | 0 % |
| 6J-315 single | 8.15 | 0 % |
| PIE-315 single | 7.56 | 0 % |
| 6J-315 two-stage | 7.16 | 0 % |
| PIE-315 two-stage | 6.43 | 0 % |

Weight changes of +-10 % that flip the winner: none.

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 2.02 | 10 | 2 | 8 | 160 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (bore) | part binds or leaks at assembly | 20.02 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 2.02 | 6 | 2 | 3 | 36 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 52.70 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 5.47 | 5 | 1 | 3 | 15 | visual / roundness after release |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 2.02 | 10 | 2 | 8 | 160 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (bore) | part binds or leaks at assembly | 20.02 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 2.02 | 6 | 2 | 3 | 36 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 52.70 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 5.47 | 5 | 1 | 3 | 15 | visual / roundness after release |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 0.05 | 0.02 |
| specific cutting force -16 % / +18 % | 0.03 | 0.05 |
| thrust / cutting force 0.3 / 0.8 | 0.04 | 0.04 |
| tool wear factor 1.0 / 1.5 | 0.03 | 0.04 |
| top-jaw mass x0.7 / x1.3 | 0.04 | 0.04 |
| chuck minimum force 4 % / 12 % of max | 0.04 | 0.04 |

Base value 0.04.

## Program read-back (verify.py)

- fanuc: PASS; 30 cutting blocks, max 911 rpm, min grip 3.54; OD 1.1 um, bore 0.7 um, guide band groove (front) 0.1 um, piston seal groove 0.3 um, guide band groove (rear) 1.0 um
- sinumerik: PASS; 30 cutting blocks, max 911 rpm, min grip 3.54; OD 1.1 um, bore 0.7 um, guide band groove (front) 0.1 um, piston seal groove 0.3 um, guide band groove (rear) 1.0 um
