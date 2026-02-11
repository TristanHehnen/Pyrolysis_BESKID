# Description of the Simulation Input Templates


## Cone_GEOM_Template_01

An updated version of the cone calorimeter geometry that was used in a previous publication (https://doi.org/10.1016/j.firesaf.2023.103926). This model is built on the technical drawing provided with Babrauskas' original report on the development of the cone calorimeter (https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir82-2611.pdf).

This model is intended for high resolution simulations of the cone calorimeter setup. The goal is to determine heat flux maps of the top sample surface under steady-state conditions of a  nominal heat flux, e.g. 50 kW/m². The flux map is used to prescribe a heat flux to the sample surface in low resolution simulations. This allows to conduct simulations during inverse modelling (IMP) without the need to use a model of the heater and reduce the overall computational cost significantly. Later on, it can also be used to assess the performance of the material model determined from the IMP, by running the full high resolution cone simulation.

The geometry is improved as to prevent too sharp angles, specifically compare the hole in the top of the cone assembly and the transition from the heater geometry to the top plate.

The heat flux gauge is now a geometrical model. The surfaces are maintained at room temperature to recreate the cooling of the gauge. The sensor window is implemented as a VENT, which applies an emissivity value to the sensor itself, according to the calibration report of our cone calorimeter.


### Heater Calibration

The spiral of the heater is approximated in this geometrical model. The surface temperatures are taken from Babrauskas' report for the desired nominal heat flux conditions. To reach the desired flux condition at the het flux gauge, the emissivity of the heater surface is to be adjusted.

At first, the heat flux gauge models are activated in the FDS input. The emissivity of the heater is adjusted until the time-average over about 20 seconds is close to the desired nominal flux. The gauge is then removed and the inert sample target introduced. The simulation is repeated and the flux map over the sample surface recorded.

With the default number of radiation angels of the FDS radiation solver, artefacts in the heat flux on the sample surface could be observed. The inert sample target is used to assess these artefacts using the recorded flux map. An optimisation step ensures that an optimal number of radiation angles is used for the simulation to minimises artefacts without increasing the computational demand too much. Once an optimal value is found, the heat flux gauge model is introduced again and the emissivity calibration fine-tuned. Then the inert sample target introduced again and the final flux map recorded. This final flux map is then mapped to simulation setups with lower fluid cell resolution, as described below.


## Calibrated Simplified Cone Calorimeter Setups

Using the procedure outlined above, simulation setups with low fluid cell resolution have been created. They consist of fluid cells with an edge length of about 3.33 cm, such that 3 by 3 cells cover the surface of a cone calorimeter sample (C3). Five external heat fluxes are available: 25 kW/m², 50 kW/m², 65 kW/m² and 75 kW/m².
