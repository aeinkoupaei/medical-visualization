# Jupyter Notebook Guide

## Overview

The `medical_2D_slice_visualization.ipynb` notebook provides **2D slice visualization** tools for medical imaging data, optimized for Google Colab and Jupyter environments.

## Features

### 1. **Multi-Format Support**
- ✅ NumPy files (`.npy`)
- ✅ NIfTI files (`.nii`, `.nii.gz`)

### 2. **Visualization Modes**

#### Static Grid View
- 3×6 grid of equidistant slices
- Automatic contrast adjustment (1st-99th percentile)
- High-resolution PNG export (300 DPI)
- Works on both Colab and local Jupyter

#### Interactive Slice Viewer
- Real-time slice navigation with sliders
- Three viewing planes (axial, sagittal, coronal)
- Adjustable contrast and colormap
- iPyWidgets-powered interface

### 3. **Batch Processing**
- Process entire folders of volumes
- Automatic slice selection
- Bulk PNG export

## Quick Start

### On Google Colab

1. **Upload the notebook** to your Google Drive
2. **Open with Google Colab**
3. **Mount your drive:**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
4. **Run the cells!**

### On Local Jupyter

1. **Install dependencies:**
   ```bash
   pip install numpy matplotlib ipywidgets nibabel plotly scipy
   jupyter nbextension enable --py widgetsnbextension
   ```

2. **Launch Jupyter:**
   ```bash
   jupyter notebook scripts/medical_2D_slice_visualization.ipynb
   ```

## Main Functions

### `load_volume(filepath)`

Load 3D medical volumes from various formats.

```python
# Load NumPy file
volume = load_volume('data/volume.npy')

# Load NIfTI file  
volume = load_volume('data/scan.nii.gz')
```

**Output:**
```
✓ Loaded NIfTI file: scan.nii.gz
  NIfTI header info:
    - Affine shape: (4, 4)
    - Voxel dims: (1.0, 1.0, 1.0)
  Volume shape: (512, 512, 133)
  Data type: float64
  Value range: [-1024.00, 3071.00]
```

### `PlotImage(volume, filename=None)`

Create a static 3×6 grid of slices.

```python
# Display in notebook
PlotImage(volume)

# Save to file
PlotImage(volume, filename='output.png')
```

**Features:**
- Automatically selects 18 equidistant slices
- Proper contrast adjustment (fixes black image issues)
- Optional high-res export

### `interactive_slice_viewer(volume, axis=2, title="Viewer", cmap='gray')`

Launch interactive slice browser with slider control.

```python
# View axial slices (default)
interactive_slice_viewer(volume, axis=2)

# View sagittal slices
interactive_slice_viewer(volume, axis=1)

# View coronal slices
interactive_slice_viewer(volume, axis=0)
```

**Controls:**
- **Slider:** Navigate through slices
- **Colormap:** Change visualization style
- **Contrast:** Adjust window/level

## Usage Examples

### Example 1: Quick Visualization

```python
import numpy as np
from medical_2D_slice_visualization import load_volume, PlotImage

# Load volume
volume = load_volume('data/nii/img0006.nii.gz')

# Display grid of slices
PlotImage(volume)
```

### Example 2: Batch Processing

```python
import os

folder_path = 'npy_images'
save_path = 'Visualized_images'

# Create output directory
os.makedirs(save_path, exist_ok=True)

# Process all .npy files
npy_files = [f for f in os.listdir(folder_path) if f.endswith('.npy')]

for npy_file in npy_files:
    file_path = os.path.join(folder_path, npy_file)
    volume = np.load(file_path)
    
    save_filename = os.path.join(save_path, npy_file.replace('.npy', '.png'))
    PlotImage(volume, filename=save_filename)
    print(f'✓ Saved: {save_filename}')
```

### Example 3: Interactive Exploration

```python
# Load volume
volume = load_volume('data/ct_scan.nii.gz')

# Launch interactive viewer
interactive_slice_viewer(
    volume,
    axis=2,  # Axial view
    title="CT Scan Explorer",
    cmap='bone'  # Bone colormap
)
```

