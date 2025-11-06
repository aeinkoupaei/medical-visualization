# Interactive 3D Medical Volume Viewer

A powerful, cross-platform GPU-accelerated 3D medical imaging visualization tool. View, interact with, and export NIfTI (.nii/.nii.gz) medical imaging volumes with full-resolution rendering and real-time interaction. Optimized for Apple Silicon (M1/M2/M3/M4) Macs with Metal GPU acceleration, but works great on Windows (DirectX/OpenGL) and Linux (OpenGL) too!


## Features

### Performance
- **Full Resolution Rendering** - No downsampling required
- **GPU Acceleration** - Automatic (Metal on macOS, DirectX/OpenGL on Windows, OpenGL on Linux)
- **Cross-Platform** - Works on macOS, Windows, and Linux
- **Optimized for Apple Silicon** - M1/M2/M3/M4 chips get extra performance boost
- **Real-time Interaction** - Smooth rotation, zoom, and pan

### Visualization Modes
1. **Volume Rendering** - Transparent 3D volume visualization
2. **Isosurface Extraction** - Surface-based rendering
3. **Multi-Planar Reconstruction (MPR)** - Three orthogonal slice planes
4. **Volume + Slices** - Hybrid visualization combining volume and slices
5. **Side-by-Side Comparison** - Compare two volumes simultaneously

### Export Features
- **Interactive HTML Export** - Save fully rotatable 3D views
- **Share in Browser** - No installation needed for viewers
- **Screenshot Capture** - High-quality image export

### 2D Slice Visualization (Jupyter Notebook)
- **Interactive Slice Browser** - Navigate slices with sliders
- **Grid View** - 3×6 static grid of equidistant slices
- **Batch Processing** - Process folders of volumes
- **Multi-Format Support** - NumPy (.npy) and NIfTI files
- **Google Colab Compatible** - Works in cloud notebooks

## Tools

This project provides two complementary visualization tools:

### 1. 3D Interactive Viewer (`medical_interactive_viewer.py`)

**Desktop application** for full 3D volume exploration with GPU acceleration.

**Use for:**
- 🔄 Interactive 3D rotation, zoom, pan
- 📦 Volume rendering with transparency control
- 🎨 Isosurface extraction
- 🔲 Multi-planar reconstruction
- ⚖️ Side-by-side volume comparison
- 🌐 Interactive HTML export

**Best for:** Deep exploration, presentations, and interactive demonstrations

### 2. 2D Slice Viewer (`visualize_generated_images.ipynb`)

**Jupyter notebook** for quick 2D slice inspection and batch processing.

**Use for:**
- 🔍 Quick slice-by-slice inspection
- 📊 Grid visualization (18 slices at once)
- 🔄 Batch processing multiple volumes
- ☁️ Working in Google Colab
- 📄 Creating figure panels for papers

**Best for:** Data screening, batch export, and publication figures

**See [NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md) for detailed notebook documentation.**

## Requirements

### All Platforms
- Python 3.8 or higher
- 8GB+ RAM (16GB recommended for large volumes)
- GPU with hardware acceleration support

### Platform-Specific
- **macOS:** 10.13+ (High Sierra or later), Metal-capable GPU
  - Optimized for Apple Silicon (M1/M2/M3/M4)
- **Windows:** Windows 10/11, DirectX or OpenGL-capable GPU
- **Linux:** Modern distribution with X11, OpenGL-capable GPU

## Installation

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install dependencies
pip install -r requirements.txt
```

### Manual Install

```bash
pip install numpy pyvista nibabel

# For HTML export (optional but recommended)
pip install nest-asyncio trame trame-vtk trame-vuetify
```

### Verify Installation

```bash
# Test 3D viewer
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz

# Or launch Jupyter for 2D notebook
jupyter notebook scripts/medical_2D_slice_visualization.ipynb
```

## Quick Start

### Basic Usage

```bash
# Run with interactive file selection
python scripts/medical_interactive_viewer.py

# Or specify file directly
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

### Python API Usage

