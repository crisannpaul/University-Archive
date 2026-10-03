from torchvision.models import resnet34
from torch.nn import Sequential, Module, Conv2d, ConvTranspose2d, ModuleList, ReLU
from torchvision.transforms import CenterCrop
import torch
import torch.nn.functional as F
from config import NUM_CLASSES, IMAGE_HEIGHT, IMAGE_WIDTH


class ResNetEncoder(torch.nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        rn = resnet34(pretrained=pretrained)
        # initial conv/bn/relu/pool
        self.initial = Sequential(rn.conv1, rn.bn1, rn.relu, rn.maxpool)
        # encoder layers
        self.layer1  = rn.layer1  # C=64
        self.layer2  = rn.layer2  # C=128
        self.layer3  = rn.layer3  # C=256
        self.layer4  = rn.layer4  # C=512

    def forward(self, x):
        f0 = self.initial(x)    # 1/4 spatial
        f1 = self.layer1(f0)    # 1/4
        f2 = self.layer2(f1)    # 1/8
        f3 = self.layer3(f2)    # 1/16
        f4 = self.layer4(f3)    # 1/32
        return [f1, f2, f3, f4]


class Block(Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        # two 3x3 convs + ReLU
        self.conv1 = Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.relu  = ReLU(inplace=True)
        self.conv2 = Conv2d(out_channels, out_channels, kernel_size=3, padding=1)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        return x


class Decoder(Module):
    def __init__(self, channels=(512, 256, 128, 64)):
        super().__init__()
        self.channels = channels
        # upsample layers
        self.upconvs = ModuleList([
            ConvTranspose2d(channels[i], channels[i+1], kernel_size=2, stride=2)
            for i in range(len(channels)-1)
        ])
        # after concatenation, input channels = 2 * channels[i+1]
        self.dec_blocks = ModuleList([
            Block(channels[i+1]*2, channels[i+1])
            for i in range(len(channels)-1)
        ])
        self.crop = CenterCrop

    def forward(self, x, encoder_features):
        # encoder_features: [f1, f2, f3] corresponding to channels[1:]
        for i in range(len(self.upconvs)):
            x = self.upconvs[i](x)
            skip = encoder_features[-(i+1)]  # reverse order
            # crop skip to match x spatial dims
            _, _, H, W = x.shape
            skip = self.crop([H, W])(skip)
            # concatenate along channel dim
            x = torch.cat([x, skip], dim=1)
            # conv block
            x = self.dec_blocks[i](x)
        return x


class MyUNetWithResNet(Module):
    def __init__(self, num_classes=NUM_CLASSES, out_size=(IMAGE_HEIGHT, IMAGE_WIDTH)):
        super().__init__()
        self.encoder = ResNetEncoder(pretrained=True)
        # decoder channels must align with encoder reversed
        self.decoder = Decoder(channels=(512, 256, 128, 64))
        self.head    = Conv2d(64, num_classes, kernel_size=1)
        self.out_size = out_size

    def forward(self, x):
        feats = self.encoder(x)  # [f1(64), f2(128), f3(256), f4(512)]
        bottleneck = feats[-1]   # f4
        # pass through decoder with skips f3,f2,f1
        dec = self.decoder(bottleneck, feats[:-1])
        logits = self.head(dec)
        # upsample to desired output size
        logits = F.interpolate(logits, self.out_size, mode='bilinear', align_corners=False)
        return logits
