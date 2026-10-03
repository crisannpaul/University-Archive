from torchvision.models import resnet34
from torch.nn import Sequential, Module, Conv2d, ConvTranspose2d, ModuleList, ReLU, BatchNorm2d, Sigmoid, AdaptiveAvgPool2d, Linear
from torchvision.transforms import CenterCrop
import torch
import torch.nn.functional as F
from config import NUM_CLASSES, IMAGE_HEIGHT, IMAGE_WIDTH


class ResNetEncoder(torch.nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        rn = resnet34(pretrained=pretrained)
        self.initial = Sequential(rn.conv1, rn.bn1, rn.relu, rn.maxpool)
        self.layer1 = rn.layer1  # 64
        self.layer2 = rn.layer2  # 128
        self.layer3 = rn.layer3  # 256
        self.layer4 = rn.layer4  # 512

    def forward(self, x):
        f0 = self.initial(x)
        f1 = self.layer1(f0)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        f4 = self.layer4(f3)
        return [f1, f2, f3, f4]


class SEBlock(Module):
    """
    Squeeze-and-Excitation block for channel-wise attention
    """
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.pool = AdaptiveAvgPool2d(1)
        self.fc1 = Linear(channels, channels // reduction, bias=False)
        self.fc2 = Linear(channels // reduction, channels, bias=False)
        self.relu = ReLU(inplace=True)
        self.sigmoid = Sigmoid()

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.pool(x).view(b, c)
        y = self.relu(self.fc1(y))
        y = self.sigmoid(self.fc2(y)).view(b, c, 1, 1)
        return x * y


class AttentionGate(Module):
    """
    Attention gate for skip connection gating
    """
    def __init__(self, F_g, F_l, F_int):
        super().__init__()
        self.W_g = Conv2d(F_g, F_int, kernel_size=1, bias=True)
        self.W_x = Conv2d(F_l, F_int, kernel_size=1, bias=True)
        self.psi = Conv2d(F_int, 1, kernel_size=1, bias=True)
        self.relu = ReLU(inplace=True)
        self.sigmoid = Sigmoid()

    def forward(self, g, x):
        g1 = self.W_g(g)
        x1 = self.W_x(x)
        psi = self.relu(g1 + x1)
        psi = self.sigmoid(self.psi(psi))
        return x * psi


class ASPP(Module):
    """
    Atrous Spatial Pyramid Pooling to gather multi-scale context.
    """
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = Conv2d(in_ch, out_ch, kernel_size=1)
        self.bn1 = BatchNorm2d(out_ch)
        self.conv6 = Conv2d(in_ch, out_ch, kernel_size=3, padding=6, dilation=6)
        self.bn6 = BatchNorm2d(out_ch)
        self.conv12 = Conv2d(in_ch, out_ch, kernel_size=3, padding=12, dilation=12)
        self.bn12 = BatchNorm2d(out_ch)
        self.conv18 = Conv2d(in_ch, out_ch, kernel_size=3, padding=18, dilation=18)
        self.bn18 = BatchNorm2d(out_ch)
        self.project = Conv2d(out_ch * 4, out_ch, kernel_size=1)
        self.bn_proj = BatchNorm2d(out_ch)
        self.relu = ReLU(inplace=True)

    def forward(self, x):
        y1 = self.relu(self.bn1(self.conv1(x)))
        y2 = self.relu(self.bn6(self.conv6(x)))
        y3 = self.relu(self.bn12(self.conv12(x)))
        y4 = self.relu(self.bn18(self.conv18(x)))
        y = torch.cat([y1, y2, y3, y4], dim=1)
        y = self.relu(self.bn_proj(self.project(y)))
        return y


class Block(Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv1 = Conv2d(in_ch, out_ch, kernel_size=3, padding=1)
        self.bn1 = BatchNorm2d(out_ch)
        self.relu = ReLU(inplace=True)
        self.conv2 = Conv2d(out_ch, out_ch, kernel_size=3, padding=1)
        self.bn2 = BatchNorm2d(out_ch)
        self.se = SEBlock(out_ch)

    def forward(self, x):
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.se(x)
        return x


class Decoder(Module):
    def __init__(self, channels=(256, 256, 128, 64)):
        super().__init__()
        self.upconvs = ModuleList([
            ConvTranspose2d(channels[i], channels[i+1], kernel_size=2, stride=2)
            for i in range(len(channels)-1)
        ])
        self.attns = ModuleList([
            AttentionGate(F_g=channels[i+1], F_l=channels[i+1], F_int=channels[i+1]//2)
            for i in range(len(channels)-1)
        ])
        self.dec_blocks = ModuleList([
            Block(channels[i+1]*2, channels[i+1]) for i in range(len(channels)-1)
        ])
        self.crop = CenterCrop

    def forward(self, x, encoder_features):
        for i in range(len(self.upconvs)):
            x = self.upconvs[i](x)
            skip = encoder_features[-(i+1)]
            # gate the skip
            skip = self.attns[i](g=x, x=skip)
            _, _, H, W = x.shape
            skip = self.crop([H, W])(skip)
            x = torch.cat([x, skip], dim=1)
            x = self.dec_blocks[i](x)
        return x


class ProMaxAtt(Module):
    def __init__(self, num_classes=NUM_CLASSES, out_size=(IMAGE_HEIGHT, IMAGE_WIDTH)):
        super().__init__()
        # encoder + ASPP + decoder with attention + SE
        self.encoder = ResNetEncoder(pretrained=True)
        self.aspp = ASPP(in_ch=512, out_ch=256)
        self.decoder = Decoder(channels=(256, 256, 128, 64))
        self.head = Conv2d(64, num_classes, kernel_size=1)
        self.out_size = out_size

    def forward(self, x):
        feats = self.encoder(x)
        bottleneck = feats[-1]
        x = self.aspp(bottleneck)
        x = self.decoder(x, feats[:-1])
        logits = self.head(x)
        logits = F.interpolate(logits, self.out_size, mode='bilinear', align_corners=False)
        return logits
