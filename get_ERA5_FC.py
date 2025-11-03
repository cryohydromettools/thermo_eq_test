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
start_minus1 = (start_dt - timedelta(days=1))
end_dt   = datetime.strptime(date_end, "%Y-%m-%d")
start_str = start_dt.strftime("%Y%m%d")
end_str   = end_dt.strftime("%Y%m%d")

# ========================
# INITIALIZE CDS CLIENT
# ========================
c = cdsapi.Client()

# ========================
# ERA5 MODEL LEVELS (COMPLETE)
# ========================
print(start_minus1)
outfile = os.path.join(save_dir, f"era5_radflux_{start_str}_{end_str}.nc")
c.retrieve(
    "reanalysis-era5-complete",
    {   
        "date"    : f"{start_minus1}/to/{end_dt}",  # ✅ fixed format
        "expver"  : "1",
        "levelist": "137",
        "levtype" : "ml",
        "param"   : "235001/235002",  # radiation fluxes
        "stream"  : "oper",
        "time"    : "00/to/23/by/1",
        "step"    : "0/to/18/by/1",
        "type"    : "fc",
        "area"    : area,
        "grid"    : "0.5/0.5",
        "format"  : "netcdf",
    },
    outfile
)

