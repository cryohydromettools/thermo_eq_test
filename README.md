# 🌡️ Thermodynamic Equation Computation

This repository contains scripts to compute the **hourly main terms** of the **thermodynamic energy equation** using **ERA5 reanalysis data**.  
The workflow automates the **download**, **processing**, and **calculation** of spatial fields representing the various components of the **temperature tendency**.

---

## 🧮 Thermodynamic Equation

The governing thermodynamic equation is expressed as:

$$
\frac{dT}{dt} = - \left(u \frac{\partial T}{\partial x} + v \frac{\partial T}{\partial y}\right) + \left(\frac{R T}{c_p P} - \frac{\partial T}{\partial p}\right) \omega + \frac{J}{c_p}
$$


---

## 🔤 Variable Definitions

| Symbol | Description | Units |
|:-------:|:-------------|:------:|
| **T** | Air temperature | K |
| **u** | Zonal wind component | m s⁻¹ |
| **v** | Meridional wind component | m s⁻¹ |
| **ω** | Vertical velocity in pressure coordinates | Pa s⁻¹ |
| **P** | Pressure | Pa |
| **R** | Gas constant for dry air (≈ 287 J kg⁻¹ K⁻¹) | J kg⁻¹ K⁻¹ |
| **cₚ** | Specific heat of air at constant pressure (≈ 1004 J kg⁻¹ K⁻¹) | J kg⁻¹ K⁻¹ |
| **J** | Diabatic heating rate (e.g., from radiation) | K s⁻¹ |

---

## ⚙️ Equation Components

### 🔸 Horizontal Advection Term

$$
- \left(u \frac{\partial T}{\partial x} + v \frac{\partial T}{\partial y}\right)
$$

Represents temperature change due to **horizontal transport** by the wind field.

### 🔸 Adiabatic Term

$$
\left(\frac{R T}{c_p P} - \frac{\partial T}{\partial p}\right) \omega
$$

Describes **temperature change due to vertical motion**, reflecting adiabatic compression or expansion.

### 🔸 Diabatic Term

$$
\frac{J}{c_p} = SW_{flux} + LW_{flux} + LHF + \frac{\partial F_H}{\partial z}
$$

Represents the **heating or cooling** produced by **radiative** and other **non-adiabatic processes**, including **turbulent sensible and latent heat fluxes**.

- **SW₍flux₎** – shortwave radiative heating (solar radiation).  
- **LW₍flux₎** – longwave radiative heating (infrared radiation).  
- **LHF** – latent heat flux due to phase changes of water (e.g., condensation, evaporation, precipitation).  
- **∂F_H/∂z** – vertical gradient of sensible heat flux associated with turbulent heat transport.

Following the approach of *Xu et al. (2021)*:
- The **sensible heat flux** is derived from the **surface sensible heat flux**, assumed to **decrease linearly with height** up to the **planetary boundary layer**.  
- The **latent heat contribution** is estimated from the **precipitation rate**, assuming that **1 mm h⁻¹ of precipitation corresponds to a heating rate of 1.5 K h⁻¹**.


> ⚠️ **Warning:** When downloading **ERA5 forecast data**, be aware that the process may take a **long time**, depending on the **number of forecast days** and the **size of the selected domain**.

---

## 🧩 Script Descriptions

### `get_ERA5.py`
Downloads the required meteorological variables from **ERA5**, including:
- Temperature (`t`)
- Zonal and meridional wind components (`u`, `v`)
- Vertical velocity (`omega`)
- Pressure levels  

The script iterates over the defined time range and spatial domain to construct a consistent dataset for thermodynamic analysis.

---

### `get_ERA5_FC.py`
Downloads **radiative flux tendencies** at **model level 137** from **ERA5 forecast data**.  
These fluxes are used to estimate the **diabatic heating term** (`J`) in the thermodynamic equation.

---

### `compute_terms.py`
Computes all terms of the thermodynamic equation:

- `compute_advection_term_ncl` → Calculates the **horizontal advection** of temperature.  
- `compute_adiabatic_term` → Computes the **adiabatic heating/cooling** due to vertical motion.  
- `compute_diabatic_term` → Derives the **diabatic heating** from radiative fluxes.  

All resulting terms are **merged and saved** into a single NetCDF file for further spatial and temporal analysis.

---

## 📦 Output Description

The final output is a **NetCDF file** containing spatial fields for:

| Variable | Description |
|-----------|--------------|
| `advection` | Horizontal advection term |
| `adiabatic` | Adiabatic term |
| `diabatic` | Diabatic term |

These datasets can be visualized or analyzed to understand the relative contribution of dynamical and thermodynamical processes in atmospheric temperature variations.

---


- **Python ≥ 3.9**  
- **NCL** (for horizontal advection computation)  
- **Copernicus Climate Data Store (CDS API)** access for ERA5 data  
- **Python libraries:**
  - `numpy`
  - `xarray`
  - `pandas`
  - `matplotlib`
  - `cartopy`
  - `cdsapi`
  - `netCDF4`
  - `ncl`
---

## 📘 Example Workflow

1. Run `get_ERA5.py` → downloads ERA5 base variables.  
2. Run `get_ERA5_FC.py` → downloads radiation flux tendencies.  
3. Run `compute_terms.py` → computes and saves the thermodynamic equation terms.  

The resulting NetCDF file can then be visualized using Python (`matplotlib`, `cartopy`) or NCL.

---

### 📊 Analysis and Plot

A Jupyter notebook named **`plot_term.ipynb`** is provided to analyze the computed components of the thermodynamic energy equation.  
This notebook allows users to visualize each term as **time series** and **spatial fields** corresponding to **12 UTC** on a selected day.

---

## 👤 Author

Developed for thermodynamic budget analysis using **ERA5 reanalysis data**.  
Contact: [cryohydromettools@gmail.com](mailto:cryohydromettools@gmail.com)

---

## 🧠 Reference

The equation and methodology are based on the **thermodynamic energy balance** in pressure coordinates, as described in standard dynamic meteorology references such as *Holton & Hakim (2012)* — *An Introduction to Dynamic Meteorology*.


* Holton, J. R., & Hakim, G. J. (2013). An introduction to dynamic meteorology (Vol. 88). Academic press.
* Xu, M., Yu, L., Liang, K., Vihma, T., Bozkurt, D., Hu, X., & Yang, Q. (2021). Dominant role of vertical air flows in the unprecedented warming on the Antarctic Peninsula in February 2020. Communications Earth & Environment, 2(1), 133.

---
