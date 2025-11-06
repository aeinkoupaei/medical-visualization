# Quick Start Guide

Get up and running with the Interactive 3D Medical Volume Viewer in 5 minutes! Works on macOS, Windows, and Linux.

## Step 1: Install Dependencies (2 minutes)

### All Platforms

```bash
# Navigate to the project directory
cd medical-visualization

# Install all required packages
pip install -r requirements.txt
```

**Platform-specific notes:**

**macOS:** Use `pip3` if `pip` doesn't work
```bash
pip3 install -r requirements.txt
```

**Windows:** Use Command Prompt or PowerShell
```bash
pip install -r requirements.txt
```

**Linux:** You may need to install system packages first
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Then install Python packages
pip3 install -r requirements.txt
```

**That's it!** All dependencies including HTML export support are installed.

## Step 2: Run the Viewer (1 minute)

### Option A: Interactive Mode (Recommended for First-Time Users)

**macOS/Linux:**
```bash
python scripts/medical_interactive_viewer.py
```

**Windows:**
```bash
python scripts\medical_interactive_viewer.py
```

Then:
1. Enter the path to your `.nii` or `.nii.gz` file when prompted
2. Choose a visualization mode (1-6)
3. Interact with the 3D viewer using your mouse!

### Option B: Direct File Mode

**macOS/Linux:**
```bash
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

**Windows:**
```bash
python scripts\medical_interactive_viewer.py data\nii\img0006.nii.gz
```

### Option C: Using the Included Sample Data

**macOS/Linux:**
```bash
# Try sample volume 1
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz

# Try sample volume 2
python scripts/medical_interactive_viewer.py data/nii/img0009.nii.gz
```

**Windows:**
```bash
# Try sample volume 1
python scripts\medical_interactive_viewer.py data\nii\img0006.nii.gz

# Try sample volume 2
python scripts\medical_interactive_viewer.py data\nii\img0009.nii.gz
```

## Step 3: Explore Visualization Modes

When the menu appears, try each mode:

### Mode 1: Volume Rendering (Recommended First!)
- Most popular mode
- Shows transparent 3D volume
- Great for seeing internal structures
- Save as HTML when prompted for sharing!

### Mode 2: Isosurface
- Extracts surfaces (like organ boundaries)
- Faster rendering
- Good for anatomy visualization

### Mode 3: Multi-Planar (MPR)
- Three orthogonal slice planes
- Traditional medical imaging view
- Good for examining specific slices

### Mode 4: Volume + Slices
- Best of both worlds
- Transparent volume with slice planes
- Excellent for HTML export

### Mode 5: Side-by-Side Comparison
- Compare two volumes
- Synchronized rotation
- Perfect for before/after analysis

## Save Interactive HTML

When prompted "Save as interactive HTML?":
1. Type `yes`
2. Enter filename (e.g., `my_brain.html`)
3. File saves to current directory
4. **Double-click to open in any browser!**

The HTML file remains fully interactive - anyone can rotate/zoom without installing anything!

## Quick Python Example

Want to use it in your own Python script? (Works on all platforms!)

```python
from scripts.medical_interactive_viewer import (
    load_nifti_volume,
    visualize_volume_interactive
)

# Load your data
volume = load_nifti_volume("path/to/your/scan.nii.gz")

# Visualize (opens interactive window)
visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',        # Transparent
    cmap='gray',                # Grayscale
    save_html='output.html'     # Save for sharing
)
```

## Verify Everything Works

Run this test:

**macOS/Linux:**
```bash
# This should open an interactive 3D viewer with the sample data
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

**Windows:**
```bash
python scripts\medical_interactive_viewer.py data\nii\img0006.nii.gz
```

If it works, you're all set!

## Common Issues

### "No module named 'pyvista'"
**Fix:** `pip install -r requirements.txt`

### "Missing dependencies for HTML export"
**Fix:** `pip install nest-asyncio trame trame-vtk trame-vuetify`

### Viewer window doesn't appear
**Fix:** `pip install pyqt5` (adds GUI backend support)

### Out of memory with large files
**Solution:** Use isosurface mode (Mode 2) or downsample:
```python
volume = volume[::2, ::2, ::2]  # Use every other voxel
```

## Next Steps

1. **Try all 5 visualization modes** with the sample data
2. **Load your own NIfTI files**
3. **Export an interactive HTML** to share with colleagues
4. **Read the full [README.md](README.md)** for advanced features

## Need Help?

- **Full Documentation:** See [README.md](README.md)
- **Report Issues:** [GitHub Issues](https://github.com/yourusername/medical-visualization/issues)
- **API Reference:** See function docstrings in `medical_interactive_viewer.py`

---

**That's it! You're ready to visualize medical imaging data in 3D!**

Typical workflow:
1. `python scripts/medical_interactive_viewer.py your_scan.nii.gz`
2. Choose Mode 1 (Volume Rendering)
3. Save as HTML
4. Share with colleagues!

---

## Alternative: 2D Slice Visualization (Jupyter Notebook)

For quick 2D slice inspection and batch processing, use the Jupyter notebook:

### Launch the Notebook

```bash
# Install Jupyter if needed
pip install jupyter ipywidgets

# Launch notebook
jupyter notebook scripts/medical_2D_slice_visualization.ipynb
```

### Quick 2D Visualization

The notebook provides:
- **Grid View**: 3×6 grid of slices (18 slices at once)
- **Interactive Slider**: Navigate through slices
- **Batch Processing**: Process entire folders
- **Google Colab Support**: Works in cloud notebooks

### When to Use Each Tool

| Task | Tool |
|------|------|
| **Quick 2D inspection** | 📓 Jupyter Notebook |
| **Batch processing** | 📓 Jupyter Notebook |
| **Full 3D exploration** | 🖥️ 3D Viewer Script |
| **Interactive presentations** | 🖥️ 3D Viewer Script |

**See [NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md) for detailed notebook documentation.**

