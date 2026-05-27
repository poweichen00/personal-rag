# Vision Meets Drones: A Challenge

**arXiv:** 1804.07437 | **License:** CC BY 4.0
**Authors:** Pengfei Zhu, Longyin Wen, Xiao Bian, Haibin Ling, Qinghua Hu
**Submitted:** April 20, 2018 (revised April 23, 2018)
**Pages/Figures:** 11 pages, 11 figures

## Abstract

The authors present VisDrone2018, a large-scale benchmark for visual object detection and tracking from drone platforms. The dataset comprises 263 video clips and 10,209 images collected from 14 Chinese cities, containing more than 2.5 million annotated instances in 179,264 images/video frames. The benchmark includes object bounding boxes, categories, occlusion data, and truncation ratios. Four tasks are defined: image-based detection, video-based detection, single object tracking, and multi-object tracking. The authors note that challenges include occlusion, large scale and pose variation, and fast motion.

## Dataset Details

- **Images:** 10,209 static images + 263 video clips (261,908 video frames)
- **Annotated instances:** Over 2.5 million bounding boxes
- **Object categories:** 10 classes — pedestrian, person, car, van, bus, truck, motor, bicycle, awning-tricycle, tricycle
- **Cities:** 14 different Chinese cities
- **Splits:** 6,471 training / 548 validation / 1,610 test images
- **Drones used:** DJI Phantom 3 Standard, DJI Phantom 4, Mavic Pro
- **Altitudes:** Ranging from 20 m to approximately 100 m

## Key Challenges Identified

- **Small object size:** Median object height is fewer than 20 pixels in 1920×1080 frames
- **High object density:** Urban scenes contain hundreds of objects per frame, causing severe overlap and occlusion
- **Large scale variation:** Objects vary greatly in apparent size across different altitudes
- **Background clutter:** Complex backgrounds resembling objects of interest lead to high false-positive rates
- **Occlusion:** Dense crowds and traffic cause frequent object-to-object occlusion
- **Pose variation:** Drone viewpoint changes cause unusual object orientations

## Evaluation Protocol

Metrics follow the COCO evaluation framework:
- AP (Average Precision) at IoU thresholds [0.50:0.05:0.95]
- AP50 at IoU = 0.50
- AP75 at IoU = 0.75
- Breakdown by object size: AP_S (small), AP_M (medium), AP_L (large)

## Tasks

1. **Task 1:** Object detection in images
2. **Task 2:** Object detection in videos
3. **Task 3:** Single-object tracking
4. **Task 4:** Multi-object tracking

## Impact

VisDrone has become the de facto standard benchmark for UAV object detection research. It drives specialized work on label assignment for tiny objects, feature pyramid designs, efficient inference, and domain adaptation from ground-level to aerial perspective.

## Citation

```
@article{zhu2018visdrone,
  title={Vision Meets Drones: A Challenge},
  author={Zhu, Pengfei and Wen, Longyin and Bian, Xiao and Ling, Haibin and Hu, Qinghua},
  journal={arXiv preprint arXiv:1804.07437},
  year={2018}
}
```
