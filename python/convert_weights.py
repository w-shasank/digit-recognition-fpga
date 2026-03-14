import numpy as np
import torch
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 10)
        self.relu = nn.ReLU()
    def forward(self, x):
        x = x.view(-1, 784)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def quantize_symmetric(tensor, num_bits=8):
    max_val = tensor.abs().max().item()
    scale   = max_val / (2**(num_bits-1) - 1)
    w_int   = torch.clamp(
                  torch.round(tensor / scale),
                  -(2**(num_bits-1) - 1),
                   (2**(num_bits-1) - 1)
              )
    return w_int.numpy().astype(np.int8), scale

def write_layer(f, weights, name, comment):
    rows, cols = weights.shape
    f.write(f"// --- {comment} ---\n")
    f.write(f"static const ap_int<8> {name}[{rows}][{cols}] = {{\n")
    for i, row in enumerate(weights):
        f.write("    {")
        f.write(", ".join(str(int(v)) for v in row))
        f.write("}")
        if i != rows - 1:
            f.write(",")
        f.write("\n")
    f.write("};\n\n")


def main():
    # load model
    model = MLP()
    model.load_state_dict(torch.load('weights/model.pt', map_location='cpu'))
    model.eval()
    print("Model loaded from weights/model.pt")

    # quantize all layers symmetrically
    w1, s1 = quantize_symmetric(model.fc1.weight.data)
    w2, s2 = quantize_symmetric(model.fc2.weight.data)
    w3, s3 = quantize_symmetric(model.fc3.weight.data)

    print(f"W1 range: {w1.min()} to {w1.max()} | scale: {s1:.8f}")
    print(f"W2 range: {w2.min()} to {w2.max()} | scale: {s2:.8f}")
    print(f"W3 range: {w3.min()} to {w3.max()} | scale: {s3:.8f}")

    # save .npy files
    np.save('weights/w1_int8.npy', w1)
    np.save('weights/w2_int8.npy', w2)
    np.save('weights/w3_int8.npy', w3)
    np.save('weights/scales.npy', np.array([s1, s2, s3]))
    print("Saved .npy weight files")

    # generate weights.h
    with open('hls/src/weights.h', 'w') as f:
        f.write("#ifndef WEIGHTS_H\n")
        f.write("#define WEIGHTS_H\n\n")
        f.write("#include <ap_int.h>\n\n")

        f.write("// --- Scale factors (symmetric) ---\n")
        f.write(f"static const float S1 = {s1:.8f}f;\n")
        f.write(f"static const float S2 = {s2:.8f}f;\n")
        f.write(f"static const float S3 = {s3:.8f}f;\n\n")

        f.write("// --- Layer dimensions ---\n")
        f.write("#define L1_IN  784\n")
        f.write("#define L1_OUT 256\n")
        f.write("#define L2_IN  256\n")
        f.write("#define L2_OUT 128\n")
        f.write("#define L3_IN  128\n")
        f.write("#define L3_OUT 10\n\n")

        write_layer(f, w1, "W1", "Layer 1: 256 x 784")
        write_layer(f, w2, "W2", "Layer 2: 128 x 256")
        write_layer(f, w3, "W3", "Layer 3: 10  x 128")

        f.write("#endif // WEIGHTS_H\n")

    print("Generated hls/src/weights.h")


if __name__ == "__main__":
    main()
