---
title: "Challenges in EOF Patterns with a Single Variable"
date: "2017-06-26"
layout: post
output:
  html_document
tags: [Statistics, Spatial Statistics]
use_math : true
---

In this post, we delve into potential challenges associated with Empirical Orthogonal Function (EOF) patterns.

### Issues with EOF Patterns

In our previous discussions, we explored how dominant spatial patterns, known as EOF patterns, can be extracted using Principal Component Analysis (PCA). However, two significant problems arise in this context. The first challenge pertains to high estimation variability. When the sample size (n) is small or the number of locations is high, EOF patterns can become excessively rough, making interpretation challenging.

Additionally, it is reasonable to assume that EOF patterns exhibit smoothness, given that the correlation between closer locations is lower. However, PCA-derived patterns often fail to capture this spatial structure. Thus, the second problem lies in the insufficient consideration of any inherent spatial characteristics in PCA-generated EOF patterns.

As an illustration, consider a randomly generated sample based on the true pattern depicted in the left panel of the following plot. The first EOF derived through PCA is shown in the right panel, appearing too noisy to identify the major signal. In reality, the true pattern is crystal clear, showcasing a localized pattern.

<div style="text-align:center;">
  <img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/true.png"   width="40%" height="40%">
  <img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/pca.png"  width="40%" height="40%">
</div>
<div style="text-align:center;">
<img src="{{ site.url }}/assets/problems_eof_patterns_with_a_single_variable/bar.png"   width="40%" height="40%">
</div>


### Summary
This post briefly highlights challenges associated with Empirical Orthogonal Function (EOF) patterns, particularly in the context of Principal Component Analysis (PCA). It addresses issues such as high estimation variability and the failure of PCA-derived EOF patterns to consider inherent spatial structures. Illustrated with examples, the article emphasizes the importance of addressing these challenges for accurate interpretation of dominant spatial patterns.

### References

* Wang and Huang, (2017). [Regularized Principal Component Analysis for Spatial Data](http://www.tandfonline.com/doi/full/10.1080/10618600.2016.1157483").


