---
layout: post
title: "From PCA to Barlow Twins: A Statistical View of Redundancy Reduction in Self-Supervised Learning"
tags: [Machine Learning, Self-Supervised Learning, Statistics, Deep Learning]
math: true
---

I originally found Barlow Twins confusing because it felt statistical, yet behaved nothing like PCA in practice. Both methods touch the same object—(cross-)correlation—but use it in opposite ways. PCA measures redundancy after a representation is learned and removes it by rotation. Barlow Twins prevents redundancy from forming by enforcing a correlation structure during learning.

### The Problem of Redundancy in Representations

Autoencoders measure success by reconstruction error, but reconstruction quality does not imply statistical efficiency. An autoencoder may perfectly reconstruct images while learning representations with highly correlated dimensions.

Reconstruction alone does not specify how information should be organized across dimensions.

### Principal Component Analysis as a Statistical Baseline

PCA operates on the **sample covariance matrix**:

$$\hat{\mathbf{C}} = \frac{1}{n-1} \sum_{i=1}^n (\mathbf{z}_i - \bar{\mathbf{z}})(\mathbf{z}_i - \bar{\mathbf{z}})^T$$

PCA is a **post-hoc transformation**: given a fixed representation, it finds an orthogonal basis that diagonalizes the sample covariance.

The eigenvectors of $\hat{\mathbf{C}}$ define directions of decreasing variance. In this particular simulation, the eigen-spectrum is visibly skewed, suggesting that variance concentrates in a few directions even when $d$ is larger.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/pca_eigenspectrum.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/pca_eigenspectrum.png" alt="PCA eigen-spectrum showing variance explained by each principal component" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 1. PCA eigen-spectrum: variance explained by each principal component for the redundant representation.</div>
</div>

A skewed eigen-spectrum indicates that variance concentrates in a few directions, even when the ambient dimension is large.

### Barlow Twins: A Statistical Formulation

Barlow Twins is a self-supervised learning method that constrains **second-order statistics** of learned representations during training.

For each image $$\mathbf{x}_i$$, we generate two augmented views,
$$\mathbf{x}_i^A$$ and $$\mathbf{x}_i^B$$, and pass them through a neural network $$f_\theta$$:


$$\mathbf{z}_i^A = f_\theta(\mathbf{x}_i^A), \quad \mathbf{z}_i^B = f_\theta(\mathbf{x}_i^B)$$

Barlow Twins computes the **sample cross-correlation matrix**:

$$\mathbf{C}_{ij} = \frac{\sum_{b=1}^B z^A_{b,i} z^B_{b,j}}{\sqrt{\sum_{b=1}^B (z^A_{b,i})^2} \sqrt{\sum_{b=1}^B (z^B_{b,j})^2}}$$

The Barlow Twins objective has two components:

1. **Invariance term**: Encourages diagonal elements $C_{ii}$ to be close to 1, making corresponding dimensions from the two views highly correlated (invariance to augmentations).

2. **Redundancy reduction term**: Encourages off-diagonal elements $C_{ij}$ (where $i \neq j$) to be close to 0, decorrelating different dimensions.

$$\mathcal{L} = \sum_i (1 - C_{ii})^2 + \lambda \sum_i \sum_{j \neq i} C_{ij}^2$$

The diagonal term enforces invariance across views, while the off-diagonal penalty discourages duplicated features.

Unlike PCA, this constraint is applied during training. The representation is learned so that its cross-view correlation is already close to the identity.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/barlow_twins_schematic.svg" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/barlow_twins_schematic.svg" alt="Schematic of Barlow Twins: two views through a shared network, cross-correlation, and an identity target" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Schematic. Two augmented views go through a shared network; training pushes the cross-correlation $\mathbf{C}$ toward the identity.</div>
</div>

### Why two views, off-diagonals, and λ

Two views provide a nontrivial alignment target: each feature must be predictive across augmentations. Without the off-diagonal penalty, this objective can be satisfied by copying the same signal across many dimensions. The parameter $\lambda$ controls how expensive such duplication is.

I find it useful to think of $\lambda$ not as a regularizer, but as a price on feature duplication.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/lambda_exploration.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/lambda_exploration.png" alt="Lambda exploration: invariance vs λ (left) and redundancy vs λ (right) on log scales" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 4. Lambda exploration showing the trade-off between invariance (diagonal mean, left) and redundancy reduction (mean and max $\lvert C_{ij}\rvert$ for $i\neq j$, right). Log-scale x-axis spans $\lambda$ from $10^{-6}$ to $10$. Error bars show bootstrap variability from finite-sample estimates.</div>
</div>

