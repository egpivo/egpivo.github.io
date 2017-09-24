---
title: "Problems: EOF patterns with a single variable"
date: "2017-06-26"
layout: post
output:
  html_document
tags: [Statistics, Spatial Statistics]
use_math : true
---



In this post, we talk about possible problems of EOF patterns.

## Problems about EOF patterns

As our previous post, we're aware that diminant spatial patterns, a.k.a. EOF patterns, can be found by principal component analysis (PCA). However, there are two major problems. The first one is about high estimation variability. 
When sample size n is smaller or the number of locations is higher, the EOF pattens are often too rough to interpret.

Besides, it is sound to assume that EOF patterns are smooth function since the correlation between two closer locations is lower. However, the patterns by PCA do not take care of it. That is, the second problem is that EOF patterns by PCA are not considered any spatial structure. 

For example, we randomly generate a sample based on the true pattern in the left panel of the below plot. The first EOF by PCA is in the right panel below, and is too noisy to identify the major signal, but, in fact, the true pattern in the left panel is crystal clear, a localied pattern.

<center>
  <img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/true.png"   width="40%" height="40%">
  <img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/pca.png"  width="40%" height="40%">
</center>
<center>
<img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/bar.png"   width="40%" height="40%">
</center>


## References

* Wang and Huang, (2017). [Regularized Principal Component Analysis for Spatial Data](http://www.tandfonline.com/doi/full/10.1080/10618600.2016.1157483").


