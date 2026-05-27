# RFLA: Gaussian Receptive Field Based Label Assignment for Tiny Object Detection

**arXiv:** 2208.08738 | **License:** CC BY 4.0
**Authors:** Chang Xu, Jinwang Wang, Wen Yang, Huai Yu, Lei Yu, Gui-Song Xia
**Submitted:** August 18, 2022 (revised October 17, 2022)
**Venue:** ECCV 2022
**Code:** Available at GitHub (mmdet-rfla)

## Abstract

The paper addresses tiny object detection, noting that standard detectors perform poorly on this task. The authors identify that conventional label assignment methods — whether anchor-based or anchor-free — create many outlier cases for small objects. They propose RFLA, which leverages the prior information that the feature receptive field follows Gaussian distribution. Instead of IoU-based assignment, they introduce Receptive Field Distance to measure similarity between the Gaussian receptive field and ground truth. A Hierarchical Label Assignment module balances learning across object sizes. Testing on four datasets shows significant improvements, including 4.0 AP points on the AI-TOD dataset.

## Problem

Label assignment is a critical component of modern object detectors. For standard-sized objects, IoU between anchor boxes and ground truth is an effective assignment criterion. However, for tiny objects (e.g., < 16×16 pixels), the absolute pixel area is so small that even a 1-pixel shift in predicted box location can reduce IoU from 1.0 to 0.0. This causes extreme instability during training.

## Core Contribution

RFLA replaces IoU-based assignment with a Gaussian distribution centered on each ground truth box. The key idea is to model each detector's receptive field as a 2D Gaussian distribution, and assign positive labels to anchors whose Gaussian distributions significantly overlap with the ground-truth Gaussian.

- **Receptive Field Distance (RFD):** Measures similarity between Gaussian receptive field and ground truth Gaussian
- **Hierarchical Label Assignment:** Balances learning across object sizes by assigning different weights to different scale levels
- **Plug-in design:** Compatible with any anchor-free detector (FCOS, ATSS, GFL) without architectural changes

## Key Results

- **AI-TOD dataset:** +4.0 AP improvement over baseline anchor-free methods
- **VisDrone-DET2021:** Significant improvements over FCOS and ATSS baselines
- The improvement is most significant for very tiny objects (< 8×8 pixels) where standard IoU-based assignment fails entirely
- RFLA provides stable gradient signal even when predicted boxes do not overlap with ground truth

## Why RFLA Works

1. **Stable gradient signal:** Gaussian overlap provides smooth gradients even for tiny objects, unlike IoU which has a cliff-edge at 0
2. **More positive samples:** The Gaussian falloff assigns fractional positive weights to nearby cells, effectively increasing positive sample density
3. **Scale-aware assignment:** Different FPN levels have different receptive field sizes (σ), naturally aligning scale-level assignment with object size

## Applicability

RFLA is a plug-in replacement for the assignment module in any anchor-free detector including FCOS, ATSS, and GFL. No architecture changes are needed beyond modifying the label assignment logic.

## Citation

```
@inproceedings{xu2022rfla,
  title={RFLA: Gaussian Receptive Field based Label Assignment for Tiny Object Detection},
  author={Xu, Chang and Wang, Jinwang and Yang, Wen and Yu, Huai and Yu, Lei and Xia, Gui-Song},
  booktitle={ECCV},
  year={2022}
}
```
