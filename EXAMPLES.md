# Usage Examples

Practical code examples for common medical imaging visualization tasks.

## Table of Contents

1. [Basic Volume Loading](#basic-volume-loading)
2. [Volume Rendering Variations](#volume-rendering-variations)
3. [Isosurface Extraction](#isosurface-extraction)
4. [Multi-Planar Views](#multi-planar-views)
5. [Comparison and Analysis](#comparison-and-analysis)
6. [Exporting and Sharing](#exporting-and-sharing)
7. [Batch Processing](#batch-processing)
8. [Advanced Customization](#advanced-customization)

---

## Basic Volume Loading

### Load and Inspect a NIfTI File

```python
from scripts.medical_interactive_viewer import load_nifti_volume
import numpy as np

# Load the volume
volume = load_nifti_volume("data/nii/img0006.nii.gz")

# Inspect properties
print(f"Shape: {volume.shape}")
print(f"Data type: {volume.dtype}")
print(f"Value range: [{volume.min():.2f}, {volume.max():.2f}]")
print(f"Mean intensity: {volume.mean():.2f}")
print(f"Non-zero voxels: {np.count_nonzero(volume)}")
```

### Load Multiple Volumes

```python
import os
from pathlib import Path

# Load all NIfTI files in a directory
data_dir = Path("data/nii")
volumes = {}

for filepath in data_dir.glob("*.nii.gz"):
    name = filepath.stem.replace('.nii', '')
    volumes[name] = load_nifti_volume(str(filepath))
    print(f"Loaded {name}: {volumes[name].shape}")
```

---

## Volume Rendering Variations

### Transparent View (See Inside)

```python
from scripts.medical_interactive_viewer import visualize_volume_interactive

# Very transparent - good for seeing internal structures
visualize_volume_interactive(
    volume,
    opacity='sigmoid_1',     # Very transparent
    cmap='gray',
    title="Transparent Brain View"
)
```

### Opaque Surface View

```python
# Opaque - good for surface features
visualize_volume_interactive(
    volume,
    opacity='sigmoid_20',    # Very opaque
    cmap='bone',
    title="Surface View"
)
```

### Balanced View (Default)

```python
# Balanced transparency
visualize_volume_interactive(
    volume,
    opacity='sigmoid',       # Balanced (default)
    cmap='gray',
    title="Balanced View"
)
```

### CT Scan Visualization

```python
# Optimized for CT scans with bone
visualize_volume_interactive(
    volume,
    opacity='sigmoid_10',    # Show bone structures
    cmap='bone',             # Bone colormap
    title="CT Scan - Bone View"
)
```

### MRI Brain Visualization

```python
# Optimized for MRI brain scans
visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',     # See internal structures
    cmap='gray',             # Standard grayscale
    title="MRI Brain Scan"
)
```

---

## Isosurface Extraction

### Extract Brain Surface

```python
from scripts.medical_interactive_viewer import visualize_isosurface_interactive

# Extract surface at 60th percentile
visualize_isosurface_interactive(
    volume,
    threshold_percentile=60,
    cmap='viridis',
    smooth=True,
    title="Brain Surface"
)
```

### Extract Multiple Surfaces

```python
from scripts.medical_interactive_viewer import create_volume_grid
import pyvista as pv

# Create grid
grid = create_volume_grid(volume, use_cell_data=False)

# Extract multiple isosurfaces
thresholds = [
    np.percentile(volume[volume > 0], 30),
    np.percentile(volume[volume > 0], 50),
    np.percentile(volume[volume > 0], 70)
]

plotter = pv.Plotter()

colors = ['red', 'green', 'blue']
for i, threshold in enumerate(thresholds):
    surface = grid.contour([threshold], scalars="values")
    surface = surface.smooth(n_iter=50, relaxation_factor=0.1)
    plotter.add_mesh(surface, color=colors[i], opacity=0.5)

plotter.show()
```

### Organ Segmentation Visualization

```python
# For pre-segmented data with different tissue labels
def visualize_segmentation(segmentation, labels_dict):
    """
    Visualize multi-label segmentation.
    
    Parameters:
    -----------
    segmentation : numpy.ndarray
        Volume with integer labels
    labels_dict : dict
        {label_value: (name, color)}
    """
    plotter = pv.Plotter()
    
    for label, (name, color) in labels_dict.items():
        # Extract surface for this label
        mask = (segmentation == label).astype(float)
        grid = create_volume_grid(mask, use_cell_data=False)
        surface = grid.contour([0.5], scalars="values")
        
        if surface.n_points > 0:
            surface = surface.smooth(n_iter=30)
            plotter.add_mesh(surface, color=color, opacity=0.8, label=name)
    
    plotter.add_legend()
    plotter.show()

# Example usage
labels = {
    1: ("Gray Matter", "gray"),
    2: ("White Matter", "white"),
    3: ("CSF", "blue")
}
visualize_segmentation(segmentation_volume, labels)
```

---

## Multi-Planar Views

### Standard MPR View

```python
from scripts.medical_interactive_viewer import visualize_multiplanar

visualize_multiplanar(
    volume,
    cmap='gray',
    title="Multi-Planar Reconstruction"
)
```

### Volume with Slices

```python
from scripts.medical_interactive_viewer import visualize_volume_with_slices

# Combines transparent volume with slice planes
visualize_volume_with_slices(
    volume,
    cmap='gray',
    title="Volume + Slices"
)
```

### Custom Slice Positions

```python
import pyvista as pv

grid = create_volume_grid(volume, use_cell_data=True)
vmin, vmax = np.percentile(volume, [1, 99])

plotter = pv.Plotter()

# Add custom slices at specific positions
x_slice = grid.slice(normal=[1, 0, 0], origin=[volume.shape[0]//2, 0, 0])
y_slice = grid.slice(normal=[0, 1, 0], origin=[0, volume.shape[1]//2, 0])
z_slice = grid.slice(normal=[0, 0, 1], origin=[0, 0, volume.shape[2]//2])

plotter.add_mesh(x_slice, cmap='gray', clim=(vmin, vmax))
plotter.add_mesh(y_slice, cmap='gray', clim=(vmin, vmax))
plotter.add_mesh(z_slice, cmap='gray', clim=(vmin, vmax))

plotter.show()
```

---

## Comparison and Analysis

### Before and After Comparison

```python
from scripts.medical_interactive_viewer import compare_volumes_side_by_side

# Load two volumes
before = load_nifti_volume("before_treatment.nii.gz")
after = load_nifti_volume("after_treatment.nii.gz")

# Compare side by side
compare_volumes_side_by_side(
    before,
    after,
    titles=["Before Treatment", "After Treatment"],
    opacity='sigmoid',
    cmap='gray'
)
```

### Difference Map

```python
# Calculate and visualize difference
difference = after - before

# Normalize for visualization
diff_normalized = (difference - difference.min()) / (difference.max() - difference.min())

visualize_volume_interactive(
    diff_normalized,
    opacity='sigmoid_5',
    cmap='seismic',  # Red=increase, Blue=decrease
    title="Treatment Effect (Difference Map)"
)
```

### Source vs Target Registration

```python
source = load_nifti_volume("moving_image.nii.gz")
target = load_nifti_volume("fixed_image.nii.gz")

compare_volumes_side_by_side(
    source,
    target,
    titles=["Source (Moving)", "Target (Fixed)"],
    opacity='sigmoid',
    cmap='viridis'
)
```

---

## Exporting and Sharing

### Save Interactive HTML

```python
# Save any visualization as interactive HTML
visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',
    cmap='gray',
    save_html='output/brain_interactive.html'
)

# The HTML file can now be:
# - Opened in any browser
# - Shared via email
# - Embedded in websites
# - Viewed without Python installation
```

### Batch Export Multiple Views

```python
import os

# Create output directory
os.makedirs('output/batch_export', exist_ok=True)

# Export multiple views of the same volume
views = [
    ('sigmoid_1', 'transparent'),
    ('sigmoid_5', 'balanced'),
    ('sigmoid_15', 'opaque')
]

for opacity, name in views:
    visualize_volume_interactive(
        volume,
        opacity=opacity,
        cmap='gray',
        save_html=f'output/batch_export/view_{name}.html',
        title=f"Brain - {name.title()} View"
    )
    print(f"✅ Exported {name} view")
```

### Create Gallery HTML

```python
# After creating multiple HTML files, create an index
html_content = """
<!DOCTYPE html>
<html>
<head><title>Medical Imaging Gallery</title></head>
<body>
    <h1>3D Medical Imaging Gallery</h1>
    <ul>
        <li><a href="view_transparent.html">Transparent View</a></li>
        <li><a href="view_balanced.html">Balanced View</a></li>
        <li><a href="view_opaque.html">Opaque View</a></li>
    </ul>
</body>
</html>
"""

with open('output/batch_export/index.html', 'w') as f:
    f.write(html_content)
```

---

## Batch Processing

### Process Multiple Files

```python
from pathlib import Path

def process_directory(input_dir, output_dir):
    """Process all NIfTI files in a directory."""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for nifti_file in input_path.glob("*.nii.gz"):
        print(f"\nProcessing {nifti_file.name}...")
        
        # Load volume
        volume = load_nifti_volume(str(nifti_file))
        
        # Create output filename
        output_name = nifti_file.stem.replace('.nii', '') + '.html'
        output_file = output_path / output_name
        
        # Visualize and save
        visualize_volume_interactive(
            volume,
            opacity='sigmoid_3',
            cmap='gray',
            save_html=str(output_file),
            title=nifti_file.stem
        )
        
        print(f"✅ Saved to {output_file}")

# Run batch processing
process_directory('data/nii', 'output/processed')
```

### Extract Statistics

```python
def analyze_volume(filepath):
    """Extract statistics from a NIfTI volume."""
    
    volume = load_nifti_volume(filepath)
    
    stats = {
        'filename': os.path.basename(filepath),
        'shape': volume.shape,
        'voxels': volume.size,
        'non_zero_voxels': np.count_nonzero(volume),
        'min': float(volume.min()),
        'max': float(volume.max()),
        'mean': float(volume.mean()),
        'std': float(volume.std()),
        'median': float(np.median(volume)),
        'percentiles': {
            '25th': float(np.percentile(volume, 25)),
            '50th': float(np.percentile(volume, 50)),
            '75th': float(np.percentile(volume, 75)),
            '95th': float(np.percentile(volume, 95))
        }
    }
    
    return stats

# Analyze all files
results = []
for filepath in Path('data/nii').glob('*.nii.gz'):
    stats = analyze_volume(str(filepath))
    results.append(stats)
    
# Print summary
import json
print(json.dumps(results, indent=2))
```

---

## Advanced Customization

### Custom Colormap

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Create custom colormap
colors = ['black', 'darkblue', 'blue', 'cyan', 'yellow', 'red', 'white']
n_bins = 256
cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

# Register it with matplotlib
plt.register_cmap(cmap=cmap)

# Use it
visualize_volume_interactive(
    volume,
    opacity='sigmoid_5',
    cmap='custom',
    title="Custom Colormap View"
)
```

### Custom Window Size and Camera

```python
import pyvista as pv

grid = create_volume_grid(volume, use_cell_data=True)
vmin, vmax = np.percentile(volume, [5, 95])

# Create plotter with custom settings
plotter = pv.Plotter(window_size=(1920, 1080))  # Full HD

# Add volume
plotter.add_volume(grid, cmap='gray', clim=(vmin, vmax), opacity='sigmoid_3')

# Custom camera position
plotter.camera_position = [
    (300, 300, 300),  # Camera position
    (128, 128, 128),  # Focal point (center of volume)
    (0, 0, 1)         # View up vector
]

# Custom background
plotter.background_color = 'white'

plotter.show()
```

### Add Annotations

```python
plotter = pv.Plotter()

# Add volume
grid = create_volume_grid(volume, use_cell_data=True)
plotter.add_volume(grid, cmap='gray', opacity='sigmoid_3')

# Add text annotations
plotter.add_text("Patient ID: 12345", position='upper_left', font_size=10)
plotter.add_text("Scan Date: 2025-01-15", position='upper_left', font_size=8)
plotter.add_text("MRI Brain T1", position='upper_edge', font_size=14)

# Add arrow pointing to region of interest
start_point = [100, 100, 100]
end_point = [150, 150, 150]
plotter.add_arrows(start_point, end_point, mag=50, color='red')

plotter.show()
```

---

## Tips and Tricks

### Optimize for Large Volumes

```python
# Downsample for faster visualization
volume_downsampled = volume[::2, ::2, ::2]  # Half resolution

# Or use slicing for ROI
roi = volume[50:150, 50:150, 50:150]  # Extract region of interest

visualize_volume_interactive(roi, opacity='sigmoid_3')
```

### Memory-Efficient Loading

```python
import nibabel as nib

# Load header without loading data
nifti = nib.load("large_file.nii.gz")
print(f"Shape: {nifti.shape}")  # Check size before loading

# Load only if size is manageable
if nifti.shape[0] * nifti.shape[1] * nifti.shape[2] < 512**3:
    volume = nifti.get_fdata()
else:
    print("File too large, will downsample...")
    # Implement downsampling strategy
```


