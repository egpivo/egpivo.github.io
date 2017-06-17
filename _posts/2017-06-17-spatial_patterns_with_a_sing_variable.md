---
title: "Spatial patterns with a single variable"
date: "2017-06-17"
layout: post
output:
  html_document
tags: [Statistics, Spatial Statistics]
use_math : true
---



In this post, we're about to discuss dominant spatial patterns formally.

## What's spatial patterns?

In climate researches, it is common to apply dominant spatial patterns to interpret physical phenomenon and spatial variation of a climate variable, e.g., sea surface temperature. 

For example, there are two major spatial patters (mode) of sea surface temperature in the Indian Ocean. That is, a basin model (top panel) and a dipole model (bottom panel) in the following graph.

<center>
  <img src="{{ site.url }}/assets/spatial_patterns_with_a_sing_variable/spatpcak1_t.png"   width="60%" height="40%">
  <div class="caption">Basin mode</div>
  <img src="{{ site.url }}/assets/spatial_patterns_with_a_sing_variable/spatpcak2_t.png" width="60%" height="40%">
  <div class="caption">Dipole mode</div>

  <img src="{{ site.url }}/assets/spatial_patterns_with_a_sing_variable/bar.png" width="60%" height="40%">
</center>
 
 
A basin-wide mode indicates that there is a sub-region with a u-shaped hole in the pattern, and means the spatial variation in this sub-region is clearly decreasing downside (or increasing upside). An east-west dipole mode illustrates that the variation of sea surface temperature in the eastern region is opposite to the one in the wester region. In other words, while the sea surface temperature in the eastern Indian Ocean becomes higher, the temperature in the western Indian Ocean more likely becomes lower. It is worth to notice that the interaction between these two patterns and El Niño–Southern Oscillation (ENSO) is a popular topic in the climate field.  

## Formalize spatial patterns mathematically

### Spatial process of interest

Suppose that a spatial process of interest is $$\{\eta_i(\cdot); i = 1,\dots, n\}$$ which is on a region $D \subset \mathbb{R}^d$, and at $n$ different time points. For simplicity, we assume that $\eta_i$'s are mean zero, mutally uncorrelated with common covariance function.

For example, we are interested in studying sea surface temperature monthly anomalies in the Indian Ocean during Jan., 2010 to Dec. 2016, formally. Then, we can define $\eta_i(\cdot)$ as a sea surface temperature monthly anomaly, $D$ as Indian Ocean (with blue color in the following plot), $n = 12\times 7$.  
<center>
 <img src="/assets/spatial_patterns_with_a_sing_variable/process_example.png" width="60%" height="40%">
  <div class="caption">A spatial process in the Indian Ocean</div>
</center>
 
 
### Observed data

We only observe data at $p$ locations, say $s_1, \dots, s_p$. The observed data are defined as
$$
  Y_i(s_j) = \eta_i(s_j) + \epsilon_{ij},
$$
where $\epsilon_{ij}$ is supposed to be a white noise with mean zero and covariance $\sigma^2$ for $i =1,\dots,n$, $j = 1, \dots,p$.

The graph below indicates that the observation at some cell, where the size of cells depends on the resolution of measurement. By the way, the gray color represent the land, and the observation here is usually define as $NA$ in datasets.
<center>
 <img src="{{ site.url }}/assets/spatial_patterns_with_a_sing_variable/data_example.png" width="60%" height="40%">
  <div class="caption">Observed Data in the Indian Ocean</div>
</center>

We can rewrite our data as a matrix form. Namely, $\textbf{Y} = (\textbf{Y}_1, \dots, \textbf{Y}_n)'$ is an $n\times p$ matrix where, at each time point, we vectorize our observations over $p$ locations as $\textbf{Y}_i = (Y_i(s_1), \dots,Y_i(s_p))'$, $i = 1, \dots n$.


