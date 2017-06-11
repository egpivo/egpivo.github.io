---
title: "How to work on sea surface temperature (SST) data"
date: "2017-06-03"
layout: post
output:
  html_document
tags: [R, Spatial]
---


In this post, I will show you step-by-step instructions to  work on SST data in R.

## Install the necessary tools for NetCDF

Before importing NetCDF files in R, we should install the necessary tools. Mac user require Xcode Command Line Tools, and can use [MacPorts](https://www.macports.org) to finish the installation of NetCDF by typing the following lines into terminal.

```
sudo port install netcdf
sudo port install nco
sudo port install ncview
```
More details can be found [here](http://mazamascience.com/WorkingWithData/?p=1474); by the way, Ubuntu users can be referred to [here](https://stackoverflow.com/questions/11319698/how-to-install-r-packages-rnetcdf-and-ncdf-on-ubuntu).



## Download an SST dataset

For convenience' sake, we download a lower resolution dataset, [Kaplan Extended SST data](ftp://ftp.cdc.noaa.gov/Datasets/kaplan_sst/sst.mon.anom.nc) from [ESRL PSD](https://www.esrl.noaa.gov/psd/data/gridded/data.kaplan_sst.html) on 5 degree latitude by 5 degree longitude ($5^{\circ} \times 5^{\circ}$) equiangular grid cells.


~~~r
# set a url of the Kaplan SST data
url <- 'ftp://ftp.cdc.noaa.gov/Datasets/kaplan_sst/sst.mon.anom.nc'
# create a name for temporary files in the working directory
file <- tempfile(tmpdir = getwd()) 
# creates a file with the given name
file.create(file)
~~~

~~~
## [1] TRUE
~~~

~~~r
#download the file
download.file(url, file)
~~~


## Import the NetCDF file

Before importing the file, we install an R package, [```ncdf4```](https://cran.r-project.org/web/packages/ncdf4/ncdf4.pdf), for the interface of NetCDF.


~~~r
install.packages("ncdf4")
~~~
Then, we can extract the SST anomalies and their corresponding coordinates from the file.


~~~r
library(ncdf4)
# open an NetCDF file
ex.nc <- nc_open(file)
# set coordinate variable: latitude
y <- ncvar_get(ex.nc, "lat")
# set coordinate variable: longitude
x <- ncvar_get(ex.nc, "lon")  
# extract SST anomalies
df <- ncvar_get(ex.nc, ex.nc$var[[1]])
# close an NetCDF file
nc_close(ex.nc)
# delete the file
file.remove(file)  
~~~

~~~
## [1] TRUE
~~~
Note that we can type ```print(ex.nc)``` to gain more information.


## Example: Indian Ocean SST
The following example is inspired by [Deser et al.(2009)](http://www.cgd.ucar.edu/staff/cdeser/docs/deser.sstvariability.annrevmarsci10.pdf). The region of Indian ocean is set between latitudes $20^{\circ}$N and $20^{\circ}$S between longitudes $40^{\circ}$E and $120^{\circ}$E. 


~~~r
# set the region of Indian Ocean
lat_ind <- y[which(y == -17.5):which(y == 17.5)]
lon_ind <- x[which(x == 42.5):which(x == 117.5)]

# print the total number of grids
print(length(lat_ind)*length(lon_ind))
~~~

~~~
## [1] 128
~~~

~~~r
# extract the Indian Ocean SST anomalies
sst_ind <- df[which(x == 42.5):which(x == 117.5), 
              which(y == -17.5):which(y == 17.5),]

# define which location is ocean (s2: Not NA) or land (s1: NA)
s1 <- which(is.na(sst_ind[,,1]))
s2 <- which(!is.na(sst_ind[,,1]))

# print the number of grids on the land
print(length(s1))
~~~

~~~
## [1] 4
~~~

~~~r
# print the dimension of sst_ind
print(dim(sst_ind))
~~~

~~~
## [1]   16    8 1937
~~~

Out of 8 × 16 = 128 grid cells, there are 4 cells on the land where no data are available. The time period are from January 1856 to April 2017. Here the data we use observed at $124$ grids and 1936 time points.

### Vectorize the SST anomalies 

We reshape the data as a $1936 \times 124$ matrix by vectorizing the anomalies corresponding to each time.


~~~r
sst <- matrix(0, nrow = dim(sst_ind)[3], ncol = length(s2))

for(i in 1:dim(sst_ind)[3])
  sst[i,] <- sst_ind[,,i][-s1]
~~~

### Detect the dominant patterns

For simplicity, we assume the time effect is ignorable. We use the [empirical orthogonal functions](https://en.wikipedia.org/wiki/Empirical_orthogonal_functions) (EOF) to represent the dominant patterns.


~~~r
# Extract the EOFs of data
eof <- svd(sst)$v

# require an R package, fields
if (!require("fields")) {
  install.packages("fields")
  library(fields)
}

# require an R package, RColorBrewer
if (!require("RColorBrewer")) {
  install.packages("RColorBrewer")
  library(RColorBrewer)
}

# Define the location in ocean
loc <- as.matrix(expand.grid(x = lon_ind, y = lat_ind))[s2,]
coltab <- colorRampPalette(brewer.pal(9,"BrBG"))(2048)
~~~

~~~r
# plot the first EOF
par(mar = c(5,5,3,3), oma=c(1,1,1,1))
quilt.plot(loc, eof[,1], nx = length(lon_ind), 
           ny = length(lat_ind), xlab = "longitude",
           ylab = "latitude", 
           main = "1st EOF", col = coltab,
           cex.lab = 3, cex.axis = 3, cex.main = 3,
           legend.cex = 20)
maps::map(database = "world", fill = TRUE, col = "gray", 
          ylim=c(-19.5, 19.5), xlim = c(39.5,119.5), add = T)
~~~

<img src="{{ site.url }}/assets/how_to_work_on_sst_data/eof1-1..svg" title="plot of chunk eof1" alt="plot of chunk eof1" height="300" width="500" style="display: block; margin: auto;" />

~~~r
# plot the second EOF
par(mar = c(5,5,3,3), oma=c(1,1,1,1))
quilt.plot(loc, eof[,2], nx = length(lon_ind), 
           ny = length(lat_ind), xlab = "longitude",
           ylab = "latitude", 
           main = "2nd EOF", col = coltab,
           cex.lab = 3, cex.axis = 3, cex.main = 3,
           legend.cex = 20)
maps::map(database = "world", fill = TRUE, col = "gray", 
          ylim=c(-19.5, 19.5), xlim = c(39.5,119.5), add = T)
~~~

<img src="{{ site.url }}/assets/how_to_work_on_sst_data/eof2-1..svg" title="plot of chunk eof2" alt="plot of chunk eof2" height="300" width="500" style="display: block; margin: auto;" />

The first EOF is known as a basin-wide mode, and the second one is a dipole mode. 


## References
* Deser et al. (2009), [Sea Surface Temperature Variability: Patterns and Mechanisms](http://www.cgd.ucar.edu/staff/cdeser/docs/deser.sstvariability.annrevmarsci10.pdf).

## R Session


~~~
## Session info --------------------------------------------------------------
~~~

~~~
##  setting  value                                             
##  version  R Under development (unstable) (2017-03-16 r72359)
##  system   x86_64, darwin13.4.0                              
##  ui       RStudio (1.0.136)                                 
##  language (EN)                                              
##  collate  zh_TW.UTF-8                                       
##  tz       Asia/Taipei                                       
##  date     2017-06-10
~~~

~~~
## Packages ------------------------------------------------------------------
~~~

~~~
##  package         * version    date       source                         
##  argparse        * 1.0.4      2016-10-28 CRAN (R 3.4.0)                 
##  assertthat        0.1        2013-12-06 CRAN (R 3.4.0)                 
##  backports         1.0.5      2017-01-18 CRAN (R 3.4.0)                 
##  colorspace        1.3-2      2016-12-14 CRAN (R 3.4.0)                 
##  cowplot         * 0.7.0      2016-10-28 CRAN (R 3.4.0)                 
##  devtools          1.12.0     2016-12-05 CRAN (R 3.4.0)                 
##  digest            0.6.12     2017-01-27 CRAN (R 3.4.0)                 
##  evaluate          0.10       2016-10-11 CRAN (R 3.4.0)                 
##  fields          * 8.10       2016-12-16 CRAN (R 3.4.0)                 
##  findpython        1.0.2      2017-03-15 CRAN (R 3.4.0)                 
##  gdtools         * 0.1.4      2017-03-17 CRAN (R 3.4.0)                 
##  getopt            1.20.0     2013-08-30 CRAN (R 3.4.0)                 
##  ggplot2         * 2.2.1.9000 2017-05-18 Github (hadley/ggplot2@f4398b6)
##  gtable            0.2.0      2016-02-26 CRAN (R 3.4.0)                 
##  highr             0.6        2016-05-09 CRAN (R 3.4.0)                 
##  htmltools         0.3.5      2016-03-21 CRAN (R 3.4.0)                 
##  htmlwidgets       0.8        2016-11-09 CRAN (R 3.4.0)                 
##  jsonlite          1.3        2017-02-28 CRAN (R 3.4.0)                 
##  knitr           * 1.15.20    2017-05-08 Github (yihui/knitr@f3a490b)   
##  lazyeval          0.2.0      2016-06-12 CRAN (R 3.4.0)                 
##  magrittr          1.5        2014-11-22 CRAN (R 3.4.0)                 
##  maps            * 3.1.1      2016-07-27 CRAN (R 3.4.0)                 
##  memoise           1.0.0      2016-01-29 CRAN (R 3.4.0)                 
##  munsell           0.4.3      2016-02-13 CRAN (R 3.4.0)                 
##  ncdf4           * 1.16       2017-04-01 CRAN (R 3.4.0)                 
##  plyr              1.8.4      2016-06-08 CRAN (R 3.4.0)                 
##  proto           * 1.0.0      2016-10-29 CRAN (R 3.4.0)                 
##  RColorBrewer    * 1.1-2      2014-12-07 CRAN (R 3.4.0)                 
##  Rcpp              0.12.10    2017-03-19 CRAN (R 3.4.0)                 
##  rebus           * 0.1-3      2017-04-25 CRAN (R 3.4.0)                 
##  rebus.base        0.0-3      2017-04-25 CRAN (R 3.4.0)                 
##  rebus.datetimes   0.0-1      2015-12-16 CRAN (R 3.4.0)                 
##  rebus.numbers     0.0-1      2015-12-16 CRAN (R 3.4.0)                 
##  rebus.unicode     0.0-2      2017-01-03 CRAN (R 3.4.0)                 
##  rjson             0.2.15     2014-11-03 CRAN (R 3.4.0)                 
##  rmarkdown         1.4        2017-03-24 CRAN (R 3.4.0)                 
##  rprojroot         1.2        2017-01-16 CRAN (R 3.4.0)                 
##  rstudioapi        0.6        2016-06-27 CRAN (R 3.4.0)                 
##  scales            0.4.1      2016-11-09 CRAN (R 3.4.0)                 
##  spam            * 1.4-0      2016-08-30 CRAN (R 3.4.0)                 
##  stringi         * 1.1.3      2017-03-21 CRAN (R 3.4.0)                 
##  stringr         * 1.2.0      2017-02-18 CRAN (R 3.4.0)                 
##  svglite         * 1.2.0      2016-11-04 CRAN (R 3.4.0)                 
##  tibble            1.2        2016-08-26 CRAN (R 3.4.0)                 
##  webshot           0.4.0      2016-12-27 CRAN (R 3.4.0)                 
##  withr             1.0.2      2016-06-20 CRAN (R 3.4.0)                 
##  yaml              2.1.14     2016-11-12 CRAN (R 3.4.0)
~~~
