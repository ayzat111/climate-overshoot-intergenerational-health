# functions.py
"""
Utility module for "Overshoot Pathways and Intergenerational Heatwave Risk" project.
Contains core functions for climate data processing, heatwave identification, 
regional aggregation, and health risk assessment.
"""

import numpy as np
import xarray as xr
import pandas as pd
import glob
import os

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
    if 'longitude' in da.coords: da = da.rename({'longitude': 'lon', 'latitude': 'lat'})
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

def identify_heatwave_days(da, thresh):
    """Calculates annual total heatwave days (any day within a 3+ day streak)."""
    da = remap_to_common(da)
    exceed = da > thresh
    
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    
    # Mark all days belonging to a valid heatwave event (streak >= 3)
    hw_events = (streak >= 3)
    # Use rolling max to ensure the first two days of the streak are also flagged
    hw_days = hw_events.rolling(time=3, center=False).max().shift(time=-2).fillna(False) | hw_events
    
    annual_days = hw_days.resample(time='Y').sum()
    return annual_days.assign_coords(year=('time', annual_days.time.dt.year.data))

# =============================================================================
# 3. ENSEMBLE STATISTICS & ERROR PROPAGATION
# =============================================================================

def get_ensemble_stats_with_variance(directory, pattern, col_name='hw_days'):
    """Calculates annual ensemble mean and inter-model variance from CSV files."""
    files = [f for f in glob.glob(os.path.join(directory, pattern)) 
             if 'region' not in os.path.basename(f)]
    df_list = []
    
    for f in files:
        _df = pd.read_csv(f).groupby('year').mean()
        if col_name in _df.columns:
            df_list.append(_df[col_name])
    
    combined = pd.concat(df_list, axis=1)
    return combined.mean(axis=1), combined.var(axis=1)

def calculate_lifetime_with_error_propagation(b_year, ts_early_mean, ts_early_var, 
                                             ts_late_mean, ts_late_var, lifespan=75):
    """Calculates cumulative lifetime exposure and propagated uncertainty (SD)."""
    total_mean, total_variance, lifetime_series = 0, 0, []
    
    for age in range(lifespan + 1):
        yr = b_year + age
        # Switch logic for multi-ensemble transition (11-model to 5-model)
        if yr <= 2100:
            if yr in ts_early_mean.index:
                m, v = ts_early_mean.loc[yr], ts_early_var.loc[yr]
            else: continue
        else:
            if yr in ts_late_mean.index:
                m, v = ts_late_mean.loc[yr], ts_late_var.loc[yr]
            else: continue
            
        total_mean += m
        total_variance += v
        lifetime_series.append(m)
            
    return total_mean, np.sqrt(total_variance), lifetime_series

# =============================================================================
# 4. REGIONAL AGGREGATION & HEALTH RISK
# =============================================================================

# Vulnerability weights based on GBD (Global Burden of Disease) 2021 age-mortality
GBD_AGE_WEIGHTS = {
    (0, 4): 0.029338843, (5, 9): 0.009090909, (10, 19): 0.01446281,
    (20, 54): 0.107438017, (55, 59): 0.293801653, (60, 75): 0.545867769 
}

def get_weight_for_age(age):
    """Returns GBD vulnerability weight for a specific age."""
    for (start, end), weight in GBD_AGE_WEIGHTS.items():
        if start <= age <= end: return weight
    return 0

def find_gbd_region_optimized(ne_name, gbd_map):
    """Maps Natural Earth country names to GBD Level 2/3 Regions."""
    manual_map = {
        "Russia": "Russian Federation", "United States of America": "United States",
        "China": "China", "Dem. Rep. Congo": "Congo, Democratic Republic of the",
        "Turkey": "Türkiye", "Vietnam": "Viet Nam"
    }
    target = manual_map.get(ne_name, ne_name)
    if target in gbd_map: return gbd_map[target]
    # Fuzzy matching for minor naming discrepancies
    for gbd_n in gbd_map.keys():
        if target in gbd_n or gbd_n in target: return gbd_map[gbd_n]
    return np.nan

# =============================================================================
# 5. COHORT METRICS CALCULATION
# =============================================================================

def calculate_cohort_metrics_simple(region_series, birth_years, lifespan=75):
    """
    Calculates lifetime exposure and weighted health risk for multiple cohorts.
    
    Parameters:
    -----------
    region_series : pandas.Series
        Time-series of heatwave days (index is year).
    birth_years : array-like
        List of birth years to calculate (e.g., 1950 to 2120).
    lifespan : int
        Lifespan to integrate (default 75).
        
    Returns:
    --------
    abs_days : np.array
        Total lifetime exposure days per cohort.
    risk_vals : np.array
        Total weighted health risk per cohort.
    """
    abs_days = []
    risk_vals = []
    
    for by in birth_years:
        t_days = 0
        t_risk = 0
        for age in range(lifespan + 1):
            year = by + age
            if year in region_series.index:
                days = region_series.loc[year]
                weight = get_weight_for_age(age)
                t_days += days
                t_risk += days * weight
        
        abs_days.append(t_days)
        risk_vals.append(t_risk)
        
    return np.array(abs_days), np.array(risk_vals)
