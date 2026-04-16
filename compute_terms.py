import subprocess 
import xarray as xr
import numpy as np
import os


## Advection Term

def compute_advection_term_ncl(
    file_levels: str,
    ncl_script: str,
    file_adv_out: str,
    work_dir: str = None,
    pressure_level: float = 975.0,
) -> xr.DataArray:
    """
    Compute the horizontal advection term (K/h) at a given pressure level
    by preparing input data, executing an NCL script, and reading the output.

    Parameters
    ----------
    file_levels : str
        Path to NetCDF file containing ERA5 't', 'u', and 'v' variables at multiple pressure levels.
    ncl_script : str
        Path to the NCL script (e.g., 'advcandgrads.ncl') that computes advection and gradients.
    file_adv_out : str
        Path to the output NetCDF file that NCL will generate.
    work_dir : str, optional
        Temporary directory for intermediate files (default: same directory as input file).
    pressure_level : float, optional
        Pressure level (hPa) to process (default: 975).

    Returns
    -------
    xr.DataArray
        Advection term at the specified pressure level (K/h).
    """

    # --- Define working directory
    if work_dir is None:
        work_dir = os.path.dirname(file_levels)

    # Temporary file for 975 hPa
    file_975hPa = os.path.join(work_dir, f"temp_{int(pressure_level)}hPa.nc")

    # --- Step 1: Extract t, u, v at specified pressure level
    print(f"📘 Extracting t, u, v at {pressure_level} hPa from {file_levels}")
    ds = xr.open_dataset(file_levels)
    required_vars = {"t", "u", "v"}
    if not required_vars.issubset(ds.variables):
        raise ValueError(f"Dataset must contain variables: {', '.join(required_vars)}")
    
    ds[list(required_vars)].sel(pressure_level=pressure_level).to_netcdf(file_975hPa)

    # --- Step 2: Run NCL script to compute advection
    print(f"⚙️ Running NCL script: {ncl_script}")
    subprocess.run([
        "ncl",
        f'input="{file_975hPa}"',
        f'output="{file_adv_out}"',
        ncl_script
    ], check=True)

    # --- Step 3: Read NCL output and process advection term
    print(f"📗 Reading advection term from {file_adv_out}")
    ds_out = xr.open_dataset(file_adv_out)
    if "t_adv" not in ds_out:
        raise ValueError(f"Variable 't_adv' not found in {file_adv_out}")

    adv_term = -(ds_out["t_adv"] * 3600)  # Convert from K/s to K/h and reverse sign
    adv_term.name = f"advection_term_{int(pressure_level)}hPa"
    adv_term.attrs["long_name"] = f"Advection_term_975hPa"
    adv_term.attrs["units"] = "K/h"

    print("✅ Advection term computed successfully!")

    return adv_term

def compute_adiabatic_term(
    file_levels: str,
    file_t2m: str,
    output_var_name: str = "adiabatic_term_975hPa",
    p_target: float = 975.0,
    p_upper: float = 850.0,
    z_surface_m: float = 2.0
) -> xr.DataArray:
    """
    Compute the adiabatic temperature tendency term (K/h) at a given pressure level
    using ERA5 pressure-level and 2 m temperature data.

    Parameters
    ----------
    file_levels : str
        Path to NetCDF file containing 't' and 'w' on pressure levels (e.g., 850 and 975 hPa).
    file_t2m : str
        Path to NetCDF file containing 2 m temperature ('t2m').
    output_var_name : str, optional
        Name of the output DataArray (default: 'adiabatic_term_975hPa').
    p_target : float, optional
        Target pressure level [hPa] at which to compute the adiabatic term (default: 975 hPa).
    p_upper : float, optional
        Upper neighboring pressure level [hPa] for centered derivative (default: 850 hPa).
    z_surface_m : float, optional
        Reference height (m) for lower boundary (default: 2 m).

    Returns
    -------
    xr.DataArray
        Adiabatic term (K/h) computed at `p_target`.
    """

    # --- Physical constants
    R = 287.0     # J/(kg·K) - gas constant for dry air
    cp = 1005.0   # J/(kg·K) - specific heat at constant pressure

    # --- Helper: height → pressure (approx. hydrostatic relation)
    def height_to_pressure(height_m):
        return 101325 * (1 - height_m / 44330) ** 5.255  # Pa

    # --- Load datasets
    ds = xr.open_dataset(file_levels)
    ds_t2m = xr.open_dataset(file_t2m)

    # Check required variables
    for var in ["t", "w"]:
        if var not in ds:
            raise ValueError(f"'{var}' not found in pressure-level file: {file_levels}")
    if "t2m" not in ds_t2m:
        raise ValueError(f"'t2m' not found in surface file: {file_t2m}")

    # --- Select required levels
    T_upper = ds["t"].sel(pressure_level=p_upper)  # K
    T_target = ds["t"].sel(pressure_level=p_target)  # K
    T_surface = ds_t2m["t2m"]  # K
    omega = ds["w"].sel(pressure_level=p_target)  # Pa/s

    # --- Compute ∂T/∂p between 850 hPa and surface (K/Pa)
    p1 = p_upper * 1e2          # Pa
    p2 = height_to_pressure(z_surface_m)  # Pa (~101325 Pa)
    dTdp = (T_surface - T_upper) / (p2 - p1)

    # --- Compute adiabatic term (K/s → K/h)
    P = p_target * 1e2  # Pa
    RT_cpP = (R * T_target) / (cp * P)
    adi_term = (RT_cpP - dTdp) * omega * 3600  # K/h

    # --- Clean metadata and coords
    drop_vars = [v for v in ['number', 'expver', 'pressure_level'] if v in adi_term.coords]
    adi_term = adi_term.drop_vars(drop_vars, errors='ignore')

    # --- Add metadata
    adi_term.name = output_var_name
    adi_term.attrs["long_name"] = f"Adiabatic_term_975hPa"
    adi_term.attrs["units"] = "K/h"
    
    return adi_term

