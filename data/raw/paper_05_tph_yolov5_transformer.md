# TPH-YOLOv5: Improved YOLOv5 Based on Transformer Prediction Head for Object Detection on Drone-Captured Scenarios

**arXiv:** 2108.11539 | **License:** CC BY 4.0
**Authors:** Xingkui Zhu, Shuchang Lyu, Xu Wang, Qi Zhao
**Submitted:** August 26, 2021
**Venue:** VisDrone 2021 ICCV Workshop (8 pages, 9 figures)

## Abstract

The authors address two key challenges in drone-based object detection: significant variation in object scale due to altitude changes and motion blur from dense, low-altitude objects. Their solution introduces an additional prediction head for multi-scale detection and replaces standard prediction heads with Transformer-based alternatives leveraging self-attention. Integration of convolutional block attention models helps identify regions of interest in cluttered scenes. On the VisDrone2021 dataset's DET-test-challenge, the method achieves 39.18% average precision, outperforming the prior state-of-the-art by 1.81%. When compared directly to YOLOv5, performance improves by approximately 7%.

## Motivation

YOLOv5 is a highly efficient single-stage detector, but its prediction heads use simple convolutional layers that capture only local context. In UAV imagery where objects are tiny and densely packed, global contextual reasoning is critical for distinguishing true objects from background texture. TPH-YOLOv5 replaces or augments the original prediction heads with Transformer-based prediction heads (TPH) to capture long-range dependencies.

## Architecture

### Key Modifications to YOLOv5

1. **Additional prediction head:** A fourth detection scale is added specifically for very small objects, targeting objects smaller than 16×16 pixels
2. **Transformer prediction heads (TPH):** Each prediction head is augmented with a multi-head self-attention module before the final convolutional layer (8 heads, d_model=256), enabling global context reasoning
3. **Convolutional Block Attention Module (CBAM):** Integrated into the backbone to identify regions of interest in cluttered backgrounds
4. **High input resolution:** 1536×1536 input (vs. standard 640×640) to preserve tiny object detail

### Why Transformers Help for Tiny Objects

Small objects lack sufficient local texture for CNNs to reliably distinguish. The transformer's global attention allows the model to leverage surrounding scene context: a tiny car near a parking lot is more confidently detected than an isolated tiny dot.

## Results on VisDrone2021

- **AP on DET-test-challenge:** 39.18%
- **Improvement over prior SOTA:** +1.81%
- **Improvement over YOLOv5l:** ~7% AP
- **Training:** ~7 days on 8× NVIDIA V100 GPUs
- **Inference:** ~35ms per 1536×1536 image on V100 (28 FPS)

## Key Insights

- High resolution is critical: doubling input from 640 to 1280 alone recovers approximately 8 AP points
- Extra P2 detection head (stride 8) specifically targets objects smaller than 16×16 pixels
- Transformer attention at prediction heads captures global scene relationships with manageable computational cost

## Limitations

- High memory footprint makes edge deployment challenging
- Transformer attention quadratic complexity limits further resolution scaling
- Not suitable for real-time embedded UAV deployment without model compression

## Citation

```
@article{zhu2021tph,
  title={TPH-YOLOv5: Improved YOLOv5 Based on Transformer Prediction Head for Object Detection on Drone-captured Scenarios},
  author={Zhu, Xingkui and Lyu, Shuchang and Wang, Xu and Zhao, Qi},
  journal={arXiv preprint arXiv:2108.11539},
  year={2021}
}
```