```python
import numpy as np
from scripts.medical_interactive_viewer import load_nifti_volume, visualize_volume_interactive

# Load your NIfTI file
volume = load_nifti_volume("path/to/your/file.nii.gz")

# Visualize interactively
visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',  # Transparent
    cmap='gray',
    save_html='my_volume.html'  # Optional: save as interactive HTML
)
```

## Detailed Usage Guide

### 1. Volume Rendering

**Best for:** Viewing internal structures, transparent visualization

```python
from scripts.medical_interactive_viewer import load_nifti_volume, visualize_volume_interactive

volume = load_nifti_volume("data/nii/img0006.nii.gz")

visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',      # Options: 'sigmoid_1' (very transparent) to 'sigmoid_20' (opaque)
    cmap='gray',              # Options: 'gray', 'bone', 'viridis', 'hot', 'cool'
    save_html='volume.html'   # Save interactive HTML
)
```

**Opacity Settings:**
- `'sigmoid_1'` to `'sigmoid_3'` - Very transparent (see inside)
- `'sigmoid'` or `'sigmoid_5'` - Balanced (default)
- `'sigmoid_10'` to `'sigmoid_20'` - Opaque (surface view)
- `'linear'`, `'geom'` - Alternative opacity curves

### 2. Isosurface Rendering

**Best for:** Surface extraction, organ boundaries

```python
from scripts.medical_interactive_viewer import visualize_isosurface_interactive

visualize_isosurface_interactive(
    volume,
    threshold_percentile=50,  # Adjust to extract different surfaces
    cmap='viridis',
    smooth=True,              # Apply smoothing
    save_html='isosurface.html'
)
```

### 3. Multi-Planar Reconstruction (MPR)

**Best for:** Examining specific slices in 3D context

```python
from scripts.medical_interactive_viewer import visualize_multiplanar

visualize_multiplanar(
    volume,
    cmap='gray',
    save_html='multiplanar.html'
)
```

### 4. Volume with Slices

**Best for:** Combining volume and slice views

```python
from scripts.medical_interactive_viewer import visualize_volume_with_slices

visualize_volume_with_slices(
    volume,
    cmap='gray',
    save_html='volume_slices.html'
)
```

### 5. Compare Two Volumes

**Best for:** Before/after comparison, source vs target

```python
from scripts.medical_interactive_viewer import compare_volumes_side_by_side

volume1 = load_nifti_volume("before.nii.gz")
volume2 = load_nifti_volume("after.nii.gz")

compare_volumes_side_by_side(
    volume1, 
    volume2,
    titles=["Before Treatment", "After Treatment"],
    opacity='sigmoid',
    cmap='gray'
)
```

## Colormap Options

Popular colormaps for medical imaging:

- `'gray'` - Standard grayscale (default for CT/MRI)
- `'bone'` - Bone-like appearance
- `'hot'` - Heat map (red/yellow/white)
- `'cool'` - Cool colors (cyan/blue)
- `'viridis'` - Perceptually uniform
- `'plasma'` - High contrast
- `'inferno'` - Dark background

