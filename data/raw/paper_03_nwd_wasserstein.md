# A Normalized Gaussian Wasserstein Distance for Tiny Object Detection

**arXiv:** 2110.13389 | **License:** CC BY 4.0
**Authors:** Jinwang Wang, Chang Xu, Wen Yang, Lei Yu
**Submitted:** October 26, 2021 (revised June 14, 2022)
**Venue:** ISPRS Journal of Photogrammetry and Remote Sensing (journal version)
**Code:** Publicly available

## Abstract

Detecting tiny objects is a very challenging problem since a tiny object only contains a few pixels in size. The authors observe that intersection-over-union metrics prove problematic for small objects due to sensitivity to locational shifts. They introduce the Normalized Wasserstein Distance (NWD), which represents bounding boxes as 2D Gaussian distributions to measure similarity. This metric integrates into anchor-based detectors for assignment, suppression, and loss calculations. Testing on the AI-TOD dataset demonstrates improvements of 6.7 AP points over baseline fine-tuning and 6.0 AP points above competing approaches.

## Problem: IoU Failure for Tiny Objects

IoU has three fundamental failure modes for tiny object detection:

1. **Zero IoU for non-overlapping predictions:** A predicted box 2 pixels away from a 5×5 ground truth box has IoU = 0, even though the prediction is geometrically very close. This provides no gradient signal during training.
2. **High sensitivity to small displacements:** A 1-pixel translation of a 4×4 box can change IoU from 1.0 to 0.0. This causes training instability.
3. **IoU ignores scale context:** The closeness of two 4×4 boxes 3 pixels apart should be evaluated differently than two 400×400 boxes 3 pixels apart, but standard IoU treats them identically.

## Core Contribution: Normalized Wasserstein Distance (NWD)

NWD models each bounding box as a 2D Gaussian distribution and measures the distance between two Gaussians using the Wasserstein-2 distance, normalized to [0, 1].

### Box-to-Gaussian Mapping

A bounding box (cx, cy, w, h) is mapped to a Gaussian: N(μ, Σ) where μ = [cx, cy]ᵀ, Σ = diag([w/2, h/2]²). This treats the bounding box as the 1-σ confidence region of the Gaussian.

### Normalized Distance Formula

NWD(b₁, b₂) = exp(-W₂(b₁, b₂) / C)

Where C is a dataset-specific constant (typically 12.8 for VisDrone) and W₂ is the Wasserstein-2 distance. NWD = 1 means perfect alignment; NWD approaching 0 means maximally dissimilar.

## Usage

NWD can replace IoU as the matching score in any label assignment strategy and also serve as a regression loss:
- Replace IoU threshold in ATSS → NWD threshold
- Use as a regression loss: L_NWD = 1 - NWD(b_pred, b_gt)

## Key Results

- **AI-TOD dataset:** +6.7 AP improvement over fine-tuned baseline
- **VisDrone:** +3 AP improvement when integrated with ATSS
- Provides smooth gradients even when prediction and ground truth do not overlap
- Computationally simple: O(1) per box pair

## Citation

```
@article{wang2021nwd,
  title={A Normalized Gaussian Wasserstein Distance for Tiny Object Detection},
  author={Wang, Jinwang and Xu, Chang and Yang, Wen and Yu, Lei},
  journal={arXiv preprint arXiv:2110.13389},
  year={2021}
}
```
