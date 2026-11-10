# GL-LD-80C: gland, LD-80 rev C

Material C45. Finished OD 79.95, bore 63.2, length 70 mm from hollow bar 85 x 50, gripped on the bar behind the part.
FE section mesh: 5303 nodes (Q8, h = 0.83 mm), harmonics k = 0, 3, ..., 48.

## Workholding strategies

| chuck | pressure | F high kN | F low kN | G50 rough / finish | min grip (>= 1.5) | worst RONt / budget um | two-point sees um | clamp sigma/Re | min per part (batch 4) | notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 3J-210 | single | 38.4 | 38.4 | 800 / 800 | 2.29 | OD: 3.7 / 15 | 0.5 | 0.34 | 11.69 |  |
| 3J-210 | two-stage | 38.4 | 22.0 | 800 / 500 | 2.29 | OD: 3.5 / 15 | 0.5 | 0.34 | 12.96 |  |
| 6J-210 | single | 38.7 | 38.7 | 800 / 800 | 2.30 | OD: 0.3 / 15 | 0.5 | 0.21 | 12.94 |  |
| 6J-210 | two-stage | 38.7 | 22.1 | 800 / 500 | 2.30 | OD: 0.2 / 15 | 0.5 | 0.21 | 14.21 |  |
| PIE-210 | single | 39.4 | 39.4 | 800 / 800 | 2.32 | OD: 0.7 / 15 | 0.1 | 0.12 | 17.94 |  |
| PIE-210 | two-stage | 39.4 | 22.5 | 800 / 550 | 2.31 | OD: 0.7 / 15 | 0.1 | 0.12 | 18.92 |  |

Chosen by the trade study: **3J-210 single**. Baseline (one pressure, 3 jaws): 3J-210 single.

## Features: baseline and chosen

**baseline: 3J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | f7 | 79.95 | 37.1 | 3.7 | 15 | 0.5 | 9.6 | 0.3 | 1.43 / 3.2 | ok |
| bore | H9 | 63.2 | 37.1 | 6.1 | 37 | 0.8 | 15.8 | 0.4 | 0.80 / 3.2 | ok |
| wiper groove | H11 | 73 | 38.0 | 0.3 | 95 | 0.0 | 0.8 | 0.0 | 0.86 / 3.2 | ok |
| rod seal groove | H9 | 75 | 38.0 | 0.6 | 37 | 0.0 | 1.6 | 0.0 | 0.86 / 1.6 | ok |
| guide ring groove | H8 | 68 | 38.0 | 1.5 | 23 | 0.0 | 3.8 | 0.0 | 0.86 / 1.6 | ok |
| O-ring groove | h9 | 72.95 | 37.8 | 2.8 | 37 | 0.1 | 7.4 | 0.0 | 1.18 / 1.6 | ok |

**chosen: 3J-210 single**

| feature | fit | D mm | force during finish kN | RONt um | budget um | two-point um | 108 deg V um | tool-load size error um | Ra um / req | R-04 |
|---|---|---|---|---|---|---|---|---|---|---|
| OD | f7 | 79.95 | 37.1 | 3.7 | 15 | 0.5 | 9.6 | 0.3 | 1.43 / 3.2 | ok |
| bore | H9 | 63.2 | 37.1 | 6.1 | 37 | 0.8 | 15.8 | 0.4 | 0.80 / 3.2 | ok |
| wiper groove | H11 | 73 | 38.0 | 0.3 | 95 | 0.0 | 0.8 | 0.0 | 0.86 / 3.2 | ok |
| rod seal groove | H9 | 75 | 38.0 | 0.6 | 37 | 0.0 | 1.6 | 0.0 | 0.86 / 1.6 | ok |
| guide ring groove | H8 | 68 | 38.0 | 1.5 | 23 | 0.0 | 3.8 | 0.0 | 0.86 / 1.6 | ok |
| O-ring groove | h9 | 72.95 | 37.8 | 2.8 | 37 | 0.1 | 7.4 | 0.0 | 1.18 / 1.6 | ok |

## Requirements

