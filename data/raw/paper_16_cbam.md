# CBAM: Convolutional Block Attention Module

**arXiv:** 1807.06521 | **License:** CC BY 4.0
**Authors:** Sanghyun Woo, Jongchan Park, Joon-Young Lee, In So Kweon
**Submitted:** July 17, 2018 (revised July 18, 2018)
**Venue:** ECCV 2018

## Abstract

The authors introduce a lightweight attention mechanism for convolutional neural networks. Their module sequentially infers attention maps along two separate dimensions, channel and spatial, then the attention maps are multiplied to the input feature map for adaptive feature refinement. The module is designed for seamless integration into existing CNN architectures without significant computational overhead. The team validated their approach through experiments on ImageNet-1K, MS COCO detection, and VOC 2007 detection datasets, demonstrating consistent improvements in classification and detection performances with various models.

## Architecture: Sequential Channel and Spatial Attention

CBAM applies attention in two sequential steps:

### Step 1: Channel Attention Module

Generates a channel attention map M_c ∈ R^(C×1×1) that emphasizes which channels are most informative:

M_c(F) = σ(MLP(AvgPool(F)) + MLP(MaxPool(F)))

- AvgPool and MaxPool: aggregate spatial information into 1×1×C descriptors
- Shared MLP: reduces channels C → C/r → C (r=16 is default reduction ratio)
- Sigmoid activation: produces attention weights ∈ [0, 1]

Using both average and max pooling captures both the general channel statistics and the most prominent features.

### Step 2: Spatial Attention Module

Generates a spatial attention map M_s ∈ R^(1×H×W) that emphasizes where to focus:

M_s(F') = σ(conv^(7×7)([AvgPool_c(F'); MaxPool_c(F')]))

- Channel-wise average and max pooling: compress C channels to 2-channel descriptor
- 7×7 convolution: capture large spatial relationships (kernel size tuned in ablation)
- Sigmoid: spatial attention weights

### Combined Application

F'' = M_c(F) ⊗ F        (channel attention applied first)
F''' = M_s(F'') ⊗ F''  (then spatial attention)

This sequential application allows each stage to focus on what (channel) and where (spatial) independently.

## Key Properties

- **Lightweight:** Adds only ~0.1% extra parameters to ResNet-50
- **Plug-and-play:** Can be inserted at any point in any CNN architecture
- **Flexible:** Can be configured as channel-only, spatial-only, or sequential attention
- **Architecture-agnostic:** Validated on VGG, ResNet, WideResNet, ResNeXt

## Results

### ImageNet Classification
- ResNet-50 + CBAM: +0.6% top-1 accuracy vs. ResNet-50
- ResNet-101 + CBAM: +0.5% top-1 accuracy

### MS COCO Object Detection (Faster R-CNN)
- ResNet-50 FPN: 36.9 AP → 37.5 AP (+0.6 AP with CBAM)
- ResNet-101 FPN: 39.5 AP → 40.1 AP (+0.6 AP)

## Application to UAV Detection

CBAM is widely used in UAV detection architectures as a drop-in enhancement:

1. **Backbone integration:** Insert CBAM after each residual block in ResNet → suppress background clutter in channel features
2. **Neck integration:** Insert in FPN feature maps → focus attention on object-dense regions
3. **Detection head:** Apply before prediction layers → refine features for tiny object classification

In UAV imagery, CBAM's spatial attention helps suppress texture-heavy background channels (foliage, road markings) while amplifying channels sensitive to object shapes.

## Comparison with SE Networks

| Aspect | SE Block | CBAM |
|---|---|---|
| Attention type | Channel only | Channel + Spatial |
| Parameters | ~2× less | More but still minimal |
| Performance gain | +0.3-0.5% | +0.5-0.8% |
| Integration cost | Very simple | Simple |

## Integration in TPH-YOLOv5

TPH-YOLOv5 (arXiv:2108.11539) integrates CBAM into its backbone to identify regions of interest in cluttered drone scenes, reporting this as one of the key components contributing to its 7% AP improvement over standard YOLOv5.

## Citation

```
@inproceedings{woo2018cbam,
  title={CBAM: Convolutional Block Attention Module},
  author={Woo, Sanghyun and Park, Jongchan and Lee, Joon-Young and Kweon, In So},
  booktitle={ECCV},
  year={2018}
}
```
