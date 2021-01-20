---
title: "String manipulation using backreference wiht `Stringr` + `rebus`"
date: "2021-01-20"
layout: post
output:
  html_document
tags: [R]
---



In practice, `backreference` is an R function in `rebus`, which is useful for replacement operations. I will apply some functions in stringr with `backreference` by a Chinese lyric. 

## Example: Chinese Lyric

### Import a lyric

We can use the function `readLines` in `base`, but we have a better choice. That is, `stri_read_lines` in `stringi`, which is faster and
more stable.


{% highlight r %}
library(stringi)
lyrics <- stri_read_lines("/Users/wen-tingwang/egpivo/_rmd/lyrics")
{% endhighlight %}



{% highlight text %}
## Warning in file(con, "rb"): cannot open file '/Users/wen-tingwang/egpivo/_rmd/
## lyrics': No such file or directory
{% endhighlight %}



{% highlight text %}
## Error in file(con, "rb"): cannot open the connection
{% endhighlight %}



{% highlight r %}
print(lyrics)
{% endhighlight %}



{% highlight text %}
## Error in print(lyrics): object 'lyrics' not found
{% endhighlight %}


### View the Match patterns with repeated characters.

We want to see which character repeated twice in the lyric. We will view which line is matched.


{% highlight r %}
library(stringr)
library(rebus)
{% endhighlight %}



{% highlight text %}
## Error in library(rebus): there is no package called 'rebus'
{% endhighlight %}



{% highlight r %}
# Define the pattern
pattern <- capture(WRD) %R% REF1
{% endhighlight %}



{% highlight text %}
## Error in capture(WRD) %R% REF1: could not find function "%R%"
{% endhighlight %}



{% highlight r %}
#View matches of pattern
str_view_all(lyrics, pattern = pattern , match = TRUE)
{% endhighlight %}



{% highlight text %}
## Error in str_view_all(lyrics, pattern = pattern, match = TRUE): object 'lyrics' not found
{% endhighlight %}

### Extract the mathced lines
Before we extracting matched lines,  we use `str_subset` to store subset of matched lines first. 


{% highlight r %}
lines <- str_subset(lyrics, pattern = pattern)
{% endhighlight %}



{% highlight text %}
## Error in type(pattern): object 'pattern' not found
{% endhighlight %}
Then, we apply `str_extract` to extract the lines, and show the repeated characters.

{% highlight r %}
# Extract matches from lines
chr <- str_extract_all(lines, pattern = pattern)
{% endhighlight %}



{% highlight text %}
## Error in type(pattern): object 'pattern' not found
{% endhighlight %}



{% highlight r %}
# Show the frequencies of repeated characters
knitr::kable(plyr::count(chr[[1]]))
{% endhighlight %}



{% highlight text %}
## Error in plyr::count(chr[[1]]): object 'chr' not found
{% endhighlight %}

### View characters with a pair that reverses


{% highlight r %}
reverse <- capture(WRD) %R% capture(WRD) %R% REF2%R% REF1
{% endhighlight %}



{% highlight text %}
## Error in capture(WRD) %R% capture(WRD) %R% REF2 %R% REF1: could not find function "%R%"
{% endhighlight %}



{% highlight r %}
str_view_all(lyrics, pattern = reverse, match = TRUE)
{% endhighlight %}



{% highlight text %}
## Error in str_view_all(lyrics, pattern = reverse, match = TRUE): object 'lyrics' not found
{% endhighlight %}

### Replace with backreferces
#### Build a pattern to be replaced
We build a pattern that finds a chines character "愛". We first check it against `lyrics`. 

{% highlight r %}
replacePattern <- "愛"
str_view_all(lyrics, pattern = replacePattern)
{% endhighlight %}



{% highlight text %}
## Error in stri_locate_all_regex(string, pattern, omit_no_match = TRUE, : object 'lyrics' not found
{% endhighlight %}

