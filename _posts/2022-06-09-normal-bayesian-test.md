---
layout: post
title: "Note: Derivation of Normal Bayesian Test"
tags: [Statistics]
---
The Normal Bayesian test is a statistical method used in hypothesis testing, particularly in the context of Bayesian statistics. It is applied to assess the validity of a null hypothesis ($H_0$) versus an alternative hypothesis ($H_1$) by considering the posterior distribution of a parameter of interest.
This method is exemplified in [Statistical Inference (2nd edition)](https://www.amazon.com/Statistical-Inference-George-Casella/dp/0534243126) by Casella and Berger, as shown on page 379.

#### Problem

Let $X_1, \dots, X_n \sim_{iid} N(\theta, \sigma^2)$ and the prior distribution $\theta \sim N(\mu, \tau^2)$. According to Example 7.2.16, the posterior $\theta \vert \bar{x} \sim N\left(\frac{n\tau^2\bar{x}+\sigma^2\mu}{n\tau^2 + \sigma^2}, \frac{\sigma^2\tau^2}{n\tau^2 + \sigma^2}\right)$.

The hypotheses of interest are:

$$\text{H}_0: \theta\leq\theta_0 \mbox{ vs. } \text{H}_1: \theta > \theta_0.$$

What is the Bayesian test?


#### Normal Bayesian Test Derivation

If we choose to accept $\text{H}_0$, we have:

$$P(\theta \in \mathcal{\Theta}_0 \|X_1, \dots, X_n) \geq P(\theta \in \mathcal{\Theta}^c_0 \|X_1, \dots, X_n) = 1 - P(\theta \in \mathcal{\Theta}_0 \|X_1, \dots, X_n).$$

Namely,

$$P(\theta \in \mathcal{\Theta}_0 \|X_1, \dots, X_n) = P(\theta \leq \theta_0 \|X_1, \dots, X_n) \geq \frac{1}{2}.$$

Let $Z$ be defined as:

$$Z = \frac{\theta - \frac{n\tau^2\bar{X}+\sigma^2\mu}{n\tau^2 + \sigma^2}}{\sqrt{\frac{\sigma^2\tau^2}{n\tau^2 + \sigma^2}}}.$$

Based on the posterior distribution $\pi(\theta \| \bar{x})$, we have:

$$Z \| X_1, \dots, X_n \sim N(0, 1).$$

Accordingly, we can rewrite the inequality as:

$$P(\theta \leq \theta_0 \| X_1, \dots, X_n) = P\left(Z \leq \frac{\theta_0 - \frac{n\tau^2\bar{X}+\sigma^2\mu}{n\tau^2 + \sigma^2}}{\sqrt{\frac{\sigma^2\tau^2}{n\tau^2 + \sigma^2}}}\| X_1, \dots, X_n\right) \geq \frac{1}{2} = P(Z \leq 0\|X_1, \dots, X_n).$$

Therefore, the acceptance region is derived as:

$$\frac{\theta_0 - \frac{n\tau^2\bar{X}+\sigma^2\mu}{n\tau^2 + \sigma^2}}{\sqrt{\frac{\sigma^2\tau^2}{n\tau^2 + \sigma^2}}} \geq 0.$$

This simplifies to:

$$(n\tau^2 + \sigma^2) \theta_0 \geq n\tau^2\bar{X} + \sigma^2\mu.$$

And further simplifies to:

$$\bar{X} \leq \theta_0 + \frac{\sigma^2(\theta_0 - \mu)}{n\tau^2}.$$


#### Summary
In summary, the Normal Bayesian test is a hypothesis test that uses the posterior distribution of a parameter to evaluate a null hypothesis that the parameter is less than or equal to a specific value under the assumption of normality. 
This test involves standardizing the parameter and defining an acceptance region for a standardized variable, allowing us to make a decision about the null hypothesis based on the observed data and posterior distribution.
