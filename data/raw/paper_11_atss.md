# Bridging the Gap Between Anchor-based and Anchor-free Detection via Adaptive Training Sample Selection

**arXiv:** 1912.02424 | **License:** CC BY 4.0
**Authors:** Shifeng Zhang, Cheng Chi, Yongqiang Yao, Zhen Lei, Stan Z. Li
**Submitted:** December 5, 2019 (revised June 20, 2020)
**Venue:** CVPR 2020 (Oral, Best Paper Nomination)

## Abstract

The research identifies that the core distinction between anchor-based and anchor-free object detection approaches concerns how positive and negative training samples are defined. When both methods apply identical sample definitions during training, performance differences become negligible. The authors present an Adaptive Training Sample Selection (ATSS) method that automatically determines positive and negative samples using object statistical properties. This approach bridges the performance gap between detection paradigms and achieves 50.7% AP without introducing any overhead on MS COCO benchmarks.

## Core Finding

The paper makes a fundamental insight: the main difference between anchor-based (e.g., RetinaNet) and anchor-free (e.g., FCOS) detectors lies not in the model architecture but in **how positive and negative training samples are selected**. When controlling for this factor, both approaches achieve similar performance.

## ATSS Algorithm

For each ground truth object, ATSS selects positive anchors as follows:

1. **Candidate selection:** For each FPN level l, select the top-k candidates based on center distance to the ground truth center (k=9 by default)
2. **Compute IoU:** Calculate IoU between each candidate and the ground truth box
3. **Statistical threshold:** Compute mean μ_g and standard deviation σ_g of IoU values across all levels for ground truth g
4. **Adaptive threshold:** Threshold = μ_g + σ_g (adapts per object, not a fixed global value)
5. **Positive selection:** Candidates with IoU ≥ threshold AND center inside ground truth box are positive

The adaptive threshold automatically adjusts based on the current object's difficulty:
- Easy, well-matched objects: high threshold (strict selection)
- Difficult, poorly-matched objects: low threshold (more lenient)

## Why ATSS Matters for UAV Detection

Standard fixed IoU thresholds (e.g., IoU > 0.5 for positive) fail for tiny objects because:
- Tiny objects with few valid candidates get fewer or zero positives
- Fixed thresholds don't account for scale-dependent matching difficulty

ATSS adapts per object, effectively behaving like an anchor-free method for small objects and anchor-based for large objects. This is particularly valuable in UAV images where object sizes vary dramatically.

## Results on MS COCO

- **50.7% AP** with ResNeXt-64x4d-101 backbone (SOTA at time of publication)
- No additional inference overhead over baseline RetinaNet
- Bridges the 0.8 AP gap between anchor-based and anchor-free methods

## Integration with UAV Detection

ATSS has become a standard label assignment strategy for UAV detection:
- Combined with NWD: +2.9 AP over standard ATSS on VisDrone
- Combined with RFLA: further improvements for tiny objects
- Base for dynamic label assignment methods (OTA, SimOTA, TOOD)

## Citation

```
@inproceedings{zhang2020atss,
  title={Bridging the Gap Between Anchor-based and Anchor-free Detection via Adaptive Training Sample Selection},
  author={Zhang, Shifeng and Chi, Cheng and Yao, Yongqiang and Lei, Zhen and Li, Stan Z.},
  booktitle={CVPR},
  year={2020}
}
```