def compute_diabatic_term(
    file_flux: str,
    file_blh: str,
    file_rad_tende: str,
    rho: float = 1.2,      # kg/m³
    cp: float = 1005.0,    # J/(kg·K)
    T_K_conv: float = 1.5, # factor: 1 mm/h ≈ 1.5 K equivalente
    output_var_name: str = "diabatic_term_975hPa"
) -> xr.DataArray:
    """
    Compute the diabatic temperature tendency term (K/h) combining
    radiative, latent and sensible heat fluxes from ERA5 data.

    Parameters
    ----------
    file_flux : str
        Path to NetCDF file containing 'tp' (precipitation) and 'sshf' (sensible heat flux).
    file_blh : str
        Path to NetCDF file containing 'blh' (boundary layer height).
    file_rad_tende : str
        Path to NetCDF file containing radiation tendencies ('avg_ttswr' and 'avg_ttlwr')
        at model level 137.
    rho : float, optional
        Air density (kg/m³), default 1.2.
    cp : float, optional
        Specific heat capacity of air (J/(kg·K)), default 1005.
    T_K_conv : float, optional
        Conversion factor from mm/h to K (default 1.5).
    output_var_name : str, optional
        Name of the output DataArray.

    Returns
    -------
    xr.DataArray
        Diabatic term (K/h)
    """

    # --- Load datasets
    ds_flux = xr.open_dataset(file_flux)
    ds_blh = xr.open_dataset(file_blh)
    ds_rad_tende = xr.open_dataset(file_rad_tende)

    # --- Verify required variables
    if "tp" not in ds_flux or "sshf" not in ds_flux:
        raise ValueError(f"'tp' or 'sshf' not found in flux file: {file_flux}")
    if "blh" not in ds_blh:
        raise ValueError(f"'blh' not found in BLH file: {file_blh}")

    # --- Compute timestep (s)
    time = ds_flux["valid_time"]
    delta_t = (time[1] - time[0]) / np.timedelta64(1, "s")
    
    # --- Convert accumulated sensible heat flux to instantaneous (W/m²)
    shf = ds_flux["sshf"] / delta_t

    # --- Total precipitation (m w.e. → mm)
    tp_mm = ds_flux["tp"] * 1000.0  # [mm]

    # --- Mass flux [kg m^-2 s^-1]
    tp_mass_flux = tp_mm / 3600.0  # [kg m^-2 s^-1]

    # --- Latent heat flux tendency [W/m²]
    tendency_lhf = tp_mass_flux * T_K_conv * 3600.0

    # --- Boundary layer height [m]
    blh = ds_blh["blh"].clip(min=300.0)

    # --- Sensible heat flux tendency [K/h]
    tendency_shf = - (1 / (rho * cp) * (shf / blh)) * 3600.0

    # --- Radiation tendencies (SW + LW)
    ds_rad_tende = ds_rad_tende.sel(model_level=137)
    ds_rad_tende.coords["longitude"] = (ds_rad_tende.coords["longitude"] + 180) % 360 - 180
    ds_rad_tende = ds_rad_tende.sortby(ds_rad_tende.longitude)
    ds_rad_tende = ds_rad_tende.sortby("valid_time")
    ds_rad_tende = ds_rad_tende[["avg_ttswr", "avg_ttlwr"]].rolling(valid_time=3, center=True, min_periods=1).mean()
    ds_rad_tende = ds_rad_tende.sel(
        valid_time=slice(
            tendency_lhf.valid_time.min().values,
            tendency_lhf.valid_time.max().values
        )
    )
    ds_rad_tende = ds_rad_tende * 3600.0  # convert from K/s → K/h

    # --- Combine all diabatic components
    diabatic_term = (
        ds_rad_tende["avg_ttswr"] +
        ds_rad_tende["avg_ttlwr"] +
        tendency_lhf +
        tendency_shf
    )

    # --- Clean redundant coordinates
    drop_vars = [v for v in ["number", "expver", "model_level"] if v in diabatic_term.coords]
    diabatic_term = diabatic_term.drop_vars(drop_vars, errors="ignore")

    # --- Metadata
    diabatic_term.name = output_var_name
    diabatic_term.attrs["long_name"] = "Diabatic_term_975hPa"
    diabatic_term.attrs["units"] = "K/h"

    return diabatic_term


