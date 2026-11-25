## Outcomes (complete / partial / empty / raised)

| family | mesh | spacing | dev | new_all | new_light | new_light_sharp |
|---|---|---|---|---|---|---|
| lines+arcs | box_irr | 1.0 | 20/0/0/0 | 20/0/0/0 | 20/0/0/0 | 20/0/0/0 |
| lines+arcs | box_irr | 0.5 | 7/2/1/10 | 13/3/0/4 | 20/0/0/0 | 20/0/0/0 |
| lines+arcs | box_irr | 0.3 | 3/2/4/11 | 10/3/0/7 | 20/0/0/0 | 20/0/0/0 |
| lines+arcs | box_reg | 1.0 | 12/5/0/3 | 15/2/0/3 | 20/0/0/0 | 20/0/0/0 |
| lines+arcs | box_reg | 0.5 | 5/3/0/12 | 12/2/0/6 | 20/0/0/0 | 20/0/0/0 |
| lines+arcs | box_reg | 0.3 | 4/1/1/14 | 6/5/0/9 | 20/0/0/0 | 20/0/0/0 |
| kinks | box_irr | 1.0 | 55/4/0/1 | 55/4/0/1 | 54/4/0/2 | 55/4/0/1 |
| kinks | box_irr | 0.5 | 25/22/0/13 | 25/25/0/10 | 54/4/0/2 | 46/13/0/1 |
| kinks | box_irr | 0.3 | 13/20/0/27 | 23/17/0/20 | 54/4/0/2 | 53/7/0/0 |
| kinks | box_reg | 1.0 | 51/3/0/6 | 51/6/0/3 | 48/2/0/10 | 51/6/0/3 |
| kinks | box_reg | 0.5 | 23/14/0/23 | 32/11/0/17 | 48/2/0/10 | 50/8/0/2 |
| kinks | box_reg | 0.3 | 14/21/0/25 | 23/17/0/20 | 48/2/0/10 | 50/8/1/1 |

## Kinks by turn angle, complete of 10 per spacing and mesh, summed (of 60)

| turn | dev | new_all | new_light | new_light_sharp |
|---|---|---|---|---|
| 10 | 34 | 38 | 60 | 60 |
| 30 | 37 | 41 | 60 | 60 |
| 60 | 36 | 46 | 60 | 60 |
| 90 | 25 | 31 | 60 | 60 |
| 120 | 28 | 32 | 45 | 45 |
| 150 | 21 | 21 | 21 | 20 |

## Traces complete on development: what changes (lines+arcs and kinks)

- new_all: 232 complete on dev; 224 still complete, 8 not. Cells differ in 0 (range 0..0); base vertices moved, mean dev 6.11 -> 6.11; trace-to-chain max/h, max over traces dev 0.500 -> 0.500
- new_light: 232 complete on dev; 209 still complete, 23 not. Cells differ in 208 (range 0..24); base vertices moved, mean dev 6.14 -> 3.25; trace-to-chain max/h, max over traces dev 0.500 -> 0.438
- new_light_sharp: 232 complete on dev; 227 still complete, 5 not. Cells differ in 190 (range 0..24); base vertices moved, mean dev 6.12 -> 3.67; trace-to-chain max/h, max over traces dev 0.500 -> 0.500

## Solves (sheared box, frictionless fault; traces complete under all three)

| trace | mesh | spacing | slip max dev | new_all | new_light | new_light_sharp | vel its dev/all/light/sharp |
|---|---|---|---|---|---|---|---|
| la0 | box_irr | 0.5 | 0.141337 | 0.141337 (+0.0e+00) | 0.141536 (+1.4e-03) | 0.141536 (+1.4e-03) | [24]/[24]/[28]/[28] |
| la2 | box_irr | 0.5 | 0.102970 | 0.102970 (+0.0e+00) | 0.110946 (+7.7e-02) | 0.110946 (+7.7e-02) | [22]/[22]/[27]/[27] |
| la0 | box_irr | 1.0 | 0.142238 | 0.142238 (+0.0e+00) | 0.141536 (-4.9e-03) | 0.141536 (-4.9e-03) | [21]/[21]/[28]/[28] |
| la1 | box_irr | 1.0 | 0.121376 | 0.121376 (+0.0e+00) | 0.121418 (+3.5e-04) | 0.121418 (+3.5e-04) | [24]/[24]/[26]/[26] |
| la2 | box_irr | 1.0 | 0.111159 | 0.111159 (+0.0e+00) | 0.110946 (-1.9e-03) | 0.110946 (-1.9e-03) | [21]/[21]/[27]/[27] |
| la3 | box_irr | 1.0 | 0.167505 | 0.167505 (+0.0e+00) | 0.165060 (-1.5e-02) | 0.165060 (-1.5e-02) | [21]/[21]/[32]/[32] |
| la4 | box_irr | 1.0 | 0.045530 | 0.045530 (+0.0e+00) | 0.045521 (-2.1e-04) | 0.045521 (-2.1e-04) | [24]/[24]/[28]/[28] |
| la5 | box_irr | 1.0 | 0.169191 | 0.169191 (+0.0e+00) | 0.169369 (+1.1e-03) | 0.169369 (+1.1e-03) | [21]/[21]/[29]/[29] |
| la0 | box_reg | 0.3 | 0.140607 | 0.140607 (+0.0e+00) | 0.141972 (+9.7e-03) | 0.141972 (+9.7e-03) | [30]/[30]/[26]/[26] |
| la0 | box_reg | 0.5 | 0.140396 | 0.140396 (+0.0e+00) | 0.141972 (+1.1e-02) | 0.141972 (+1.1e-02) | [26]/[26]/[26]/[26] |
| la0 | box_reg | 1.0 | 0.141624 | 0.141624 (+0.0e+00) | 0.141972 (+2.5e-03) | 0.141972 (+2.5e-03) | [27]/[27]/[26]/[26] |
| la3 | box_reg | 1.0 | 0.166900 | 0.166900 (+0.0e+00) | 0.167972 (+6.4e-03) | 0.167972 (+6.4e-03) | [32]/[32]/[28]/[28] |
| la4 | box_reg | 1.0 | 0.044792 | 0.044792 (+0.0e+00) | 0.044801 (+2.0e-04) | 0.044801 (+2.0e-04) | [25]/[25]/[46]/[46] |
