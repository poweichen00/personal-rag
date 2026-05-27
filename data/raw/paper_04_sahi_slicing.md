# Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection

**arXiv:** 2202.06934 | **License:** Apache 2.0 (open-source library)
**Authors:** Fatih Cagatay Akyon, Sinan Onur Altinuc, Alptekin Temizel
**Submitted:** February 14, 2022 (revised October 24, 2022)
**Venue:** IEEE ICIP 2022 (5 pages, 4 figures, 2 tables)

## Abstract

The work addresses detection challenges for small and distant objects in surveillance contexts. The authors propose SAHI, an open-source framework providing a generic pipeline for improved small object detection through slicing-aided inference and fine-tuning. This technique works with existing detectors without requiring modifications. Testing on aerial datasets demonstrated significant performance gains: 6.8%, 5.1%, and 5.3% improvement across three detector types during inference, with further gains of 12.7%, 13.4%, and 14.5% when combining slicing-aided fine-tuning methods.

## Core Algorithm

SAHI is a model-agnostic inference and fine-tuning framework that significantly improves small object detection without modifying the detector architecture. The key insight is that detectors trained on standard input resolutions fail on tiny objects because those objects are simply too small to activate detector features. SAHI overcomes this by slicing the image into overlapping sub-regions and running inference on each slice at full resolution.

### Inference Phase

1. **Full-image inference:** Run the detector on the entire image at standard resolution to capture large and medium objects
2. **Slicing:** Divide the original full-resolution image into overlapping slices (common: 640×640 slices with 20% overlap)
3. **Per-slice inference:** Run the same detector on each slice; objects that were tiny in the full image now appear at normal scale
4. **Prediction merging:** Map slice-level predictions back to full-image coordinates; apply NMS or NMW to merge overlapping predictions

### Fine-tuning Phase

SAHI also supports sliced fine-tuning: generating training crops using the same slicing strategy, then training the detector on both full images and sliced crops. This aligns training and inference distributions.

## Key Parameters

- **Slice size:** Best matched to detector training resolution (e.g., 640×640 for YOLOv5)
- **Overlap ratio:** 0.2 recommended (too small → boundary missed detections; too large → excessive computation)
- **Postprocess:** NMW (Non-Maximum Weighted) > standard NMS for localization accuracy

## Compatibility

SAHI is detector-agnostic and supports YOLOv5, YOLOv8, YOLOv9, Detectron2, MMDetection, and Hugging Face models. Available as a Python package (`pip install sahi`).

## Results

- **Inference improvement:** 6.8%, 5.1%, 5.3% AP improvement across three different detector types
- **Fine-tuning improvement:** 12.7%, 13.4%, 14.5% additional AP when combining slicing-aided fine-tuning
- **Latency:** Approximately 10-20× slower inference due to multiple per-slice passes
- Not suitable for real-time edge UAV deployment due to latency

## Open-Source Usage

```python
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

model = AutoDetectionModel.from_pretrained("yolov8", "yolov8x.pt")
result = get_sliced_prediction(
    "image.jpg", model,
    slice_height=640, slice_width=640,
    overlap_height_ratio=0.2
)
```

## Citation

```
@inproceedings{akyon2022sahi,
  title={Slicing Aided Hyper Inference and Fine-tuning for Small Object Detection},
  author={Akyon, Fatih Cagatay and Altinuc, Sinan Onur and Temizel, Alptekin},
  booktitle={IEEE ICIP},
  year={2022}
}
```