file_flux = "/home/lacrio/Documents/thermo_eq_test/data/era5_tp_shf_20200201_20200214.nc"
file_rad_tende = "/home/lacrio/Documents/thermo_eq_test/data/era5_radflux_20200201_20200214.nc"
file_t2m_blh ='/home/lacrio/Documents/thermo_eq_test/data/era5_t2m_blh_20200201_20200214.nc'

file_levels = '/home/lacrio/Documents/thermo_eq_test/data/era5_t_uvw_20200201_20200214.nc'
file_adv_term = "/home/lacrio/Documents/thermo_eq_test/data/posproc/adv_20200201_20200214_975hPa.nc"
work_dir = "/home/lacrio/Documents/thermo_eq_test/data/temp"

adve_term = compute_advection_term_ncl(file_levels=file_levels, ncl_script="advcandgrads.ncl",
                                      file_adv_out=file_adv_term, work_dir=work_dir,)
adia_term = compute_adiabatic_term(file_levels=file_levels, file_t2m=file_t2m_blh)
diab_term = compute_diabatic_term(file_flux, file_t2m_blh, file_rad_tende)


# --- Function to ensure latitude is in ascending order ---
def ensure_ascending_lat(da):
    if "latitude" in da.dims:
        if da.latitude[0] > da.latitude[-1]:  # descending → ascending
            da = da.sortby("latitude", ascending=True)
    return da

adve_term = ensure_ascending_lat(adve_term)
adia_term = ensure_ascending_lat(adia_term)
diab_term = ensure_ascending_lat(diab_term)

# --- Create dataset ---
ds_terms = xr.Dataset({
    adve_term.name: adve_term,
    adia_term.name: adia_term,
    diab_term.name: diab_term
})

print(ds_terms)

# 1️⃣ Remove empty or malformed variables and coordinates
for coord in list(ds_terms.coords):
    if ds_terms[coord].size == 0:
        print(f"⚠️ Removing empty coordinate: {coord}")
        ds_terms = ds_terms.drop_vars(coord)

# 2️⃣ Remove problematic attributes (e.g., 'bounds' or 'expver')
for coord in ["latitude", "longitude", "valid_time"]:
    if coord in ds_terms.coords:
        for bad_attr in ["bounds", "actual_range", "expver"]:
            if bad_attr in ds_terms[coord].attrs:
                del ds_terms[coord].attrs[bad_attr]

# 3️⃣ Ensure coordinates are properly aligned
ds_terms = ds_terms.assign_coords({
    "latitude": ds_terms.latitude.values,
    "longitude": ds_terms.longitude.values,
})

# 4️⃣ Reset encoding (to avoid metadata carried over from original NetCDF files)
for var in ds_terms.variables:
    ds_terms[var].encoding = {}

print(ds_terms)

# --- Save to NetCDF ---
output_file = "/home/lacrio/Documents/thermo_eq_test/data/posproc/thermo_terms_20200201_20200214.nc"

#breakpoint()
ds_terms.to_netcdf(output_file)

