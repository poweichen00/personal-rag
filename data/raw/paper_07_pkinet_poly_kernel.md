# Poly Kernel Inception Network for Remote Sensing Detection

**arXiv:** 2403.06258 | **License:** CC BY 4.0
**Authors:** Xinhao Cai, Qiuxia Lai, Yuwei Wang, Wenguan Wang, Zeren Sun, Yazhou Yao
**Submitted:** March 10, 2024 (revised March 20, 2024)
**Venue:** IEEE CVPR 2024

## Abstract

Object detection in remote sensing images (RSIs) often suffers from several increasing challenges, including the large variation in object scales and the diverse-ranging context. The paper proposes PKINet, which employs multi-scale convolution kernels without dilation to extract object features of varying scales and capture local context. Additionally, a Context Anchor Attention module captures long-range contextual information, with both components working together to improve performance across DOTA-v1.0, DOTA-v1.5, HRSC2016, and DIOR-R benchmarks.

## Motivation

Remote sensing and UAV imagery present a unique multi-scale challenge: objects span multiple orders of magnitude in apparent size within a single image. Standard convolutional kernels (3×3) have fixed receptive fields inadequate for simultaneously encoding tiny vehicles and large runways. PKINet introduces Poly Kernel (PK) convolutions and Context Anchor Attention (CAA) as new primitives optimized for this challenge.

## Architecture

### Poly Kernel Inception (PKI) Module

The PKI module replaces standard convolutions with parallel depthwise convolutions of different kernel sizes:

- Branch k=3: standard 3×3 DWConv
- Branch k=5: 5×5 DWConv
- Branch k=7: 7×7 DWConv
- Branch k=9: 9×9 DWConv
- Branch k=1: identity (channel mixing)

All branches use depthwise separable convolutions for efficiency. Outputs are concatenated and fused via a 1×1 pointwise convolution.

### Context Anchor Attention (CAA)

A lightweight attention mechanism that reweights feature channels based on global context, using global average pooling followed by squeeze-excite layers. CAA helps the network focus on scale-relevant features given global scene context.

## Key Design Insights

1. **Variable kernel sizes model scale diversity:** Tiny objects use k=3 branches; large objects use k=7/9 branches
2. **Depthwise convolutions are critical:** Standard k=9 convolution would multiply parameters by 27× — depthwise keeps it tractable
3. **Context matters for scale disambiguation:** CAA implicitly conditions scale selection on global scene understanding

## Results

### DOTA-v1.0 (Oriented Object Detection)

| Method | mAP | Params |
|---|---|---|
| Oriented R-CNN (ResNet50) | 75.87 | 41M |
| PKINet-S | 79.35 | 23M |
| PKINet-T | 77.12 | 14M |
| PKINet-B | 82.04 | 51M |

PKINet-S achieves higher accuracy than ResNet-101 while using 43% fewer parameters.

## Benchmarks

Evaluated on: DOTA-v1.0, DOTA-v1.5, HRSC2016, DIOR-R

## Citation

```
@inproceedings{cai2024pkinet,
  title={Poly Kernel Inception Network for Remote Sensing Detection},
  author={Cai, Xinhao and Lai, Qiuxia and Wang, Yuwei and Wang, Wenguan and Sun, Zeren and Yao, Yazhou},
  booktitle={CVPR},
  year={2024}
}
```
