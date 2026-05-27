# LAM-YOLO: Drones-based Small Object Detection on Lighting-Occlusion Attention Mechanism YOLO

**arXiv:** 2411.00485 | **License:** CC BY 4.0
**Authors:** Yuchen Zheng, Yuxin Jing, Jufeng Zhao, Guangmang Cui
**Submitted:** November 1, 2024

## Abstract

The authors address challenges in drone-based object detection, including dense target overlap and reduced visibility under varying lighting. Their proposed model incorporates three main contributions: a light-occlusion attention mechanism to enhance small target visibility, Involution modules to strengthen feature layer interactions, and an improved SIB-IoU loss function for faster convergence and better localization. The approach also introduces auxiliary detection heads for smaller-scale targets. Testing on the VisDrone2019 dataset demonstrates performance gains of 7.1% in average precision compared to baseline YOLOv8, with improvements over competing methods like Faster R-CNN and YOLOv10.

## Motivation

Standard UAV object detectors (including YOLOv8) struggle with two specific challenges in real-world drone footage:

1. **Lighting variation:** Objects under shadow, overexposure, or low-light conditions have dramatically different visual appearances. A car at dusk looks very different from the same car at noon.
2. **Occlusion from overlap:** Dense urban scenes with hundreds of pedestrians and vehicles create layered occlusion that standard detectors fail to resolve.

## Key Contributions

### 1. Lighting-Occlusion Attention Mechanism (LAM)

LAM is a dual-path attention module designed to handle both lighting and occlusion challenges simultaneously:

- **Lighting branch:** Learns adaptive luminance normalization using spatial attention along the illumination gradient
- **Occlusion branch:** Uses depth-aware spatial attention to distinguish foreground (partially visible) objects from background
- **Fusion:** Learned weighted combination of both attention maps

The combined attention reweights feature maps to suppress poorly-lit or occluded background while amplifying object-relevant features.

### 2. Involution Modules

Involution (Ding et al., 2021) generates spatially-specific convolutional kernels, unlike standard convolution which uses the same kernel at all positions:
- More location-specific feature extraction
- Improves interaction between overlapping object features
- Reduces parameter count compared to standard convolution for same receptive field

### 3. Improved SIB-IoU Loss

SIB-IoU (Spatially Informed Bounded IoU) extends standard IoU loss to handle tiny objects:
- Adds a scale-aware penalty for objects below a size threshold
- Incorporates boundary sensitivity for accurate localization of small objects
- Faster convergence in early training epochs compared to CIoU or DIoU losses

### 4. Auxiliary Small-Scale Detection Heads

Additional detection heads specifically targeting objects <16×16 pixels:
- Extra stride-8 head for very small objects
- Similar to TPH-YOLOv5's approach but integrated with LAM attention

## Results on VisDrone2019

- **+7.1% average precision** compared to baseline YOLOv8
- Outperforms: Faster R-CNN, YOLOv9, YOLOv10
- Evaluated on VisDrone2019 DET task (10 categories)

## Comparison with Related Work

| Method | Innovation | AP on VisDrone |
|---|---|---|
| YOLOv8 (baseline) | — | ~29% |
| TPH-YOLOv5 | Transformer heads | ~39% |
| LAM-YOLO | Lighting+occlusion attention | YOLOv8 + 7.1% |

## Practical Significance

LAM-YOLO is specifically designed for real-world drone deployment scenarios where lighting changes across the day and objects occlude each other in dense urban environments. This makes it more robust than methods evaluated only under controlled lighting.

## Citation

```
@article{zheng2024lamyolo,
  title={LAM-YOLO: Drones-based Small Object Detection on Lighting-Occlusion Attention Mechanism YOLO},
  author={Zheng, Yuchen and Jing, Yuxin and Zhao, Jufeng and Cui, Guangmang},
  journal={arXiv preprint arXiv:2411.00485},
  year={2024}
}
```