| ID | requirement | source | method | baseline | chosen |
|---|---|---|---|---|---|
| R-01 | Every cut shall leave a grip of mu (F_set - F_c(n)) / F_transfer >= S_z = 1.5 at the speed it runs | VDI 3106 clamping-force method | A; T | met (min grip 2.29) | met (min grip 2.29) |
| R-02 | The static clamping force set on the chuck shall lie within the chuck's range | chuck data | I | met (38.4 / 38.4 kN) | met (38.4 / 38.4 kN) |
| R-03 | The program shall carry a spindle-speed limit (G50 / LIMS) at which R-01 still holds, never above the chuck rating | VDI 3106; EN 1550 rating | A; I | met (G50 800 / 800 rpm) | met (G50 800 / 800 rpm) |
| R-04 | Each toleranced diameter shall be round within half its IT band after release (RONt about the LS circle) | ISO 14405-1 envelope on fits, machined at mid tolerance (derived) | A; T | met (OD: 3.7 / 15 um) | met (OD: 3.7 / 15 um) |
| R-05 | Seal and guide groove bottoms Ra <= 1.6 um, other turned surfaces Ra <= 3.2 um | seal maker catalogue Table V (groove surface Ra < 1.6 um); 3.2 um project choice | A; T | met (max Ra 1.43 um) | met (max Ra 1.43 um) |
| R-06 | The clamping stress shall stay below Re / 1.5 in the gripped section | project rule: no permanent set or jaw marks | A | met (sigma/Re 0.34) | met (sigma/Re 0.34) |
| R-07 | The inspection method shall see the lobing order the chuck produces | ISO 12181 (roundness), derived | I | met (lobing small or visible) | met (lobing small or visible) |
| R-08 | Cutting power shall not exceed the spindle power | machine data | A | met (7.1 kW) | met (7.1 kW) |

## Trade study

| candidate | score | wins of 2000 random weight sets |
|---|---|---|
| 3J-210 single | 9.33 | 100 % |
| 3J-210 two-stage | 8.76 | 0 % |
| 6J-210 single | 7.57 | 0 % |
| 6J-210 two-stage | 7.15 | 0 % |
| PIE-210 single | 6.51 | 0 % |
| PIE-210 two-stage | 6.14 | 0 % |

Weight changes of +-10 % that flip the winner: none.

## FMEA (RPN = S x O x D; O from the computed margin)

**baseline**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.53 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (OD) | part binds or leaks at assembly | 4.07 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 1.53 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| clamp yields the section (jaw marks, permanent set) | scrap | 1.96 | 5 | 3 | 3 | 45 | visual / roundness after release |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 23.02 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |

**chosen**

| failure mode | effect | margin | S | O | D | RPN | detection |
|---|---|---|---|---|---|---|---|
| part thrown at speed (centrifugal loss of grip) | injury, machine damage | 1.53 | 10 | 3 | 8 | 240 | none in the program; only the VDI calculation or a slip test |
| lobed fit not detected (OD) | part binds or leaks at assembly | 4.07 | 7 | 1 | 9 | 63 | two-point gauge blind to odd lobes |
| part slips under the cutting torque | scrap, tool breakage | 1.53 | 6 | 3 | 3 | 54 | witness marks / spindle load |
| clamp yields the section (jaw marks, permanent set) | scrap | 1.96 | 5 | 3 | 3 | 45 | visual / roundness after release |
| groove bottom off size (wall deflects under the tool) | seal squeeze out of range | 23.02 | 6 | 1 | 6 | 36 | internal groove diameter is hard to gauge |

## Sensitivity (3 jaws, two-stage: worst RONt / budget)

| input | low | high |
|---|---|---|
| jaw friction mu 0.08 / 0.20 | 0.29 | 0.12 |
| specific cutting force -16 % / +18 % | 0.19 | 0.27 |
| thrust / cutting force 0.3 / 0.8 | 0.23 | 0.23 |
| tool wear factor 1.0 / 1.5 | 0.18 | 0.27 |
| top-jaw mass x0.7 / x1.3 | 0.23 | 0.23 |
| chuck minimum force 4 % / 12 % of max | 0.23 | 0.23 |

Base value 0.23.

## Program read-back (verify.py)

- fanuc: PASS; 27 cutting blocks, max 800 rpm, min grip 2.29; OD 3.7 um, bore 6.1 um, wiper groove 0.3 um, rod seal groove 0.6 um, guide ring groove 1.5 um, O-ring groove 2.8 um
- sinumerik: PASS; 27 cutting blocks, max 800 rpm, min grip 2.29; OD 3.7 um, bore 6.1 um, wiper groove 0.3 um, rod seal groove 0.6 um, guide ring groove 1.5 um, O-ring groove 2.8 um
