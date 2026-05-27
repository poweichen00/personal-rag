# Deformable DETR: Deformable Transformers for End-to-End Object Detection

**arXiv:** 2010.04159 | **License:** CC BY 4.0
**Authors:** Xizhou Zhu, Weijie Su, Lewei Lu, Bin Li, Xiaogang Wang, Jifeng Dai
**Submitted:** October 8, 2020 (revised March 18, 2021)
**Venue:** ICLR 2021 (Oral presentation)
**Code:** Released on GitHub

## Abstract

The paper addresses limitations in the original DETR model by proposing Deformable DETR. The key innovation involves attention modules that only attend to a small set of key sampling points around a reference. This approach delivers improved results compared to standard DETR, particularly for small object detection, while requiring significantly fewer training iterations.

## Background: DETR Limitations

DETR (Detection Transformer, Carion et al. 2020) introduced end-to-end object detection using Transformers without NMS or anchor boxes, but had two critical problems:
1. **Slow convergence:** Requires 500 epochs to converge on COCO vs. 12 for Faster R-CNN
2. **Low feature resolution:** Operates on stride-32 features, making tiny object detection poor
3. **Quadratic attention complexity:** O(N²) where N = H×W prevents using high-resolution features

## Core Innovation: Deformable Attention

Standard attention attends to all N spatial positions:
`Attention(q, K, V) = softmax(qKᵀ/√d_k)V`

Deformable attention samples only K=4 reference points per query per feature level:
- Each query learns offset vectors (Δx_k, Δy_k) for K sampling locations
- Sampling locations are relative to a reference point
- Much more efficient: O(N·K) instead of O(N²)
- Naturally focuses on the most informative spatial locations

## Architecture

1. **Multi-scale feature maps:** Uses P2, P3, P4, P5 (like FPN) for better small object handling
2. **Multi-scale deformable attention:** Cross-level attention for each query point
3. **Convergence:** 50 training epochs (10× faster than DETR)
4. **Object queries:** 300 learnable queries (vs. DETR's 100)

## Results

- **Faster convergence:** Achieves comparable DETR performance in just 1/10 the training time
- **Better small objects:** Significantly improved AP_S due to multi-scale features
- **State-of-the-art on COCO:** 46.2 AP with ResNet-50 (vs. DETR's 42.0 in 500 epochs)
- **Practical inference:** ~25 FPS on V100

## Relevance to UAV Detection

For UAV imagery with dense small objects, Deformable DETR offers:
- **No NMS required:** Eliminates NMS failures in dense pedestrian/vehicle scenes
- **Multi-scale features:** Handles tiny objects through P2-level features
- **Efficient attention:** Scales to high-resolution UAV imagery better than original DETR
- **Competitive accuracy:** Matches FCOS P2 performance at lower computational cost

## Comparison with YOLO Approaches

| Criterion | Deformable DETR | YOLOv8 |
|---|---|---|
| Dense scenes (NMS free) | Better | Worse |
| Real-time (< 30ms) | No (40ms) | Yes |
| Small object AP | Competitive | Slightly behind |
| Implementation | Complex | Simple |

## Citation

```
@inproceedings{zhu2020deformable,
  title={Deformable DETR: Deformable Transformers for End-to-End Object Detection},
  author={Zhu, Xizhou and Su, Weijie and Lu, Lewei and Li, Bin and Wang, Xiaogang and Dai, Jifeng},
  booktitle={ICLR},
  year={2021}
}
```
