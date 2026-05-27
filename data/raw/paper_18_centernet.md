# Objects as Points (CenterNet)

**arXiv:** 1904.07850 | **License:** CC BY 4.0
**Authors:** Xingyi Zhou, Dequan Wang, Philipp Krähenbühl
**Submitted:** April 16, 2019 (revised April 25, 2019)
**Pages/Figures:** 12 pages, 5 figures

## Abstract

The paper presents an alternative approach to object detection that represents objects as center points rather than enumerated bounding boxes. The method, called CenterNet, uses keypoint estimation to identify object centers and regresses other properties including size, 3D location, orientation, and pose. The authors report that their approach is end-to-end differentiable, simpler, faster, and more accurate than traditional bounding box detectors. Performance metrics include 28.1% AP at 142 FPS on MS COCO, with competitive results on 3D detection and pose estimation benchmarks.

## Core Idea: Center Point Representation

Rather than predicting bounding boxes via anchors or proposals, CenterNet detects objects as:
1. **Center heatmap:** H × W × C Gaussian heatmap (C = number of classes), where peaks represent object centers
2. **Size regression:** For each detected center, predict (w, h) of the object
3. **Local offset:** Correct quantization error from feature map downsampling

The output stride is 4 (feature map is 1/4 of input size), producing a fine-grained center heatmap.

## Training

- Center heatmaps use Gaussian-rendered targets (σ proportional to object size)
- Loss: focal loss for heatmap + L1 loss for size and offset
- No NMS required: local maxima in the heatmap directly correspond to objects

## Advantages for UAV Tiny Object Detection

1. **No anchors:** No need to cluster anchors for UAV-specific tiny object sizes
2. **Center point is always detectable:** Even a 5×5 pixel object has a well-defined center
3. **No NMS:** Local maximum suppression avoids the dense NMS failure mode common in UAV scenes
4. **Efficient inference:** At 142 FPS (DLA-34 backbone), fastest among comparable detectors
5. **Generalization:** Same architecture handles 2D detection, 3D detection, and pose estimation

## Architecture

- **Backbone:** DLA-34 (Deep Layer Aggregation), Hourglass-104, or ResNet-101
- **Upsampling:** Learned transposed convolutions to achieve stride-4 output
- **Output heads:** Parallel heads for classification heatmap, size, and offset

## Results on MS COCO

| Model | AP | Speed (FPS) |
|---|---|---|
| DLA-34 | 37.4 | 52 |
| ResNet-101 | 34.8 | 45 |
| Hourglass-104 (multi-scale) | 45.1 | 1.4 |
| DLA-34 (fast) | 28.1 | 142 |

## Performance on UAV Datasets

CenterNet on VisDrone achieves ~22.3 AP (DLA-34 backbone):
- Competitive with FCOS baseline (21.4 AP)
- Better than anchor-based Faster R-CNN with default anchors (19.4 AP)
- Dense center heatmaps can detect crowded small objects better than anchor methods

## Limitations for UAV Detection

- Center heatmaps for very dense tiny objects may merge adjacent centers (objects < 5px apart)
- Stride-4 output still insufficient for objects < 8×8 pixels in the original image
- Requires large input resolution (512×512 minimum; 1024×1024 preferred for UAV)

## Multi-Task Extensions

CenterNet simultaneously supports:
- 2D object detection (COCO)
- 3D object detection (KITTI autonomous driving)
- Human pose estimation (COCO keypoints)

All from the same backbone with minimal task-specific heads, demonstrating strong representation learning.

## Citation

```
@article{zhou2019centernet,
  title={Objects as Points},
  author={Zhou, Xingyi and Wang, Dequan and Kr{\"a}henb{\"u}hl, Philipp},
  journal={arXiv preprint arXiv:1904.07850},
  year={2019}
}
```
