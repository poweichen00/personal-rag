# Large Selective Kernel Network for Remote Sensing Object Detection

**arXiv:** 2303.09030 | **License:** CC BY 4.0
**Authors:** Yuxuan Li, Qibin Hou, Zhaohui Zheng, Ming-Ming Cheng, Jian Yang, Xiang Li
**Submitted:** March 16, 2023 (revised March 20, 2023)
**Venue:** ICCV 2023 (pages 16794-16805)
**Code:** Available on GitHub

## Abstract

The paper addresses remote sensing object detection by proposing LSKNet, which dynamically adjusts its large spatial receptive field to better model the ranging context of various objects in remote sensing scenarios. The authors note this marks the initial exploration of large and selective kernel mechanisms in this domain. The method achieves state-of-the-art results on three benchmarks: HRSC2016 (98.46% mAP), DOTA-v1.0 (81.85% mAP), and FAIR1M-v1.0 (47.87% mAP).

## Motivation

Remote sensing images pose distinct challenges: objects at different distances from the sensor appear at vastly different scales, and local context alone is insufficient for reliable object recognition. A tiny car near a road may be confused with background, while a ship far from water can be identified by its context. LSKNet proposes that the spatial receptive field should be dynamically adjusted per object, not fixed for all spatial locations.

## Core Innovation: Large Selective Kernel (LSK) Mechanism

Unlike SKNet which performs channel-wise kernel selection, LSKNet introduces spatial-dimension selective kernel aggregation:

1. **Large kernel sequence:** Apply multiple large depthwise convolutions (k=5, k=7, k=9, k=11) in sequence using kernel decomposition (e.g., 5×5 = 1×5 + 5×1)
2. **Spatial selective aggregation:** Learn input-dependent weights to combine outputs at each spatial location
3. **Dynamic receptive field:** Each spatial position adaptively selects how much context to incorporate based on local content

This is more intuitive than channel-wise selection because different objects at different spatial positions need different context sizes.

## Architecture

```
Input feature map
  → Large depthwise conv (k=5)
  → Large depthwise conv (k=7)
  → Spatial selective aggregation (learned weights per position)
  → Fused feature map with dynamic receptive field
```

## Key Results

| Benchmark | Metric | LSKNet Score |
|---|---|---|
| HRSC2016 | mAP | 98.46% |
| DOTA-v1.0 | mAP (OBB) | 81.85% |
| FAIR1M-v1.0 | mAP | 47.87% |

Sets new state-of-the-art scores on all three benchmarks without additional bells and whistles.

## Competition Achievement

Based on the LSK technique, the authors ranked **2nd place in the 2022 Greater Bay Area International Algorithm Competition**.

## Extended Work

A follow-up paper, "LSKNet: A Foundation Lightweight Backbone for Remote Sensing" (arXiv: 2403.11735), proposes a lightweight LSKNet backbone for classification, object detection, and semantic segmentation, achieving new SOTA across all three tasks.

## Comparison with PKINet

Both LSKNet and PKINet address multi-scale challenges in remote sensing:
- LSKNet: dynamic large kernel selection per spatial position
- PKINet: fixed multi-scale poly kernel inception with context attention
- PKINet-B slightly outperforms LSKNet on DOTA (82.04 vs 81.85 mAP)

## Citation

```
@inproceedings{li2023lsknet,
  title={Large Selective Kernel Network for Remote Sensing Object Detection},
  author={Li, Yuxuan and Hou, Qibin and Zheng, Zhaohui and Cheng, Ming-Ming and Yang, Jian and Li, Xiang},
  booktitle={ICCV},
  year={2023}
}
```
