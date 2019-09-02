# LTSP-tools
Tools for AODN Long Time Series Products

## TEMP and PSAL in the same file

From the aggregated files (one from TEMP and other for PSAL) join both paramenters using `instrument_id`
You need manually change the name of the TEMP and PSAL files and also modify the `site_code`
In the future, this will be done simply by specifying the `site_code`

**NOTE**: The code is not optimised for memory,s oit is possible that with some sites with many deployments the code fails due to lack of memory to do the join.

