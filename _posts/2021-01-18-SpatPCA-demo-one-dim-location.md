---
layout: post
title:  "Appy SpatPCA to capture the dominant spatial pattern with one-dimensional locations"
tags: [Software, R, Statistics, Spatial Statistics]
---


We have two objectives
1. Demonstrate how **SpatPCA** captures the most dominant spatial pattern of variation based on different signal-to-noise ratios.
2. Represent how to use **SpatPCA** for one-dimensional data

### Basic settings
#### Used packages

{% highlight r %}
library(SpatPCA)
library(ggplot2)
library(dplyr)
library(tidyr)
library(gifski)
base_theme <- theme_classic(base_size = 18, base_family = "Times")
{% endhighlight %}
#### True spatial pattern (eigenfunction)
The underlying spatial pattern below indicates realizations will vary dramatically at the center and be almost unchanged at the both ends of the curve.

{% highlight r %}
set.seed(1024)
position <- matrix(seq(-5, 5, length = 100))
true_eigen_fn <- exp(-position^2) / norm(exp(-position^2), "F")

data.frame(
  position = position,
  eigenfunction = true_eigen_fn
) %>%
  ggplot(aes(position, eigenfunction)) +
  geom_line() +
  base_theme
{% endhighlight %}

![plot of chunk unnamed-chunk-3](figure/posts/2021-01-18-SpatPCA-demo-one-dim-location/unnamed-chunk-3-1.png)

### Case I: Higher signal of the true eigenfunction
#### Generate realizations 
We want to generate 100 random sample based on 
  - The spatial signal for the true spatial pattern is distributed normally with $\sigma=20$
  - The noise follows the standard normal distribution.


{% highlight r %}
realizations <- rnorm(n = 100, sd = 20) %*% t(true_eigen_fn) + matrix(rnorm(n = 100 * 100), 100, 100)
{% endhighlight %}

#### Animate realizations
We can see simulated central realizations change in a wide range more frequently than the others.

{% highlight r %}
for (i in 1:100) {
  plot(x = position, y = realizations[i, ], ylim = c(-10, 10), ylab = "realization")
}
{% endhighlight %}

![plot of chunk unnamed-chunk-5](figure/posts/2021-01-18-SpatPCA-demo-one-dim-location/unnamed-chunk-5-.gif)

#### Apply `SpatPCA::spatpca`

{% highlight r %}
cv <- spatpca(x = position, Y = realizations)
eigen_est <- cv$eigenfn
{% endhighlight %}
#### Compare **SpatPCA** with PCA
There are two comparison remarks 
  1. Two estimates are similar to the true eigenfunctions
  2. **SpatPCA** can perform better at the both ends.

{% highlight r %}
data.frame(
  position = position,
  true = true_eigen_fn,
  spatpca = eigen_est[, 1],
  pca = svd(realizations)$v[, 1]
) %>%
  gather(estimate, eigenfunction, -position) %>%
  ggplot(aes(x = position, y = eigenfunction, color = estimate)) +
  geom_line() +
  base_theme
{% endhighlight %}

![plot of chunk unnamed-chunk-7](figure/posts/2021-01-18-SpatPCA-demo-one-dim-location/unnamed-chunk-7-1.png)

### Case II: Lower signal of the true eigenfunction
#### Generate realizations with $\sigma=3$

{% highlight r %}
realizations <- rnorm(n = 100, sd = 3) %*% t(true_eigen_fn) + matrix(rnorm(n = 100 * 100), 100, 100)
{% endhighlight %}

#### Animate realizations
It is hard to see a crystal clear spatial pattern via the simluated sample shown below.

{% highlight r %}
for (i in 1:100) {
  plot(x = position, y = realizations[i, ], ylim = c(-10, 10), ylab = "realization")
}
{% endhighlight %}

![plot of chunk unnamed-chunk-9](figure/posts/2021-01-18-SpatPCA-demo-one-dim-location/unnamed-chunk-9-.gif)

#### Compare resultant patterns
The following panel indicates that **SpatPCA** outperforms to PCA visually when the signal-to-noise ratio is quite lower.


{% highlight r %}
cv <- spatpca(x = position, Y = realizations)
eigen_est <- cv$eigenfn

data.frame(
  position = position,
  true = true_eigen_fn,
  spatpca = eigen_est[, 1],
  pca = svd(realizations)$v[, 1]
) %>%
  gather(estimate, eigenfunction, -position) %>%
  ggplot(aes(x = position, y = eigenfunction, color = estimate)) +
  geom_line() +
  base_theme
{% endhighlight %}

![plot of chunk unnamed-chunk-10](figure/posts/2021-01-18-SpatPCA-demo-one-dim-location/unnamed-chunk-10-1.png)
