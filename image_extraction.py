import numpy as np
import shutil
from torchvision import datasets, transforms
import torch
import torch.nn as nn


class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(784, 64,bias=False)
        self.fc2 = nn.Linear(64, 32,bias=False)
        self.fc3 = nn.Linear(32, 10,bias=False)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(-1, 784)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x


model = MLP()
model.load_state_dict(torch.load('weights/model.pt', map_location='cpu'))
model.eval()
print("Model loaded from weights/model.pt")


transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
dataset    = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
image, label = dataset[3]
pixels     = image.view(-1).numpy()


with torch.no_grad():
    out          = model(image.unsqueeze(0))
    pytorch_pred = out.argmax().item()

print(f'Label:              {label}')
print(f'PyTorch prediction: {pytorch_pred}')

if pytorch_pred != label:
    print("WARNING: PyTorch prediction wrong — check model training")
else:
    print("PyTorch prediction correct — model is good")


p_max        = np.abs(pixels).max()
scale_p      = p_max / 127.0
pixels_int8  = np.clip(
                   np.round(pixels / scale_p),
                   -127, 127
               ).astype(np.int8)

print(f'Pixel min: {pixels_int8.min()}, max: {pixels_int8.max()}')


def save_test_image_header(path, pixels_int8, label):
    with open(path, 'w') as f:
        f.write('#ifndef TEST_IMAGE_H\n')
        f.write('#define TEST_IMAGE_H\n\n')
        f.write(f'#define EXPECTED_LABEL {label}\n\n')
        f.write('static const int TEST_IMAGE[784] = {\n    ')
        vals = [str(int(v)) for v in pixels_int8]
        for i, v in enumerate(vals):
            f.write(v)
            if i != 783:
                f.write(', ')
            if (i + 1) % 16 == 0:
                f.write('\n    ')
        f.write('\n};\n\n')
        f.write('#endif\n')
    print(f'Saved {path}')


save_test_image_header('hls/src/test_image.h', pixels_int8, label)
save_test_image_header('hls/tb/test_image.h',  pixels_int8, label)
