# Feature Pyramid Networks for Object Detection

**arXiv:** 1612.03144 | **License:** CC BY 4.0
**Authors:** Tsung-Yi Lin, Piotr Dollár, Ross Girshick, Kaiming He, Bharath Hariharan, Serge Belongie
**Submitted:** December 9, 2016 (revised April 19, 2017)
**Venue:** CVPR 2017

## Abstract

The paper addresses multi-scale object detection by leveraging the hierarchical structure of deep convolutional networks to construct feature pyramids efficiently. The authors propose a top-down architecture with lateral connections called a Feature Pyramid Network (FPN) that generates semantic feature maps across all scales. When integrated with Faster R-CNN, the method achieves state-of-the-art performance on the COCO benchmark, operates at 5 FPS on GPU hardware, and represents a practical and accurate solution to multi-scale object detection.

## Core Architecture

### Bottom-Up Pathway
Standard backbone (ResNet) forward pass, producing feature maps at different resolutions:
- C2: stride 4 (from res2)
- C3: stride 8 (from res3)
- C4: stride 16 (from res4)
- C5: stride 32 (from res5)

### Top-Down Pathway
Starting from C5 (semantically rich but spatially coarse), progressively upsample and merge with lower-level features:
- P5 = conv1×1(C5)
- P4 = conv1×1(C4) + upsample(P5)
- P3 = conv1×1(C3) + upsample(P4)
- P2 = conv1×1(C2) + upsample(P3)
- Each Pi passed through a 3×3 conv to reduce aliasing effects

### Lateral Connections
1×1 convolution on each Ci to standardize channel dimensions (typically to 256) before merging with upsampled Pi+1.

### Detection Heads
Separate detection heads at each Pi:
- P2/P3: detects small objects (stride 4-8)
- P4: medium objects (stride 16)
- P5: large objects (stride 32)
- Optional P6: extra-large objects (stride 64)

## Key Insight

Without FPN, a deep CNN's feature map at stride 32 has rich semantics but poor spatial resolution for tiny objects. FPN creates a multi-scale feature hierarchy that is semantically strong at every scale, enabling accurate detection across all object sizes in a single forward pass.

## Why FPN is Foundational for UAV Detection

All major UAV detection methods build upon FPN:
- **TPH-YOLOv5:** BiFPN-like neck with extra P2 head
- **FCOS:** Multi-level FPN (P3-P7) for anchor-free detection
- **QueryDet:** FPN + sparse attention for efficient high-resolution detection
- **Deformable DETR:** Multi-scale FPN features as encoder input
- **SlimNeck/GSConv:** Lightweight replacement for FPN neck modules

The P2 detection head (stride 8, 320×320 features for 1280×1280 input) is especially critical for UAV tiny objects (<16px).

## FPN Variants for UAV Detection

| Variant | Key Change | Benefit |
|---|---|---|
| PANet | Adds bottom-up path | Better information flow |
| BiFPN | Weighted bidirectional | Learnable cross-scale fusion |
| Gold-YOLO neck | Gather-distribute mechanism | Better small object context |
| SlimNeck | GSConv lightweight | Edge deployment efficiency |
| Extra P2 head | Stride-4 detection | Tiny object coverage |

## Integration with Faster R-CNN Results

On COCO test-dev:
- Faster R-CNN + FPN (ResNet-101): 36.2 AP, 59.1 AP50
- Faster R-CNN (no FPN, ResNet-101): 25.2 AP, 45.0 AP50
- **+11 AP improvement from FPN alone**

## Citation

```
@inproceedings{lin2017fpn,
  title={Feature Pyramid Networks for Object Detection},
  author={Lin, Tsung-Yi and Doll{\'a}r, Piotr and Girshick, Ross and He, Kaiming and Hariharan, Bharath and Belongie, Serge},
  booktitle={CVPR},
  year={2017}
}
```
