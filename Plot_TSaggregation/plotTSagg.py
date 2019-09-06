## tool for plotting TS aggregated product

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## sample file
fname = "IMOS_ANMN-QLD_TSZ_20120221_PIL050_FV01_TS-aggregated-time-series_20140727_C-20190830.nc"

nc = xr.open_dataset("LTSP-tools/Plot_TSaggregation/"+fname)

TEMP1 = nc.TEMP.isel(INSTRUMENT=1)


