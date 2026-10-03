from imutils import paths
from sklearn.model_selection import train_test_split
from unet.dataset import SegmentationDataset
from torch.utils.data import DataLoader
from torchvision import transforms
import matplotlib.pyplot as plt
from unet.model import UNet
import matplotlib.cm as cm
from unet import config
import numpy as np
import torch
import os


def iou_metric(predictions, labels, num_classes=config.NUM_CLASSES):
    iou_list = []
    pred = predictions.view(-1)
    lab = labels.view(-1)
    for sem_class in range(num_classes):
        pred_inds = pred == sem_class
        target_inds = lab == sem_class
        intersection = (pred_inds[target_inds]).sum().float()
        union = pred_inds.sum().float() + target_inds.sum().float() - intersection
        if union == 0:
            iou_list.append(float('nan'))  # If there is no ground truth, do not include in evaluation
        else:
            iou_list.append((intersection / union).item())
    return np.array(iou_list)


def main():
    # Load the pre-trained model and set it to evaluation mode
    unet = UNet().to(config.DEVICE)
    unet = torch.load("output/unet_tgs_medical_2023-05-16.pth")
    unet.eval()

    # Load the image and mask filepaths
    imagePaths = sorted(list(paths.list_images(config.IMAGE_DATASET_PATH)))
    maskPaths = sorted(list(paths.list_images(config.MASK_DATASET_PATH)))

    # Partition the data into training and testing splits
    split = train_test_split(imagePaths, maskPaths,
                             test_size=config.TEST_SPLIT, random_state=42)

    (trainImages, testImages) = split[:2]
    (trainMasks, testMasks) = split[2:]

    # Define transformations
    transformations = transforms.Compose([transforms.ToPILImage(),
                                          transforms.Resize((config.INPUT_IMAGE_HEIGHT,
                                                             config.INPUT_IMAGE_WIDTH)),
                                          transforms.ToTensor()])

    # Create the test dataset

    testDS = SegmentationDataset(imagePaths=testImages, maskPaths=testMasks,
                                 transforms=transformations)
    print(f"[INFO] found {len(testDS)} examples in the test set...")
    testLoader = DataLoader(testDS, shuffle=True,
                            batch_size=config.BATCH_SIZE, pin_memory=config.PIN_MEMORY,
                            num_workers=os.cpu_count())

    # ====================================
    # ===========TESTING LOOP=============
    # ====================================
    print(f"[INFO] model is predicting...")
    for (i, (x, y)) in enumerate(testLoader):
        x = x.to(config.DEVICE)
        y = y.to(config.DEVICE)

        with torch.no_grad():
            # Make prediction => 4D Tensor
            pred = unet(x)
            pred_class = torch.argmax(pred, dim=1)

            # Calculate IoU
            iou = iou_metric(pred_class, y)
            mean_iou = np.nanmean(iou)

            # Convert the input image to a format that can be displayed
            test_image = x[0].permute(1, 2, 0).cpu().numpy()
            test_image = (test_image * 255).astype(np.uint8)

            # Get the predicted classes and normalize the predicted mask
            pred_mask = torch.argmax(pred[0], dim=0)
            pred_mask_normalized = pred_mask.cpu().numpy() / np.max(pred_mask.cpu().numpy())

            # Convert the truth mask to a format that can be displayed
            truth_mask = y[0].cpu().numpy()

            # Convert the class labels in the predicted mask to colors using the colormap
            if config.WATERSHED_VIEW:
                color_mask = np.zeros((pred_mask.shape[0], pred_mask.shape[1], 3), dtype=np.float32)
                pred_mask_np = pred_mask.cpu().numpy().astype(np.int32)
                for class_label, color in config.WATERSHED_CLASS_COLOR_MAP.items():
                    color_mask[pred_mask_np == class_label] = np.array(color) / 255.0
            else:
                color_mask = cm.jet(pred_mask_normalized)[:, :, :3]

            # Display the input image and predicted mask with the corresponding IoU
            fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))
            axes[0].imshow(test_image)
            axes[0].set_title("Test Image")
            axes[1].imshow(truth_mask, cmap='gray')
            axes[1].set_title("Truth Mask")
            axes[2].imshow(color_mask)
            axes[2].set_title(f"Predicted Mask (IoU: {mean_iou:.2f})")
            plt.show()

            input("[INFO] press Enter to display the next image")


if __name__ == '__main__':
    main()