For small $\lambda$, invariance is already high, but redundancy remains large. Increasing $\lambda$ rapidly suppresses off-diagonal correlations. Beyond $\lambda \approx 10^{-2}$, redundancy approaches a numerical floor in this toy setup, and further increases offer limited additional benefit.

Figure 4b summarizes this trade-off: moving along the curve corresponds to increasing $\lambda$, with the saturated regime clustering near the bottom-left.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/pareto_lambda_tradeoff.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/pareto_lambda_tradeoff.png" alt="Pareto view of lambda trade-off: invariance error vs redundancy on log-log scale" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 4b. Pareto view of the $\lambda$ trade-off: invariance error (1 − mean diag$(\mathbf{C})$) vs redundancy (max $\lvert\mathrm{offdiag}(\mathbf{C})\rvert$) on log-log scale. Moving along the curve corresponds to increasing $\lambda$. The saturated regime ($\lambda \ge 10^{-2}$) clusters near the bottom-left, indicating diminishing returns.</div>
</div>

### What redundancy looks like (Matérn toy example)

To make redundancy concrete, we construct a toy representation with Matérn-structured covariance across feature dimensions. This creates structured redundancy: nearby dimensions are highly correlated, with correlation decaying with distance. The resulting covariance matrix has a banded structure rather than uniform correlation. PCA removes this redundancy by rotating the representation post-hoc. In contrast, a Barlow Twins-style objective learns a linear transformation that minimizes cross-correlation between two noisy views, producing a representation whose covariance is already near-diagonal.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/cov_and_corr_comparison.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/cov_and_corr_comparison.png" alt="Covariance and redundancy maps: original (redundant), PCA (post-hoc), and Barlow Twins-style (learned)" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 2. Top: covariance matrices. Bottom: redundancy maps $1-\lvert\mathrm{Corr}\rvert$ (0 = redundant, 1 = decorrelated). Original (redundant), PCA (post-hoc), and Barlow Twins-style (learned).</div>
</div>

The original representation exhibits structured redundancy between nearby dimensions. PCA removes this structure by rotation. Barlow Twins-style learning produces near-decorrelation directly, without an explicit post-hoc transform.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/offdiag_corr_hist.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/offdiag_corr_hist.png" alt="Distribution of absolute off-diagonal correlations showing redundancy reduction" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 3. Distribution of $\log_{10}(\lvert C_{ij}\rvert)$ for off-diagonal entries ($i\neq j$). PCA and Barlow Twins-style learning concentrate mass near zero correlation, so a log scale makes the shrinkage visible.</div>
</div>

### What this example does *not* show

This toy setup is intentionally narrow. It does not claim that Barlow Twins produces semantically better features than PCA, nor that decorrelation alone is sufficient for representation quality. The goal here is only to make the statistical role of the loss explicit.

### Basis alignment

Barlow Twins-style learning isn’t “just decorrelating”: because the constraint is defined **across views**, the learned solution can also rotate the basis (not necessarily match PCA’s eigenvectors).

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/basis_alignment_heatmap.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/basis_alignment_heatmap.png" alt="Basis alignment heatmap showing |Q_PCA^T Q_BT|" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 5. Basis alignment: absolute cosine similarities between PCA and Barlow Twins-style bases. If bases matched, this would be a permuted identity.</div>
</div>

Because the constraint is defined across views, Barlow Twins is free to rotate the representation. The learned basis need not coincide with PCA eigenvectors.

<div style="text-align:center; margin: 1rem 0;">
  <a href="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/principal_angles.png" target="_blank">
    <img src="{{ site.baseurl }}/assets/2025-12-27-from-pca-to-barlow-twins-statistical-view-redundancy-reduction/principal_angles.png" alt="Principal angles between PCA and Barlow Twins subspaces" style="max-width:100%; height:auto; cursor: pointer;" />
  </a>
  <div style="color: var(--text-secondary); font-size: var(--font-size-sm); margin-top: .25rem;">Figure 6. Principal angles between PCA and Barlow Twins subspaces. Small angles indicate similar subspaces; large angles indicate different orientations.</div>
</div>

Here, the subspaces are similar (small principal angles), but the coordinate systems differ—same effective representation, different basis.

### Why this isn’t a generative model

Barlow Twins is not a generative model. It aligns augmentation-invariant information across views but does not learn a decoder or likelihood for reconstruction.

### Summary

- PCA removes redundancy *after* learning by reparameterization.
- Barlow Twins shapes correlation *during* learning through an explicit constraint.
- The role of $\lambda$ is practical and visible: once duplication is sufficiently penalized, the system enters a saturated regime.
