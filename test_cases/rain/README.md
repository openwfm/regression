## Rain

This simulation takes place on a plain with a hill in the domain. The fuels are homogeneous (fuel type 3 (Tall grass)). In this case, there is rain in the simulation. 

This simulation should use ~16 cores. Any more or any less will likely result in a crash. This simulation should take around 10 minutes to run (depending on the cluster used and the CPU's). 

List of Interesting Variables

| Variable  | Type  |   Desctiption     | Units |
|:----------|:-----:| :--------------:| :------: |
| U        | 4D  | x-wind component | $\frac{m}{s}$ |
| V        | 4D  | y-wind component | $\frac{m}{s}$ |
| W        | 4D  | z-wind component | $\frac{m}{s}$ |
| QVAPOR   | 4D  | Water vapor mixing ratio | $\frac{kg}{kg}$ |
| tr17_1   | 4D  | Smoke | Dimensionless |
| FIRE_AREA| 3D  | fraction of cell area on fire | Dimensionless |
| U10      | 3D  | x-wind component at 10m AGL | $\frac{m}{s}$ |
| V10      | 3D  | Y-wind component at 10m AGL | $\frac{m}{s}$ |
| T2   | 3D  | 
| Q2   | 3D  |
| UF   | 3D  |
| VF   | 3D  |
| RAINC   | 3D  |
| PSFC   | 3D  |
| ROS   | 3D  |
| ZSF   | 3D  |
| NFUEL_FRAC   | 3D  |
| FGRNHFX   | 3D  |

