from datetime import date
import torch
import os

WATERSHED_CLASS_COLOR_MAP = {
    0: [50, 50, 50],  # Class 0: Black Background
    1: [11, 11, 11],  # Class 1: Abdominal Wall
    2: [21, 21, 21],  # Class 2: Liver
    3: [13, 13, 13],  # Class 3: Gastrointestinal Tract
    4: [12, 12, 12],  # Class 4: Fat
    5: [31, 31, 31],  # Class 5: Grasper
    6: [23, 23, 23],  # Class 6: Connective Tissue
    7: [24, 24, 24],  # Class 7: Blood
    8: [25, 25, 25],  # Class 8: Cystic Duct
    9: [32, 32, 32],  # Class 9: L-hook Electrocautery
    10: [22, 22, 22],  # Class 10: Gallbladder
    11: [33, 33, 33],  # Class 11: Hepatic Vein
    12: [5, 5, 5]  # Class 12: Liver Ligament
}
WATERSHED_VIEW = False

DATASET_PATH = os.path.join("dataset", "train")

IMAGE_DATASET_PATH = os.path.join(DATASET_PATH, "images")
MASK_DATASET_PATH = os.path.join(DATASET_PATH, "masks")

TEST_SPLIT = 0.15

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PIN_MEMORY = True if DEVICE == "cuda" else False

NUM_CHANNELS = 1
NUM_CLASSES = 13
NUM_LEVELS = 3

INIT_LR = 0.001
NUM_EPOCHS = 40
BATCH_SIZE = 64

INPUT_IMAGE_WIDTH = 256
INPUT_IMAGE_HEIGHT = 256

THRESHOLD = 0.5

BASE_OUTPUT = "output"


MODEL_PATH = os.path.join(BASE_OUTPUT, f"unet_tgs_medical.pth")
PLOT_PATH = os.path.sep.join([BASE_OUTPUT, f"plot.png"])
TEST_PATHS = os.path.sep.join([BASE_OUTPUT, "test_paths.txt"])
