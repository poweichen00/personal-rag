# Scale Optimization Using Evolutionary Reinforcement Learning for Object Detection on Drone Imagery

**arXiv:** 2312.15219 | **License:** CC BY 4.0
**Authors:** Jialu Zhang, Xiaoying Yang, Wentao He, Jianfeng Ren, Qian Zhang, Titian Zhao, Ruibin Bai, Xiangjian He, Jiang Liu
**Submitted:** December 23, 2023
**Venue:** AAAI 2024

## Abstract

Object detection in aerial imagery presents a significant challenge due to large scale variations among objects. This paper proposes an evolutionary reinforcement learning agent, integrated within a coarse-to-fine object detection framework, to optimize the scale for more effective detection of objects in such images. The approach includes patch generation, reward mechanisms measuring localization and label accuracy with scale consistency, a spatial-semantic attention mechanism, and combines proximal policy optimization with evolutionary strategy. Results on VisDrone dataset achieve AP of 42.2%, an improvement of 1.9% over the previous best model AdaZoom.

## Motivation

Scale variation is one of the most severe challenges in UAV object detection. Objects at different distances from the drone appear at vastly different scales — from 3×3 pixels (distant pedestrians) to 200×200 pixels (nearby vehicles). Fixed-scale inference misses tiny objects while wasting computation on large background regions. Adaptive scale selection can focus compute on regions where it matters most.

## Core Approach: Evolutionary Reinforcement Learning for Scale

### Framework Overview

The method operates in a coarse-to-fine manner:
1. **Coarse detection:** Run a lightweight detector on the full image to identify candidate regions
2. **RL agent:** A reinforcement learning agent decides which regions to zoom into and at what scale
3. **Fine detection:** Run a more powerful detector on the selected zoomed regions
4. **Aggregation:** Merge detections from full-image and zoomed passes

### Evolutionary Reinforcement Learning (ERL)

Combines two optimization paradigms:
- **Proximal Policy Optimization (PPO):** Gradient-based RL for stable policy learning; optimizes current policy based on reward signal
- **Evolutionary Strategy (ES):** Population-based search that maintains diversity; explores novel scale selection policies

The combination avoids local optima (PPO's weakness) while maintaining sample efficiency (ES's weakness). ERL finds optimal scale selection policies that neither pure gradient descent nor random search alone would discover.

### Reward Function

The reward for each scale selection decision measures:
1. **Localization accuracy:** IoU between detected boxes and ground truth
2. **Label accuracy:** Classification confidence for detected objects
3. **Scale consistency:** Penalty for selecting inconsistent scales for nearby objects of similar size

### Spatial-Semantic Attention

A dual-path attention mechanism conditions scale decisions on:
- **Spatial features:** What parts of the image contain objects (from coarse detection)
- **Semantic features:** What type of objects are present (affects optimal viewing scale)

A car cluster requires different optimal scale than a pedestrian crowd.

## Results

### VisDrone Dataset

| Method | AP |
|---|---|
| FCOS baseline | 21.4 |
| TPH-YOLOv5 | 38.0 |
| AdaZoom (previous best adaptive) | 40.3 |
| ERL Scale Opt (this work) | 42.2 |

**+1.9% AP over AdaZoom** while maintaining similar inference time budget.

### Why ERL Outperforms Fixed Scale

Fixed-scale methods allocate equal compute to all image regions. ERL allocates more compute (higher resolution, more detector passes) to object-dense regions, particularly effective for:
- Scenes with extreme scale variation
- Images where one altitude (scale) dominates object appearance
- Temporally consistent video sequences where scale policies can be learned per scene type

## Computational Efficiency

- ERL policy inference: <5ms overhead per image
- Selective zooming: typically 2-4 high-resolution passes per image (vs. 12+ for full SAHI)
- Net result: better accuracy than fixed-scale methods at lower compute than exhaustive slicing

## Connection to Related Work

- Similar to SAHI but uses learned policies rather than fixed slicing grids
- Similar to QueryDet's coarse-to-fine idea but at image scale level rather than feature map level
- Complements cluster-based approaches (ClusDet) by optimizing the scale of each cluster crop

## Citation

```
@inproceedings{zhang2024erl,
  title={Scale Optimization Using Evolutionary Reinforcement Learning for Object Detection on Drone Imagery},
  author={Zhang, Jialu and Yang, Xiaoying and He, Wentao and Ren, Jianfeng and Zhang, Qian and Zhao, Titian and Bai, Ruibin and He, Xiangjian and Liu, Jiang},
  booktitle={AAAI},
  year={2024}
}
```
