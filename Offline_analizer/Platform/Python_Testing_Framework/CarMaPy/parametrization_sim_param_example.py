#created by Ventsislav Negentsov
#copyright Robert Bosch GMBH
#date : 20.Jan.2025
#this is a CarMaPy example : ported from CarMaker examples and made compilable and somehow working

import sys
sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11")
sys.path.append("C:/IPG/carmaker/win64-12.0.2/Python/python3.11/cmapi")

import cmapi
from pathlib import Path

sim_params = cmapi.Parametrization()
sim_params.set_path(pathlib.Path("Data/Config/SimParameters"))
cmapi.Project.instance().load_parametrization(sim_params)
sim_params.set_parameter_value("DStore.BufSize_kB", 131072)
cmapi.Project.instance().write_parametrization(sim_params)