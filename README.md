# PX4-NetCDF - file format converter

This repository provides a Python-based conversion tool to transform PX4 uLog flight log into WMO standardized NetCDF format. The tool was developed as part of the [WMO Uncrewed Aircraft Systems Demonstration Campaign (UAS DC)](https://community.wmo.int/en/uas-demonstration), which aims to compare meteorological data collected by UAV platforms.

## Purpose

PX4-based UAVs commonly store onboard telemetry in the uLog format. However, this format is not natively compatible with the NetCDF-based specification required for UAS DC data sharing. This script automates the extraction and transformation of relevant flight and environmental data to meet the CF-compliant NetCDF format described in the [wmo-uasdc repository](https://github.com/synoptic/wmo-uasdc).

## Features

* Parses ULog files from PX4-based systems
* Extracts selected datasets including GPS position, barometric pressure, and hygrometer data
* Interpolates data to ensure continuity
* Renames variables and assigns CF-compliant metadata
* Outputs a NetCDF file with UAS DC naming and structure conventions

## Output

The generated NetCDF file includes variables such as:

* `lat`, `lon`, `altitude` (trajectory coordinates)
* `air_temperature`, `relative_humidity`, `air_pressure`
* Attributes compliant with CF-1.8 and WMO-CF-1.0 conventions

The file naming convention follows:

```
UASDC_<operatorID>_<airframeID>_<timestamp>.nc
```

## Dependencies

* Python 3.x
* `xarray`
* `numpy`
* `pandas`
* `pyulog`
* `netCDF4`

Install dependencies using:

```bash
pip install -r requirements.txt
```

## Usage

Modify the script with the desired input ULog filename (default: `mc.ulg`) and set metadata fields like `operator_id` and `airframe_id` before running:

```bash
python ulog-to-netcdf.py
```

---

This tool is developed by [ThunderFly s.r.o.](https://www.thunderfly.cz/) for collaborative use in atmospheric research and UAV data standardization.
