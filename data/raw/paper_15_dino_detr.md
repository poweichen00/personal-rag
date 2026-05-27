# DINO: DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection

**arXiv:** 2203.03605 | **License:** CC BY 4.0
**Authors:** Hao Zhang, Feng Li, Shilong Liu, Lei Zhang, Hang Su, Jun Zhu, Lionel M. Ni, Heung-Yeung Shum
**Submitted:** March 7, 2022 (revised July 11, 2022)
**Code:** Available at IDEACVR/DINO on GitHub

## Abstract

The paper presents DINO, a state-of-the-art end-to-end object detector that improves upon prior DETR variants through three key techniques: contrastive denoising training, mixed query selection for anchor initialization, and a look-forward-twice scheme for box prediction. The model achieves significant performance gains — 49.4 AP in 12 epochs and 51.3 AP in 24 epochs on COCO with ResNet-50, representing improvements of +6.0 AP and +2.7 AP respectively over DN-DETR. When pre-trained on Objects365 with a SwinL backbone, DINO attains 63.2 AP on COCO val2017 and 63.3 AP on test-dev, demonstrating superior results while using fewer parameters and less pre-training data than competing models.

## Context: DETR Evolution

DETR family evolution for convergence speed:
1. **DETR (2020):** 500 epochs needed, original transformer detector
2. **Deformable DETR (2020):** 50 epochs, multi-scale deformable attention
3. **DAB-DETR (2022):** 50 epochs, anchor-based queries
4. **DN-DETR (2022):** 12 epochs, denoising training
5. **DINO (2022):** 12 epochs, highest accuracy, uses all previous improvements

## Three Key Innovations

### 1. Contrastive Denoising Training

DN-DETR adds noised ground truth boxes as denoising queries during training. DINO extends this with **contrastive denoising**:
- Add two groups of noising queries: positive (small noise) and negative (large noise)
- The detector must predict the GT box for positive queries and predict "no object" for negative queries
- This contrastive formulation improves convergence and discrimination ability

### 2. Mixed Query Selection

Previous methods either use static learnable queries (DETR) or initialize from encoder output (anchor DETR). DINO uses mixed selection:
- **Anchor points:** Selected from encoder output (data-dependent, good initialization)
- **Content features:** Initialized as learnable parameters (consistent across samples)
- This combination avoids cold-start for content while maintaining spatial diversity

### 3. Look-Forward-Twice

Standard decoder: each layer predicts from current layer's output. DINO's look-forward-twice: each layer's box prediction is also updated by the next layer's gradient. This gives more accurate gradient flow for box refinement.

## Results

| Model | Backbone | Epochs | AP (COCO) |
|---|---|---|---|
| DN-DETR | ResNet-50 | 12 | 43.4 |
| DINO | ResNet-50 | 12 | 49.4 |
| DINO | ResNet-50 | 24 | 51.3 |
| DINO | SwinL + Objects365 pretrain | 36 | 63.3 |

## Relevance to UAV Detection

For UAV imagery with dense small objects, DINO-DETR offers:
- **End-to-end (no NMS):** Eliminates NMS failure in dense pedestrian/vehicle UAV scenes
- **Strong AP_S:** Multi-scale attention with higher-resolution features
- **Flexible query count:** Can increase from 300 to 900 queries for very dense scenes
- On VisDrone (1280×1280 input): ~34 AP, competitive with TPH-YOLOv5

## Citation

```
@article{zhang2022dino,
  title={DINO: DETR with Improved DeNoising Anchor Boxes for End-to-End Object Detection},
  author={Zhang, Hao and Li, Feng and Liu, Shilong and Zhang, Lei and Su, Hang and Zhu, Jun and Ni, Lionel M. and Shum, Heung-Yeung},
  journal={arXiv preprint arXiv:2203.03605},
  year={2022}
}
```
