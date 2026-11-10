# GL-HD-160B: gland, HD-160 rev B

Material C45. Finished OD 159.95, bore 100.2, length 110 mm from hollow bar 165 x 85, gripped on the bar behind the part.
FE section mesh: 4590 nodes (Q8, h = 2.00 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-315 | single | 39.3 | 39.3 | 350 / 350 | 2.31 | OD: 2.1 / 20 | 0.6 | 0.14 | 29.10 |  |
| 3J-315 | two-stage | 39.3 | 23.7 | 350 / 300 | 2.31 | OD: 1.6 / 20 | 0.4 | 0.14 | 30.33 |  |
| 6J-315 | single | 39.5 | 39.5 | 400 / 400 | 2.30 | OD: 0.3 / 20 | 0.6 | 0.09 | 27.96 |  |
| 6J-315 | two-stage | 39.5 | 23.7 | 400 / 300 | 2.30 | OD: 0.2 / 20 | 0.4 | 0.09 | 30.04 |  |
| PIE-315 | single | 40.3 | 40.3 | 350 / 350 | 2.34 | OD: 0.4 / 20 | 0.1 | 0.03 | 35.35 |  |
| PIE-315 | two-stage | 40.3 | 24.2 | 350 / 250 | 2.34 | OD: 0.3 / 20 | 0.1 | 0.03 | 38.36 |  |

Chosen by the trade study: **3J-315 single**. Baseline (one pressure, 3 jaws): 3J-315 single.

## Features: baseline and chosen

**baseline: 3J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | f7 | 159.95 | 38.3 | 2.1 | 20 | 0.6 | 5.5 | 0.2 | 1.43 / 3.2 | ok |
| bore | H9 | 100.2 | 38.3 | 2.5 | 44 | 0.4 | 6.5 | 0.1 | 0.80 / 3.2 | ok |
| wiper groove | H11 | 112.5 | 38.6 | 0.1 | 110 | 0.0 | 0.3 | 0.0 | 0.86 / 3.2 | ok |
| rod seal groove | H9 | 115 | 38.7 | 0.2 | 44 | 0.0 | 0.4 | 0.0 | 0.86 / 1.6 | ok |
| guide ring groove | H8 | 106.25 | 38.6 | 0.5 | 27 | 0.0 | 1.2 | 0.0 | 0.86 / 1.6 | ok |
| O-ring groove | h9 | 151.2 | 38.8 | 1.0 | 50 | 0.0 | 2.5 | 0.0 | 1.18 / 1.6 | ok |

**chosen: 3J-315 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | f7 | 159.95 | 38.3 | 2.1 | 20 | 0.6 | 5.5 | 0.2 | 1.43 / 3.2 | ok |
| bore | H9 | 100.2 | 38.3 | 2.5 | 44 | 0.4 | 6.5 | 0.1 | 0.80 / 3.2 | ok |
| wiper groove | H11 | 112.5 | 38.6 | 0.1 | 110 | 0.0 | 0.3 | 0.0 | 0.86 / 3.2 | ok |
| rod seal groove | H9 | 115 | 38.7 | 0.2 | 44 | 0.0 | 0.4 | 0.0 | 0.86 / 1.6 | ok |
| guide ring groove | H8 | 106.25 | 38.6 | 0.5 | 27 | 0.0 | 1.2 | 0.0 | 0.86 / 1.6 | ok |
| O-ring groove | h9 | 151.2 | 38.8 | 1.0 | 50 | 0.0 | 2.5 | 0.0 | 1.18 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 2.31) | met (min grip 2.31) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (39.3 / 39.3 kN) | met (39.3 / 39.3 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 350 / 350 rpm) | met (G50 350 / 350 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | met (OD: 2.1 / 20 um) | met (OD: 2.1 / 20 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 1.43 um) | met (max Ra 1.43 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.14) | met (sigma/Re 0.14) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met (lobing small or visible) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (7.1 kW) | met (7.1 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 3J-315 single | 9.24 | 99 % |
| 3J-315 two-stage | 8.83 | 0 % |
| 6J-315 single | 7.83 | 0 % |
| 6J-315 two-stage | 7.50 | 0 % |
| PIE-315 single | 7.20 | 0 % |
| PIE-315 two-stage | 6.78 | 0 % |

Weight changes of +-10 % that flip the winner: none.

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.54 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.54 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 62.31 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| lobed fit not detected (OD) | part binds or leaks at assembly | 9.32 | 7 | 1 | 4 | 28 | visible to the two-point gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 4.93 | 5 | 1 | 3 | 15 | visual / roundness after release |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.54 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| part slips under the cutting torque | scrap, tool breakage | 1.54 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 62.31 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |
| lobed fit not detected (OD) | part binds or leaks at assembly | 9.32 | 7 | 1 | 4 | 28 | visible to the two-point gauge |
| clamp yields the section (jaw marks, permanent set) | scrap | 4.93 | 5 | 1 | 3 | 15 | visual / roundness after release |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 0.10 | 0.04 |
| specific cutting force -16 % / +18 % | 0.07 | 0.10 |
| thrust / cutting force 0.3 / 0.8 | 0.08 | 0.08 |
| tool wear factor 1.0 / 1.5 | 0.06 | 0.09 |
| top-jaw mass x0.7 / x1.3 | 0.08 | 0.08 |
| chuck minimum force 4 % / 12 % of max | 0.08 | 0.08 |

Base value 0.08.

## Program read-back (verify.py)

- fanuc: PASS; 29 cutting blocks, max 350 rpm, min grip 2.29; OD 2.1 um, bore 2.5 um, wiper groove 0.1 um, rod seal groove 0.2 um, guide ring groove 0.5 um, O-ring groove 1.0 um
- sinumerik: PASS; 29 cutting blocks, max 350 rpm, min grip 2.29; OD 2.1 um, bore 2.5 um, wiper groove 0.1 um, rod seal groove 0.2 um, guide ring groove 0.5 um, O-ring groove 1.0 um
