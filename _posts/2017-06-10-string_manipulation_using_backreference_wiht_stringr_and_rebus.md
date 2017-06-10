---
title: "String manipulation: backreference with `Stringr` + `rebus`"
date: "2017-06-10"
layout: post
output:
  html_document
tags: [R]
---



In practice, `backreference` is an R function in `rebus`, which is useful for replacement operations. I will apply some functions in stringr with `backreference` to a Chinese lyric. 

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
##  [1] "風到這裡就是黏 黏住過客的思念"                        
##  [2] "雨到了這裡纏成線 纏著我們流連人世間"                  
##  [3] "妳在身邊就是緣 緣分寫在三生石上面"                    
##  [4] "愛有萬分之一甜 寧願我就葬在這一點"                    
##  [5] ""                                                     
##  [6] "圈圈圓圓圈圈 天天年年天天的我 深深看你的臉"           
##  [7] "生氣的溫柔 埋怨的溫柔的臉"                            
##  [8] ""                                                     
##  [9] "不懂愛恨情仇煎熬的我們 都以為相愛就像風雲的善變"      
## [10] "相信愛一天 抵過永遠 在這一剎那凍結了時間"             
## [11] ""                                                     
## [12] "不懂怎麼表現溫柔的我們 還以為殉情只是古老的傳言"      
## [13] "離愁能有多痛 痛有多濃 當夢被埋在江南煙雨中 心碎了才懂"
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



|x    | freq|
|:----|----:|
|年年 |    1|
|圈圈 |    2|
|深深 |    1|
|天天 |    2|
|圓圓 |    1|

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
##  [1] "風到這裡就是黏 黏住過客的思念"                        
##  [2] "雨到了這裡纏成線 纏著我們流連人世間"                  
##  [3] "妳在身邊就是緣 緣分寫在三生石上面"                    
##  [4] "♡愛♡有萬分之一甜 寧願我就葬在這一點"                  
##  [5] ""                                                     
##  [6] "圈圈圓圓圈圈 天天年年天天的我 深深看你的臉"           
##  [7] "生氣的溫柔 埋怨的溫柔的臉"                            
##  [8] ""                                                     
##  [9] "不懂♡愛♡恨情仇煎熬的我們 都以為相♡愛♡就像風雲的善變"  
## [10] "相信♡愛♡一天 抵過永遠 在這一剎那凍結了時間"           
## [11] ""                                                     
## [12] "不懂怎麼表現溫柔的我們 還以為殉情只是古老的傳言"      
## [13] "離愁能有多痛 痛有多濃 當夢被埋在江南煙雨中 心碎了才懂"
~~~

## References
* DataCamp: [String Manipulation in R with stringr](https://www.datacamp.com/courses/string-manipulation-in-r-with-stringr).
