# FCOS: Fully Convolutional One-Stage Object Detection

**arXiv:** 1904.01355 | **License:** CC BY-NC-SA 4.0
**Authors:** Zhi Tian, Chunhua Shen, Hao Chen, Tong He
**Submitted:** April 2, 2019 (revised August 20, 2019)
**Venue:** ICCV 2019 (13 pages)
**Code:** Available on GitHub

## Abstract

The authors present an anchor-free object detection approach that operates on a per-pixel prediction fashion, analogue to semantic segmentation. Unlike conventional detectors relying on predefined anchor boxes, their method eliminates such anchors and their associated hyperparameters, reducing computational overhead. Using ResNeXt-64x4d-101, the detector achieved 44.7% in AP with single-model and single-scale testing, outperforming comparable one-stage methods while maintaining architectural simplicity.

## Core Idea: Per-Pixel Box Prediction

At each spatial location (x, y) in a feature map:
- **Classification:** Predict class probability vector
- **Regression:** Predict (l, r, t, b) — distances to the left, right, top, bottom edges of the nearest ground truth box
- **Centerness:** Predict a centerness score to down-weight off-center predictions

### Centerness Branch

The centerness score penalizes predictions far from the object center:
`centerness* = sqrt((min(l*,r*)/max(l*,r*)) × (min(t*,b*)/max(t*,b*)))`

This is a scalar ∈ [0, 1]. During inference, the final score is classification_score × centerness, effectively suppressing low-quality off-center detections without NMS tuning.

### FPN for Multi-Scale

FCOS uses all 5 FPN levels (P3-P7) for detection:
- Objects of different sizes are assigned to different FPN levels based on the regression target scale
- No anchors needed — each level handles objects within a predefined size range

## Why FCOS is Important for UAV Detection

1. **No anchor clustering:** Standard anchor-based methods require dataset-specific anchor clustering for UAV data (tiny anchor sizes). FCOS eliminates this
2. **More positive samples:** Every pixel within an object is a positive sample (vs. only matched anchors), critical for tiny objects with few pixels
3. **Easy integration with improved label assignment:** RFLA replaces FCOS's centerness-based assignment with Gaussian receptive field assignment, directly improving tiny object handling
4. **Simplicity:** Fewer hyperparameters means easier adaptation to new UAV datasets

## Results

| Backbone | AP | AP50 | AP75 | AP_S |
|---|---|---|---|---|
| ResNet-50 | 38.7 | 57.4 | 41.9 | 22.2 |
| ResNeXt-64x4d-101 | 44.7 | 64.1 | 48.4 | 27.5 |

## FCOS on VisDrone

FCOS baseline on VisDrone achieves ~21.4 AP. Combined with:
- RFLA: +6.5 AP (→ 27.9 AP)
- High resolution (1280×1280): +8 AP
- Extra P2 head: +2 AP for tiny objects

## Comparison with Anchor-Based Methods

| Aspect | FCOS (anchor-free) | RetinaNet (anchor-based) |
|---|---|---|
| Anchor tuning | Not needed | Required per dataset |
| Positive samples | All pixels in GT box | Only matched anchors |
| Small object handling | Better with proper sampling | Depends on anchor config |
| Training stability | Centerness helps | IoU threshold matters |

## Citation

```
@inproceedings{tian2019fcos,
  title={FCOS: Fully Convolutional One-Stage Object Detection},
  author={Tian, Zhi and Shen, Chunhua and Chen, Hao and He, Tong},
  booktitle={ICCV},
  year={2019}
}
```
