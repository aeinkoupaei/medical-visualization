# Output Directory

This directory contains exported interactive HTML visualizations.

## What Are These Files?

The HTML files in this directory are **fully interactive 3D medical imaging visualizations** that can be opened in any modern web browser.

### Key Features

- **Fully Interactive** - Rotate, zoom, pan with your mouse  
- **No Installation Required** - Works in any browser  
- **Standalone** - No server or Python needed  

## Example Files

### `volume_render_1.html`
- 3D volume rendering
- Transparent visualization
- Shows internal structures

### `Isosurface_1.html`
- Surface extraction
- Shows organ boundaries
- Faster rendering

### `Multiplaner_1.html`
- Three orthogonal slice planes
- Traditional medical imaging view
- Good for examining specific slices

### `volume_slices_1.html`
- Volume rendering + slice planes
- Best of both worlds
- Excellent for presentations

## Creating Your Own Exports

To create HTML exports like these:

```python
from scripts.medical_interactive_viewer import visualize_volume_interactive

# Load your volume
volume = load_nifti_volume("your_scan.nii.gz")

# Export to HTML
visualize_volume_interactive(
    volume,
    opacity='sigmoid_3',
    cmap='gray',
    save_html='output/my_visualization.html'
)
```

Or use the interactive menu:
```bash
python scripts/medical_interactive_viewer.py
# Choose visualization mode
# When prompted, say "yes" to save HTML
```

## Organizing Exports

### Suggested File Naming

```
output/
├── patient_001_brain_volume.html
├── patient_001_brain_isosurface.html
├── patient_002_ct_bone.html
└── comparison_before_after.html
```

### By Date
```
output/
├── 2025-01-15_scan.html
├── 2025-02-20_followup.html
└── 2025-03-10_final.html
```

### By Type
```
output/
├── volumes/
│   ├── brain_01.html
│   └── brain_02.html
├── isosurfaces/
│   └── skull.html
└── comparisons/
    └── before_after.html
```

## Additional Resources

- **Main Documentation:** [../README.md](../README.md)
- **Usage Examples:** [../EXAMPLES.md](../EXAMPLES.md)
- **Quick Start:** [../QUICK_START.md](../QUICK_START.md)


