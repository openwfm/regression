## Hill

This simulation takes place on a plain with a mountain placed in the middle of the domain with a homogeneous fuel (fuel type 3 (Tall grass)). Ignition takes place as a walking ignition line normal to the ambient wind so the fire will burn directly into the hill. 

This simulation should be run using 16 cores and should take around 10 minutes (depending on the cluster and CPU used). Any more or less than this and the simulation will likely crash.

List of important variables:

## 3D vars
* FIRE_AREA
* U10
* V10
* T2
* Q2
* UF
* VF
* PSFC
* ROS
* ZSF
* NFUEL_FRAC
* FGRNHFX

## 4D vars
* T
* U
* V
* W
* QVAPOR
* tr17_1

