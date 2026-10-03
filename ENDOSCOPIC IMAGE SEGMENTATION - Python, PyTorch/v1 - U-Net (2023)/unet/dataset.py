import torch
from torch.utils.data import Dataset
import cv2

from unet import config


class SegmentationDataset(Dataset):
    def __init__(self, imagePaths, maskPaths, transforms):
        # Store the image and mask filepaths, and transformations
        self.imagePaths = imagePaths
        self.maskPaths = maskPaths
        self.transforms = transforms

    def __len__(self):
        return len(self.imagePaths)

    def __getitem__(self, idx):
        # Grab the image and mask paths from the current index
        imagePath = self.imagePaths[idx]
        maskPath = self.maskPaths[idx]

        # Load the image from disk, swap its channels from BGR to RGB,
        # and read the associated mask from disk
        image = cv2.imread(imagePath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mask = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, (config.INPUT_IMAGE_WIDTH, config.INPUT_IMAGE_HEIGHT),
                          interpolation=cv2.INTER_NEAREST)

        # Masks are scaled to [0, 12] because we have to predict 13 classes
        mask = (mask / 255.0 * (config.NUM_CLASSES-1)).round().astype('uint8')

        if self.transforms is not None:
            # Apply the transformations to both image and its mask
            image = self.transforms(image)
            mask = torch.from_numpy(mask).long()

        # return a tuple of the image and its mask
        return image, mask

    # def __getitem__(self, idx):
    #     # Grab the image path from the current index
    #     imagePath = self.imagePaths[idx]
    #
    #     # Load the image from disk, swap its channels from BGR to RGB
    #     image = cv2.imread(imagePath)
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #
    #     # Mask paths for training
    #     # No mask paths for testing
    #     if self.maskPaths is not None:
    #         # Read the mask from disk and resize it
    #         maskPath = self.maskPaths[idx]
    #         mask = cv2.imread(maskPath, cv2.IMREAD_GRAYSCALE)
    #         mask = cv2.resize(mask, (config.INPUT_IMAGE_WIDTH, config.INPUT_IMAGE_HEIGHT),
    #                           interpolation=cv2.INTER_NEAREST)
    #
    #         # Masks are scaled to [0, 11] because we have to predict 12 classes
    #         mask = (mask / 255.0 * (config.NUM_CLASSES-1)).round().astype('uint8')
    #
    #         if self.transforms is not None:
    #             # Apply the transformations to both image and its mask
    #             image = self.transforms(image)
    #             mask = torch.from_numpy(mask).long()
    #
    #         # Return a tuple of the image and its mask
    #         return image, mask
    #     else:
    #         if self.transforms is not None:
    #             image = self.transforms(image)
    #         return image