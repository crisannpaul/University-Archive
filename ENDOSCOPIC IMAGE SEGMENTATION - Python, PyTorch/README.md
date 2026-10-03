# Endoscopic image segmentation (Python, PyTorch)

Semantic segmentation of laparoscopic surgery frames into 13 classes, on the CholecSeg8k dataset. Two iterations:

- `v1 - U-Net (2023)`: bachelor Image Processing project. A small U-Net with a train/test pipeline, plus a later SegFormer experiment (`seg_former.py`). The U-Net structure follows the PyImageSearch U-Net tutorial.
- `v2 - Model comparison (2025)`: master's Image Processing and Computer Vision project. U-Net, custom U-Net variants (ResNet encoder, attention), DeepLabV3 and SegFormer-B0 compared on the same data. Report: `DocumentatieIPCV.pdf`.

Not included: the dataset and trained weights. `v2/code/train.py` imports a `config.py` that was not kept and has to be recreated.
