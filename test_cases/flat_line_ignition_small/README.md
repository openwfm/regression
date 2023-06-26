# walking_flat_small Simulation
This simulation takes place on a flat plain with homogeneous fuels (fuel type 3 (Tall grass)) in this case. This wind profile is constant at 2m/s and the simulation is run in a one-way coupled (fire_atm_feedback = 0) mode. The igntion line occurs in a walking ignition pattern along the y axis. 

This simulation should use ~16 cores. Any more or less than this will likely result in a crash, or the simulation will take much longer than the expected amount of time. This simulation should take about 10 minutes to run (this also varies based on the cluster and CPU's used). 

List of Interesting Variables:

| Variable  | Type  | Desctiption     | Units | Dimensions |
|:----------|:-----: | :--------------:| :------: | :----: |
| U        | 4D  | x-wind component | m/s | Time, Height, Latitude, Longitude |
| V        | 4D  | y-wind component | m/s | Time, Height, Latitude, Longitude |
| W        | 4D  | z-wind component | m/s | Time, Height, Latitude, Longitude |
| QVAPOR   | 4D  | Water vapor mixing ratio | m/s | Time, Height, Latitude, Longitude |
| tr17_1   | 4D  | Smoke | Dimensionless | Time, Height, Latitude, Longitude |
| FIRE_AREA| 3D  | fraction of cell area on fire | Dimensionless | Time, Fire Grid Latitude, Fire Grid Longitude |
| U10      | 3D  | x-wind component at 10m AGL | m/s | Time, Latitude, Longitude |
| V10      | 3D  | Y-wind component at 10m AGL | m/s | Time, Latitude, Longitude |
| T2   | 3D  | Temperature at 2M | K | Time, Latitude, Longitude |
| Q2   | 3D  | QV at 2 M | kg/kg | Time, Latitude, Longitude |
| UF   | 3D  | fire x-wind component | m/s | Time, Fire Grid Latitude, Fire Grid Longitude |
| VF   | 3D  | fire y-wind component | m/s | Time, Fire Grid Latitude, Fire Grid Longitude |
| PSFC   | 3D  | Surface pressure | Pa | Time, Latitude, Longitude |
| ROS   | 3D  | Rate of spread | m/s | Time, Fire Grid Latitude, Fire Grid Longitude |
| ZSF   | 3D  | Height of surface above sea level | m | Time, Fire Grid Latitude, Fire Grid Longitude |
| NFUEL_CAT   | 3D  | Fuel Data | Unitless | Time, Fire Grid Latitude, Fire Grid Longitude |
| FGRNHFX   | 3D  | heat flux from ground fire | w/$m^2$ | Time, Fire Grid Latitude, Fire Grid Longitude |