### Example 4: Multi-Plane Viewing

```python
# View all three anatomical planes
volume = load_volume('scan.nii.gz')

# Axial (horizontal slices)
interactive_slice_viewer(volume, axis=2, title="Axial View")

# Sagittal (side view)
interactive_slice_viewer(volume, axis=1, title="Sagittal View")

# Coronal (front view)
interactive_slice_viewer(volume, axis=0, title="Coronal View")
```

## Comparison with 3D Viewer

| Feature | Notebook (2D Slices) | `medical_interactive_viewer.py` (3D) |
|---------|----------------------|--------------------------------------|
| **Platform** | Colab, Jupyter | Desktop (Windows, Linux, macOS) |
| **Visualization** | 2D slices, grids | Full 3D volume rendering |
| **Interactivity** | Slider navigation | 3D rotation, zoom, pan |
| **Use Case** | Quick inspection, batch processing | Deep exploration, presentations |
| **GPU** | Not required | GPU accelerated (Metal/DirectX/OpenGL) |
| **Export** | PNG images | Interactive HTML |

## Use Cases

### When to Use the Notebook

✅ **Quick 2D slice inspection**  
✅ **Batch processing multiple volumes**  
✅ **Working in Google Colab**  
✅ **Creating figure panels for papers**  
✅ **Comparing slices across datasets**

### When to Use 3D Viewer Script

✅ **Full 3D exploration**  
✅ **Volume rendering with transparency**  
✅ **Interactive presentations**  
✅ **Isosurface extraction**  
✅ **Side-by-side 3D comparison**

## Troubleshooting

### Issue: Black Images on MacBook

**Cause:** Incorrect intensity range scaling

**Solution:** Already fixed! The `PlotImage` function uses proper percentile-based scaling:
```python
vmin = np.percentile(images, 1)
vmax = np.percentile(images, 99)
```

### Issue: Widgets Not Working

**Solution:** Enable Jupyter widgets:
```bash
jupyter nbextension enable --py widgetsnbextension
```

### Issue: NIfTI Files Not Loading

**Solution:** Install nibabel:
```bash
pip install nibabel
```

### Issue: Out of Memory in Colab

**Solution:** Process files one at a time and clear memory:
```python
import gc

for file in files:
    volume = load_volume(file)
    PlotImage(volume)
    del volume
    gc.collect()
```

## Tips & Best Practices

### 1. **Memory Management**
```python
# Clear previous plots
import matplotlib.pyplot as plt
plt.close('all')

# Free memory after processing
import gc
gc.collect()
```

### 2. **High-Quality Exports**
```python
# Increase DPI for publication-quality figures
plt.savefig('output.png', bbox_inches='tight', dpi=600)
```

### 3. **Custom Slice Selection**
```python
# Manually select specific slices
slices = [10, 25, 40, 55, 70, 85]
for i, slice_idx in enumerate(slices):
    plt.subplot(2, 3, i+1)
    plt.imshow(volume[:,:,slice_idx], cmap='gray')
```

### 4. **Different Colormaps**
```python
# Try different visualization styles
colormaps = ['gray', 'bone', 'hot', 'viridis', 'plasma']
for cmap in colormaps:
    interactive_slice_viewer(volume, cmap=cmap, title=f"{cmap} view")
```

## Integration with Main Project

The notebook complements the 3D viewer:

1. **Use notebook for:** Quick 2D inspection and batch processing
2. **Use 3D script for:** Deep 3D exploration and presentations
3. **Workflow:**
   - Screen datasets with notebook
   - Explore interesting volumes in 3D
   - Export both 2D figures and 3D HTML

## Requirements

```
numpy>=1.20.0
matplotlib>=3.3.0
ipywidgets>=7.6.0
nibabel>=3.2.0
plotly>=5.0.0
scipy>=1.7.0
```

For Jupyter:
```bash
jupyter nbextension enable --py widgetsnbextension
```

---

**Ready to visualize!** 

Start with the notebook for quick 2D inspection, then use the 3D viewer (`medical_interactive_viewer.py`) for deep exploration.

