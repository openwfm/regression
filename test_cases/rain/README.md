## Rain

This simulation takes place on a plain with a hill in the domain. The fuels are homogeneous (fuel type 3 (Tall grass)). In this case, there is rain in the simulation. 

This simulation should use ~16 cores. Any more or any less will likely result in a crash. This simulation should take around 10 minutes to run (depending on the cluster used and the CPU's). 

List of Interesting Variables

| Variable  | Type  | Desctiption     | Units | Dimensions |
|:----------|:-----: | :--------------:| :------: | :----: |
| U        | 4D  | x-wind component | $\frac{m}{s}$ | Time, Height, Latitude, Longitude |
| V        | 4D  | y-wind component | $\frac{m}{s}$ | Time, Height, Latitude, Longitude |
| W        | 4D  | z-wind component | $\frac{m}{s}$ | Time, Height, Latitude, Longitude |
| QVAPOR   | 4D  | Water vapor mixing ratio | $\frac{kg}{kg}$ | Time, Height, Latitude, Longitude |
| tr17_1   | 4D  | Smoke | Dimensionless | Time, Height, Latitude, Longitude |
| FIRE_AREA| 3D  | fraction of cell area on fire | Dimensionless | Time, Latitude, Longitude |
| U10      | 3D  | x-wind component at 10m AGL | $\frac{m}{s}$ | Time, Latitude, Longitude |
| V10      | 3D  | Y-wind component at 10m AGL | $\frac{m}{s}$ | Time, Latitude, Longitude |
| T2   | 3D  | Temperature at 2M | K | Time, Latitude, Longitude |
| Q2   | 3D  | QV at 2 M | $\frac{kg}{kg}$ | Time, Latitude, Longitude |
| UF   | 3D  | fire x-wind component | $\frac{m}{s}$ | Time, Latitude, Longitude |
| VF   | 3D  | fire y-wind component | $\frac{m}{s}$ | Time, Latitude, Longitude |
| RAINNC   | 3D  | Accumulated total grid scale precipitation | mm | Time, Latitude, Longitude |
| PSFC   | 3D  | Surface pressure | Pa | Time, Latitude, Longitude |
| ROS   | 3D  | Rate of spread | $\frac{m}{s}$ | Time, Latitude, Longitude |
| ZSF   | 3D  | Height of surface above sea level | m | Time, Latitude, Longitude |
| NFUEL_FRAC   | 3D  | Fuel Data | Unitless | Time, Latitude, Longitude |
| FGRNHFX   | 3D  | heat flux from ground fire | $\frac{w}{m^2}$ | Time, Latitude, Longitude |

