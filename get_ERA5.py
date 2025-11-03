#!/usr/bin/env python3
import cdsapi
from datetime import datetime, timedelta
import os

# ========================
# INPUT PARAMETERS
# ========================
date_start = "2020-02-01"
date_end   = "2020-02-14"
area = [-70, -85, -40, -48]  # [S, W, N, E] adjust as needed
save_dir = "/home/lacrio/Documents/thermo_eq_test/data"  # ✅ Change this to your desired folder

# ========================
# CREATE OUTPUT DIRECTORY
# ========================
os.makedirs(save_dir, exist_ok=True)

# ========================
# FORMAT DATES FOR FILENAMES
# ========================
start_dt = datetime.strptime(date_start, "%Y-%m-%d")
end_dt   = datetime.strptime(date_end, "%Y-%m-%d")
start_str = start_dt.strftime("%Y%m%d")
end_str   = end_dt.strftime("%Y%m%d")

# ========================
# INITIALIZE CDS CLIENT
# ========================
c = cdsapi.Client()

# ========================
# ERA5 PRESSURE LEVELS
# ========================
outfile = os.path.join(save_dir, f"era5_t_uvw_{start_str}_{end_str}.nc")
c.retrieve(
    "reanalysis-era5-pressure-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": [
            "temperature",
            "u_component_of_wind",
            "v_component_of_wind",
            "vertical_velocity"
        ],
        "pressure_level": ["850", "975"],
        "date": f"{date_start}/{date_end}",   # ✅ new format
        "time": "00/to/23/by/1",
        "area": area,
        "grid": "0.5/0.5",
    },
    outfile
)

# ========================
# ERA5 SINGLE LEVELS - T2M, BLH
# ========================
outfile = os.path.join(save_dir, f"era5_t2m_blh_{start_str}_{end_str}.nc")
c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": [
            "2m_temperature",
            "boundary_layer_height"
        ],
        "date": f"{date_start}/{date_end}",
        "time": "00/to/23/by/1",
        "area": area,
        "grid": "0.5/0.5",
    },
    outfile
)

# ========================
# ERA5 SINGLE LEVELS - PRECIPITATION, HEAT FLUX
# ========================
outfile = os.path.join(save_dir, f"era5_tp_shf_{start_str}_{end_str}.nc")
c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": [
            "total_precipitation",
            "surface_sensible_heat_flux"
        ],
        "date": f"{date_start}/{date_end}",
        "time": "00/to/23/by/1",
        "area": area,
        "grid": "0.5/0.5",
    },
    outfile
)

