#!/usr/bin/env python3
"""
Simulation demonstrating PCA post-hoc decorrelation vs Barlow Twins-style learning.

Shows that PCA decorrelates a fixed representation,
while Barlow Twins-style learning produces decorrelated representations directly.

Includes additional statistical diagnostics and plots:
- eigen-spectrum (variance explained by PCA axes)
- off-diagonal correlation histograms (redundancy proxy)
- bootstrap variability/error bars for empirical cross-correlation
- lambda trade-off plots (with error bars)
"""

import numpy as np
import torch
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass

# Setup output directory
out_dir = Path(__file__).parent
out_dir.mkdir(parents=True, exist_ok=True)

np.random.seed(0)
torch.manual_seed(0)

# -----------------------------
# Statistical utilities
# -----------------------------

def standardize_np(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Column-wise standardization: zero mean, unit std."""
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True)
    return (X - mu) / (sd + eps)

def cov_np(X: np.ndarray) -> np.ndarray:
    """Sample covariance with rowvar=False."""
    return np.cov(X, rowvar=False)

def corr_np(X: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Sample correlation matrix from standardized data."""
    Xs = standardize_np(X, eps=eps)
    # correlation = cov of standardized variables
    return cov_np(Xs)

def cross_corr_np(Xa: np.ndarray, Xb: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    """Sample cross-correlation Corr(Xa, Xb) computed over rows."""
    Xa_s = standardize_np(Xa, eps=eps)
    Xb_s = standardize_np(Xb, eps=eps)
    return (Xa_s.T @ Xb_s) / Xa_s.shape[0]

def offdiag_elements(M: np.ndarray) -> np.ndarray:
    """Flattened off-diagonal elements of a square matrix."""
    d = M.shape[0]
    mask = ~np.eye(d, dtype=bool)
    return M[mask]

@dataclass
class StatsSummary:
    diag_mean: float
    diag_rmse_to_1: float
    offdiag_mean_abs: float
    offdiag_rms: float
    fro_offdiag: float

def summarize_corr(C: np.ndarray) -> StatsSummary:
    """Summarize correlation/cross-correlation structure."""
    d = C.shape[0]
    diag = np.diag(C)
    off = offdiag_elements(C)
    diag_rmse = float(np.sqrt(np.mean((diag - 1.0) ** 2)))
    off_mean_abs = float(np.mean(np.abs(off)))
    off_rms = float(np.sqrt(np.mean(off ** 2)))
    fro_off = float(np.linalg.norm(C - np.diag(diag), ord='fro') / np.sqrt(d * (d - 1)))
    return StatsSummary(
        diag_mean=float(np.mean(diag)),
        diag_rmse_to_1=diag_rmse,
        offdiag_mean_abs=off_mean_abs,
        offdiag_rms=off_rms,
        fro_offdiag=fro_off,
    )

def print_summary(name: str, C: np.ndarray) -> None:
    s = summarize_corr(C)
    print(f"{name}: diag_mean={s.diag_mean:.3f}, diag_rmse_to_1={s.diag_rmse_to_1:.3f}, "
          f"off_mean_abs={s.offdiag_mean_abs:.3f}, off_rms={s.offdiag_rms:.3f}, fro_offdiag={s.fro_offdiag:.3f}")

def save_heatmap(mat: np.ndarray, title: str, path: Path, vmin: float = -1.2, vmax: float = 1.2):
    fig, ax = plt.subplots(figsize=(4.8, 4.2))
    im = ax.imshow(mat, cmap='RdBu_r', vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel('Dimension')
    ax.set_ylabel('Dimension')
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)

# --- Basis/subspace diagnostics ---
def orthonormal_basis(M: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Return an orthonormal basis for the column space of M via QR."""
    Q, R = np.linalg.qr(M)
    # Handle near-zero columns
    diag = np.abs(np.diag(R))
    keep = diag > eps
    if keep.ndim == 0:
        keep = np.array([bool(keep)])
    return Q[:, keep] if keep.any() else Q[:, :0]

def principal_angles(Qa: np.ndarray, Qb: np.ndarray) -> np.ndarray:
    """Principal angles (radians) between two subspaces with orthonormal bases Qa, Qb."""
    if Qa.size == 0 or Qb.size == 0:
        return np.array([])
    M = Qa.T @ Qb
    s = np.linalg.svd(M, compute_uv=False)
    s = np.clip(s, 0.0, 1.0)
    return np.arccos(s)

def effective_rank_from_eigs(eigs: np.ndarray, eps: float = 1e-12) -> float:
    """Effective rank from eigenvalues using exp(entropy) on normalized spectrum."""
    p = np.maximum(eigs, 0.0)
    p = p / (p.sum() + eps)
    p = np.clip(p, eps, 1.0)
    H = -np.sum(p * np.log(p))
    return float(np.exp(H))

def participation_ratio(eigs: np.ndarray, eps: float = 1e-12) -> float:
    """Participation ratio: (sum e)^2 / sum e^2; another effective dimension measure."""
    e = np.maximum(eigs, 0.0)
    num = (e.sum() ** 2)
    den = (np.sum(e ** 2) + eps)
    return float(num / den)

# --- Matérn kernel helper ---
def matern_kernel_1d(dims: int, lengthscale: float = 1.0, nu: float = 1.5, sigma2: float = 1.0) -> np.ndarray:
    """Matérn covariance matrix on a 1D grid of `dims` points.

    nu=0.5 => exponential, nu=1.5 and nu=2.5 are common closed forms.
    """
    x = np.arange(dims, dtype=float)[:, None]
    r = np.abs(x - x.T)
    ell = max(lengthscale, 1e-8)

    if np.isclose(nu, 0.5):
        K = np.exp(-r / ell)
    elif np.isclose(nu, 1.5):
        s = np.sqrt(3.0) * r / ell
        K = (1.0 + s) * np.exp(-s)
    elif np.isclose(nu, 2.5):
        s = np.sqrt(5.0) * r / ell
        K = (1.0 + s + (s ** 2) / 3.0) * np.exp(-s)
    else:
        # Fallback: approximate with exponential if nu not in closed-form set
        K = np.exp(-r / ell)

    return sigma2 * K

# 1. Setup: deliberately redundant representation
n = 10_000  # samples
d = 5       # dimensions

# Matérn-correlated representation across feature dimensions.
# Think of the feature index as a 1D "coordinate" and impose smooth correlation.
K = matern_kernel_1d(dims=d, lengthscale=1.0, nu=1.5, sigma2=1.0)

# Sample Z ~ N(0, K) for each of n samples.
# Use Cholesky for stability (add tiny jitter).
L = np.linalg.cholesky(K + 1e-6 * np.eye(d))
Z = np.random.randn(n, d) @ L.T

# Add small independent noise so the structure isn't perfectly smooth.
Z = Z + 0.05 * np.random.randn(n, d)

# 2. Observe redundancy (before PCA)
cov_Z = np.cov(Z, rowvar=False)
print("Original covariance matrix:")
print(np.round(cov_Z, 2))

# Correlation diagnostics
corr_Z = corr_np(Z)
print_summary("Original Corr(Z)", corr_Z)

# 3. PCA: post-hoc decorrelation
eigvals, eigvecs = np.linalg.eigh(cov_Z)
Z_pca = Z @ eigvecs
cov_Z_pca = np.cov(Z_pca, rowvar=False)
print("\nPCA-transformed covariance matrix:")
print(np.round(cov_Z_pca, 2))

# Note: PCA rotation decorrelates only after the representation exists.
corr_Z_pca = corr_np(Z_pca)
print_summary("PCA Corr(Z_pca)", corr_Z_pca)

# Eigen-spectrum (variance along principal axes)
eigvals_sorted = np.sort(eigvals)[::-1]
explained = eigvals_sorted / eigvals_sorted.sum()
explained_cum = np.cumsum(explained)

# Effective dimension diagnostics
print(f"\nPCA spectrum stats: effective_rank={effective_rank_from_eigs(eigvals_sorted):.2f}, participation_ratio={participation_ratio(eigvals_sorted):.2f}")

# 4. Barlow Twins-style objective
Z1 = Z + 0.05 * np.random.randn(*Z.shape)
Z2 = Z + 0.05 * np.random.randn(*Z.shape)

Z1_t = torch.tensor(Z1, dtype=torch.float32)
Z2_t = torch.tensor(Z2, dtype=torch.float32)

W = torch.randn(d, d, requires_grad=True)
opt = torch.optim.Adam([W], lr=1e-2)

def barlow_loss(Za: torch.Tensor, Zb: torch.Tensor, lam: float = 1.0):
    """Barlow Twins loss + returns cross-correlation matrix C for diagnostics."""
    Za = (Za - Za.mean(0)) / (Za.std(0) + 1e-8)
    Zb = (Zb - Zb.mean(0)) / (Zb.std(0) + 1e-8)
    C = (Za.T @ Zb) / Za.shape[0]

    on = torch.diagonal(C).add(-1).pow(2).sum()
    off = (C - torch.diag(torch.diagonal(C))).pow(2).sum()
    return on + lam * off, C

lam_main = 1.0
for _ in range(500):
    opt.zero_grad()
    loss, _ = barlow_loss(Z1_t @ W, Z2_t @ W, lam=lam_main)
    loss.backward()
    opt.step()

# 5. Inspect learned representation
Z_bt = Z @ W.detach().numpy()
cov_bt = np.cov(Z_bt, rowvar=False)
print("\nBarlow Twins-style learned covariance matrix:")
print(np.round(cov_bt, 2))

# Correlation diagnostics for learned features
corr_Z_bt = corr_np(Z_bt)
print_summary("BT-style Corr(Z_bt)", corr_Z_bt)

# Cross-correlation across views after learning
Z1_bt = (Z1_t @ W).detach().numpy()
Z2_bt = (Z2_t @ W).detach().numpy()
C_bt = cross_corr_np(Z1_bt, Z2_bt)
print_summary("BT-style CrossCorr(Z1_bt, Z2_bt)", C_bt)

# -----------------------------
# Basis / representation comparison
# -----------------------------

# PCA basis: eigenvectors are already orthonormal (columns)
Q_pca = eigvecs

# BT-style basis: columns of W are not orthonormal; compare their column space via QR
W_np = W.detach().numpy()
Q_bt = orthonormal_basis(W_np)

# Alignment matrix between bases (absolute cosine similarities)
# Use min(d, Q_bt.shape[1]) because QR may drop near-zero directions.
k_max = min(d, Q_bt.shape[1])
A = np.abs(Q_pca[:, :k_max].T @ Q_bt[:, :k_max])  # shape: k_max x k_max

print(f"\nBasis comparison: k_max={k_max}")
print(f"Mean |cos| alignment (top-k): {A.mean():.3f}")

# Principal angles between top-k subspaces
angles = principal_angles(Q_pca[:, :k_max], Q_bt[:, :k_max])
if angles.size > 0:
    print("Principal angles (degrees):", np.round(np.degrees(angles), 2))

# -----------------------------
# Plots: covariance/correlation + eigen-spectrum
# -----------------------------

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

# Row 1: covariance heatmaps
im1 = axes[0, 0].imshow(cov_Z, cmap='RdBu_r', vmin=-1.2, vmax=1.2)
axes[0, 0].set_title('Cov: Original (redundant)')
axes[0, 0].set_xlabel('Dimension')
axes[0, 0].set_ylabel('Dimension')
plt.colorbar(im1, ax=axes[0, 0])

im2 = axes[0, 1].imshow(cov_Z_pca, cmap='RdBu_r', vmin=-1.2, vmax=1.2)
axes[0, 1].set_title('Cov: PCA (post-hoc)')
axes[0, 1].set_xlabel('Dimension')
axes[0, 1].set_ylabel('Dimension')
plt.colorbar(im2, ax=axes[0, 1])

im3 = axes[0, 2].imshow(cov_bt, cmap='RdBu_r', vmin=-1.2, vmax=1.2)
axes[0, 2].set_title('Cov: BT-style (learned)')
axes[0, 2].set_xlabel('Dimension')
axes[0, 2].set_ylabel('Dimension')
plt.colorbar(im3, ax=axes[0, 2])

# Row 2: redundancy maps (1 - |Corr|) (scale invariant)
corr_Z = corr_np(Z)
corr_Z_pca = corr_np(Z_pca)
corr_Z_bt = corr_np(Z_bt)

# Redundancy map: 1 - |Corr| highlights how much linear redundancy remains.
# (0 means perfectly correlated; 1 means uncorrelated.)
red_Z = 1.0 - np.abs(corr_Z)
red_Z_pca = 1.0 - np.abs(corr_Z_pca)
red_Z_bt = 1.0 - np.abs(corr_Z_bt)

im4 = axes[1, 0].imshow(red_Z, cmap='viridis', vmin=0.0, vmax=1.0)
axes[1, 0].set_title('Redundancy: 1-|Corr| (Original)')
axes[1, 0].set_xlabel('Dimension')
axes[1, 0].set_ylabel('Dimension')
plt.colorbar(im4, ax=axes[1, 0])

im5 = axes[1, 1].imshow(red_Z_pca, cmap='viridis', vmin=0.0, vmax=1.0)
axes[1, 1].set_title('Redundancy: 1-|Corr| (PCA)')
axes[1, 1].set_xlabel('Dimension')
axes[1, 1].set_ylabel('Dimension')
plt.colorbar(im5, ax=axes[1, 1])

im6 = axes[1, 2].imshow(red_Z_bt, cmap='viridis', vmin=0.0, vmax=1.0)
axes[1, 2].set_title('Redundancy: 1-|Corr| (BT-style)')
axes[1, 2].set_xlabel('Dimension')
axes[1, 2].set_ylabel('Dimension')
plt.colorbar(im6, ax=axes[1, 2])

plt.tight_layout()
plt.savefig(out_dir / 'cov_and_corr_comparison.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"\nPlot saved to: {out_dir / 'cov_and_corr_comparison.png'}")

# Eigen-spectrum plot (variance explained by PCA axes)
fig, ax = plt.subplots(figsize=(6.6, 4.2))
xs = np.arange(1, d + 1)
ax.plot(xs, explained, marker='o', linewidth=2, label='Explained variance')
ax.plot(xs, explained_cum, marker='s', linewidth=2, label='Cumulative explained')
ax.set_xlabel('Component')
ax.set_ylabel('Fraction of total variance')
ax.set_title('PCA eigen-spectrum (explained variance)')
ax.set_xticks(xs)
ax.grid(True, alpha=0.3)
ax.legend(loc='best', fontsize=10)
plt.tight_layout()
plt.savefig(out_dir / 'pca_eigenspectrum.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Plot saved to: {out_dir / 'pca_eigenspectrum.png'}")

# Off-diagonal correlation histograms
# NOTE: After PCA / BT, |offdiag| can be extremely close to 0, which makes density histograms
# look "empty" (a delta spike at 0 implies huge density). A log-scale histogram is clearer.
off_orig = np.abs(offdiag_elements(corr_Z))
off_pca = np.abs(offdiag_elements(corr_Z_pca))
off_bt = np.abs(offdiag_elements(corr_Z_bt))

eps_hist = 1e-12
log_off_orig = np.log10(np.maximum(off_orig, eps_hist))
log_off_pca  = np.log10(np.maximum(off_pca,  eps_hist))
log_off_bt   = np.log10(np.maximum(off_bt,   eps_hist))

fig, ax = plt.subplots(figsize=(7.2, 4.2))
bins = np.linspace(-12, 0, 49)  # 0 => |corr|=1, -12 => |corr|=1e-12
ax.hist(log_off_orig, bins=bins, alpha=0.55, label='Original', density=False)
ax.hist(log_off_pca,  bins=bins, alpha=0.55, label='PCA', density=False)
ax.hist(log_off_bt,   bins=bins, alpha=0.55, label='BT-style', density=False)

ax.set_xlabel('log10(|off-diagonal correlation|)')
ax.set_ylabel('Count')
ax.set_title('Redundancy proxy: distribution of log10 |off-diagonal correlations|')
ax.grid(True, alpha=0.3)
ax.legend()

# Show the epsilon floor used for the log transform
ax.axvline(np.log10(eps_hist), color='gray', linestyle='--', alpha=0.4)

plt.tight_layout()
plt.savefig(out_dir / 'offdiag_corr_hist.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Plot saved to: {out_dir / 'offdiag_corr_hist.png'}")

# Basis alignment heatmap
fig, ax = plt.subplots(figsize=(5.6, 4.6))
im = ax.imshow(A, cmap='viridis', vmin=0.0, vmax=1.0)
ax.set_title(r'Basis alignment: $|Q_{\mathrm{PCA}}^{\top} Q_{\mathrm{BT}}|$ (top-$k$)')
ax.set_xlabel('BT basis index')
ax.set_ylabel('PCA basis index')
ax.set_xticks(np.arange(k_max))
ax.set_yticks(np.arange(k_max))

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Absolute cosine similarity', rotation=90)

plt.tight_layout()
plt.savefig(out_dir / 'basis_alignment_heatmap.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Plot saved to: {out_dir / 'basis_alignment_heatmap.png'}")

# Principal angles plot
fig, ax = plt.subplots(figsize=(6, 4))
if angles.size > 0:
    ax.plot(np.arange(1, angles.size + 1), np.degrees(angles), marker='o', linewidth=2)
    ax.set_xticks(np.arange(1, angles.size + 1))
ax.set_xlabel('Component')
ax.set_ylabel('Angle (degrees)')
ax.set_title('Subspace difference: principal angles (PCA vs BT basis)')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(out_dir / 'principal_angles.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Plot saved to: {out_dir / 'principal_angles.png'}")

# 6. Explore lambda effect
def corr_matrix(Za, Zb):
    Za = (Za - Za.mean(0)) / Za.std(0)
    Zb = (Zb - Zb.mean(0)) / Zb.std(0)
    return (Za.T @ Zb) / Za.shape[0]

def offdiag_mean(C):
    d = C.shape[0]
    return (C - torch.diag(torch.diagonal(C))).abs().mean().item()

def offdiag_max_abs(C):
    off = C - torch.diag(torch.diagonal(C))
    return off.abs().max().item()

print("\n" + "="*60)
print("Lambda exploration:")
print("="*60)

# Wider λ sweep so the trade-off is visually apparent
lambdas = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0]
diag_means = []
offdiag_means = []
offdiag_maxabs = []

# For bootstrap error bars
diag_std = []
offdiag_std = []
offdiag_max_std = []
n_boot = 30
batch_size_boot = min(512, Z1_t.shape[0])
rng = np.random.default_rng(0)

for lam in lambdas:
    W = torch.randn(d, d, requires_grad=True)
    opt = torch.optim.Adam([W], lr=1e-2)

    def loss_fn(Za, Zb):
        C = corr_matrix(Za, Zb)
        on = torch.diagonal(C).add(-1).pow(2).sum()
        off = (C - torch.diag(torch.diagonal(C))).pow(2).sum()
        return on + lam * off

    for _ in range(300):
        opt.zero_grad()
        loss = loss_fn(Z1_t @ W, Z2_t @ W)
        loss.backward()
        opt.step()

    C = corr_matrix(Z1_t @ W, Z2_t @ W).detach()
    diag_mean = torch.diagonal(C).mean().item()
    offdiag_mean_val = offdiag_mean(C)
    offdiag_max_val = offdiag_max_abs(C)
    diag_means.append(diag_mean)
    offdiag_means.append(offdiag_mean_val)
    offdiag_maxabs.append(offdiag_max_val)

    # Bootstrap variability: empirical cross-correlation depends on finite batch samples
    diag_samples = []
    off_samples = []
    off_max_samples = []
    for _ in range(n_boot):
        idx = rng.integers(0, Z1_t.shape[0], size=batch_size_boot)
        Cb = corr_matrix((Z1_t[idx] @ W), (Z2_t[idx] @ W)).detach()
        diag_samples.append(torch.diagonal(Cb).mean().item())
        off_samples.append(offdiag_mean(Cb))
        off_max_samples.append((Cb - torch.diag(torch.diagonal(Cb))).abs().max().item())

    diag_std.append(float(np.std(diag_samples)))
    offdiag_std.append(float(np.std(off_samples)))
    offdiag_max_std.append(float(np.std(off_max_samples)))
    print(
        f"lambda={lam:>6}: diag_mean={diag_mean:.3f}±{diag_std[-1]:.3f}, "
        f"offdiag_mean={offdiag_mean_val:.3f}±{offdiag_std[-1]:.3f}, "
        f"max|offdiag|={offdiag_max_val:.3f}±{offdiag_max_std[-1]:.3f}"
    )

# Generate markdown summary of key points
print("\n" + "="*60)
print("Key points summary (for article):")
print("="*60)
print("\n```markdown")

# Find key lambda values
lam_small = 1e-6
lam_mid = 1e-4
lam_large = 1e-2

idx_small = lambdas.index(lam_small) if lam_small in lambdas else 0
idx_mid = lambdas.index(lam_mid) if lam_mid in lambdas else len(lambdas) // 2
# Find first lambda >= 1e-2
idx_large = next((i for i, lam in enumerate(lambdas) if lam >= lam_large), len(lambdas) - 1)

max_off_small = offdiag_maxabs[idx_small]
max_off_mid = offdiag_maxabs[idx_mid]
max_off_large = offdiag_maxabs[idx_large]

# Find average for saturated region (lambda >= 1e-2)
large_indices = [i for i, lam in enumerate(lambdas) if lam >= lam_large]
if large_indices:
    max_off_large_avg = np.mean([offdiag_maxabs[i] for i in large_indices])
    lam_large_str = f"\\lambda \\geq 10^{{-2}}"
else:
    max_off_large_avg = max_off_large
    lam_large_str = f"\\lambda = {lambdas[idx_large]:g}"

# Format lambda values in LaTeX notation
def format_lambda(lam):
    """Format lambda value as 10^{-n} for small values, or as-is for larger."""
    if lam < 1e-3:
        exp = int(np.log10(lam))
        return f"10^{{{exp}}}"
    else:
        return f"{lam:g}"

print(f"- $\\lambda = {format_lambda(lam_small)}$: max |offdiag| = {max_off_small:.3f} (almost no redundancy reduction)")
print(f"- $\\lambda = {format_lambda(lam_mid)}$: max |offdiag| = {max_off_mid:.3f} (redundancy reduction becomes effective)")
print(f"- ${lam_large_str}$: max |offdiag| $\\approx$ {max_off_large_avg:.3f} (saturated; further increasing $\\lambda$ helps little)")

print("```\n")

# Plot lambda exploration results (make readability the priority)
# We avoid a twin-y axis (it tends to look messy) and instead show:
# - Left: invariance metric vs λ
# - Right: redundancy metrics vs λ (with log-y to reveal small values)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 4.2))

# --- Panel A: invariance ---
ax1.set_xscale('log')
ax1.errorbar(
    lambdas, diag_means, yerr=diag_std,
    fmt='o-', linewidth=2, markersize=6, capsize=3, label='Diag mean'
)
ax1.axhline(1.0, color='gray', linestyle='--', alpha=0.5)
ax1.set_title('Invariance vs λ')
ax1.set_xlabel('λ (log scale)')
ax1.set_ylabel('Mean diag(C)')
ax1.grid(True, which='both', alpha=0.25)

# Focus on the interesting region automatically
lo = min(diag_means) - 3 * max(diag_std)
hi = max(diag_means) + 3 * max(diag_std)
ax1.set_ylim(max(0.0, lo), min(1.01, hi))
ax1.legend(loc='lower left', fontsize=10)

# --- Panel B: redundancy ---
# Use log-y so that "0.001 vs 0.01" is visible; add epsilon to avoid log(0).
eps = 1e-6
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.errorbar(
    lambdas, np.maximum(offdiag_means, eps), yerr=np.maximum(offdiag_std, 0.0),
    fmt='s--', linewidth=2, markersize=5, capsize=3, label='Mean |offdiag|'
)
ax2.errorbar(
    lambdas, np.maximum(offdiag_maxabs, eps), yerr=np.maximum(offdiag_max_std, 0.0),
    fmt='^--', linewidth=2, markersize=5, capsize=3, label='Max |offdiag|'
)
ax2.set_title('Redundancy vs λ')
ax2.set_xlabel('λ (log scale)')
ax2.set_ylabel('|offdiag(C)| (log scale)')
ax2.grid(True, which='both', alpha=0.25)

# Set y-limits to the data range (with padding)
y_min = max(eps, min(np.minimum(offdiag_means, offdiag_maxabs)) * 0.7)
y_max = max(offdiag_maxabs) * 1.3
ax2.set_ylim(y_min, y_max)
ax2.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig(out_dir / 'lambda_exploration.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"\nLambda exploration plot saved to: {out_dir / 'lambda_exploration.png'}")

#
# Optional: Pareto view (make x-axis non-degenerate)
# Plot invariance error vs redundancy; annotate selectively to avoid clutter.
inv_err = 1.0 - np.array(diag_means)
red_max = np.array(offdiag_maxabs)

eps_p = 1e-6
xv = np.maximum(inv_err, eps_p)
yv = np.maximum(red_max, eps_p)

fig, ax = plt.subplots(figsize=(7.0, 4.8))
ax.set_xscale('log')
ax.set_yscale('log')
ax.plot(xv, yv, 'o-', linewidth=2, markersize=7)

ax.set_xlabel('Invariance error: 1 − mean diag(C)')
ax.set_ylabel('Redundancy: max |offdiag(C)|')
ax.set_title('Pareto view: λ trade-off (error vs redundancy)')
ax.grid(True, which='both', alpha=0.3)

# Choose which points to annotate directly (small λ region + one mid + one representative large)
# This prevents the large-λ cluster from overlapping.
annotate_lams = {1e-6, 1e-5, 1e-4, 1e-3, 1e-2}
# include 1.0 as a representative of the saturated regime if present
if 1.0 in lambdas:
    annotate_lams.add(1.0)

# Draw annotations for the selected set
for i, lam in enumerate(lambdas):
    if lam not in annotate_lams:
        continue
    x, y = xv[i], yv[i]
    # Offset: push labels away from points; vary with i for readability
    dx = 14
    dy = 10 if (i % 2 == 0) else -14
    ax.annotate(
        f'λ={lam:g}',
        xy=(x, y),
        xytext=(dx, dy),
        textcoords='offset points',
        fontsize=9,
        arrowprops=dict(arrowstyle='-', alpha=0.35, lw=1.0)
    )

# For the remaining (typically large) lambdas that cluster together, show a compact legend box.
other_lams = [lam for lam in lambdas if lam not in annotate_lams]
if other_lams:
    other_txt = 'Saturated regime:\n' + ', '.join([f'λ={lam:g}' for lam in other_lams])
    ax.text(
        0.98, 0.02, other_txt,
        transform=ax.transAxes,
        ha='right', va='bottom', fontsize=9,
        bbox=dict(boxstyle='round,pad=0.35', facecolor='white', alpha=0.85, edgecolor='gray')
    )

plt.tight_layout()
plt.savefig(out_dir / 'pareto_lambda_tradeoff.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"Pareto plot saved to: {out_dir / 'pareto_lambda_tradeoff.png'}")

print("\nAdditional plots generated:")
print(f"- {out_dir / 'cov_and_corr_comparison.png'}")
print(f"- {out_dir / 'pca_eigenspectrum.png'}")
print(f"- {out_dir / 'offdiag_corr_hist.png'}")
print(f"- {out_dir / 'basis_alignment_heatmap.png'}")
print(f"- {out_dir / 'principal_angles.png'}")
print(f"- {out_dir / 'lambda_exploration.png'}")
print(f"- {out_dir / 'pareto_lambda_tradeoff.png'}")

