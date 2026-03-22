# Digit Recognition on FPGA
### MNIST Handwritten Digit Recognition accelerated on Numato Mimas A7 (Xilinx Artix-7 XC7A50T)
 
A complete end-to-end implementation of a neural network inference accelerator on FPGA. A small MLP (Multi-Layer Perceptron) is trained in PyTorch, quantized to INT8, synthesized to RTL using Vitis HLS, integrated in Vivado, and deployed on the Mimas A7 FPGA board. The predicted digit is displayed on the onboard 7-segment display.
 
---

 
## Table of Contents
 
- [Project Overview](#project-overview)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Project Structure](#project-structure)
- [FPGA Resource Utilization](#fpga-resource-utilization)
- [Setup and Installation](#setup-and-installation)
- [Running the Project](#running-the-project)
- [Testing](#testing)
- [Flashing to Board](#flashing-to-board)
- [Workflow Summary](#workflow-summary)
 
---
 
## Project Overview
 
```
PyTorch (CPU/GPU)         Vitis HLS               Vivado              Mimas A7
─────────────────    ──────────────────    ──────────────────    ──────────────────
Train MLP model   →  Write C++ inference →  VHDL wrapper      →  7-segment shows
Quantize INT8        Add HLS pragmas        Connect pixel ROM      predicted digit
Export weights.h     C Simulation           XDC constraints
                     C Synthesis            Generate bitstream
                     Package as IP
```
 
**Model Architecture:**
```
Input: 784 pixels (28×28 MNIST image, INT8)
  ↓
Dense Layer 1: 784 → 64  (ReLU, serialized MAC)
  ↓
Dense Layer 2: 64  → 32  (ReLU, serialized MAC)
  ↓
Dense Layer 3: 32  → 10  (argmax)
  ↓
Output: predicted digit 0-9
```
 
**Key design decisions:**
- INT8 symmetric quantization (range -127 to 127)
- No bias terms (trained with `bias=False`)
- Serialized matrix multiplication (one MAC unit reused)
- Weights stored in BRAM as ROM
- Test image hardcoded in `pixel_rom.vhd`
 
---
 
## Hardware Requirements
 
| Component | Details |
|-----------|---------|
| FPGA Board | Numato Mimas A7 V4.0 |
| FPGA Chip | Xilinx Artix-7 XC7A50T-1FGG484C |
| Interface | USB (FT2232H) |
| Display | Onboard 4-digit 7-segment (common anode, active LOW) |
| Clock | 100 MHz onboard oscillator |
 

 
Install Python dependencies:
```bash
cd digit-recognition-fpga
python3 -m venv .venv
source .venv/bin/activate
pip install torch torchvision numpy pillow
```
 
---
 
## Project Structure
 
```
digit-recognition-fpga/
│
├── scripts/
│   ├── train.ipynb              # Train MLP, quantize, save model.pt
│   ├── convert_weights.py       # Load model.pt → generate weights.h
│   ├── generate_pixel_rom.py    # MNIST image → generate pixel_rom.vhd
│   └── image_extraction.py      # Generate test_image.h for HLS testbench
│
├── weights/
│   ├── model.pt                 # Saved PyTorch model (FP32)
│   ├── w1_int8.npy              # Layer 1 weights (INT8, 64×784)
│   ├── w2_int8.npy              # Layer 2 weights (INT8, 32×64)
│   ├── w3_int8.npy              # Layer 3 weights (INT8, 10×32)
│   └── scales.npy               # Quantization scale factors
│
├── hls/
│   ├── src/
│   │   ├── mlp.h                # Type declarations and function signatures
│   │   ├── mlp.cpp              # HLS inference logic with pragmas
│   │   ├── weights.h            # C arrays of INT8 weights (generated)
│   │   └── test_image.h         # Test image for C simulation (generated)
│   ├── tb/
│   │   ├── tb_mlp.cpp           # HLS testbench
│   │   └── test_image.h         # Copy of test image
│   └── hls_component/
│       └── hls_config.cfg       # Vitis HLS project configuration
│
├── vivado/
│   ├── top.vhd                  # Top level VHDL wrapper
│   ├── seg7_decoder.vhd         # 7-segment display decoder
│   ├── pixel_rom.vhd            # Hardcoded input image ROM (generated)
│   └── mimas_a7.xdc             # Pin constraints for Mimas A7
│
└── .gitignore
```
 
---
 
## FPGA Resource Utilization
 
### HLS Synthesis (Vitis HLS 2024.2)
Target device: `xc7a50t-fgg484-1` | Clock: 10ns (100 MHz)
 
| Module | Latency (cycles) | BRAM | DSP | FF | LUT |
|--------|-----------------|------|-----|----|-----|
| mlp_inference (total) | 52,589 | 34 | 4 | 1072 | 1360 |
| Layer 1 (784→64) | 50,186 | 32 | 2 | 368 | 393 |
| Layer 2 (64→32) | 2,056 | 1 | 1 | 279 | 353 |
| Layer 3 (32→10) | 327 | 1 | 1 | 256 | 303 |
| Argmax | 12 | 0 | 0 | 102 | 141 |
 
**Timing:** Estimated 7.082 ns (meets 10 ns target)
 
### Vivado Implementation
Target device: `xc7a50t-fgg484-1`
 
| Resource | Used | Available | Utilization |
|----------|------|-----------|-------------|
| LUT | 387 | 32,600 | 1.19% |
| FF | 412 | 65,200 | 0.63% |
| BRAM | 17.5 | 75 | 23.3% |
| DSP | 3 | 120 | 2.5% |
 
**Timing Summary:**
```
Worst Negative Slack (WNS): 5.264 ns  
Worst Hold Slack (WHS):     0.263 ns  
Failing Endpoints:          0         
All timing constraints met
```
 

 
---
 
## Running the Project
 
### Phase 1 — Train the Model
 
Open `scripts/train.ipynb` in VS Code and run all cells. This:
- Trains a 784→64→32→10 MLP on MNIST for 10 epochs
- Quantizes weights symmetrically to INT8
- Saves `weights/model.pt` and `.npy` weight files
 
Expected output:
```
Epoch 10/10 | Loss: 0.031 | Accuracy: 99.1%
Saved all weights to weights/ folder
```
 
### Phase 2 — Generate HLS Source Files
 
```bash
# from project root
python3 scripts/convert_weights.py
```
 
Expected output:
```
Model loaded from weights/model.pt
W1 range: -127 to 127 | scale: 0.00XXXXXX
W2 range: -127 to 127 | scale: 0.00XXXXXX
W3 range: -127 to 127 | scale: 0.00XXXXXX
Generated hls/src/weights.h
```
 
Generate test image for HLS simulation:
```bash
python3 scripts/image_extraction.py
```
 
### Phase 3 — Vitis HLS
 
1. Open Vitis HLS: `vitis_hls &`
2. Open workspace: `hls/`
3. Open component: `hls_component`
4. Run **C Simulation** → expect `TEST PASSED`
5. Run **C Synthesis** → check resource report
6. Run **Package** → generates IP zip
 
### Phase 4 — Generate Test Image ROM
 
```bash
# generate pixel_rom.vhd for MNIST index 0 (digit 7)
python3 scripts/generate_pixel_rom.py 0
 
# or any other index
python3 scripts/generate_pixel_rom.py 15
```
 
Expected output:
```
MNIST Index: 0
Label:            7
PyTorch predicts: 7
Pixel range: -19 to 127
Generated vivado/pixel_rom.vhd for digit 7
```
 
### Phase 5 — Vivado
 
1. Open Vivado: `vivado &`
2. Open project: `vivado/minst_fpga/minst_fpga.xpr`
3. Add HLS IP repository: `Tools → Settings → IP → Repository`
   - Point to: `hls/hls_component/mlp_inference`
4. Run **Synthesis**
5. Run **Implementation**
6. Run **Generate Bitstream**
 
---
 
## Testing
 
### HLS C Simulation
 
In Vitis HLS click **Run** under **C SIMULATION**:
 
```
Expected : 7
Predicted: 7
TEST PASSED 
```
 

 
### Verify PyTorch prediction before synthesizing
 
The `generate_pixel_rom.py` script always prints the PyTorch prediction before generating the ROM. If PyTorch predicts wrong, the FPGA will also predict wrong — fix the image first.
 
---
 
## Flashing to Board
 
### Using openFPGALoader (recommended)
 
```bash
# flash to SRAM (volatile, lost on power off)
openFPGALoader -b mimas_a7 \
  ~/projects/digit-recognition-fpga/vivado/minst_fpga/minst_fpga.runs/impl_1/top.bit
 
# flash to SPI Flash (persistent, survives power cycle)
# step 1: generate .mcs in Vivado Tcl console
write_cfgmem -format mcs \
  -interface spix4 \
  -size 128 \
  -loadbit "up 0x0 /path/to/top.bit" \
  -file /path/to/top.mcs
 
# step 2: flash
openFPGALoader -b mimas_a7 --write-flash top.mcs
```
 
### Expected board output
 
After flashing, the rightmost digit of the 7-segment display shows the predicted digit. For the default test image (MNIST index 0):
 
```
7-segment displays: 7
```
 
---
 
## Workflow Summary
 
```
1. Train model      scripts/train.ipynb
        ↓
2. Export weights   scripts/convert_weights.py  →  hls/src/weights.h
        ↓
3. HLS simulation   Vitis HLS C Simulation      →  TEST PASSED
        ↓
4. HLS synthesis    Vitis HLS C Synthesis       →  RTL generated
        ↓
5. Package IP       Vitis HLS Package           →  mlp_inference.zip
        ↓
6. Generate ROM     scripts/generate_pixel_rom.py  →  vivado/pixel_rom.vhd
        ↓
7. Vivado synthesis + implementation + bitstream
        ↓
8. Flash            openFPGALoader -b mimas_a7 top.bit
        ↓
9. Board shows predicted digit on 7-segment 
```
 
---
 
## Changing the Test Image
 
To test with a different MNIST image:
 
```bash
python3 scripts/generate_pixel_rom.py <mnist_index>
```
 
Then re-run Vivado implementation and flash. The pixel ROM is the only file that changes.
 
---

 