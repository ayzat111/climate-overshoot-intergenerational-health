# functions.py
"""
Utility module for "Overshoot Pathways and Intergenerational Heatwave Risk" project.
Contains core functions for climate data processing, heatwave identification, 
and ensemble-based scenario synthesis.
"""

import numpy as np
import xarray as xr
import pandas as pd

# =============================================================================
# 1. DATA I/O & GRID PREPROCESSING
# =============================================================================

# Define a standard 1.0 degree global grid for harmonization
target_lon = np.arange(-179.5, 180.5, 1.0)
target_lat = np.arange(-89.5, 90.5, 1.0)
target_ds  = xr.Dataset({'lon': target_lon, 'lat': target_lat})

def open_concat(paths, dask_kwargs={'chunks': {'time': 365}}):
    """Concatenates multiple NetCDF files along the time dimension using Dask."""
    if len(paths) == 1:
        return xr.open_dataset(paths[0], **dask_kwargs)
    return xr.open_mfdataset(paths, combine='by_coords', **dask_kwargs)

def remap_to_common(da):
    """Interpolates a DataArray to the common 1x1 degree target grid."""
    return da.interp(lon=target_ds.lon, lat=target_ds.lat,
                     method='linear', kwargs={'fill_value': 'extrapolate'})

# =============================================================================
# 2. CORE CLIMATE ALGORITHMS (HEATWAVES)
# =============================================================================

def calc_threshold(his_files):
    """Calculates the historical 95th percentile threshold (1850-1900)."""
    ds = xr.open_mfdataset(his_files, combine='by_coords', use_cftime=True)['tasmax'].squeeze()
    ds = ds.sel(time=slice('1850', '1900'))
    return remap_to_common(ds).quantile(0.95, dim='time').compute()

def identify_heatwave(da, thresh):
    """Calculates annual heatwave frequency (events with 3+ day streaks)."""
    da = remap_to_common(da)
    exceed = da > thresh
    
    # Calculate streak duration
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    
    # Identify the start of a heatwave (first time streak reaches 3)
    hw_start = (streak >= 3) & (streak.shift(time=1) < 3)
    
    annual = hw_start.resample(time='Y').sum()
    return annual.assign_coords(year=('time', annual.time.dt.year.data))

def identify_heatwave_days(da, thresh):
    """Calculates annual total heatwave days (any day within a 3+ day streak)."""
    da = remap_to_common(da)
    exceed = da > thresh
    
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    
    # Mark all days belonging to a valid heatwave event
    hw_events = (streak >= 3)
    # Use rolling max to ensure the first two days of the streak are also flagged
    hw_days = hw_events.rolling(time=3, center=False).max().shift(time=-2).fillna(False) | hw_events
    
    annual_days = hw_days.resample(time='Y').sum()
    return annual_days.assign_coords(year=('time', annual_days.time.dt.year.data))

def identify_heatwave_intensity(da, thresh):
    """
    Calculates annual cumulative heatwave intensity.
    Intensity is defined as the sum of (Tmax - threshold) for all days 
    belonging to a 3+ day exceedance streak.
    """
    da = remap_to_common(da)
    diff = da - thresh
    is_hot = diff > 0
    
    # Identify streaks of at least 3 days
    hot_3d = is_hot.rolling(time=3, center=False).sum() >= 3
    
    # Backfill to ensure all days in the 3-day window are marked
    hw_day = (hot_3d | 
              hot_3d.shift(time=-1, fill_value=False) | 
              hot_3d.shift(time=-2, fill_value=False))
    
    # Extract exceedance values only during heatwave days
    hw_exceedance = diff.where(hw_day, 0.0)
    
    # Sum exceedance annually
    annual_intensity = hw_exceedance.resample(time='Y').sum()
    return annual_intensity.assign_coords(year=('time', annual_intensity.time.dt.year.data))

# =============================================================================
# 3. SPATIAL & STATISTICAL ANALYSIS
# =============================================================================

def global_mean(da):
    """Calculates area-weighted global mean using cosine of latitude."""
    cos_lat = np.cos(np.deg2rad(da.lat))
    weight = cos_lat * (da * 0 + 1)
    return (da * weight).sum(dim=('lat', 'lon')) / weight.sum(dim=('lat', 'lon'))

def population_weighted_mean(da, pop):
    """
    Calculates population-weighted mean for a climate variable.
    da: DataArray (time/year, lat, lon)
    pop: DataArray (lat, lon) or (time, lat, lon) - population distribution
    """
    # Ensure the heatwave data is interpolated to the population grid
    da_interp = da.interp_like(pop, method='nearest')
    
    # Calculate weights: Pop_grid / Total_Global_Pop
    # We sum over lat and lon to get the total population at each time step
    weights = pop / pop.sum(dim=['lat', 'lon'])
    
    # Weighted average
    weighted_mean = (da_interp * weights).sum(dim=['lat', 'lon'])
    return weighted_mean

# =============================================================================
# 4. SCENARIO SYNTHESIS (OVERSHOOT HANDLING)
# =============================================================================

def make_ssp534os_full(df, model):
    """Concatenates SSP585 (up to 2039) and SSP534os (from 2040) for frequency data."""
    df585 = df.query("model==@model & scenario=='ssp585' & year<=2039").copy().assign(scenario='ssp534os')
    df534 = df.query("model==@model & scenario=='ssp534os'").copy()
    
    df_out = df[~((df['model']==model) & (df['scenario']=='ssp534os'))]
    return pd.concat([df_out, df585, df534], ignore_index=True)

def make_ssp534os_full_days(df, model):
    """Concatenates SSP585 (up to 2039) and SSP534os (from 2040) for duration data."""
    # Logic is identical to frequency; kept separate for workflow clarity
    return make_ssp534os_full(df, model)

# =============================================================================
# 5. COHORT ANALYSIS (NEW SECTION)
# =============================================================================

def calculate_lifetime_exposure(df_series, birth_year, lifespan=75):
    """
    Integrates total exposure over a fixed lifespan for a specific birth cohort.
    
    Parameters:
    -----------
    df_series : pandas.Series
        The time-series of heatwave days/frequency with 'year' as the index.
    birth_year : int
        The year the cohort was born.
    lifespan : int
        Number of years to integrate (default 75 for life expectancy).
        
    Returns:
    --------
    float : Total cumulative exposure over 75 years.
    """
    start_yr = birth_year
    end_yr = birth_year + lifespan - 1 # e.g., 1990 to 2064 is 75 years
    
    if start_yr in df_series.index and end_yr in df_series.index:
        return df_series.loc[start_yr:end_yr].sum()
    else:
        # Returns NaN if the time series doesn't cover the full lifespan
        return np.nan
