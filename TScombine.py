import sys
import os.path
import json
from dateutil.parser import parse
from datetime import datetime

import xarray as xr
import pandas as pd
import numpy as np


def write_netCDF_aggfile(agg_dataset, ncout_filename, encoding, base_path):
    """
    write netcdf file

    :param agg_dataset: aggregated xarray dataset
    :param ncout_filename: name of the netCDF file to be written
    :return: name of the netCDf file written
    """

    agg_dataset.to_netcdf(os.path.join(base_path, ncout_filename), encoding=encoding, format='NETCDF4_CLASSIC')

    return ncout_filename


def generate_netcdf_output_filename(nc, facility_code, data_code, VoI, site_code, product_type, file_version):
    """
    generate the output filename for the VoI netCDF file

    :param nc: aggregated dataset
    :param facility_code: facility code from file name
    :param data_code: data code sensu IMOS convention
    :param VoI: name of the variable to aggregate
    :param product_type: name of the product
    :param file_version: version of the output file
    :return: name of the output file
    """

    file_timeformat = '%Y%m%d'

    if '_' in VoI:
        VoI = VoI.replace('_', '-')
    t_start = pd.to_datetime(nc.TIME.min().values).strftime(file_timeformat)
    t_end = pd.to_datetime(nc.TIME.max().values).strftime(file_timeformat)

    output_name = '_'.join(
        ['IMOS', facility_code, data_code, t_start, site_code, ('FV0' + str(file_version)), (VoI + "-" + product_type),
         t_end, 'C-' + datetime.utcnow().strftime(file_timeformat)]) + '.nc'

    return output_name


def get_facility_code(fileURL):
    """
    get the facility code from the file URL

    :param fileURL: URL of a file
    :return: facility code
    """
    split_filename = fileURL.split("/")[-1].split("_")
    return split_filename[1]


def create_empty_dataframe(columns):
    """
    create empty dataframe from a dict with data types

    :param: variable name and variable file. List of tuples
    :return: empty dataframe
    """

    return pd.DataFrame({k: pd.Series(dtype=t) for k, t in columns})


def set_globalattr(agg_dataset, templatefile, varname, site_code, add_attribute):
    """
    global attributes from a reference nc file and nc file

    :param agg_dataset: aggregated xarray dataset
    :param templatefile: name of the attributes JSON file
    :param varname: name of the variable of interest to aggregate
    :param site_code: site code
    :param add_attribute: dictionary of additional attributes to add name:value
    :return: dictionary of global attributes
    """

    timeformat = '%Y-%m-%dT%H:%M:%SZ'
    with open(templatefile) as json_file:
        global_metadata = json.load(json_file)["_global"]

    agg_attr = {'title': ("Long Timeseries Aggregated product: " + varname + " at " + site_code + " between " + \
                          pd.to_datetime(agg_dataset.TIME.values.min()).strftime(timeformat) + " and " + \
                          pd.to_datetime(agg_dataset.TIME.values.max()).strftime(timeformat)),
                'site_code': site_code,
                'local_time_zone': '',
                'time_coverage_start': pd.to_datetime(agg_dataset.TIME.values.min()).strftime(timeformat),
                'time_coverage_end': pd.to_datetime(agg_dataset.TIME.values.max()).strftime(timeformat),
                'geospatial_vertical_min': float(agg_dataset.DEPTH.min()),
                'geospatial_vertical_max': float(agg_dataset.DEPTH.max()),
                'geospatial_lat_min': agg_dataset.LATITUDE.values.min(),
                'geospatial_lat_max': agg_dataset.LATITUDE.values.max(),
                'geospatial_lon_min': agg_dataset.LONGITUDE.values.min(),
                'geospatial_lon_max': agg_dataset.LONGITUDE.values.max(),
                'date_created': datetime.utcnow().strftime(timeformat),
                'history': datetime.utcnow().strftime(timeformat) + ': Aggregated file created.',
                'keywords': ', '.join(list(agg_dataset.variables) + ['TS-AGGREGATED'])}
    global_metadata.update(agg_attr)
    global_metadata.update(add_attribute)

    return dict(sorted(global_metadata.items()))


