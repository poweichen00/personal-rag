# QueryDet: Cascaded Sparse Query for Accelerating High-Resolution Small Object Detection

**arXiv:** 2103.09136 | **License:** CC BY-NC-ND 4.0
**Authors:** Chenhongyi Yang, Zehao Huang, Naiyan Wang
**Submitted:** March 16, 2021 (revised March 24, 2022)
**Venue:** CVPR 2022

## Abstract

The researchers address challenges in detecting small objects by proposing a two-step pipeline. First, the method identifies coarse object locations using low-resolution features. Then, it computes precise detections with high-resolution features guided by those positions. This approach improves the detection mAP by 1.0 and mAP-small by 2.0 while achieving 3.0× faster inference on COCO and 2.3× acceleration on VisDrone datasets.

## Problem

High-resolution inference is essential for detecting tiny objects, but running a full-resolution detector is computationally prohibitive. For example, detecting objects in 4K drone footage at 3840×2160 pixels would require processing billions of FLOPs per frame. The key observation is that most of the image is background — objects of interest occupy less than 1% of all pixels. Standard detectors waste computation equally over background and foreground regions.

## Core Idea: Cascaded Sparse Query

QueryDet uses a coarse-to-fine approach:

1. **Coarse detection on low-resolution feature map:** Run a lightweight detector on downsampled (P5/P6) feature map to identify regions likely containing objects. Fast because the feature map is small.

2. **Sparse queries for high-resolution features:** Generate sparse spatial queries only for the candidate regions identified in step 1. These queries are projected onto the high-resolution (P2/P3) feature map using deformable attention.

3. **Fine-grained classification and localization:** The sparse high-res features are used for precise box regression and classification of small objects.

This avoids processing the full P2 feature map (which is 16× more computations than P3).

## Architecture

- **Backbone:** ResNet-50/ResNet-101 with FPN (P2, P3, P4, P5)
- **Coarse stage:** FCOS-like detector on P4 and P5; detects medium/large objects and generates candidate regions for small objects
- **Sparse query stage:** For each candidate region, extract sparse feature vectors from P2/P3 using deformable attention (K=4 sampling points per query)

## Efficiency Analysis

For a 1280×1280 image:

| Stage | Feature Resolution | Relative Operations |
|---|---|---|
| Full P2 processing | 320×320 | 100% (baseline) |
| QueryDet coarse | 40×40 (P5) | 1.6% |
| QueryDet sparse P2 queries | ~2% of P2 | ~3% |
| **QueryDet total** | - | **~5%** |

**~20× reduction in FLOPs** for the high-resolution processing stage.

## Results

- **COCO:** +1.0 mAP, +2.0 mAP-small improvement over FCOS baseline
- **COCO inference speed:** 3.0× faster than full P2 FCOS
- **VisDrone inference speed:** 2.3× faster than baseline
- Achieves similar accuracy to full P2 FCOS at 36% of the computational cost

## Query Selection Strategy

The coarse stage's confidence threshold for generating sparse queries is critical:
- Low threshold → more queries → higher recall, higher computation
- High threshold → fewer queries → risk of missing small objects
- Adaptive thresholding (start low at 0.05, increase to 0.3 for inference) improves both accuracy and efficiency

## Limitations

- Coarse detection errors propagate (missed candidate regions → missed small objects)
- Two-stage pipeline increases implementation complexity
- Less effective for isolated objects not detected in the coarse stage

## Citation

```
@inproceedings{yang2022querydet,
  title={QueryDet: Cascaded Sparse Query for Accelerating High-Resolution Small Object Detection},
  author={Yang, Chenhongyi and Huang, Zehao and Wang, Naiyan},
  booktitle={CVPR},
  year={2022}
}
```
