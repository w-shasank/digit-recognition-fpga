import numpy as np
from torchvision import datasets, transforms
import sys
import torch
import torch.nn as nn

def quantize(pixels):
    p_max = np.abs(pixels).max()
    if p_max == 0:
        return pixels.astype(np.int8)
    scale_p = p_max / 127.0
    return np.clip(np.round(pixels / scale_p), -127, 127).astype(np.int8)

def write_pixel_rom(pixels_int8):
    with open('vivado/pixel_rom.vhd', 'w') as f:
        f.write("library IEEE;\n")
        f.write("use IEEE.STD_LOGIC_1164.ALL;\n")
        f.write("use IEEE.NUMERIC_STD.ALL;\n\n")
        f.write("entity pixel_rom is\n")
        f.write("    port (\n")
        f.write("        clk  : in  STD_LOGIC;\n")
        f.write("        addr : in  STD_LOGIC_VECTOR(9 downto 0);\n")
        f.write("        ce   : in  STD_LOGIC;\n")
        f.write("        data : out STD_LOGIC_VECTOR(7 downto 0)\n")
        f.write("    );\n")
        f.write("end pixel_rom;\n\n")
        f.write("architecture Behavioral of pixel_rom is\n\n")
        f.write("    type rom_type is array (0 to 783) of STD_LOGIC_VECTOR(7 downto 0);\n")
        f.write("    constant ROM : rom_type := (\n")
        for i, p in enumerate(pixels_int8):
            val = int(p) & 0xFF
            bits = format(val, '08b')
            comma = "," if i < 783 else " "
            f.write(f'        {i} => "{bits}"{comma}\n')
        f.write("    );\n\n")
        f.write("begin\n\n")
        f.write("    process(clk)\n")
        f.write("    begin\n")
        f.write("        if rising_edge(clk) then\n")
        f.write("            if ce = '1' then\n")
        f.write("                data <= ROM(to_integer(unsigned(addr)));\n")
        f.write("            end if;\n")
        f.write("        end if;\n")
        f.write("    end process;\n\n")
        f.write("end Behavioral;\n")

def run_pytorch_inference(pixels_float):
    class MLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.fc1 = nn.Linear(784, 64, bias=False)
            self.fc2 = nn.Linear(64,  32, bias=False)
            self.fc3 = nn.Linear(32,  10, bias=False)
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
    with torch.no_grad():
        tensor = torch.tensor(pixels_float, dtype=torch.float32).unsqueeze(0)
        out    = model(tensor)
        pred   = out.argmax().item()
        scores = out.numpy()[0]
    return pred, scores

# ─────────────────────────────────────────
# Load MNIST image
# ─────────────────────────────────────────
index = int(sys.argv[1]) if len(sys.argv) > 1 else 0

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])
dataset     = datasets.MNIST('./data', train=False, download=True, transform=transform)
image, label = dataset[index]
pixels_flat  = image.view(-1).numpy()

# ─────────────────────────────────────────
# Inference + generate ROM
# ─────────────────────────────────────────
pred, scores = run_pytorch_inference(pixels_flat)
print(f"Index:            {index}")
print(f"Label:            {label}")
print(f"PyTorch predicts: {pred}")
print(f"Scores:           {np.round(scores, 2)}")

pixels_int8 = quantize(np.array(pixels_flat).flatten())
print(f"Pixel range:      {pixels_int8.min()} to {pixels_int8.max()}")

write_pixel_rom(pixels_int8)
print(f"Generated vivado/pixel_rom.vhd for digit {label}")