def TS_combine(site_code):
    """
    combine TEMP and PSAL aggregated files into one

    :param site_code: site code
    :return: file name of the aggregated file
    """

    ##TODO: implement lookup of the file names
    # filePSAL = 'IMOS_ANMN-NRS_SZ_20081120_NRSROT_FV01_PSAL-aggregated-timeseries_END-20190523_C-20190822.nc'
    # fileTEMP = 'IMOS_ANMN-NRS_TZ_20081120_NRSROT_FV01_TEMP-aggregated-timeseries_END-20190523_C-20190819.nc'
    filePSAL = 'Sample/IMOS_ANMN-QLD_SZ_20120221_PIL050_FV01_PSAL-aggregated-timeseries_END-20140727_C-20190822.nc'
    fileTEMP = 'Sample/IMOS_ANMN-QLD_TZ_20120221_PIL050_FV01_TEMP-aggregated-timeseries_END-20140816_C-20190819.nc'

    nc1 = xr.open_dataset(filePSAL)
    nc2 = xr.open_dataset(fileTEMP)

    ## salinity file
    ## we assume that this will be controlling the merging, not temperature
    ## get list of instruments
    instruments1 = list(nc1.instrument_id.values)
    instruments2 = list(nc2.instrument_id.values)
    instrumentDict = {}
    for i in range(0, len(instruments1)):
        dd = {i: instruments2.index(instruments1[i])}
        instrumentDict.update(dd)

    ## create empty DF for main and auxiliary variables
    MainDF_types = [('TEMP', float),
                    ('TEMP_quality_control', np.byte),
                    ('PSAL', float),
                    ('PSAL_quality_control', np.byte),
                    ('TIME', np.float64),
                    ('DEPTH', float),
                    ('DEPTH_quality_control', np.byte),
                    ('PRES', np.float64),
                    ('PRES_quality_control', np.byte),
                    ('PRES_REL', np.float64),
                    ('PRES_REL_quality_control', np.byte),
                    ('instrument_index', int)]

    AuxDF_types = [('source_file', str),
                   ('instrument_id', str),
                   ('LONGITUDE', float),
                   ('LATITUDE', float),
                   ('NOMINAL_DEPTH', float)]
    variableMainDF = create_empty_dataframe(MainDF_types)
    variableAuxDF = create_empty_dataframe(AuxDF_types)

    fileIndex = 0
    for key in instrumentDict.keys():
        print(fileIndex)
        ncPSAL = nc1.where(nc1.instrument_index == key, drop=True)
        ncTEMP = nc2.where(nc2.instrument_index == instrumentDict[key], drop=True)

        nobsPSAL = len(ncPSAL.TIME)
        nobsTEMP = len(ncTEMP.TEMP)

        ## if different sizes STOP
        if nobsPSAL != nobsTEMP:
            sys.exit('T and S of different sizes')

        ## main data frame
        DF = pd.DataFrame({'TIME': ncPSAL.TIME,
                           'TEMP': ncTEMP.TEMP,
                           'TEMP_quality_control': ncTEMP.TEMP_quality_control,
                           'PSAL': ncPSAL.PSAL,
                           'PSAL_quality_control': ncPSAL.PSAL_quality_control,
                           'DEPTH': ncPSAL.DEPTH,
                           'DEPTH_quality_control': ncPSAL.DEPTH_quality_control,
                           'PRES': ncPSAL.PRES,
                           'PRES_quality_control': ncPSAL.PRES_quality_control,
                           'PRES_REL': ncPSAL.PRES_REL,
                           'PRES_REL_quality_control': ncPSAL.PRES_REL_quality_control,
                           'instrument_index': np.repeat(fileIndex, nobsPSAL)})

        variableMainDF = pd.concat([variableMainDF, DF], ignore_index=True, sort=False)

        variableAuxDF = variableAuxDF.append({'source_file': filePSAL + "," + fileTEMP,
                                              'instrument_id': nc1.instrument_id.values[key],
                                              'LONGITUDE': nc1.LONGITUDE.values[key],
                                              'LATITUDE': nc1.LATITUDE.values[key],
                                              'NOMINAL_DEPTH': nc1.NOMINAL_DEPTH.values[key]}, ignore_index=True)
        fileIndex += 1

    ## rename indices
    variableAuxDF.index.rename('INSTRUMENT', inplace=True)
    variableMainDF.index.rename('OBSERVATION', inplace=True)

    ## build the output file
    agg_dataset = xr.Dataset(
        {'TIME': (['OBSERVATION'], variableMainDF['TIME'], ncPSAL.TIME.attrs),
         'TEMP': (['OBSERVATION'], variableMainDF['TEMP'].astype('float32'), ncTEMP.TEMP.attrs),
         'TEMP_quality_control': (
         ['OBSERVATION'], variableMainDF['TEMP_quality_control'].astype(np.byte), ncTEMP.TEMP_quality_control.attrs),
         'PSAL': (['OBSERVATION'], variableMainDF['PSAL'].astype('float32'), ncPSAL.PSAL.attrs),
         'PSAL_quality_control': (
         ['OBSERVATION'], variableMainDF['TEMP_quality_control'].astype(np.byte), ncPSAL.PSAL_quality_control.attrs),
         'DEPTH': (['OBSERVATION'], variableMainDF['DEPTH'].astype('float32'), ncPSAL.DEPTH.attrs),
         'DEPTH_quality_control': (
         ['OBSERVATION'], variableMainDF['DEPTH_quality_control'].astype(np.byte), ncPSAL.DEPTH_quality_control.attrs),
         'PRES': (['OBSERVATION'], variableMainDF['PRES'].astype('float32'), ncPSAL.PRES.attrs),
         'PRES_quality_control': (
         ['OBSERVATION'], variableMainDF['PRES_quality_control'].astype(np.byte), ncPSAL.PRES_quality_control.attrs),
         'PRES_REL': (['OBSERVATION'], variableMainDF['PRES_REL'].astype('float32'), ncPSAL.PRES_REL.attrs),
         'PRES_REL_quality_control': (['OBSERVATION'], variableMainDF['PRES_REL_quality_control'].astype(np.byte),
                                      ncPSAL.PRES_REL_quality_control.attrs),
         'instrument_index': (
         ['OBSERVATION'], variableMainDF['instrument_index'].astype('int64'), ncPSAL.instrument_index.attrs),
         'LONGITUDE': (['INSTRUMENT'], variableAuxDF['LONGITUDE'].astype('float32'), ncPSAL.LONGITUDE.attrs),
         'LATITUDE': (['INSTRUMENT'], variableAuxDF['LATITUDE'].astype('float32'), ncPSAL.LATITUDE.attrs),
         'NOMINAL_DEPTH': (
         ['INSTRUMENT'], variableAuxDF['NOMINAL_DEPTH'].astype('float32'), ncPSAL.NOMINAL_DEPTH.attrs),
         'instrument_id': (['INSTRUMENT'], variableAuxDF['instrument_id'].astype('|S256'), ncPSAL.instrument_id.attrs),
         'source_file': (['INSTRUMENT'], variableAuxDF['source_file'].astype('|S256'), ncPSAL.source_file.attrs)})

    ## Set global attrs
    var_to_agg = 'TS'
    globalattr_file = 'PSALTEMP_metadata.json'
    add_attribute = {}
    agg_dataset.attrs = set_globalattr(agg_dataset, globalattr_file, var_to_agg, site_code, add_attribute)

    ## create the output file name and write the aggregated product as netCDF
    facility_code = get_facility_code(filePSAL)
    data_code = 'TSZ'
    product_type = 'aggregated-time-series'
    file_version = 1
    ncout_filename = generate_netcdf_output_filename(nc=agg_dataset, facility_code=facility_code, data_code=data_code,
                                                     VoI=var_to_agg, site_code=site_code, product_type=product_type,
                                                     file_version=file_version)

    encoding = {'TIME': {'_FillValue': False,
                         'units': 'days since 1950-01-01 00:00:00 UTC',
                         'calendar': 'gregorian'},
                'LONGITUDE': {'_FillValue': False},
                'LATITUDE': {'_FillValue': False},
                'instrument_id': {'dtype': '|S256'},
                'source_file': {'dtype': '|S256'}}

    write_netCDF_aggfile(agg_dataset, ncout_filename, encoding, base_path='./')

    return ncout_filename


if __name__ == "__main__":
    site_code = 'PIL050'
    print(TS_combine(site_code))
