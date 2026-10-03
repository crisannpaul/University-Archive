import torch
from torch.nn import Module, Conv2d, ConvTranspose2d, MaxPool2d, ModuleList, ReLU
import torch.nn.functional as F
from torchvision.transforms import CenterCrop
from config import NUM_CLASSES, IMAGE_HEIGHT, IMAGE_WIDTH


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


class Encoder(Module):
    def __init__(self, channels=(3, 32, 64, 128, 256)):
        super().__init__()
        self.channels = channels
        self.enc_blocks = ModuleList([
            Block(channels[i], channels[i+1]) for i in range(len(channels)-1)
        ])
        self.pool = MaxPool2d(kernel_size=2)

    def forward(self, x):
        features = []
        for block in self.enc_blocks:
            x = block(x)
            features.append(x)
            x = self.pool(x)
        return features


class Decoder(Module):
    def __init__(self, channels=(256, 128, 64, 32)):
        super().__init__()
        self.channels = channels
        # upsample from channels[i] -> channels[i+1]
        self.upconvs = ModuleList([
            ConvTranspose2d(channels[i], channels[i+1], kernel_size=2, stride=2)
            for i in range(len(channels)-1)
        ])
        # after concat, input channels = 2 * channels[i+1]
        self.dec_blocks = ModuleList([
            Block(channels[i+1]*2, channels[i+1]) for i in range(len(channels)-1)
        ])
        self.crop = CenterCrop

    def forward(self, x, encoder_features):
        # encoder_features: list of encoder outputs in order
        for i in range(len(self.upconvs)):
            x = self.upconvs[i](x)
            enc_feat = encoder_features[-(i+1)]
            # crop encoder feature to current upsampled size
            _, _, H, W = x.shape
            enc_cropped = self.crop([H, W])(enc_feat)
            # concatenate along channels
            x = torch.cat([x, enc_cropped], dim=1)
            # decode
            x = self.dec_blocks[i](x)
        return x


class MyUNet(Module):
    """
    A U-Net architecture with customizable encoder/decoder channels.
    """
    def __init__(
        self,
        enc_channels=(3, 32, 64, 128, 256),
        dec_channels=(256, 128, 64, 32),
        num_classes=NUM_CLASSES,
        retain_dim=True,
        out_size=(IMAGE_HEIGHT, IMAGE_WIDTH)
    ):
        super().__init__()
        self.encoder = Encoder(enc_channels)
        self.decoder = Decoder(dec_channels)
        self.head    = Conv2d(dec_channels[-1], num_classes, kernel_size=1)
        self.retain_dim = retain_dim
        self.out_size   = out_size

    def forward(self, x):
        # encode
        enc_feats = self.encoder(x)
        bottleneck = enc_feats[-1]
        # decode
        dec = self.decoder(bottleneck, enc_feats[:-1])
        logits = self.head(dec)
        # optional upsampling to original
        if self.retain_dim:
            logits = F.interpolate(logits, self.out_size, mode='bilinear', align_corners=False)
        return logits
