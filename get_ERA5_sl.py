#!/usr/bin/env python3
import cdsapi
from datetime import datetime, timedelta
import os

# ========================
# INPUT PARAMETERS
# ========================
date_start = "2020-02-01"
date_end   = "2020-02-09"
area = [-70, -85, -40, -48]  # [S, W, N, E] adjust as needed
save_dir = "/home/lacrio/Documents/thermo_eq_test_lev/data"  # ✅ Change this to your desired folder

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
outfile = os.path.join(save_dir, f"era5_t_uv_2m_{start_str}_{end_str}.nc")
c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": [
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "2m_temperature",
        ],
        "date": f"{date_start}/{date_end}",   # ✅ new format
        "time": "00/to/23/by/1",
        "area": area,
        "grid": "0.5/0.5",
    },
    outfile
)

