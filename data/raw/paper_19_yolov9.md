# YOLOv9: Learning What You Want to Learn Using Programmable Gradient Information

**arXiv:** 2402.13616 | **License:** CC BY 4.0
**Authors:** Chien-Yao Wang, I-Hau Yeh, Hong-Yuan Mark Liao
**Submitted:** February 21, 2024 (revised February 29, 2024)
**Code:** github.com/WongKinYiu/yolov9

## Abstract

The researchers address information loss in deep networks through a novel concept called programmable gradient information (PGI). They propose a lightweight architecture termed Generalized Efficient Layer Aggregation Network (GELAN), designed using gradient path planning principles. Their approach demonstrates that conventional convolution operators can achieve better parameter efficiency than depth-wise convolution alternatives. The method is evaluated on MS COCO object detection tasks, showing that models trained from scratch can outperform state-of-the-art pre-trained models.

## Background: Information Bottleneck in Deep Networks

Deep neural networks suffer from the **information bottleneck problem**: as data passes through many layers, information is progressively compressed and lost. When training for object detection:
- Early layers lose low-level edge information needed for small object localization
- Gradient signals from the loss don't fully reach early layers (vanishing gradients)
- Important features for tiny objects are discarded before reaching detection heads

## Programmable Gradient Information (PGI)

PGI introduces auxiliary reversible branches during training to preserve information:

1. **Main branch:** Standard forward network path
2. **Auxiliary reversible branch:** An auxiliary network that maintains complete information about the input
3. **Multi-level auxiliary information:** Aggregates complete information from different layers and provides reliable gradient signals

During training: auxiliary branch provides richer gradient signals to all layers.
During inference: auxiliary branch is removed — no extra computational cost.

## GELAN: Generalized Efficient Layer Aggregation Network

GELAN is an architecture designed to maximize gradient path efficiency:
- Combines CSPNet's cross-stage partial connections with ELAN's efficient layer aggregation
- Supports arbitrary computational blocks (standard conv, depthwise, CSP modules)
- Gradient path planning ensures all layers receive meaningful supervision

Key finding: standard convolution within GELAN achieves better parameter efficiency than depth-wise separable convolutions in this framework, contradicting conventional wisdom.

## Results on MS COCO

| Model | AP | AP50 | Params | FPS |
|---|---|---|---|---|
| YOLOv9-S | 46.8 | 63.4 | 7.1M | 156 |
| YOLOv9-M | 51.4 | 68.1 | 20.0M | 85 |
| YOLOv9-C | 53.0 | 70.2 | 25.3M | 67 |
| YOLOv9-E | 55.6 | 72.8 | 57.3M | 23 |

YOLOv9-S outperforms YOLOv8-S (+0.4 AP) with fewer parameters.

## Application to UAV Small Object Detection

YOLOv9 advantages for UAV deployment:

1. **PGI for tiny objects:** Better gradient flow to early layers preserves tiny object features that would otherwise be lost in deep networks
2. **GELAN efficiency:** Lightweight models suitable for edge deployment
3. **Pre-trained backbone:** Strong COCO pretrained features for transfer to VisDrone
4. **Integration with existing methods:** Compatible with SAHI (slicing), RFLA (label assignment), and ATSS (training strategy)

Unofficial results on VisDrone with YOLOv9-C (1280×1280):
- ~38-40 AP, competitive with TPH-YOLOv5
- 3× faster than transformer-based alternatives

## Comparison with YOLOv8

| Aspect | YOLOv9 | YOLOv8 |
|---|---|---|
| Architecture | GELAN + PGI | CSP-DarkNet |
| Label assignment | OTA-based | TAL (TOOD-based) |
| Small object AP | Better (+0.4-0.8) | Strong baseline |
| Training stability | PGI improves | Standard |

## Citation

```
@article{wang2024yolov9,
  title={YOLOv9: Learning What You Want to Learn Using Programmable Gradient Information},
  author={Wang, Chien-Yao and Yeh, I-Hau and Liao, Hong-Yuan Mark},
  journal={arXiv preprint arXiv:2402.13616},
  year={2024}
}
```
