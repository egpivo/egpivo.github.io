---
layout: post
title: "Three Fundamental Aspects of Statistical Models"
date: "May 19th, 2017"
output:
    html_document
tags: [Statistics]
use_math : true
---

Recently, I delved into a classic Annals article, [Additive Regression and Other Nonparametric Models](http://digitalassets.lib.berkeley.edu/sdtr/ucb/text/33.pdf)” by Stones (1985). The insights gleaned from this piece revolve around three fundamental aspects of statistical models:

- **Flexibility**: This pertains to the accuracy of the fitted model across a wide variety of situations, often associated with bias in estimation.
- **Dimensionality**: The amount of data required to avoid unacceptably large variance increases rapidly with rising dimensionality, reflecting the variance in estimation.
- **Interpretability**: The essence of interpretability lies in the potential for shedding light on the underlying structure of the data.

> Trade off (flexibility, dimensionality) = Trade off(bias, variance)

The trade-off between flexibility and dimensionality is akin to the trade-off between bias and variance. As practitioners, we often rely on experiences or rules of thumb to explore, manipulate, and model data, ultimately transforming insights into solutions or explanations for real-world problems. In the current era of massive data, these three enduring aspects remain crucial considerations.

Stones also shared insightful words from Box et al. (1978):

```
While blind faith in a particular model is foolhardy, refusal to associate data with any model is to eschew a powerful tool. As implied earlier, a middle course may be followed. On the other hand, inadequacies in proposed models should be looked for; on the other hand, if a model appears reasonably appropriate, advantage should be take of the greater simplicity and clarity of interpretation that it provides.
```

These wise words serve as a reminder that a useful statistical model cannot be built without considering these fundamental aspects, even with the plethora of fashionable analytic tools available. The underlying principle remains: simplicity often leads to better outcomes.


### References

* Stones (1985), [Additive regression and other nonparametric models](http://digitalassets.lib.berkeley.edu/sdtr/ucb/text/33.pdf).
* Box et al. (1978), [Statistics for Experimenters](http://onlinelibrary.wiley.com/doi/10.1002/aic.690250233/abstract)
