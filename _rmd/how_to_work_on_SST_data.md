---
title: "How to work on sea surface temperature (SST) data"
date: "2021-01-20"
layout: post
output:
  html_document
tags: [R, Statistics, Spatial Statistics]
---


{% highlight text %}
## Error in library("cowplot"): there is no package called 'cowplot'
{% endhighlight %}



{% highlight text %}
## Error in library("svglite"): there is no package called 'svglite'
{% endhighlight %}



{% highlight text %}
## Error in theme_set(theme_grey()): could not find function "theme_set"
{% endhighlight %}
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


{% highlight r %}
# set a url of the Kaplan SST data
url <- 'ftp://ftp.cdc.noaa.gov/Datasets/kaplan_sst/sst.mon.anom.nc'
# create a name for temporary files in the working directory
file <- tempfile(tmpdir = getwd()) 
# creates a file with the given name
file.create(file)
{% endhighlight %}



{% highlight text %}
## [1] TRUE
{% endhighlight %}



{% highlight r %}
#download the file
download.file(url, file)
{% endhighlight %}


## Import the NetCDF file

Before importing the file, we install an R package, [```ncdf4```](https://cran.r-project.org/web/packages/ncdf4/ncdf4.pdf), for the interface of NetCDF.


{% highlight r %}
install.packages("ncdf4")
{% endhighlight %}
Then, we can extract the SST anomalies and their corresponding coordinates from the file.


{% highlight r %}
library(ncdf4)
{% endhighlight %}



{% highlight text %}
## Error in library(ncdf4): there is no package called 'ncdf4'
{% endhighlight %}



{% highlight r %}
# open an NetCDF file
ex.nc <- nc_open(file)
{% endhighlight %}



{% highlight text %}
## Error in nc_open(file): could not find function "nc_open"
{% endhighlight %}



{% highlight r %}
# set coordinate variable: latitude
y <- ncvar_get(ex.nc, "lat")
{% endhighlight %}



{% highlight text %}
## Error in ncvar_get(ex.nc, "lat"): could not find function "ncvar_get"
{% endhighlight %}



{% highlight r %}
# set coordinate variable: longitude
x <- ncvar_get(ex.nc, "lon")  
{% endhighlight %}



{% highlight text %}
## Error in ncvar_get(ex.nc, "lon"): could not find function "ncvar_get"
{% endhighlight %}



{% highlight r %}
# extract SST anomalies
df <- ncvar_get(ex.nc, ex.nc$var[[1]])
{% endhighlight %}



{% highlight text %}
## Error in ncvar_get(ex.nc, ex.nc$var[[1]]): could not find function "ncvar_get"
{% endhighlight %}



{% highlight r %}
# close an NetCDF file
nc_close(ex.nc)
{% endhighlight %}



{% highlight text %}
## Error in nc_close(ex.nc): could not find function "nc_close"
{% endhighlight %}



{% highlight r %}
# delete the file
file.remove(file)  
{% endhighlight %}



{% highlight text %}
## [1] TRUE
{% endhighlight %}
Note that we can type ```print(ex.nc)``` to gain more information.


## Example: Indian Ocean SST
The following example is inspired by [Deser et al.(2009)](http://www.cgd.ucar.edu/staff/cdeser/docs/deser.sstvariability.annrevmarsci10.pdf). The region of Indian ocean is set between latitudes $20^{\circ}$N and $20^{\circ}$S between longitudes $40^{\circ}$E and $120^{\circ}$E. 


{% highlight r %}
# set the region of Indian Ocean
lat_ind <- y[which(y == -17.5):which(y == 17.5)]
{% endhighlight %}



{% highlight text %}
## Error in eval(expr, envir, enclos): object 'y' not found
{% endhighlight %}



{% highlight r %}
lon_ind <- x[which(x == 42.5):which(x == 117.5)]
{% endhighlight %}



{% highlight text %}
## Error in eval(expr, envir, enclos): object 'x' not found
{% endhighlight %}



{% highlight r %}
# print the total number of grids
print(length(lat_ind)*length(lon_ind))
{% endhighlight %}



{% highlight text %}
## Error in print(length(lat_ind) * length(lon_ind)): object 'lat_ind' not found
{% endhighlight %}



{% highlight r %}
# extract the Indian Ocean SST anomalies
sst_ind <- df[which(x == 42.5):which(x == 117.5), 
              which(y == -17.5):which(y == 17.5),]
{% endhighlight %}



{% highlight text %}
## Error in which(x == 42.5): object 'x' not found
{% endhighlight %}



{% highlight r %}
# define which location is ocean (s2: Not NA) or land (s1: NA)
s1 <- which(is.na(sst_ind[,,1]))
{% endhighlight %}



{% highlight text %}
## Error in which(is.na(sst_ind[, , 1])): object 'sst_ind' not found
{% endhighlight %}



{% highlight r %}
s2 <- which(!is.na(sst_ind[,,1]))
{% endhighlight %}



{% highlight text %}
## Error in which(!is.na(sst_ind[, , 1])): object 'sst_ind' not found
{% endhighlight %}



{% highlight r %}
# print the number of grids on the land
print(length(s1))
{% endhighlight %}



{% highlight text %}
## Error in print(length(s1)): object 's1' not found
{% endhighlight %}



{% highlight r %}
# print the dimension of sst_ind
print(dim(sst_ind))
{% endhighlight %}



{% highlight text %}
## Error in print(dim(sst_ind)): object 'sst_ind' not found
{% endhighlight %}

Out of 8 × 16 = 128 grid cells, there are 4 cells on the land where no data are available. The time period are from January 1856 to April 2017. Here the data we use observed at $124$ grids and 1936 time points.

### Vectorize the SST anomalies 

We reshape the data as a $1936 \times 124$ matrix by vectorizing the anomalies corresponding to each time.


{% highlight r %}
sst <- matrix(0, nrow = dim(sst_ind)[3], ncol = length(s2))
{% endhighlight %}



{% highlight text %}
## Error in matrix(0, nrow = dim(sst_ind)[3], ncol = length(s2)): object 'sst_ind' not found
{% endhighlight %}



{% highlight r %}
for(i in 1:dim(sst_ind)[3])
  sst[i,] <- sst_ind[,,i][-s1]
{% endhighlight %}



{% highlight text %}
## Error in eval(expr, envir, enclos): object 'sst_ind' not found
{% endhighlight %}

### Detect the dominant patterns

For simplicity, we assume the time effect is ignorable. We use the [empirical orthogonal functions](https://en.wikipedia.org/wiki/Empirical_orthogonal_functions) (EOF) to represent the dominant patterns.


{% highlight r %}
# Extract the EOFs of data
eof <- svd(sst)$v
{% endhighlight %}



{% highlight text %}
## Error in as.matrix(x): object 'sst' not found
{% endhighlight %}



{% highlight r %}
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
{% endhighlight %}



{% highlight text %}
## Error in expand.grid(x = lon_ind, y = lat_ind): object 'lon_ind' not found
{% endhighlight %}



{% highlight r %}
coltab <- colorRampPalette(brewer.pal(9,"BrBG"))(2048)
{% endhighlight %}

{% highlight r %}
# plot the first EOF
par(mar = c(5,5,3,3), oma=c(1,1,1,1))
quilt.plot(loc, eof[,1], nx = length(lon_ind), 
           ny = length(lat_ind), xlab = "longitude",
           ylab = "latitude", 
           main = "1st EOF", col = coltab,
           cex.lab = 3, cex.axis = 3, cex.main = 3,
           legend.cex = 20)
{% endhighlight %}



{% highlight text %}
## Error in as.matrix(x): object 'loc' not found
{% endhighlight %}



{% highlight r %}
maps::map(database = "world", fill = TRUE, col = "gray", 
          ylim=c(-19.5, 19.5), xlim = c(39.5,119.5), add = T)
{% endhighlight %}



{% highlight text %}
## Error in polygon(coord, col = col, ...): plot.new has not been called yet
{% endhighlight %}

{% highlight r %}
# plot the second EOF
par(mar = c(5,5,3,3), oma=c(1,1,1,1))
quilt.plot(loc, eof[,2], nx = length(lon_ind), 
           ny = length(lat_ind), xlab = "longitude",
           ylab = "latitude", 
           main = "2nd EOF", col = coltab,
           cex.lab = 3, cex.axis = 3, cex.main = 3,
           legend.cex = 20)
{% endhighlight %}



{% highlight text %}
## Error in as.matrix(x): object 'loc' not found
{% endhighlight %}



{% highlight r %}
maps::map(database = "world", fill = TRUE, col = "gray", 
          ylim=c(-19.5, 19.5), xlim = c(39.5,119.5), add = T)
{% endhighlight %}



{% highlight text %}
## Error in polygon(coord, col = col, ...): plot.new has not been called yet
{% endhighlight %}

The first EOF is known as a basin-wide mode, and the second one is a dipole mode. 


## References
* Deser et al. (2009), [Sea Surface Temperature Variability: Patterns and Mechanisms](http://www.cgd.ucar.edu/staff/cdeser/docs/deser.sstvariability.annrevmarsci10.pdf).

## R Session


{% highlight text %}
## ─ Session info ───────────────────────────────────────────────────────────────
##  setting  value                                             
##  version  R Under development (unstable) (2019-12-29 r77627)
##  os       macOS High Sierra 10.13.6                         
##  system   x86_64, darwin15.6.0                              
##  ui       X11                                               
##  language (EN)                                              
##  collate  en_US.UTF-8                                       
##  ctype    en_US.UTF-8                                       
##  tz       Asia/Taipei                                       
##  date     2021-01-20                                        
## 
## ─ Packages ───────────────────────────────────────────────────────────────────
##  package      * version date       lib source        
##  assertthat     0.2.1   2019-03-21 [1] CRAN (R 4.0.0)
##  blogdown       0.21    2020-10-11 [1] CRAN (R 4.0.0)
##  callr          3.5.1   2020-10-13 [1] CRAN (R 4.0.0)
##  cli            2.2.0   2020-11-20 [1] CRAN (R 4.0.0)
##  crayon         1.3.4   2017-09-16 [1] CRAN (R 4.0.0)
##  desc           1.2.0   2018-05-01 [1] CRAN (R 4.0.0)
##  devtools       2.3.2   2020-09-18 [1] CRAN (R 4.0.0)
##  digest         0.6.27  2020-10-24 [1] CRAN (R 4.0.0)
##  dotCall64    * 1.0-0   2018-07-30 [1] CRAN (R 4.0.0)
##  ellipsis       0.3.1   2020-05-15 [1] CRAN (R 4.0.0)
##  evaluate       0.14    2019-05-28 [1] CRAN (R 4.0.0)
##  fansi          0.4.1   2020-01-08 [1] CRAN (R 4.0.0)
##  fields       * 11.6    2020-10-09 [1] CRAN (R 4.0.0)
##  fs             1.5.0   2020-07-31 [1] CRAN (R 4.0.0)
##  glue           1.4.2   2020-08-27 [1] CRAN (R 4.0.0)
##  knitr        * 1.30    2020-09-22 [1] CRAN (R 4.0.0)
##  magrittr       1.5     2014-11-22 [1] CRAN (R 4.0.0)
##  maps           3.3.0   2018-04-03 [1] CRAN (R 4.0.0)
##  memoise        1.1.0   2017-04-21 [1] CRAN (R 4.0.0)
##  pkgbuild       1.1.0   2020-07-13 [1] CRAN (R 4.0.0)
##  pkgload        1.1.0   2020-05-29 [1] CRAN (R 4.0.0)
##  prettyunits    1.1.1   2020-01-24 [1] CRAN (R 4.0.0)
##  processx       3.4.4   2020-09-03 [1] CRAN (R 4.0.0)
##  ps             1.4.0   2020-10-07 [1] CRAN (R 4.0.0)
##  R6             2.5.0   2020-10-28 [1] CRAN (R 4.0.0)
##  RColorBrewer * 1.1-2   2014-12-07 [1] CRAN (R 4.0.0)
##  remotes        2.2.0   2020-07-21 [1] CRAN (R 4.0.0)
##  rlang          0.4.9   2020-11-26 [1] CRAN (R 4.0.0)
##  rprojroot      2.0.2   2020-11-15 [1] CRAN (R 4.0.0)
##  sessioninfo    1.1.1   2018-11-05 [1] CRAN (R 4.0.0)
##  spam         * 2.5-1   2019-12-12 [1] CRAN (R 4.0.0)
##  stringi        1.5.3   2020-09-09 [1] CRAN (R 4.0.0)
##  stringr        1.4.0   2019-02-10 [1] CRAN (R 4.0.0)
##  testthat       3.0.1   2020-12-17 [1] CRAN (R 4.0.0)
##  usethis        1.6.3   2020-09-17 [1] CRAN (R 4.0.0)
##  withr          2.3.0   2020-09-22 [1] CRAN (R 4.0.0)
##  xfun           0.19    2020-10-30 [1] CRAN (R 4.0.0)
##  yaml           2.2.1   2020-02-01 [1] CRAN (R 4.0.0)
## 
## [1] /Library/Frameworks/R.framework/Versions/4.0/Resources/library
{% endhighlight %}
