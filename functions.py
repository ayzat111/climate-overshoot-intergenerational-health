# functions.py
import numpy as np
import xarray as xr
import pandas as pd

# --- 1. Grid Definition and Interpolation Logic ---
# Define a standard 1.0 degree global grid
target_lon = np.arange(-179.5, 180.5, 1.0)
target_lat = np.arange(-89.5, 90.5, 1.0)
target_ds  = xr.Dataset({'lon': target_lon, 'lat': target_lat})

def remap_to_common(da):
    """Interpolates a DataArray to the common 1x1 degree grid."""
    return da.interp(lon=target_ds.lon, lat=target_ds.lat,
                     method='linear', kwargs={'fill_value': 'extrapolate'})

# --- 2. Core Computational Logic ---
def calc_threshold(his_files):
    """Calculates the historical baseline threshold (95th percentile)."""
    # Open historical files and extract maximum temperature (tasmax)
    ds = xr.open_mfdataset(his_files, combine='by_coords', use_cftime=True)['tasmax'].squeeze()
    # Select the pre-industrial period (1850-1900)
    ds = ds.sel(time=slice('1850', '1900'))
    # Remap to common grid and calculate the 95th quantile across the time dimension
    return remap_to_common(ds).quantile(0.95, dim='time').compute()

def identify_heatwave(da, thresh):
    """Identifies heatwave frequency based on a 3-day exceedance streak."""
    da = remap_to_common(da)
    exceed = da > thresh
    
    # Calculate consecutive days using cumulative sum and forward fill
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    
    # Identify the start of a heatwave (where streak reaches 3 days for the first time)
    hw_start = (streak >= 3) & (streak.shift(time=1) < 3)
    
    # Resample to annual frequency to get total heatwave counts per year
    annual = hw_start.resample(time='Y').sum()
    return annual.assign_coords(year=('time', annual.time.dt.year.data))

def global_mean(da):
    """Calculates the area-weighted global mean using cosine of latitude."""
    cos_lat = np.cos(np.deg2rad(da.lat))
    # Create weight matrix matching the DataArray shape
    weight = cos_lat * (da * 0 + 1)
    return (da * weight).sum(dim=('lat', 'lon')) / weight.sum(dim=('lat', 'lon'))

def make_ssp534os_full(df, model):
    """Concatenates historical SSP585 and SSP534-overwash data for a complete timeline."""
    # Extract SSP585 data up to 2039 and relabel as SSP534os
    df585 = df.query("model==@model & scenario=='ssp585' & year<=2039").copy().assign(scenario='ssp534os')
    # Extract existing SSP534os data
    df534 = df.query("model==@model & scenario=='ssp534os'").copy()
    
    # Filter out original incomplete SSP534os entries and merge with synthesized timeline
    df_out = df[~((df['model']==model) & (df['scenario']=='ssp534os'))]
    return pd.concat([df_out, df585, df534], ignore_index=True)

def open_concat(paths, dask_kwargs={'chunks': {'time': 365}}):
    """Concatenates multiple files along the time dimension."""
    if len(paths) == 1:
        return xr.open_dataset(paths[0], **dask_kwargs)
    return xr.open_mfdataset(paths, combine='by_coords', **dask_kwargs)

def identify_heatwave_days(da, thresh):
    """
    Calculates annual total heatwave days.
    A heatwave day is defined as any day that is part of a 3+ day exceedance streak.
    """
    da = remap_to_common(da)
    exceed = da > thresh
    
    # Calculate streaks
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    
    # Identify all days belonging to a streak of at least 3 days
    # First, mark the end points, then backfill to cover the entire duration
    hw_events = (streak >= 3)
    # To ensure the first 2 days of a 3-day streak are also counted:
    # We use a rolling maximum or similar logic to 'spread' the True value backward
    hw_days = hw_events.rolling(time=3, center=False).max().shift(time=-2).fillna(False) | hw_events
    
    # Sum days annually
    annual_days = hw_days.resample(time='Y').sum()
    return annual_days.assign_coords(year=('time', annual_days.time.dt.year.data))

def make_ssp534os_full_days(df, model):
    """
    Specifically handles the concatenation for SSP534os duration data.
    Merges historical/SSP585 (up to 2039) with SSP534os (from 2040).
    """
    df585 = df.query("model==@model & scenario=='ssp585' & year<=2039").copy().assign(scenario='ssp534os')
    df534 = df.query("model==@model & scenario=='ssp534os'").copy()
    
    df_out = df[~((df['model']==model) & (df['scenario']=='ssp534os'))]
    return pd.concat([df_out, df585, df534], ignore_index=True)
