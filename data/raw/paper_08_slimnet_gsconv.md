# Slim-Neck by GSConv: A Lightweight-Design for Real-Time Detector Architectures

**arXiv:** 2206.02424 | **License:** CC BY 4.0
**Authors:** Hulin Li, Jun Li, Hanbing Wei, Zheng Liu, Zhenfei Zhan, Qiliang Ren
**Submitted:** June 6, 2022 (revised July 2, 2024)
**Code:** Available on GitHub

## Abstract

The authors present GSConv, a novel lightweight convolutional technique designed to reduce model size while preserving accuracy for real-time object detection on edge devices. They introduce Slim-Neck (SNs), a design approach built on GSConv that improves computational efficiency in real-time detectors. Their method achieves competitive performance: 70.9% AP50 for the SODA10M at a speed of ~100FPS on a Tesla T4 compared to baseline approaches.

## Motivation

The neck of a detection network (PAN, BiFPN) is responsible for multi-scale feature fusion. In standard architectures like YOLOv5 and YOLOv7, neck modules use full convolutional layers that are computationally expensive. For UAV-based small object detection requiring edge deployment (onboard compute), the neck often represents 40-60% of total model parameters. GSConv reduces neck computation while maintaining or improving feature fusion quality.

## GSConv: Group Separable Convolution

GSConv is a drop-in replacement for standard convolutional blocks in the neck:

**Design:**
1. 1×1 Conv: C → C/2 (pointwise, mixes channel info)
2. Depthwise 3×3 Conv on C/2 channels (spatial filtering)
3. Shuffle channels between the two halves
4. Concatenate: [conv half] + [identity half] → C channels
5. 1×1 Conv: C → C (fusion)

**Efficiency:** GSConv reduces neck parameters by ~5.7× compared to standard convolution at equal channel count. The channel shuffle operation (from ShuffleNet) allows depthwise-processed and identity channels to exchange information without additional parameters.

## Slim-Neck Architecture

SlimNeck applies GSConv throughout the neck module, replacing C3/CSP modules used in YOLOv5's neck with GSConv blocks, reducing parameters while maintaining accuracy.

## Results

- **70.9% AP50** on SODA10M at **~100 FPS** on Tesla T4
- Significantly reduced model size compared to standard necks (up to 5.7× fewer neck parameters)
- Competitive performance on COCO and VisDrone benchmarks
- Improved FPS on edge hardware (Jetson series)

## Application for UAV Edge Deployment

GSConv addresses UAV deployment constraints:
- **Memory bandwidth:** Large feature maps on edge devices
- **Parameter count:** Limited SRAM
- **Compute:** Limited FLOP budget per frame

SlimNeck is the preferred neck design for real-time UAV applications requiring onboard inference.

## VoVGSCSP Module

For deeper neck feature extraction, the authors propose VoVGSCSP, which combines VoVNet's one-shot aggregation with GSConv to reduce gradient vanishing in deep necks.

## Citation

```
@article{li2022slimnet,
  title={Slim-neck by GSConv: A lightweight-design for real-time detector architectures},
  author={Li, Hulin and Li, Jun and Wei, Hanbing and Liu, Zheng and Zhan, Zhenfei and Ren, Qiliang},
  journal={arXiv preprint arXiv:2206.02424},
  year={2022}
}
```
