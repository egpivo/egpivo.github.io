---
layout: post
title: "Three fundamental aspects of statistical models"
date: "May 19th, 2017"
output:
    html_document
tags: [Statistics]
use_math : true
---

I have read the Annals’ article, “[Additive regression and other nonparametric models](http://digitalassets.lib.berkeley.edu/sdtr/ucb/text/33.pdf)” by Stones (1985). There are a bunch of inspiring thoughts. Mainly, Stones stated that three fundamental aspects of statistical models:

- Flexibility: the accuracy of the fitted model in a wide variety of situations (bias in estimation)
- Dimensionality: the amount of data required to avoid an unacceptably large variance increases rapidly with increasing dimensionality. (variance in estimation)
- Interpretability: interpretability lies in the potential for shedding light on the underlying structure.
Trade off (flexibility, dimensionality) = Trade off(bias, variance)

Remark: We usually have to follow the experience and rules to look into data, understand data, model data, and turn the insights to a solution or explanation of a real-world problem. There aspects are still suitable in this "massive-data" era now.

Stones also quoted meaningful words from Box et al. (1978):

```
While blind faith in a particular model is foolhardy, refusal to associate data with any model is to eschew a powerful tool. As implied earlier, a middle course may be followed. On the other hand, inadequacies in proposed models should be looked for; on the other hand, if a model appears reasonably appropriate, advantage should be take of the greater simplicity and clarity of interpretation that it provides.
```

Remark: These wise words can remind us that we cannot build a useful statistical model without the aspects, even if there are a tons of fashion analytic tools. Simple is better.


## References

* Stones (1985), [Additive regression and other nonparametric models](http://digitalassets.lib.berkeley.edu/sdtr/ucb/text/33.pdf).
* Box et al. (1978), [Statistics for Experimenters](http://onlinelibrary.wiley.com/doi/10.1002/aic.690250233/abstract)
