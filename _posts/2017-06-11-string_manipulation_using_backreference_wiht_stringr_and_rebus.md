---
title: "String manipulation: backreference with `stringr` + `rebus`"
date: "2017-06-11"
layout: post
output:
  html_document
tags: [R]
---



In practice, `backreference` is an R function in `rebus`, which is useful for replacement operations. I will apply some functions in `stringr` combined with `backreference` to a Chinese lyric. 

## Example: Chinese Lyric

### Download a Chinese lyric
We download the file first.

~~~r
# set a url of the lyric
url <- 'egpivo.github.io/assets/string_manipulation_using_backreference_wiht_stringr_and_rebus/lyrics'
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

### Import the lyric

We can use the function `readLines` in `base`, but we have a better choice. That is, `stri_read_lines` in `stringi`, which is faster and
more stable.


~~~r
library(stringi)
lyrics <- stri_read_lines(file)
print(lyrics)
~~~

~~~
##  [1] ""                                                                                                  
##  [2] "\t\t<script language=\"Javascript\">"                                                              
##  [3] "\t\t\twindow.location = \"https://www.wifly.com.tw/StarbucksFree/rule.aspx?DeviceKind=2&RTYPE=2\";"
##  [4] "\t\t</script>"                                                                                     
##  [5] ""                                                                                                  
##  [6] "<html>"                                                                                            
##  [7] "<head>"                                                                                            
##  [8] "<title>WIFLY</title>"                                                                              
##  [9] "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"                           
## [10] "<meta http-equiv=\"Expires\" content=\"-1\">"                                                      
## [11] "<script language=\"javascript\" src=\"/WiflyLogin/js/codec.js\" type=\"text/javascript\"></script>"
## [12] "<script type=\"text/javascript\" src=\"/WiflyLogin/js/cookie.js\"></script>"                       
## [13] "\t"                                                                                                
## [14] "</head>"                                                                                           
## [15] "<body>"                                                                                            
## [16] "\t<p align=center style=\"font-size:40px;\">"                                                      
## [17] "\t<BR>"                                                                                            
## [18] "\t</p>"                                                                                            
## [19] ""                                                                                                  
## [20] "</body>"                                                                                           
## [21] "</html>"
~~~


### View the matched patterns with repeated characters.

We want to see which character repeated twice in the lyric. We will view which line is matched by using `capture()` in `stringr` and a backreference `REF1` in `rebus` where beckreferecens can be `REF1` $\dots$ `REF9`.



~~~r
library(stringr)
library(rebus)

# Define the pattern
pattern <- capture(WRD) %R% REF1

#View matches of pattern
str_view_all(lyrics, pattern = pattern , match = TRUE)
~~~

![plot of chunk unnamed-chunk-4]({{ site.url }}/assets/string_manipulation_using_backreference_wiht_stringr_and_rebus/unnamed-chunk-4-1.png)

### Extract the matched lines
Before we extracting matched lines,  we use `str_subset` to store subset of matched lines first. 


~~~r
lines <- str_subset(lyrics, pattern = pattern)
~~~
Then, we apply `str_extract` to extract the lines, and show the repeated characters.

~~~r
# Extract matches from lines
chr <- str_extract_all(lines, pattern = pattern)
# Show the frequencies of repeated characters
knitr::kable(plyr::count(chr[[1]]))
~~~



|x  | freq|
|:--|----:|
|ee |    1|
|tt |    1|
|ww |    1|

### View characters with a pair that reverses
Here we want to detect a reversed pair by using `REF1` and `REF2`.

~~~r
reverse <- capture(WRD) %R% capture(WRD) %R% REF2 %R% REF1
str_view_all(lyrics, pattern = reverse, match = TRUE)
~~~

![plot of chunk unnamed-chunk-7]({{ site.url }}/assets/string_manipulation_using_backreference_wiht_stringr_and_rebus/unnamed-chunk-7-1.png)

### Replace with backreferces
#### Build a pattern to be replaced
We build a pattern that finds a chines character "愛". We first check it against `lyrics`. 

~~~r
replacePattern <- "愛"
str_view_all(lyrics, pattern = replacePattern)
~~~

![plot of chunk unnamed-chunk-8]({{ site.url }}/assets/string_manipulation_using_backreference_wiht_stringr_and_rebus/unnamed-chunk-8-1.png)

#### Test out the replacement 
Then, we apply `str_replace_all` to replace the pattern with some words including '愛' and a unicode, ♡, around it. 


~~~r
str_replace_all(lyrics, pattern = capture(replacePattern), str_c("\u2661", REF1, "\u2661", sep = ""))
~~~

~~~
##  [1] ""                                                                                                  
##  [2] "\t\t<script language=\"Javascript\">"                                                              
##  [3] "\t\t\twindow.location = \"https://www.wifly.com.tw/StarbucksFree/rule.aspx?DeviceKind=2&RTYPE=2\";"
##  [4] "\t\t</script>"                                                                                     
##  [5] ""                                                                                                  
##  [6] "<html>"                                                                                            
##  [7] "<head>"                                                                                            
##  [8] "<title>WIFLY</title>"                                                                              
##  [9] "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">"                           
## [10] "<meta http-equiv=\"Expires\" content=\"-1\">"                                                      
## [11] "<script language=\"javascript\" src=\"/WiflyLogin/js/codec.js\" type=\"text/javascript\"></script>"
## [12] "<script type=\"text/javascript\" src=\"/WiflyLogin/js/cookie.js\"></script>"                       
## [13] "\t"                                                                                                
## [14] "</head>"                                                                                           
## [15] "<body>"                                                                                            
## [16] "\t<p align=center style=\"font-size:40px;\">"                                                      
## [17] "\t<BR>"                                                                                            
## [18] "\t</p>"                                                                                            
## [19] ""                                                                                                  
## [20] "</body>"                                                                                           
## [21] "</html>"
~~~

## References
* DataCamp: [String Manipulation in R with stringr](https://www.datacamp.com/courses/string-manipulation-in-r-with-stringr).
