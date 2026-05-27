# TOOD: Task-Aligned One-Stage Object Detection

**arXiv:** 2108.07755 | **License:** CC BY 4.0
**Authors:** Chengjian Feng, Yujie Zhong, Yu Gao, Matthew R. Scott, Weilin Huang
**Submitted:** August 17, 2021 (revised August 28, 2021)
**Venue:** ICCV 2021 (Oral)

## Abstract

The paper addresses spatial misalignment between classification and localization tasks in one-stage object detectors. The authors introduce a Task-aligned Head (T-Head) that balances task-interactive and task-specific feature learning, along with Task Alignment Learning (TAL) that unifies optimal anchors during training. On MS-COCO, the method achieves 51.1 AP at single-model single-scale testing, outperforming recent detectors like ATSS, GFL, and PAA while using fewer parameters and FLOPs.

## Problem: Task Misalignment

Standard one-stage detectors use independent classification and regression branches that share the same feature backbone but produce predictions independently:
- The optimal spatial feature for **classification** (centered, fully visible object region) may differ from the optimal feature for **localization** (object boundaries)
- This misalignment causes high-confidence detections with poor localization, and good localizations with low confidence
- NMS may then suppress well-localized boxes in favor of poorly-localized high-confidence ones

## Task-Aligned Head (T-Head)

T-Head addresses misalignment through task-interactive feature learning:

1. **Shared feature extraction:** Both tasks start from the same FPN feature
2. **Task-interactive attention:** Apply attention that considers both classification and localization signals jointly before task-specific layers
3. **Task-specific prediction:** Separate classification and localization heads, but informed by shared attention

This forces the network to learn feature representations that are optimal for both tasks simultaneously, not independently.

## Task Alignment Learning (TAL)

TAL defines a unified "alignment score" that measures how well each anchor candidate serves both tasks:

`t = s^α × u^β`

Where:
- s = classification score for the anchor
- u = IoU between predicted box and ground truth
- α, β = weighting hyperparameters (default α=β=0.5)

Positive anchors are selected based on this combined score rather than geometry alone (unlike ATSS which uses only IoU statistics). This ensures that selected positive anchors are actually "good" for both classification and regression.

## Benefits for UAV Small Object Detection

1. **Better positive sample quality:** TAL's combined score selects anchors that are actually beneficial for both tasks, more critical for tiny objects where most anchors are poor
2. **Reduced false positives:** Alignment score correlation between confidence and localization reduces high-confidence mis-localizations
3. **Plug-in head:** T-Head can replace standard detection heads in any one-stage detector

## Results

| Method | AP (COCO) |
|---|---|
| ATSS | 43.6 |
| GFL | 45.0 |
| PAA | 44.8 |
| TOOD | 51.1 |

TOOD outperforms ATSS by 7.5 AP on COCO while using similar compute.

## Integration with YOLO

TOOD's TAL has been adopted in YOLOv8 and YOLOv9 as the default label assignment strategy (SimOTA was replaced by TAL in YOLOv8). This shows the practical impact of task-aligned training.

## Citation

```
@inproceedings{feng2021tood,
  title={TOOD: Task-aligned One-stage Object Detection},
  author={Feng, Chengjian and Zhong, Yujie and Gao, Yu and Scott, Matthew R. and Huang, Weilin},
  booktitle={ICCV},
  year={2021}
}
```
