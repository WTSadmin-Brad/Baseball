# Phase 1: Ryan Gunther Deep Dive & Technical Evaluation

This document answers the core questions outlining how the research from Ryan Gunther's computational statistics master's thesis and independent computer vision projects scales into our broader baseball pipeline.

## 1. Can we replicate his dimensionality reduction in Python?

**Yes, the methodology maps seamlessly to the Python data science stack.**

### Core Implementation
Gunther's pipeline relies on two major mathematical operations implemented in `DimensionalityReductionBiomechData.R` and `dynamic_PPCA_pipeline.R`:

1.  **Principal Feature Analysis (PFA)**: Using Principal Component Analysis (PCA) combined with K-Means clustering to isolate the optimal marker subset.
2.  **Probabilistic PCA (PPCA)**: Building dynamic, local linear segmentations of the swing using a sliding window. It evaluates breakpoints using the Mahalanobis distance matched against a Chi-squared threshold.

### Python Translation Plan
Migrating these implementations involves mapping the algorithms to `numpy` and `scikit-learn`.

```python
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import chi2

# 1. PCA + K-Means Mapping
# In R: sv <- svd(D), then km <- kmeans(W, centers = K)
pca = PCA(n_components=0.99) # Keep 99% of variance
transformed = pca.fit_transform(Y_centered)
weights = np.abs(pca.components_.T) # Equivalent to W in the R script
kmeans = KMeans(n_clusters=K, n_init=150, random_state=42).fit(weights)

# 2. Mahalanobis distance & Chi-Squared Threshold
# In R: chi_thresh <- infl * qchisq(q, df = T * p) / T
infl = 1000  # Scaling factor used in Gunther's script
chi_thresh = infl * chi2.ppf(0.99, df=T * p) / T

# PPCA Covariance Tracking
# You can efficiently build segment evaluations using np.cov without needing a dedicated PPCA module
mu = np.mean(segment_data, axis=0)
diffs = probe_data - mu
# Calculate Mahalanobis distances
H_vals = np.sum(diffs.dot(np.linalg.inv(cov_matrix)) * diffs, axis=1)
H_avg = np.mean(H_vals)

if H_avg > chi_thresh:
    # Trigger swing state change (breakpoint detected)
    pass
```

> [!TIP]
> **Performance Edge**: The dynamic sliding window in Python is functionally identical but can be significantly sped up by caching covariance matrices and avoiding matrix inversion bottlenecks (using `np.linalg.solve` or Cholesky decomposition rather than `np.linalg.inv`).

---

## 2. What specific covariance structures predict bat speed/exit velo?

Gunther evaluates the predictive value of dynamic segments in `feat_vec_LASSO.R` by extracting feature vectors (covariances + means) and passing them into a Lasso regression model (`cv.glmnet`).

**Findings:**
*   **The Model Structure:** He extracted the upper triangle of the 18×18 covariance matrix (171 values) along with 18 means, representing each clustered behavior segment.
*   **Exit Velocity is Difficult:** The Lasso model failed to establish a strong, low-RMSE linear correlation between the pure marker covariance structures and Exit Velocity.
*   **Why?** Exit velocity is heavily reliant on factors invisible to marker skeletons: collision physics, contact quality (topping/bottoming), pitch velocity, and bat mass properties.
*   **Bat Speed Results:** The covariances *did* have value indicating "more efficient and less efficient ways to move." 

> [!IMPORTANT]
> **Implications for Our Project:** Replicating the Lasso model against Exit Velocity directly is likely a dead end. However, applying these covariance feature vectors to evaluate *Bat Speed* and *Kinematic Efficiency* remains a highly promising vector for our deep learning heuristics.

---

## 3. How does his SAM2 pipeline improve on standard pose estimation?

Gunther's experiments in `SAM2_isomap_pipeline.ipynb` represent a significant departure from standard point-based pose estimation (e.g., MediaPipe or YOLO-Pose).

### The Standard Approach
Traditional pose estimation maps sparse 2D coordinates (ankles, hips, elbows). It is lightweight but fully sacrifices body volume, structural depth, and micro-postures (like wrist angle or torso twist).

### The SAM2 / Isomap Architecture
1.  **Dense Segmentation**: Uses Facebook's Segment Anything Model 2 (SAM2) localized by manual prompts to generate a highly accurate, frame-by-frame binary silhouette mask of the hitter.
2.  **Distance Transformation**: Replaces the binary mask with an $L_2$ Distance Transform (producing continuous gradients or "magma" maps). This weights the dense center of mass higher than the noisy extremities of the silhouette.
3.  **Dimensionality Reduction**: Passes the high-dimensional transformed mask data through **Isomap** (a non-linear manifold learning technique dependent on neighborhood graphs).
4.  **2D Trajectory Output**: Reduces the entire shape-changing swing into a continuous geometric curve on a 2-dimensional grid (Component 1 vs. Component 2), effectively turning the swing sequence into a trajectory.
5.  **Dynamic Time Warping (DTW)**: Compares the swing trajectory distances between players directly using DTW.

> [!NOTE]
> By processing the *entire silhouette mask* into a continuous 2D manifold rather than connecting 18 keypoints, the system implicitly models mass shift, limb thickness, bat orientation, and holistic posture states that point-graphs completely miss.

---

## 4. Minimum marker set needed for accurate swing reconstruction?

A core goal of Gunther's thesis was to establish the minimum tracking dependencies necessary to capture highly correlated biomechanics. Using a recursive testing loop dropping "least important" markers via K-means clustering (PFA), he successfully reconstructed complete Driveline open biomechanics dataset swings using just **6 markers (18 dimensions)**.

### The 6 Critical Points:
1.  **Left Ankle** (`LANK`)
2.  **Front of Left Hip** (`LASI`)
3.  **Right Inner Knee** (`RMKNE`)
4.  **Right Wrist** (`RWRA` or `RWRB`)
5.  **Bat Marker 1** (The Knob/Lower Handle)
6.  **Bat Marker 2** (The Barrel)

By projecting from these 6 points, the local linear models generated by his probabilistic PCA segments correctly calculate the hidden offsets for all remaining bodily joints (shoulders, backfoot, head).

> [!CAUTION]
> **For Project Integration**: If we move toward our own custom 3D kinematics inference later, we do *not* need to predict a complex 30+ point skeleton. A simpler neural network architecture trained explicitly on generating 3D spaces for these 6 specific locations will be significantly more robust and cheaper to train, allowing mathematical reconstruction of the remaining geometry.
