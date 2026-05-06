# functions.py
import numpy as np
import xarray as xr
import pandas as pd

# --- 1. 网格与插值逻辑 ---
target_lon = np.arange(-179.5, 180.5, 1.0)
target_lat = np.arange(-89.5, 90.5, 1.0)
target_ds  = xr.Dataset({'lon': target_lon, 'lat': target_lat})

def remap_to_common(da):
    return da.interp(lon=target_ds.lon, lat=target_ds.lat,
                     method='linear', kwargs={'fill_value': 'extrapolate'})

# --- 2. 核心计算逻辑 ---
def calc_threshold(his_files):
    """计算历史基准期阈值"""
    ds = xr.open_mfdataset(his_files, combine='by_coords', use_cftime=True)['tasmax'].squeeze()
    ds = ds.sel(time=slice('1850', '1900'))
    return remap_to_common(ds).quantile(0.95, dim='time').compute()

def identify_heatwave(da, thresh):
    """识别热浪频率 (3-day streak)"""
    da = remap_to_common(da)
    exceed = da > thresh
    cum = exceed.cumsum(dim='time')
    streak = cum - cum.where(~exceed).ffill(dim='time').fillna(0)
    hw_start = (streak >= 3) & (streak.shift(time=1) < 3)
    annual = hw_start.resample(time='Y').sum()
    return annual.assign_coords(year=('time', annual.time.dt.year.data))

def global_mean(da):
    """全球纬度加权平均"""
    cos_lat = np.cos(np.deg2rad(da.lat))
    weight = cos_lat * (da * 0 + 1)
    return (da * weight).sum(dim=('lat', 'lon')) / weight.sum(dim=('lat', 'lon'))

def make_ssp534os_full(df, model):
    """拼接Overshoot情景"""
    df585 = df.query("model==@model & scenario=='ssp585' & year<=2039").copy().assign(scenario='ssp534os')
    df534 = df.query("model==@model & scenario=='ssp534os'").copy()
    df_out = df[~((df['model']==model) & (df['scenario']=='ssp534os'))]
    return pd.concat([df_out, df585, df534], ignore_index=True)
