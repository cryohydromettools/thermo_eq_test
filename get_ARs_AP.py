import xarray as xr
import pandas as pd
import numpy as np

filename = '/home/cr2/cmtorres/ARs_DATA/Global_AR_dataset_Guan.nc'
ds = xr.open_dataset(filename).sel(time=slice('1980-01-01', '2022-12-31'), ens = 1, lev = 0)
ds.coords['lon'] = (ds.coords['lon'] + 180) % 360 - 180
ds = ds.sortby(ds.lon)
ds = ds.sel(lon=slice(-100, -30), lat=slice(-35, -72))
ds = ds.sel(time=ds['time'].dt.month.isin([11, 12, 1, 2, 3]))

ds_AP = ds.sel(lon=slice(-80, -55), lat=slice(-60, -70))

df_AR_6h = ds_AP[['shapemap', 'axismap']].count(dim=['lat', 'lon']).to_dataframe()

df_AR_6h_25 = df_AR_6h.copy()
df_AR_6h_25 = df_AR_6h_25[['shapemap']].groupby(df_AR_6h_25.index.date).max()
df_AR_6h_25.loc[:,'shapemap'] = df_AR_6h_25['shapemap'].where(df_AR_6h_25['shapemap'] >= 500, np.nan)
df_AR_6h_25.index.name = ('date')

filename = '/home/cr2/cmtorres/repos/Patagonia-Antarctic_Peninsula/data/ARs_Guan_AP_day.csv'
df_AR_6h_25.to_csv(filename, index=True, sep='\t')