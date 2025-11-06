# Installation Guide

Complete installation instructions for the Interactive 3D Medical Volume Viewer - Cross-Platform Edition.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Platform-Specific Installation](#platform-specific-installation)
4. [Installation Methods](#installation-methods)
5. [Verifying Installation](#verifying-installation)
6. [Troubleshooting](#troubleshooting)

---

## System Requirements

### All Platforms

#### Required
- **Python:** 3.8 or higher
- **RAM:** Minimum 8GB (16GB+ recommended for large volumes)
- **Storage:** 500MB+ free space for dependencies
- **GPU:** Any modern GPU with hardware acceleration support

#### Recommended
- Python 3.10 or 3.11
- 16GB+ RAM
- SSD storage
- Dedicated GPU

### Platform-Specific Requirements

#### macOS
- **OS Version:** macOS 10.13 (High Sierra) or later
- **GPU:** Metal-capable GPU (most Macs 2012+)
- **Optimal:** Apple Silicon (M1/M2/M3/M4) for best performance
- **Display:** Native macOS display or external monitor

#### Windows
- **OS Version:** Windows 10 or Windows 11 (64-bit)
- **GPU:** DirectX 11+ or OpenGL 3.3+ capable GPU
- **Display:** Any Windows-compatible monitor
- **Architecture:** x64 (64-bit)

#### Linux
- **Distribution:** Any modern Linux distribution (Ubuntu 20.04+, Fedora 35+, etc.)
- **GPU:** OpenGL 3.3+ capable GPU
- **Display Server:** X11 or Wayland with XWayland
- **Architecture:** x86_64 (64-bit)

---

## Quick Installation

For most users on any platform, this is the fastest way to get started:

```bash
# Clone the repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install dependencies
pip install -r requirements.txt

# Test the installation
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

That's it! If a 3D viewer window opens, you're all set.

---

## Platform-Specific Installation

### macOS Installation

#### Option 1: Standard Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install dependencies
pip3 install -r requirements.txt

# Test
python3 scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

#### Option 2: Using Homebrew Python

```bash
# Install Python via Homebrew (if not already installed)
brew install python@3.11

# Clone and install
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization
pip3 install -r requirements.txt
```

**Note for Apple Silicon users:** Everything works natively! Metal GPU acceleration is automatic.

### Windows Installation

#### Prerequisites
Ensure Python is installed and added to PATH:
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify: Open Command Prompt and run `python --version`

#### Installation Steps

**Using Command Prompt or PowerShell:**

```bash
# Clone repository (requires Git for Windows)
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install dependencies
pip install -r requirements.txt

# Test the installation
python scripts\medical_interactive_viewer.py data\nii\img0006.nii.gz
```

**Alternative: Download ZIP**
1. Download repository as ZIP from GitHub
2. Extract to desired location
3. Open Command Prompt in that folder
4. Run: `pip install -r requirements.txt`

**Note:** Windows will automatically use DirectX or OpenGL for GPU acceleration.

### Linux Installation

#### Debian/Ubuntu

```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-tk git

# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install Python dependencies
pip3 install -r requirements.txt

# Test
python3 scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

#### Fedora/RHEL/CentOS

```bash
# Install system dependencies
sudo dnf install python3 python3-pip python3-tkinter git

# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install Python dependencies
pip3 install -r requirements.txt

# Test
python3 scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

#### Arch Linux

```bash
# Install system dependencies
sudo pacman -S python python-pip tk git

# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install Python dependencies
pip install -r requirements.txt

# Test
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

**Note for Linux users:** 
- X11 server must be running (usually default on desktop environments)
- For headless servers, use HTML export feature instead of interactive viewer
- OpenGL 3.3+ support required for GPU acceleration

---

## Installation Methods

### Method 1: Using pip (Recommended)

#### Standard Installation

```bash
# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install with pip
pip install -r requirements.txt
```

#### Install with HTML Export Support

```bash
# Install core + HTML export dependencies
pip install -r requirements.txt
```

All dependencies including HTML export are included by default.

#### Install from setup.py (Alternative)

```bash
# Basic installation
pip install -e .

# With HTML export
pip install -e ".[html]"

# With development tools
pip install -e ".[dev]"

# With everything
pip install -e ".[all]"
```

### Method 2: Using Conda/Mamba

```bash
# Create a new conda environment
conda create -n medviz python=3.10
conda activate medviz

# Install dependencies
pip install -r requirements.txt

# Or install packages individually
conda install numpy
pip install pyvista nibabel
pip install nest-asyncio trame trame-vtk trame-vuetify
```

### Method 3: Using Poetry

```bash
# Install Poetry if you haven't
curl -sSL https://install.python-poetry.org | python3 -

# Initialize Poetry project
cd medical-visualization
poetry init

# Add dependencies
poetry add numpy pyvista nibabel
poetry add nest-asyncio trame trame-vtk trame-vuetify

# Install
poetry install
```

### Method 4: Manual Installation

If you prefer to install dependencies manually:

```bash
# Core dependencies
pip install numpy>=1.20.0
pip install pyvista>=0.40.0
pip install nibabel>=3.2.0

# HTML export dependencies (optional but recommended)
pip install nest-asyncio>=1.5.6
pip install trame>=2.5.0
pip install trame-vtk>=2.5.0
pip install trame-vuetify>=2.3.0
```

---

## Verifying Installation

### Check Python Version

```bash
python --version
# Should show Python 3.8 or higher
```

### Check Installed Packages

```bash
pip list | grep -E "numpy|pyvista|nibabel|trame"
```

Expected output:
```
nibabel         3.2.0 (or higher)
numpy           1.20.0 (or higher)
pyvista         0.40.0 (or higher)
trame           2.5.0 (or higher)
trame-vtk       2.5.0 (or higher)
trame-vuetify   2.3.0 (or higher)
```

### Test Basic Functionality

```python
# Test imports
python -c "import numpy; import pyvista; import nibabel; print('All imports successful!')"
```

### Run Sample Visualization

```bash
# This should open a 3D viewer window
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

If the viewer opens and you can rotate the volume, installation is successful!

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pyvista'`

**Solution:**
```bash
pip install pyvista
```

### Issue: `ModuleNotFoundError: No module named 'nibabel'`

**Solution:**
```bash
pip install nibabel
```

### Issue: HTML Export Fails

**Symptoms:**
```
❌ Error: Missing dependencies for HTML export
```

**Solution:**
```bash
pip install nest-asyncio trame trame-vtk trame-vuetify
```

### Issue: Viewer Window Doesn't Appear

**Platform-specific solutions:**

**macOS:**
```bash
# Install Tkinter support
brew install python-tk@3.11

# Or install PyQt5
pip install pyqt5
```

**Windows:**
```bash
# Usually works by default, but if needed:
pip install pyqt5
```

**Linux (Debian/Ubuntu):**
```bash
# Install Tkinter
sudo apt install python3-tk

# Or install PyQt5
pip install pyqt5
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3-tkinter
```

**All Platforms - SSH/Remote Access:**
- If using SSH without display, use HTML export feature instead:
  ```python
  visualize_volume_interactive(volume, save_html='output.html')
  ```
- On Linux, enable X11 forwarding: `ssh -X user@host`

### Issue: `ImportError: dlopen failed` (macOS Apple Silicon)

**Solution:**
Install Rosetta 2 (if not already installed):
```bash
softwareupdate --install-rosetta
```

Then reinstall packages:
```bash
pip uninstall pyvista vtk
pip install --no-cache-dir pyvista
```

### Issue: GPU Acceleration Not Working

**Check GPU support:**

**macOS:**
```bash
# Check Metal support
system_profiler SPDisplaysDataType | grep Metal
```

**Windows:**
```bash
# Check DirectX version
dxdiag
# Look for DirectX 11 or higher
```

**Linux:**
```bash
# Check OpenGL version
glxinfo | grep "OpenGL version"
# Should show 3.3 or higher
```

**Solution if GPU not detected:**
- Update graphics drivers (especially on Windows and Linux)
- On Linux: Install proprietary GPU drivers if available
- The viewer will still work with CPU rendering, just slower

### Issue: Slow Performance

**Solutions:**

1. **Close other GPU-intensive apps** (Chrome, other 3D viewers)

2. **Reduce volume resolution:**
   ```python
   volume = volume[::2, ::2, ::2]  # Downsample by 2x
   ```

3. **Use isosurface mode** instead of volume rendering

4. **Reduce window size:**
   ```python
   visualize_volume_interactive(volume, window_size=(800, 600))
   ```

### Issue: Out of Memory Errors

**For large volumes (>2GB):**

```python
# Option 1: Downsample
volume_ds = volume[::2, ::2, ::2]

# Option 2: Extract ROI
roi = volume[100:400, 100:400, 100:400]

# Option 3: Use lower precision
volume = volume.astype(np.float32)  # Instead of float64
```

### Issue: Permission Denied

**Solution:**
```bash
chmod +x scripts/medical_interactive_viewer.py
```

### Issue: Incompatible Python Version

**Check version:**
```bash
python --version
```

**If < 3.8, update Python:**
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
```

---

## Using Virtual Environments (Recommended)

Virtual environments help avoid dependency conflicts across all platforms.

### macOS/Linux

```bash
# Create virtual environment
python3 -m venv medviz_env

# Activate
source medviz_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Use the viewer
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz

# Deactivate when done
deactivate
```

### Windows

```bash
# Create virtual environment
python -m venv medviz_env

# Activate
medviz_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Use the viewer
python scripts\medical_interactive_viewer.py data\nii\img0006.nii.gz

# Deactivate when done
deactivate
```

---

## GPU Acceleration Notes

### Automatic Platform Detection

The viewer automatically detects and uses the best available GPU backend:

- **macOS:** Metal (optimal on M1/M2/M3/M4, good on Intel)
- **Windows:** DirectX 11+ or OpenGL (whichever is better)
- **Linux:** OpenGL 3.3+

No configuration needed - it just works!

### Performance Expectations

| Platform | GPU Type | Expected Performance |
|----------|----------|---------------------|
| macOS (Apple Silicon) | Metal | Excellent (optimal) |
| macOS (Intel) | Metal | Good |
| Windows | NVIDIA/AMD (DirectX) | Excellent |
| Windows | Intel (OpenGL) | Good |
| Linux | NVIDIA (proprietary) | Excellent |
| Linux | AMD/Intel (Mesa) | Good |

---

## Alternative: Docker Installation (Coming Soon)

Docker support is planned for future releases. This will provide:
- Isolated environment
- No dependency conflicts
- Easy distribution
- Consistent behavior across platforms

Stay tuned!

---

**Installation complete! Ready to visualize medical imaging data!**

