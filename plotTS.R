## plot aggregated TEMP PSAL from a single file
library(ncdf4)
library(ggplot2)
library(cowplot)
library(dplyr)

fname = "IMOS_ANMN-QLD_TSZ_20120221_PIL050_FV01_TS-aggregated-time-series_20140727_C-20190830.nc"
nc = nc_open(fname)

## look what variables we have
names(nc$var)

## build the dataframe
DFdata = data.frame(instrument = ncvar_get(nc, "instrument_index"),
                time = ncvar_get(nc, "TIME"),
                depth = ncvar_get(nc, "DEPTH"), 
                TEMP = ncvar_get(nc, "TEMP"), 
                TEMPqc = ncvar_get(nc, "TEMP_quality_control"),
                PSAL = ncvar_get(nc, "PSAL"), 
                PSALqc = ncvar_get(nc, "PSAL_quality_control"))
## convert to date object
DFdata$time = as.POSIXct(DFdata$time*60*60*24, origin="1950-01-01T00:00:00+00:00")

## select only good quality data (i.e. qcflag <=2)
DFdata = DFdata %>% filter(TEMPqc<=2, PSALqc<=2)

## plot TEMP and PSAL
pp1 = ggplot(DFdata, aes(time, TEMP))
pp1 = pp1 + geom_point(size=0.5, aes(colour=factor(instrument))) + 
  theme(legend.position = "none")
pp1

pp2 = ggplot(DFdata, aes(time, PSAL))
pp2 = pp2 + geom_point(size=0.5, aes(colour=factor(instrument)))+ 
  theme(legend.position = "none")
pp2

plot_grid(pp1, pp2, ncol = 1, nrow = 2, labels="AUTO")

## uncommnet to save the plot
# ggsave("TEMP.png", pp1)
# ggsave("PSAL.png", pp2)

## plot TEMP vs PSAL
pp3 = ggplot(DFdata, aes(TEMP, PSAL))
pp3 = pp3 + geom_point(size=0.5, aes(colour=factor(instrument)))+ 
  theme(legend.position = "none")
pp3
## uncommnet to save the plot
# ggsave("TS.png", pp3)