See [PyVista colormap docs](https://docs.pyvista.org/examples/02-plot/cmap.html) for full list.

## HTML Export

Save interactive 3D visualizations that work in any web browser:

```python
# Any visualization function accepts save_html parameter
visualize_volume_interactive(
    volume,
    save_html='interactive_brain.html'
)

# The saved HTML file is:
# - Fully interactive (rotate, zoom, pan)
# - No installation needed for viewers
# - Works in any modern browser
# - Can be shared via email or web
```

**Open the HTML file:**
- Double-click to open in browser
- Or: `open interactive_brain.html`
- Share with colleagues who don't have Python installed!

## Sample Data

The repository includes sample NIfTI files in `data/nii/`:
- `img0006.nii.gz` - Sample medical volume 1
- `img0009.nii.gz` - Sample medical volume 2

To use your own data, simply provide the path to any `.nii` or `.nii.gz` file.

## Platform-Specific Notes

### macOS
- **GPU:** Metal acceleration automatic (optimal performance on M1/M2/M3/M4)
- **Display issues?** Install Python with framework support: `brew install python-tk@3.11`

### Windows
- **GPU:** DirectX or OpenGL acceleration automatic
- **Installation:** Use regular `pip install` commands
- **Display backend:** Usually works out of the box

### Linux
- **GPU:** OpenGL acceleration automatic
- **Requirements:** X11 server must be running
- **Display backend:** May need: `sudo apt install python3-tk` (Debian/Ubuntu)

## Troubleshooting

### Missing Dependencies for HTML Export

If you see: `Error: Missing dependencies for HTML export`

**Fix:**
```bash
pip install nest-asyncio trame trame-vtk trame-vuetify
```

### Viewer Window Doesn't Appear

**macOS:**
```bash
brew install python-tk@3.11
```

**Linux:**
```bash
sudo apt install python3-tk  # Debian/Ubuntu
sudo yum install python3-tkinter  # RHEL/CentOS
```

**Windows:**
Usually works by default. If not, try: `pip install pyqt5`

### Out of Memory Errors

For very large volumes (>2GB):

```python
# Use downsampling
volume_downsampled = volume[::2, ::2, ::2]  # Reduce by factor of 2
visualize_volume_interactive(volume_downsampled)
```

### Performance Optimization

For maximum performance:

1. **Close other GPU-intensive applications**
2. **Use isosurface rendering for large datasets**
3. **Adjust opacity for volume rendering** (more transparent = faster)
4. **Reduce window size** if needed:

```python
visualize_volume_interactive(volume, window_size=(800, 600))
```

## Project Structure

```
medical-visualization/
├── scripts/
│   ├── medical_interactive_viewer.py        # 3D viewer script
│   └── medical_2D_slice_visualization.ipynb # 2D slice notebook
├── data/
│   └── nii/                              # Sample NIfTI files
│       ├── img0006.nii.gz
│       └── img0009.nii.gz
├── output/                               # Generated HTML exports
├── requirements.txt                      # Python dependencies
├── QUICK_START.md                       # Quick start guide
├── NOTEBOOK_GUIDE.md                    # Jupyter notebook guide
├── INSTALLATION.md                      # Detailed installation
├── CROSS_PLATFORM_SUPPORT.md            # Platform compatibility
└── README.md                            # This file
```

## Quick Reference: Which Tool to Use?

| Task | Use This Tool |
|------|---------------|
| Quick 2D inspection | 📓 Jupyter Notebook |
| Batch processing 50+ volumes | 📓 Jupyter Notebook |
| Create figure for paper | 📓 Jupyter Notebook |
| Work in Google Colab | 📓 Jupyter Notebook |
| Full 3D exploration | 🖥️ 3D Viewer Script |
| Interactive presentation | 🖥️ 3D Viewer Script |
| Volume rendering with transparency | 🖥️ 3D Viewer Script |
| Side-by-side comparison (live) | 🖥️ 3D Viewer Script |
| Export interactive HTML | 🖥️ 3D Viewer Script |

**Typical Workflow:**
1. Screen datasets with notebook (2D slices)
2. Identify interesting cases
3. Explore in 3D viewer for detailed analysis
4. Export both 2D figures and 3D HTML for sharing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization
pip install -r requirements.txt
```

### Running Tests

```bash
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

## Acknowledgments

Built with:
- [PyVista](https://docs.pyvista.org/) - 3D visualization
- [NiBabel](https://nipy.org/nibabel/) - NIfTI file handling
- [NumPy](https://numpy.org/) - Numerical computing
- [Trame](https://kitware.github.io/trame/) - Interactive HTML export

## Support

- **Issues:** [GitHub Issues](https://github.com/aeinkoupaei/medical-visualization/issues)
- **Discussions:** [GitHub Discussions](https://github.com/aeinkoupaei/medical-visualization/discussions)

## Roadmap

- [ ] Support for DICOM files
- [ ] Additional visualization presets
- [ ] Measurement tools (distance, angle)
- [ ] Animation export (GIF, video)
- [ ] Segmentation overlay support
- [ ] Custom colormap editor

---

**If you find this useful, please star the repository!**

