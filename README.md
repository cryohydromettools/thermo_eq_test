# 🌡️ Thermodynamic Equation Computation

This repository contains scripts to compute the **main physical contributions to atmospheric temperature tendency** using **ERA5 reanalysis data**.  
The workflow automates the **download**, **processing**, and **calculation** of the dominant terms of the thermodynamic energy equation associated with extreme temperature events.

The methodology follows approaches similar to those proposed by González-Herrero et al. (2022) and Lemus-Canovas et al. (2025) for diagnosing the relative contribution of dynamical and thermodynamical processes during temperature extremes.

---

## 🧮 Thermodynamic Equation

The thermodynamic energy equation in pressure coordinates is expressed as:

$$
\underbrace{\frac{\Delta T}{\Delta t}}_{\mathrm{Tend}}
=
\underbrace{-\vec{V}\cdot\nabla_p T}_{\mathrm{Adv}}
\underbrace{-\omega \frac{T}{\theta}\frac{\partial \theta}{\partial p}}_{\mathrm{Adiab}}
+
\underbrace{Q_{\mathrm{diab}}}_{\mathrm{Diab}}
$$

where:

- **Tend** → local temperature tendency  
- **Adv** → horizontal temperature advection  
- **Adiab** → adiabatic heating/cooling associated with vertical motion  
- **Diab** → diabatic contribution and residual processes  

---

## 🔤 Variable Definitions

| Symbol | Description | Units |
|:-------:|:-------------|:------:|
| **T** | Air temperature | K |
| **u** | Zonal wind component | m s⁻¹ |
| **v** | Meridional wind component | m s⁻¹ |
| **ω** | Vertical velocity in pressure coordinates | Pa s⁻¹ |
| **p** | Atmospheric pressure | Pa |
| **θ** | Potential temperature | K |

---

## ⚙️ Methodology

For each identified event day, the contribution of the three main physical forcings to the temperature tendency was assessed using the thermodynamic equation.

### 🔸 Horizontal Advection Term

The first term represents **horizontal heat advection**, which depends on the wind field and the horizontal temperature gradient:

$$
-\vec{V} \cdot \nabla_p T
$$

This term was calculated using:

- Temperature at **700 hPa**
- Zonal wind (**u**) at **700 hPa**
- Meridional wind (**v**) at **700 hPa**

The **700 hPa level** was selected to minimize the influence of topography on the calculations, following Lemus-Canovas et al. (2025).

---

### 🔸 Adiabatic Term

The second term describes the temperature change associated with **vertical motion**:

$$
-\omega \frac{T}{\theta} \frac{\partial \theta}{\partial p}
$$

The vertical potential temperature gradient at 700 hPa was estimated from the difference between:

- **750 hPa**
- **650 hPa**

using:

$$
\frac{\partial \theta}{\partial p}
$$

and ERA5 vertical velocity (**ω**) at **700 hPa**.

---

### 🔸 Diabatic / Residual Term

The third term was calculated as the **residual** of the thermodynamic equation:

$$
Q_{diab}
$$

This residual may include:

- diabatic heating/cooling processes
- radiative effects
- turbulent fluxes
- latent heat release
- numerical and interpolation errors

---

## 📥 ERA5 Variables

All variables required for the calculations were obtained from **ERA5 reanalysis**.

The following variables are used:

| Variable | Pressure Level |
|-----------|----------------|
| Temperature (`t`) | 700 hPa |
| Zonal wind (`u`) | 700 hPa |
| Meridional wind (`v`) | 700 hPa |
| Vertical velocity (`omega`) | 700 hPa |
| Potential temperature (`θ`) | 650–750 hPa |

---

## 🧩 Script Descriptions

### `get_ERA5.py`

Downloads ERA5 atmospheric variables required for the thermodynamic calculations, including:

- Temperature (`t`)
- Zonal wind (`u`)
- Meridional wind (`v`)
- Vertical velocity (`omega`)

for the selected pressure levels and spatial domain.

---

### `compute_terms.py`

Computes the thermodynamic equation components:

- `compute_advection_term` → horizontal temperature advection  
- `compute_adiabatic_term` → adiabatic heating/cooling due to vertical motion  
- `compute_residual_term` → residual diabatic contribution  

All resulting terms are merged and saved into a NetCDF dataset.

---

## 📦 Output Description

The final output is a NetCDF file containing:

| Variable | Description |
|-----------|--------------|
| `advection` | Horizontal advection term |
| `adiabatic` | Adiabatic term |
| `residual` | Residual / diabatic contribution |

These fields can be analyzed spatially and temporally to assess the dominant mechanisms driving atmospheric temperature variability during extreme events.

---

## ⚠️ Notes

- ERA5 data are downloaded from the Copernicus Climate Data Store (CDS).
- Large spatial domains and long periods may substantially increase download time and storage requirements.
- The residual term may contain accumulated numerical uncertainties from the different equation components.

---

## 📘 Example Workflow

1. Run `get_ERA5.py` → download ERA5 atmospheric variables  
2. Run `compute_terms.py` → compute thermodynamic equation terms  
3. Analyze the resulting NetCDF files using Python or NCL  

---

## 📊 Analysis and Visualization

A Jupyter notebook named `plot_term.ipynb` is provided to:

- visualize spatial fields
- analyze time series
- compare thermodynamic contributions during event days

---

## 🛠️ Requirements

- Python ≥ 3.9
- CDS API access
- Python libraries:
  - `numpy`
  - `xarray`
  - `pandas`
  - `matplotlib`
  - `cartopy`
  - `metpy`
  - `cdsapi`
  - `netCDF4`

---

## 👤 Author

Developed for thermodynamic budget analysis using ERA5 reanalysis data.  

Contact: cryohydromettools@gmail.com

---

## 📚 References

- González-Herrero, S., Barriopedro, D., Trigo, R. M., López-Bustins, J. A., & Oliva, M. (2022). Climate warming amplified the 2020 record-breaking heatwave in the Antarctic Peninsula. Communications Earth & Environment, 3(1), 122. https://doi.org/10.1038/s43247-022-00450-5
- Lemus-Canovas, M., Gonzalez-Herrero, S., Trapero, L., Albalat, A., Insua-Costa, D., Senande-Rivera, M., & Miguez-Macho, G. (2025). Exploring the interplay between observed warming, atmospheric circulation, and soil–atmosphere feedbacks on heatwaves in a temperate mountain region. Natural Hazards and Earth System Sciences, 25(7), 2503-2518. https://doi.org/10.5194/nhess-25-2503-2025


---