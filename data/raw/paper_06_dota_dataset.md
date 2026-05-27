# DOTA: A Large-Scale Dataset for Object Detection in Aerial Images

**arXiv:** 1711.10398 | **License:** CC BY 4.0
**Authors:** Gui-Song Xia, Xiang Bai, Jian Ding, Zhen Zhu, Serge Belongie, Jiebo Luo, Mihai Datcu, Marcello Pelillo, Liangpei Zhang
**Submitted:** November 28, 2017 (revised May 19, 2019)
**Venue:** IEEE CVPR 2018

## Abstract

The researchers introduce a substantial collection of aerial imagery designed to advance object recognition in Earth observation applications. They gathered approximately 2,806 images from various sensors and platforms, each spanning roughly 4000×4000 pixels. The dataset contains 188,282 instances labeled across 15 object categories using quadrilateral annotations to capture varied orientations. The authors note that while significant progress has occurred in natural scene recognition, aerial contexts present unique challenges due to huge variation in the scale, orientation and shape.

## Dataset Statistics

### DOTA-v1.0
- **2,806 images** from multiple aerial platforms
- **188,282 instances** (average ~67 per image)
- **15 categories:** plane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, large vehicle, small vehicle, helicopter, roundabout, soccer ball field, swimming pool
- Image sizes: 800×800 to 4000×4000 pixels (arbitrary resolution)
- Annotations: **oriented bounding boxes (OBB)** at arbitrary angles (not axis-aligned)

### DOTA-v1.5 and DOTA-v2.0
- v1.5: Same images + adds container crane category; more complete annotation of very small instances
- v2.0: 11,268 images, 1,793,658 instances, 18 categories, more diverse geographic coverage

## Key Distinguishing Features

### Oriented Bounding Boxes (OBB)
Unlike VisDrone which uses horizontal boxes, DOTA requires oriented bounding box detection. Objects like planes, ships, and bridges are often at arbitrary angles. OBB format: (cx, cy, w, h, θ) where θ ∈ [-90°, 90°) is the rotation angle.

### Multi-Scale Objects
DOTA spans objects from small vehicles (<10×10 pixels) to entire airport runways, requiring robust feature pyramid designs.

### Challenges
- **Aspect ratio variation:** Bridges, runways, ships have extreme aspect ratios (up to 20:1)
- **Dense instances:** Harbors and parking lots contain hundreds of small vehicles with significant overlap
- **Scale variation:** Small vehicles (10-40px) to ground track fields (500-2000px)

## Evaluation Protocol

Two tasks:
- **Task 1 (OBB):** Oriented bounding box detection
- **Task 2 (HBB):** Horizontal bounding box detection
- mAP reported as mean over all 15 categories at IoU = 0.5

## Representative Results

| Method | mAP (OBB) |
|---|---|
| Faster R-CNN (HBB) | 52.93 |
| Oriented R-CNN | 75.87 |
| LSKNet | 81.85 |
| PKINet-B | 82.04 |

## Impact

DOTA catalyzed the development of oriented object detection methods, including Oriented R-CNN, S2A-Net, ReDet, and LSKNet. It is widely used for remote sensing, traffic monitoring, and airport surveillance research.

## Citation

```
@inproceedings{xia2018dota,
  title={DOTA: A Large-scale Dataset for Object Detection in Aerial Images},
  author={Xia, Gui-Song and Bai, Xiang and Ding, Jian and others},
  booktitle={CVPR},
  year={2018}
}
```
