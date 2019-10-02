# LTSP-tools
Tools for AODN Long Time Series Products

## Get THREDDS URL from AODN Geoserver

This tool allows you to get the file's URL using different filters. It returns a list of URL that can be redirected to a text file.

```
python geoserverCatalog.py --help
usage: geoserverCatalog.py [-h] [-var VARNAME] [-site SITE] [-ft FEATURETYPE]
                           [-fv FILEVERSION] [-ts TIMESTART] [-te TIMEEND]
                           [-dc DATACATEGORY] [-realtime REALTIME]
                           [-rm FILTEROUT [FILTEROUT ...]]

Get a list of urls from the AODN geoserver

optional arguments:
  -h, --help            show this help message and exit
  -var VARNAME          name of the variable of interest, like TEMP
  -site SITE            site code, like NRMMAI
  -ft FEATURETYPE       feature type, like timeseries
  -fv FILEVERSION       file version, like 1
  -ts TIMESTART         start time like 2015-12-01
  -te TIMEEND           end time like 2018-06-30
  -dc DATACATEGORY      data category like Temperature
  -realtime REALTIME    yes or no. If absent, all modes will be retrieved
  -rm FILTEROUT [FILTEROUT ...]
                        regex to filter out the url list. Case sensitive

```




## TEMP and PSAL in the same file

From the aggregated files (one from TEMP and other for PSAL) join both paramenters using `instrument_id`
You need to manually change the name of the TEMP and PSAL file names and also modify the `site_code` in the function call.
In the future, this will be done simply by specifying the `site_code`

**NOTE**: The code is not optimised for memory, so it is possible that with some sites with many deployments the code fails due to lack of memory to do the join.

There are two plots as an example. The R code for generating the plot are also in this repo.