#### Test out the replacement 
Then, we apply `str_replace_all` to replace the pattern with some words including '愛' and a unicode around it. 


{% highlight r %}
str_replace_all(lyrics, pattern = capture(replacePattern), str_c("\u2661", REF1, "\u2661", sep = ""))
{% endhighlight %}



{% highlight text %}
## Error in stri_c(..., sep = sep, collapse = collapse, ignore_null = TRUE): object 'REF1' not found
{% endhighlight %}

## References
* DataCamp: [String Manipulation in R with stringr](https://www.datacamp.com/courses/string-manipulation-in-r-with-stringr).

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
##  package     * version date       lib source        
##  assertthat    0.2.1   2019-03-21 [1] CRAN (R 4.0.0)
##  blogdown      0.21    2020-10-11 [1] CRAN (R 4.0.0)
##  callr         3.5.1   2020-10-13 [1] CRAN (R 4.0.0)
##  cli           2.2.0   2020-11-20 [1] CRAN (R 4.0.0)
##  crayon        1.3.4   2017-09-16 [1] CRAN (R 4.0.0)
##  desc          1.2.0   2018-05-01 [1] CRAN (R 4.0.0)
##  devtools      2.3.2   2020-09-18 [1] CRAN (R 4.0.0)
##  digest        0.6.27  2020-10-24 [1] CRAN (R 4.0.0)
##  ellipsis      0.3.1   2020-05-15 [1] CRAN (R 4.0.0)
##  evaluate      0.14    2019-05-28 [1] CRAN (R 4.0.0)
##  fansi         0.4.1   2020-01-08 [1] CRAN (R 4.0.0)
##  fs            1.5.0   2020-07-31 [1] CRAN (R 4.0.0)
##  glue          1.4.2   2020-08-27 [1] CRAN (R 4.0.0)
##  knitr         1.30    2020-09-22 [1] CRAN (R 4.0.0)
##  magrittr      1.5     2014-11-22 [1] CRAN (R 4.0.0)
##  memoise       1.1.0   2017-04-21 [1] CRAN (R 4.0.0)
##  pkgbuild      1.1.0   2020-07-13 [1] CRAN (R 4.0.0)
##  pkgload       1.1.0   2020-05-29 [1] CRAN (R 4.0.0)
##  plyr          1.8.6   2020-03-03 [1] CRAN (R 4.0.0)
##  prettyunits   1.1.1   2020-01-24 [1] CRAN (R 4.0.0)
##  processx      3.4.4   2020-09-03 [1] CRAN (R 4.0.0)
##  ps            1.4.0   2020-10-07 [1] CRAN (R 4.0.0)
##  R6            2.5.0   2020-10-28 [1] CRAN (R 4.0.0)
##  Rcpp          1.0.5   2020-07-06 [1] CRAN (R 4.0.0)
##  remotes       2.2.0   2020-07-21 [1] CRAN (R 4.0.0)
##  rlang         0.4.9   2020-11-26 [1] CRAN (R 4.0.0)
##  rprojroot     2.0.2   2020-11-15 [1] CRAN (R 4.0.0)
##  sessioninfo   1.1.1   2018-11-05 [1] CRAN (R 4.0.0)
##  stringi     * 1.5.3   2020-09-09 [1] CRAN (R 4.0.0)
##  stringr     * 1.4.0   2019-02-10 [1] CRAN (R 4.0.0)
##  testthat      3.0.1   2020-12-17 [1] CRAN (R 4.0.0)
##  usethis       1.6.3   2020-09-17 [1] CRAN (R 4.0.0)
##  withr         2.3.0   2020-09-22 [1] CRAN (R 4.0.0)
##  xfun          0.19    2020-10-30 [1] CRAN (R 4.0.0)
##  yaml          2.2.1   2020-02-01 [1] CRAN (R 4.0.0)
## 
## [1] /Library/Frameworks/R.framework/Versions/4.0/Resources/library
{% endhighlight %}
