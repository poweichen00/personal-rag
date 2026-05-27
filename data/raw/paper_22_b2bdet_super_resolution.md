# From Blurry to Brilliant Detection: YOLO-Based Aerial Object Detection with Super Resolution

**arXiv:** 2401.14661 | **License:** CC BY 4.0
**Authors:** Ragib Amin Nihal, Benjamin Yen, Takeshi Ashizawa, Katsutoshi Itoyama, Kazuhiro Nakadai
**Submitted:** January 26, 2024 (revised July 9, 2025)

## Abstract

The paper tackles aerial object detection challenges including small object sizes, high-density clustering, and degradation from distance and motion blur. The B2BDet framework combines domain-specific super-resolution during inference with an enhanced YOLOv5 architecture. Key innovations include aerial-optimized SRGAN fine-tuning, an Efficient Attention Module (EAM), and Cross-Layer Feature Pyramid Network (CLFPN). Testing across four aerial datasets demonstrates performance gains, achieving 52.5% mAP on VisDrone with only 27.7M parameters. Ablation studies reveal super-resolution preprocessing contributes +2.6% mAP improvement while architectural enhancements add +2.9%, totaling +5.5% over baseline YOLOv5. The method achieves 53.8% parameter reduction compared to recent approaches while maintaining strong small object detection capabilities.

## Motivation

Aerial images from UAVs suffer from unique degradations beyond just small object size:
1. **Motion blur:** Drone vibration and fast movement blur object boundaries
2. **Atmospheric haze:** Altitude introduces atmospheric scattering, reducing contrast
3. **Compression artifacts:** Onboard video encoding at low bitrates introduces blocking artifacts
4. **Distance-dependent focus:** Objects at varying altitudes have different defocus blur levels

Standard super-resolution models (trained on synthetic downsampling degradations) perform poorly on these real-world aerial degradations. Domain-specific SR fine-tuning is needed.

## B2BDet Architecture

### Component 1: Aerial-Optimized SRGAN

The authors fine-tune a pre-trained SRGAN model on aerial-specific image pairs:
- Collect paired data: original full-resolution drone captures + naturally degraded versions
- Fine-tune discriminator and generator on aerial textures (roads, vehicles, vegetation)
- Result: SR model generates sharper edges specifically for aerial imagery textures

SR preprocessing at inference: apply 2× or 4× SR before running the detector.

### Component 2: Efficient Attention Module (EAM)

EAM is a computationally efficient channel + spatial attention module:
- **Lightweight channel attention:** Reduces to 1/4 channels (vs. SE block's default reduction ratio)
- **Depth-wise spatial attention:** 3×3 depthwise conv instead of 7×7 standard conv
- **Parallel application:** Apply channel and spatial attention in parallel (not sequential like CBAM)

Parameters: ~60% fewer than CBAM while achieving comparable attention quality.

### Component 3: Cross-Layer Feature Pyramid Network (CLFPN)

CLFPN extends standard FPN with cross-layer connections:
- Each FPN level receives features from all other levels (not just adjacent levels)
- Cross-level fusion: weighted sum of features from P2, P3, P4, P5 at each target level
- Addresses scale ambiguity by incorporating global scale context at every detection level

This is particularly effective for UAV imagery where the same object type appears at multiple scales within a single image.

## Ablation Results

| Component | mAP on VisDrone |
|---|---|
| YOLOv5 baseline | 47.0 |
| + Aerial SR preprocessing | 49.6 (+2.6) |
| + EAM | 50.7 (+1.1) |
| + CLFPN | 51.8 (+1.1) |
| Full B2BDet | 52.5 (+5.5) |

## Multi-Dataset Evaluation

| Dataset | Method | mAP |
|---|---|---|
| VisDrone | B2BDet | 52.5% |
| SeaDroneSee | B2BDet | 78.3% |
| VEDAI | B2BDet | 72.1% |
| NWPU VHR-10 | B2BDet | 88.4% |

Strong performance across diverse aerial datasets demonstrates generalization.

## Efficiency

- **27.7M parameters** — 53.8% reduction vs. comparable methods
- Super-resolution adds ~30ms latency per frame (2× SR on 1920×1080)
- Net inference: ~80ms/frame on GPU (suitable for offline analysis, not real-time)

## When SR Preprocessing Helps Most

Based on ablation:
- Objects < 16×16 pixels benefit most (+4.8 AP for small objects)
- Motion-blurred sequences show largest improvement
- Clear daytime footage with large objects sees minimal SR benefit

## Datasets Used

- **VisDrone2019-DET:** Primary benchmark
- **SeaDroneSee:** Maritime drone surveillance
- **VEDAI:** Vehicle detection in aerial imagery
- **NWPU VHR-10:** Very high resolution aerial detection

## Citation

```
@article{nihal2024b2bdet,
  title={From Blurry to Brilliant Detection: YOLO-Based Aerial Object Detection with Super Resolution},
  author={Nihal, Ragib Amin and Yen, Benjamin and Ashizawa, Takeshi and Itoyama, Katsutoshi and Nakadai, Kazuhiro},
  journal={arXiv preprint arXiv:2401.14661},
  year={2024}
}
```
