# Description of the Simulation Input Templates


## Cone_GEOM_Template_01

An updated version of the cone calorimeter geometry that was used in a previous publication (https://doi.org/10.1016/j.firesaf.2023.103926). This model is built on the technical drawing provided with Babrauskas' original report on the develompent of the cone calorimeter (https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir82-2611.pdf).

This model is intended for high resolution simulations of the cone calorimeter setup. The goal is to determine heat flux maps of the top sample surface under steady-state conditions of a  nominal heat flux, e.g. 50 kW/m². The flux map is used to prescribe a heat flux to the sample surface in low resolution simulations. This allows to conduct simulations during inverse modelling (IMP) without the need to use a model of the heater and reduce the overall computational cost significantly. Later on, it can also be used to assess the performance of the material model determined from the IMP, by running the full high resolution cone simulation.

The gemoetry is improved as to prevent too sharp angles, specifically compare the hole in the top of the cone assembly and the transition from the heater geometry to the top plate.

The heat flux gauge is now a geometrical model. The surfaces are maintained at room temperature to recreate the cooling of the gauge. The sensor window is implemented as a VENT, which applies an emissivity value to the sensor itself, according to the calibration report of our cone calorimeter.


### Heater Calibration

The spiral of the heater is approximated in this geometrical model. The surface temperatures are taken from Babrauskas' report for the desired nominal heat flux conditions. To reach the desired flux condition at the het flux gauge, the emissivity of the heater surface is to be adjusted.

At first, the heat flux gauge models are activated in the FDS input. The emissivity of the heater is adjusted until the time-average over about 20 seconds is close to the desired nominal flux. The gauge is then removed and the inert sample target introduced. The simulation is repeated and the flux map over the sample surface recorded.
