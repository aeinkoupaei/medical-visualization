#!/usr/bin/env python3
"""
Flask-based Medical Visualization Platform
Docker-ready application for 3D medical imaging
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image
import io
import platform
from pathlib import Path
import shutil
import base64
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Try to import PyVista (optional - only needed for legacy rendering)
try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
    # Configure PyVista for headless rendering
    os.environ['MPLBACKEND'] = 'Agg'
    if platform.system() == 'Linux':
        try:
            pv.start_xvfb()
        except:
            pass
    pv.OFF_SCREEN = True
    pv.global_theme.notebook = False
except ImportError:
    PYVISTA_AVAILABLE = False
    print("Warning: PyVista not available. Legacy 3D rendering disabled. Using Plotly for all 3D rendering.")

app = Flask(__name__)
CORS(app)

# Configuration
# Use project-local folders by default (works on macOS/local dev),
# but allow overriding via environment variables (for Docker/HF Spaces).
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_UPLOAD_FOLDER = BASE_DIR / 'uploads'
DEFAULT_OUTPUT_FOLDER = BASE_DIR / 'outputs'

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(DEFAULT_UPLOAD_FOLDER))
OUTPUT_FOLDER = os.environ.get('OUTPUT_FOLDER', str(DEFAULT_OUTPUT_FOLDER))
ALLOWED_EXTENSIONS = {'nii', 'gz', 'npy'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def allowed_file(filename):
    return '.' in filename and \
           any(filename.lower().endswith(ext) or filename.lower().endswith(f'.{ext}') 
               for ext in ['nii', 'nii.gz', 'npy'])

def clamp_index(value, max_index):
    """Clamp slice indices to a valid range."""
    try:
        idx = int(value)
    except (TypeError, ValueError):
        idx = 0
    return max(0, min(idx, max_index))

def load_volume(filepath):
    """Load 3D medical volume from NIfTI or NumPy file."""
    filepath_str = str(filepath).lower()
    file_ext = Path(filepath).suffix.lower()
    
    if filepath_str.endswith('.nii.gz') or filepath_str.endswith('.nii') or (file_ext == '.gz' and 'nii' in filepath_str):
        nifti_img = nib.load(filepath)
        volume = nifti_img.get_fdata()
        header = nifti_img.header
        spacing = header.get_zooms()[:3] if len(header.get_zooms()) >= 3 else (1.0, 1.0, 1.0)
        
        metadata = {
            'format': 'NIfTI',
            'shape': [int(x) for x in volume.shape],
            'dtype': str(volume.dtype),
            'spacing': [float(x) for x in spacing],
            'value_range': [float(volume.min()), float(volume.max())],
            'mean': float(volume.mean()),
            'std': float(volume.std())
        }
        
    elif file_ext == '.npy':
        volume = np.load(filepath)
        if volume.ndim != 3:
            raise ValueError(f"Expected 3D array, got {volume.ndim}D array")
        
        metadata = {
            'format': 'NumPy',
            'shape': [int(x) for x in volume.shape],
            'dtype': str(volume.dtype),
            'spacing': [1.0, 1.0, 1.0],
            'value_range': [float(volume.min()), float(volume.max())],
            'mean': float(volume.mean()),
            'std': float(volume.std())
        }
    else:
        raise ValueError(f"Unsupported file format")
    
    return volume, metadata

def render_slice_image(volume, axis=2, slice_idx=None, cmap='gray'):
    """Render a 2D slice from the volume."""
    if slice_idx is None:
        slice_idx = volume.shape[axis] // 2
    slice_idx = clamp_index(slice_idx, volume.shape[axis] - 1)
    
    if axis == 0:
        # Sagittal: slice along X, show Y-Z plane (transpose for proper orientation)
        slice_data = volume[slice_idx, :, :].T
    elif axis == 1:
        # Coronal: slice along Y, show X-Z plane (transpose for proper orientation)
        slice_data = volume[:, slice_idx, :].T
    else:
        # Axial: slice along Z, show X-Y plane
        slice_data = volume[:, :, slice_idx].T
    
    fig = Figure(figsize=(8, 8), dpi=100)
    ax = fig.add_subplot(111)
    
    vmin, vmax = np.percentile(slice_data, [1, 99]) if slice_data.size else (0, 1)
    im = ax.imshow(slice_data, cmap=cmap, vmin=vmin, vmax=vmax, origin='lower', aspect='auto')
    
    axis_names = ['Sagittal (X)', 'Coronal (Y)', 'Axial (Z)']
    ax.set_title(f"{axis_names[axis]} - Slice {slice_idx}/{volume.shape[axis]-1}")
    ax.axis('off')
    fig.colorbar(im, ax=ax)
    
    # Save to bytes
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)
    
    return buf

def render_multiview(volume, slices=None, cmap='gray'):
    """Render axial, coronal, and sagittal views with crosshairs."""
    if slices is None:
        slices = {}
    max_x, max_y, max_z = (volume.shape[0] - 1, volume.shape[1] - 1, volume.shape[2] - 1)
    sx = clamp_index(slices.get('slice_x', max_x // 2), max_x)
    sy = clamp_index(slices.get('slice_y', max_y // 2), max_y)
    sz = clamp_index(slices.get('slice_z', max_z // 2), max_z)

    vmin, vmax = np.percentile(volume, [1, 99]) if volume.size else (0, 1)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(volume[sx, :, :], cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    axes[0].axhline(y=sy, color='r', linestyle='--', alpha=0.5)
    axes[0].axvline(x=sz, color='b', linestyle='--', alpha=0.5)
    axes[0].set_title(f"Sagittal (X={sx})")
    axes[0].set_xlabel('Y')
    axes[0].set_ylabel('Z')

    axes[1].imshow(volume[:, sy, :], cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    axes[1].axhline(y=sx, color='g', linestyle='--', alpha=0.5)
    axes[1].axvline(x=sz, color='b', linestyle='--', alpha=0.5)
    axes[1].set_title(f"Coronal (Y={sy})")
    axes[1].set_xlabel('X')
    axes[1].set_ylabel('Z')

    axes[2].imshow(volume[:, :, sz], cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    axes[2].axhline(y=sx, color='g', linestyle='--', alpha=0.5)
    axes[2].axvline(x=sy, color='r', linestyle='--', alpha=0.5)
    axes[2].set_title(f"Axial (Z={sz})")
    axes[2].set_xlabel('X')
    axes[2].set_ylabel('Y')

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)

    return buf

def render_compare_slices(volume_a, volume_b, axis=2, slice_idx=None, cmap='gray'):
    """Render side-by-side comparison of the same slice index across two volumes."""
    # Ensure slice index is within bounds of both volumes
    max_a = volume_a.shape[axis] - 1
    max_b = volume_b.shape[axis] - 1
    max_idx = min(max_a, max_b)
    if slice_idx is None:
        slice_idx = max_idx // 2
    slice_idx = clamp_index(slice_idx, max_idx)

    if axis == 0:
        slice_a = volume_a[slice_idx, :, :]
        slice_b = volume_b[slice_idx, :, :]
    elif axis == 1:
        slice_a = volume_a[:, slice_idx, :]
        slice_b = volume_b[:, slice_idx, :]
    else:
        slice_a = volume_a[:, :, slice_idx]
        slice_b = volume_b[:, :, slice_idx]

    # Use a shared intensity range for fair visual comparison
    combined = np.concatenate([slice_a.flatten(), slice_b.flatten()])
    vmin, vmax = np.percentile(combined, [1, 99]) if combined.size else (0, 1)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    im0 = axes[0].imshow(slice_a, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    axes[0].set_title(f'Volume A - Slice {slice_idx}')
    axes[0].axis('off')

    im1 = axes[1].imshow(slice_b, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    axes[1].set_title(f'Volume B - Slice {slice_idx}')
    axes[1].axis('off')

    fig.colorbar(im1, ax=axes.ravel().tolist(), shrink=0.8)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
    buf.seek(0)
    plt.close(fig)

    return buf

def render_3d_volume(volume, opacity='sigmoid_3', cmap='gray'):
    """Render 3D volume visualization (Legacy PyVista method)."""
    if not PYVISTA_AVAILABLE:
        raise RuntimeError("PyVista not available. Use Plotly rendering instead.")
    grid = pv.ImageData()
    grid.dimensions = np.array(volume.shape) + 1
    grid.cell_data["values"] = volume.flatten(order="F")
    
    vmin, vmax = np.percentile(volume, [1, 99])
    
    # Create opacity mapping
    opacity_mappings = {
        'sigmoid_1': 'sigmoid_1',
        'sigmoid_2': 'sigmoid_2',
        'sigmoid_3': 'sigmoid_3',
        'sigmoid_5': 'sigmoid_5',
        'sigmoid_10': 'sigmoid_10'
    }
    opacity_func = opacity_mappings.get(opacity, 'sigmoid_3')
    
    plotter = pv.Plotter(off_screen=True, window_size=(1200, 900))
    plotter.add_volume(
        grid,
        cmap=cmap,
        clim=(vmin, vmax),
        opacity=opacity_func,
        shade=False
    )
    
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    plotter.enable_anti_aliasing('fxaa')
    plotter.show_axes()
    plotter.background_color = '#1a1a1a'
    
    # Save screenshot
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=OUTPUT_FOLDER)
    temp_file.close()
    
    plotter.screenshot(temp_file.name, transparent_background=False)
    plotter.close()
    
    return temp_file.name

def render_3d_html(volume, opacity='sigmoid_3', cmap='gray'):
    """Generate an interactive 3D HTML viewer using PyVista/vtk.js (Legacy method)."""
    if not PYVISTA_AVAILABLE:
        raise RuntimeError("PyVista not available. Use Plotly rendering instead.")
    grid = pv.ImageData()
    grid.dimensions = np.array(volume.shape) + 1
    grid.cell_data["values"] = volume.flatten(order="F")

    vmin, vmax = np.percentile(volume, [1, 99])

    opacity_mappings = {
        'sigmoid_1': 'sigmoid_1',
        'sigmoid_2': 'sigmoid_2',
        'sigmoid_3': 'sigmoid_3',
        'sigmoid_5': 'sigmoid_5',
        'sigmoid_10': 'sigmoid_10'
    }
    opacity_func = opacity_mappings.get(opacity, 'sigmoid_3')

    plotter = pv.Plotter(off_screen=True, window_size=(1200, 900))
    plotter.add_volume(
        grid,
        cmap=cmap,
        clim=(vmin, vmax),
        opacity=opacity_func,
        shade=False
    )
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    plotter.enable_anti_aliasing('fxaa')
    plotter.show_axes()
    plotter.background_color = '#1a1a1a'

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER)
    temp_file.close()

    try:
        # Try to export with trame (if available)
        plotter.export_html(temp_file.name)
    except (ImportError, RuntimeError, Exception) as e:
        # Fallback: create a simple HTML with rotating static images
        print(f"Warning: Interactive export failed ({str(e)}), using fallback method")
        plotter.close()
        return render_3d_html_fallback(volume, opacity, cmap)
    
    plotter.close()
    return temp_file.name

def render_3d_html_fallback(volume, opacity='sigmoid_3', cmap='gray'):
    """Fallback: Generate HTML with multiple angle screenshots for pseudo-interactive viewing (Legacy method)."""
    if not PYVISTA_AVAILABLE:
        raise RuntimeError("PyVista not available. Use Plotly rendering instead.")
    grid = pv.ImageData()
    grid.dimensions = np.array(volume.shape) + 1
    grid.cell_data["values"] = volume.flatten(order="F")
    
    vmin, vmax = np.percentile(volume, [1, 99])
    
    opacity_mappings = {
        'sigmoid_1': 'sigmoid_1',
        'sigmoid_2': 'sigmoid_2',
        'sigmoid_3': 'sigmoid_3',
        'sigmoid_5': 'sigmoid_5',
        'sigmoid_10': 'sigmoid_10'
    }
    opacity_func = opacity_mappings.get(opacity, 'sigmoid_3')
    
    # Generate screenshots from multiple angles
    angles = [
        ('front', 0, 0),
        ('right', 0, 90),
        ('top', 90, 0),
        ('left', 0, -90),
        ('bottom', -90, 0),
        ('back', 0, 180)
    ]
    
    screenshots = []
    for name, elevation, azimuth in angles:
        plotter = pv.Plotter(off_screen=True, window_size=(800, 800))
        plotter.add_volume(
            grid,
            cmap=cmap,
            clim=(vmin, vmax),
            opacity=opacity_func,
            shade=False
        )
        plotter.camera_position = 'xy'
        plotter.camera.elevation = 30 + elevation
        plotter.camera.azimuth = 45 + azimuth
        plotter.enable_anti_aliasing('fxaa')
        plotter.show_axes()
        plotter.background_color = '#1a1a1a'
        
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=OUTPUT_FOLDER)
        temp_img.close()
        plotter.screenshot(temp_img.name, transparent_background=False)
        plotter.close()
        
        # Read image and convert to base64
        with open(temp_img.name, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
            screenshots.append((name, img_data))
        
        # Clean up temp image
        try:
            os.remove(temp_img.name)
        except OSError:
            pass
    
    # Pre-build dynamic HTML fragments to avoid complex f-string expressions
    buttons_html = ''.join(
        f'<button onclick="showView(\\"{name}\\")" id="btn-{name}">{name.capitalize()}</button>'
        for name, _ in screenshots
    )
    views_js = ','.join(
        f'"{name}": "data:image/png;base64,{img_data}"'
        for name, img_data in screenshots
    )

    # Create interactive HTML with view selector
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Volume Viewer (Fallback)</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: white;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}
        .controls {{
            padding: 15px;
            background: #2a2a2a;
            border-bottom: 2px solid #3a3a3a;
            text-align: center;
        }}
        .controls button {{
            margin: 5px;
            padding: 10px 20px;
            background: #4a4a4a;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        .controls button:hover {{
            background: #5a5a5a;
        }}
        .controls button.active {{
            background: #667eea;
        }}
        .viewer {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .viewer img {{
            max-width: 100%;
            max-height: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }}
        .info {{
            padding: 10px;
            text-align: center;
            background: #2a2a2a;
            border-top: 2px solid #3a3a3a;
            font-size: 12px;
            color: #aaa;
        }}
    </style>
</head>
<body>
    <div class="controls">
        <strong>View Angle:</strong>
        {buttons_html}
    </div>
    <div class="viewer">
        <img id="volume-view" src="" alt="3D Volume View">
    </div>
    <div class="info">
        Interactive 3D export not available. Use buttons above to view from different angles.
    </div>
    <script>
        const views = {{
            {views_js}
        }};
        
        let currentView = 'front';
        
        function showView(viewName) {{
            currentView = viewName;
            document.getElementById('volume-view').src = views[viewName];
            
            // Update button states
            document.querySelectorAll('.controls button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.getElementById('btn-' + viewName).classList.add('active');
        }}
        
        // Show initial view
        showView('front');
        
        // Keyboard navigation
        const viewNames = Object.keys(views);
        document.addEventListener('keydown', (e) => {{
            const currentIndex = viewNames.indexOf(currentView);
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {{
                const nextIndex = (currentIndex + 1) % viewNames.length;
                showView(viewNames[nextIndex]);
            }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
                const prevIndex = (currentIndex - 1 + viewNames.length) % viewNames.length;
                showView(viewNames[prevIndex]);
            }}
        }});
    </script>
</body>
</html>
"""
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(html_content)
    temp_file.close()
    
    return temp_file.name

def render_compare_3d_html(volume_a, volume_b, opacity='sigmoid_3', cmap='gray'):
    """Generate side-by-side interactive 3D comparison HTML (Legacy PyVista method)."""
    if not PYVISTA_AVAILABLE:
        raise RuntimeError("PyVista not available. Use Plotly rendering instead.")
    # Check if we need fallback mode by testing export
    grid_test = pv.ImageData()
    grid_test.dimensions = (10, 10, 10)
    grid_test.cell_data["values"] = np.zeros(9*9*9)
    plotter_test = pv.Plotter(off_screen=True)
    plotter_test.add_volume(grid_test)
    
    use_fallback = False
    test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER)
    test_file.close()
    
    try:
        plotter_test.export_html(test_file.name)
        plotter_test.close()
        os.remove(test_file.name)
    except (ImportError, RuntimeError, Exception):
        use_fallback = True
        plotter_test.close()
        try:
            os.remove(test_file.name)
        except:
            pass
    
    if use_fallback:
        # Use fallback comparison with screenshots
        return render_compare_3d_html_fallback(volume_a, volume_b, opacity, cmap)
    
    # Create two separate HTML files
    html_a = render_3d_html(volume_a, opacity, cmap)
    html_b = render_3d_html(volume_b, opacity, cmap)
    
    # Read both HTML files
    with open(html_a, 'r') as f:
        content_a = f.read()
    with open(html_b, 'r') as f:
        content_b = f.read()
    
    # Create iframes for side-by-side comparison
    combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Volume Comparison</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: white;
        }}
        .container {{
            display: flex;
            height: 100vh;
            gap: 10px;
            padding: 10px;
            box-sizing: border-box;
        }}
        .volume-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #2a2a2a;
            border-radius: 8px;
            padding: 10px;
            box-sizing: border-box;
        }}
        .volume-panel h2 {{
            margin: 0 0 10px 0;
            padding: 10px;
            background: #3a3a3a;
            border-radius: 6px;
            text-align: center;
            font-size: 1.2em;
        }}
        iframe {{
            flex: 1;
            border: none;
            border-radius: 8px;
            background: #1a1a1a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="volume-panel">
            <h2>Volume A</h2>
            <iframe srcdoc='{content_a.replace("'", "&#39;")}'></iframe>
        </div>
        <div class="volume-panel">
            <h2>Volume B</h2>
            <iframe srcdoc='{content_b.replace("'", "&#39;")}'></iframe>
        </div>
    </div>
</body>
</html>
"""
    
    # Save combined HTML
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(combined_html)
    temp_file.close()
    
    # Clean up individual files
    try:
        os.remove(html_a)
        os.remove(html_b)
    except OSError:
        pass
    
    return temp_file.name

def render_compare_3d_html_fallback(volume_a, volume_b, opacity='sigmoid_3', cmap='gray'):
    """Fallback comparison with screenshot-based viewers."""
    # Use the fallback renderer for both volumes
    html_a = render_3d_html_fallback(volume_a, opacity, cmap)
    html_b = render_3d_html_fallback(volume_b, opacity, cmap)
    
    with open(html_a, 'r') as f:
        content_a = f.read()
    with open(html_b, 'r') as f:
        content_b = f.read()
    
    # Create side-by-side comparison
    combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Volume Comparison (Fallback)</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #1a1a1a;
            color: white;
        }}
        .container {{
            display: flex;
            height: 100vh;
            gap: 10px;
            padding: 10px;
            box-sizing: border-box;
        }}
        .volume-panel {{
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #2a2a2a;
            border-radius: 8px;
            padding: 10px;
            box-sizing: border-box;
        }}
        .volume-panel h2 {{
            margin: 0 0 10px 0;
            padding: 10px;
            background: #3a3a3a;
            border-radius: 6px;
            text-align: center;
            font-size: 1.2em;
        }}
        iframe {{
            flex: 1;
            border: none;
            border-radius: 8px;
            background: #1a1a1a;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="volume-panel">
            <h2>Volume A</h2>
            <iframe srcdoc='{content_a.replace("'", "&#39;")}'></iframe>
        </div>
        <div class="volume-panel">
            <h2>Volume B</h2>
            <iframe srcdoc='{content_b.replace("'", "&#39;")}'></iframe>
        </div>
    </div>
</body>
</html>
"""
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(combined_html)
    temp_file.close()
    
    # Clean up individual files
    try:
        os.remove(html_a)
        os.remove(html_b)
    except OSError:
        pass
    
    return temp_file.name

def render_compare_3d(volume_a, volume_b, opacity='sigmoid_3', cmap='gray'):
    """Render two 3D volumes and stitch the screenshots side-by-side (Legacy PyVista method)."""
    if not PYVISTA_AVAILABLE:
        raise RuntimeError("PyVista not available. Use Plotly rendering instead.")
    path_a = render_3d_volume(volume_a, opacity=opacity, cmap=cmap)
    path_b = render_3d_volume(volume_b, opacity=opacity, cmap=cmap)

    # Load images
    img_a = Image.open(path_a).convert("RGB")
    img_b = Image.open(path_b).convert("RGB")

    # Match heights
    h = max(img_a.height, img_b.height)
    w_a, w_b = img_a.width, img_b.width
    if img_a.height != h:
        img_a = img_a.resize((w_a, h))
    if img_b.height != h:
        img_b = img_b.resize((w_b, h))

    combined = Image.new("RGB", (w_a + w_b, h), color=(255, 255, 255))
    combined.paste(img_a, (0, 0))
    combined.paste(img_b, (w_a, 0))

    buf = io.BytesIO()
    combined.save(buf, format='PNG')
    buf.seek(0)

    # Cleanup temp files
    for p in [path_a, path_b]:
        try:
            os.remove(p)
        except OSError:
            pass

    return buf

def render_3d_volume_plotly(volume, opacity=0.1, cmap='gray', downsample_factor=2):
    """Render interactive 3D volume visualization using Plotly."""
    # Auto-adjust downsampling based on volume size to prevent OOM
    total_voxels = np.prod(volume.shape)
    if total_voxels > 50_000_000:  # >50M voxels
        downsample_factor = max(downsample_factor, 4)
    elif total_voxels > 10_000_000:  # >10M voxels
        downsample_factor = max(downsample_factor, 3)
    
    # Downsample for performance
    if downsample_factor > 1:
        volume_ds = volume[::downsample_factor, ::downsample_factor, ::downsample_factor]
    else:
        volume_ds = volume
    
    # Safety check - limit max size
    if np.prod(volume_ds.shape) > 8_000_000:  # Still too large after downsampling
        # Force more aggressive downsampling
        extra_factor = 2
        volume_ds = volume_ds[::extra_factor, ::extra_factor, ::extra_factor]
    
    # Normalize volume data to 0-1 range for better visualization
    vmin, vmax = np.percentile(volume_ds, [1, 99])
    volume_normalized = np.clip((volume_ds - vmin) / (vmax - vmin + 1e-8), 0, 1)
    
    # Create mesh grid for volume
    X, Y, Z = np.mgrid[0:volume_ds.shape[0], 0:volume_ds.shape[1], 0:volume_ds.shape[2]]
    
    # Colormap mapping
    colormap_dict = {
        'gray': 'gray',
        'bone': 'bone',
        'viridis': 'viridis',
        'hot': 'hot',
        'cool': 'blues',
        'plasma': 'plasma'
    }
    plotly_cmap = colormap_dict.get(cmap, 'gray')
    
    # Create 3D volume using isosurface (better performance than full volume)
    # We'll create multiple isosurfaces at different intensity levels
    fig = go.Figure()
    
    # Add multiple isosurface layers for depth perception
    isomin = volume_normalized.min()
    isomax = volume_normalized.max()
    
    # Adjust surface count based on volume size for memory efficiency
    voxel_count = np.prod(volume_ds.shape)
    if voxel_count > 5_000_000:
        surface_count = 10
    elif voxel_count > 2_000_000:
        surface_count = 12
    else:
        surface_count = 17
    
    # Main volume rendering using volume trace
    fig.add_trace(go.Volume(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=volume_normalized.flatten(),
        opacity=opacity,
        surface_count=surface_count,  # Adaptive based on size
        colorscale=plotly_cmap,
        isomin=isomin,
        isomax=isomax,
        caps=dict(x_show=False, y_show=False, z_show=False),
        hoverinfo='skip'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
        title='Interactive 3D Medical Volume',
        scene=dict(
            xaxis=dict(title='X', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray', showbackground=True),
            yaxis=dict(title='Y', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray', showbackground=True),
            zaxis=dict(title='Z', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray', showbackground=True),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        paper_bgcolor='rgb(10, 10, 10)',
        plot_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800
    )
    
    # Generate HTML
    html_string = fig.to_html(
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['toImage'],
            'modeBarButtonsToAdd': ['hoverclosest', 'hovercompare']
        }
    )
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(html_string)
    temp_file.close()
    
    return temp_file.name

def render_3d_volume_plotly_slices(volume, opacity=0.5, cmap='gray', num_slices=3):
    """Render interactive 3D volume with orthogonal slice planes using Plotly."""
    # Normalize volume
    vmin, vmax = np.percentile(volume, [1, 99])
    volume_normalized = np.clip((volume - vmin) / (vmax - vmin + 1e-8), 0, 1)
    
    # Get middle slices
    mid_x = volume.shape[0] // 2
    mid_y = volume.shape[1] // 2
    mid_z = volume.shape[2] // 2
    
    # Colormap mapping
    colormap_dict = {
        'gray': 'gray',
        'bone': 'bone',
        'viridis': 'viridis',
        'hot': 'hot',
        'cool': 'blues',
        'plasma': 'plasma'
    }
    plotly_cmap = colormap_dict.get(cmap, 'gray')
    
    fig = go.Figure()
    
    # Add sagittal slice (YZ plane at mid X)
    slice_x = volume_normalized[mid_x, :, :]
    y_coords, z_coords = np.meshgrid(np.arange(volume.shape[1]), np.arange(volume.shape[2]))
    x_coords = np.ones_like(y_coords) * mid_x
    
    fig.add_trace(go.Surface(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        surfacecolor=slice_x.T,
        colorscale=plotly_cmap,
        showscale=False,
        opacity=0.9,
        name='Sagittal',
        hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z}<br>Value: %{surfacecolor:.3f}<extra></extra>'
    ))
    
    # Add coronal slice (XZ plane at mid Y)
    slice_y = volume_normalized[:, mid_y, :]
    x_coords2, z_coords2 = np.meshgrid(np.arange(volume.shape[0]), np.arange(volume.shape[2]))
    y_coords2 = np.ones_like(x_coords2) * mid_y
    
    fig.add_trace(go.Surface(
        x=x_coords2,
        y=y_coords2,
        z=z_coords2,
        surfacecolor=slice_y.T,
        colorscale=plotly_cmap,
        showscale=False,
        opacity=0.9,
        name='Coronal',
        hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z}<br>Value: %{surfacecolor:.3f}<extra></extra>'
    ))
    
    # Add axial slice (XY plane at mid Z)
    slice_z = volume_normalized[:, :, mid_z]
    x_coords3, y_coords3 = np.meshgrid(np.arange(volume.shape[0]), np.arange(volume.shape[1]))
    z_coords3 = np.ones_like(x_coords3) * mid_z
    
    fig.add_trace(go.Surface(
        x=x_coords3,
        y=y_coords3,
        z=z_coords3,
        surfacecolor=slice_z.T,
        colorscale=plotly_cmap,
        showscale=True,
        opacity=0.9,
        name='Axial',
        hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z}<br>Value: %{surfacecolor:.3f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='Interactive 3D Volume with Orthogonal Slices',
        scene=dict(
            xaxis=dict(title='X', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            yaxis=dict(title='Y', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            zaxis=dict(title='Z', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            aspectmode='data'
        ),
        paper_bgcolor='rgb(10, 10, 10)',
        plot_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800
    )
    
    # Generate HTML
    html_string = fig.to_html(
        include_plotlyjs='cdn',
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'responsive': True
        }
    )
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(html_string)
    temp_file.close()
    
    return temp_file.name

def render_3d_isosurface_plotly(volume, threshold_percentile=50, cmap='gray', downsample_factor=2):
    """Render lightweight 3D isosurface using Plotly (much faster than volume rendering)."""
    # Downsample
    if downsample_factor > 1:
        volume_ds = volume[::downsample_factor, ::downsample_factor, ::downsample_factor]
    else:
        volume_ds = volume
    
    # Normalize
    vmin, vmax = np.percentile(volume_ds, [1, 99])
    volume_normalized = np.clip((volume_ds - vmin) / (vmax - vmin + 1e-8), 0, 1)
    
    # Calculate threshold
    threshold = np.percentile(volume_normalized, threshold_percentile)
    
    # Colormap
    colormap_dict = {
        'gray': 'gray',
        'bone': 'bone',
        'viridis': 'viridis',
        'hot': 'hot',
        'cool': 'blues',
        'plasma': 'plasma'
    }
    plotly_cmap = colormap_dict.get(cmap, 'gray')
    
    # Create mesh grid
    X, Y, Z = np.mgrid[0:volume_ds.shape[0], 0:volume_ds.shape[1], 0:volume_ds.shape[2]]
    
    # Create figure with isosurface (single surface = much lighter)
    fig = go.Figure(data=go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=volume_normalized.flatten(),
        isomin=threshold - 0.1,
        isomax=threshold + 0.1,
        surface_count=3,  # Just 3 surfaces for speed
        colorscale=plotly_cmap,
        caps=dict(x_show=False, y_show=False, z_show=False),
        hoverinfo='skip'
    ))
    
    # Update layout
    fig.update_layout(
        title='Interactive 3D Medical Volume (Isosurface)',
        scene=dict(
            xaxis=dict(title='X', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            yaxis=dict(title='Y', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            zaxis=dict(title='Z', backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            aspectmode='data'
        ),
        paper_bgcolor='rgb(10, 10, 10)',
        plot_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white'),
        margin=dict(l=0, r=0, t=40, b=0),
        height=800
    )
    
    # Generate HTML
    html_string = fig.to_html(
        include_plotlyjs='cdn',
        config={'displayModeBar': True, 'displaylogo': False, 'responsive': True}
    )
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(html_string)
    temp_file.close()
    
    return temp_file.name

def render_compare_3d_plotly(volume_a, volume_b, opacity=0.1, cmap='gray', downsample_factor=3):
    """Render side-by-side interactive 3D comparison using Plotly."""
    # Use more aggressive downsampling for comparison (2 volumes = 2x memory)
    total_voxels_a = np.prod(volume_a.shape)
    total_voxels_b = np.prod(volume_b.shape)
    max_voxels = max(total_voxels_a, total_voxels_b)
    
    if max_voxels > 30_000_000:
        downsample_factor = max(downsample_factor, 5)
    elif max_voxels > 10_000_000:
        downsample_factor = max(downsample_factor, 4)
    
    # Downsample both volumes
    if downsample_factor > 1:
        volume_a_ds = volume_a[::downsample_factor, ::downsample_factor, ::downsample_factor]
        volume_b_ds = volume_b[::downsample_factor, ::downsample_factor, ::downsample_factor]
    else:
        volume_a_ds = volume_a
        volume_b_ds = volume_b
    
    # Normalize volumes
    vmin_a, vmax_a = np.percentile(volume_a_ds, [1, 99])
    vmin_b, vmax_b = np.percentile(volume_b_ds, [1, 99])
    
    volume_a_normalized = np.clip((volume_a_ds - vmin_a) / (vmax_a - vmin_a + 1e-8), 0, 1)
    volume_b_normalized = np.clip((volume_b_ds - vmin_b) / (vmax_b - vmin_b + 1e-8), 0, 1)
    
    # Colormap
    colormap_dict = {
        'gray': 'gray',
        'bone': 'bone',
        'viridis': 'viridis',
        'hot': 'hot',
        'cool': 'blues',
        'plasma': 'plasma'
    }
    plotly_cmap = colormap_dict.get(cmap, 'gray')
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'volume'}, {'type': 'volume'}]],
        subplot_titles=('Volume A', 'Volume B'),
        horizontal_spacing=0.05
    )
    
    # Reduce surface count for comparison to save memory
    voxel_count = max(np.prod(volume_a_ds.shape), np.prod(volume_b_ds.shape))
    if voxel_count > 2_000_000:
        surface_count = 8
    elif voxel_count > 1_000_000:
        surface_count = 10
    else:
        surface_count = 12
    
    # Volume A
    X_a, Y_a, Z_a = np.mgrid[0:volume_a_ds.shape[0], 0:volume_a_ds.shape[1], 0:volume_a_ds.shape[2]]
    fig.add_trace(
        go.Volume(
            x=X_a.flatten(),
            y=Y_a.flatten(),
            z=Z_a.flatten(),
            value=volume_a_normalized.flatten(),
            opacity=opacity,
            surface_count=surface_count,
            colorscale=plotly_cmap,
            isomin=volume_a_normalized.min(),
            isomax=volume_a_normalized.max(),
            caps=dict(x_show=False, y_show=False, z_show=False),
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    # Volume B
    X_b, Y_b, Z_b = np.mgrid[0:volume_b_ds.shape[0], 0:volume_b_ds.shape[1], 0:volume_b_ds.shape[2]]
    fig.add_trace(
        go.Volume(
            x=X_b.flatten(),
            y=Y_b.flatten(),
            z=Z_b.flatten(),
            value=volume_b_normalized.flatten(),
            opacity=opacity,
            surface_count=surface_count,
            colorscale=plotly_cmap,
            isomin=volume_b_normalized.min(),
            isomax=volume_b_normalized.max(),
            caps=dict(x_show=False, y_show=False, z_show=False),
            hoverinfo='skip'
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title='Interactive 3D Volume Comparison',
        paper_bgcolor='rgb(10, 10, 10)',
        plot_bgcolor='rgb(10, 10, 10)',
        font=dict(color='white'),
        height=800,
        scene=dict(
            xaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            yaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            zaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        ),
        scene2=dict(
            xaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            yaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            zaxis=dict(backgroundcolor='rgb(20, 20, 20)', gridcolor='gray'),
            bgcolor='rgb(10, 10, 10)',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        )
    )
    
    # Generate HTML
    html_string = fig.to_html(
        include_plotlyjs='cdn',
        config={'displayModeBar': True, 'displaylogo': False, 'responsive': True}
    )
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html', dir=OUTPUT_FOLDER, mode='w')
    temp_file.write(html_string)
    temp_file.close()
    
    return temp_file.name

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Supported: .nii, .nii.gz, .npy'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Load volume and get metadata
        volume, metadata = load_volume(filepath)
        
        # Store volume path in session (simplified - in production use proper session management)
        return jsonify({
            'success': True,
            'filename': filename,
            'metadata': metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/slice', methods=['POST'])
def visualize_slice():
    try:
        data = request.json
        filename = data.get('filename')
        axis = int(data.get('axis', 2))
        slice_idx = data.get('slice_idx')
        cmap = data.get('cmap', 'gray')
        
        if slice_idx is not None:
            slice_idx = int(slice_idx)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        volume, _ = load_volume(filepath)
        
        img_buffer = render_slice_image(volume, axis, slice_idx, cmap)
        
        return send_file(img_buffer, mimetype='image/png')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/multiview', methods=['POST'])
def visualize_multiview():
    try:
        data = request.json
        filename = data.get('filename')
        cmap = data.get('cmap', 'gray')
        slices = data.get('slices', {})

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        volume, _ = load_volume(filepath)

        img_buffer = render_multiview(volume, slices=slices, cmap=cmap)

        return send_file(img_buffer, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/compare', methods=['POST'])
def visualize_compare():
    try:
        data = request.json
        filename_a = data.get('filename_a')
        filename_b = data.get('filename_b')
        axis = int(data.get('axis', 2))
        slice_idx = data.get('slice_idx')
        cmap = data.get('cmap', 'gray')

        if slice_idx is not None:
            slice_idx = int(slice_idx)

        filepath_a = os.path.join(app.config['UPLOAD_FOLDER'], filename_a)
        filepath_b = os.path.join(app.config['UPLOAD_FOLDER'], filename_b)

        volume_a, _ = load_volume(filepath_a)
        volume_b, _ = load_volume(filepath_b)

        img_buffer = render_compare_slices(volume_a, volume_b, axis, slice_idx, cmap)

        return send_file(img_buffer, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/compare3d', methods=['POST'])
def visualize_compare_3d():
    """Render interactive 3D comparison using Plotly (returns HTML)."""
    try:
        data = request.json
        filename_a = data.get('filename_a')
        filename_b = data.get('filename_b')
        opacity_str = data.get('opacity', 'sigmoid_3')
        cmap = data.get('cmap', 'gray')

        # Convert opacity string to numeric value for Plotly
        opacity_map = {
            'sigmoid_1': 0.05,
            'sigmoid_2': 0.1,
            'sigmoid_3': 0.15,
            'sigmoid_5': 0.2,
            'sigmoid_10': 0.3
        }
        opacity = opacity_map.get(opacity_str, 0.15)

        filepath_a = os.path.join(app.config['UPLOAD_FOLDER'], filename_a)
        filepath_b = os.path.join(app.config['UPLOAD_FOLDER'], filename_b)

        volume_a, _ = load_volume(filepath_a)
        volume_b, _ = load_volume(filepath_b)

        html_path = render_compare_3d_plotly(volume_a, volume_b, opacity=opacity, cmap=cmap)

        return send_file(html_path, mimetype='text/html')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/3d_html')
def visualize_3d_html():
    """Legacy endpoint - redirects to Plotly rendering if PyVista unavailable"""
    try:
        filename = request.args.get('filename')
        opacity = request.args.get('opacity', 'sigmoid_3')
        cmap = request.args.get('cmap', 'gray')

        if not filename:
            return jsonify({'error': 'filename is required'}), 400

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        volume, _ = load_volume(filepath)

        # Use Plotly if PyVista not available
        if not PYVISTA_AVAILABLE:
            opacity_map = {
                'sigmoid_1': 0.05,
                'sigmoid_2': 0.1,
                'sigmoid_3': 0.15,
                'sigmoid_5': 0.2,
                'sigmoid_10': 0.3
            }
            html_path = render_3d_volume_plotly(volume, opacity=opacity_map.get(opacity, 0.15), cmap=cmap)
        else:
            html_path = render_3d_html(volume, opacity=opacity, cmap=cmap)
        
        return send_file(html_path, mimetype='text/html')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/compare3d_html')
def visualize_compare_3d_html():
    """Legacy endpoint - redirects to Plotly rendering if PyVista unavailable"""
    try:
        filename_a = request.args.get('filename_a')
        filename_b = request.args.get('filename_b')
        opacity = request.args.get('opacity', 'sigmoid_3')
        cmap = request.args.get('cmap', 'gray')

        if not filename_a or not filename_b:
            return jsonify({'error': 'Both filename_a and filename_b are required'}), 400

        filepath_a = os.path.join(app.config['UPLOAD_FOLDER'], filename_a)
        filepath_b = os.path.join(app.config['UPLOAD_FOLDER'], filename_b)

        volume_a, _ = load_volume(filepath_a)
        volume_b, _ = load_volume(filepath_b)

        # Use Plotly if PyVista not available
        if not PYVISTA_AVAILABLE:
            opacity_map = {
                'sigmoid_1': 0.05,
                'sigmoid_2': 0.1,
                'sigmoid_3': 0.15,
                'sigmoid_5': 0.2,
                'sigmoid_10': 0.3
            }
            html_path = render_compare_3d_plotly(volume_a, volume_b, opacity=opacity_map.get(opacity, 0.15), cmap=cmap)
        else:
            html_path = render_compare_3d_html(volume_a, volume_b, opacity=opacity, cmap=cmap)
        
        return send_file(html_path, mimetype='text/html')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualize/3d', methods=['POST'])
def visualize_3d():
    """Render interactive 3D volume using Plotly (returns HTML)."""
    try:
        data = request.json
        filename = data.get('filename')
        opacity_str = data.get('opacity', 'sigmoid_3')
        cmap = data.get('cmap', 'gray')
        render_mode = data.get('render_mode', 'volume')  # 'volume' or 'slices'
        
        # Convert opacity string to numeric value for Plotly
        opacity_map = {
            'sigmoid_1': 0.05,
            'sigmoid_2': 0.1,
            'sigmoid_3': 0.15,
            'sigmoid_5': 0.2,
            'sigmoid_10': 0.3
        }
        opacity = opacity_map.get(opacity_str, 0.15)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        volume, _ = load_volume(filepath)
        
        # Choose rendering method based on mode
        # Default to slices mode (much lighter on memory)
        if render_mode == 'volume':
            # Full volume rendering - use aggressive downsampling
            output_path = render_3d_volume_plotly(volume, opacity, cmap, downsample_factor=4)
        elif render_mode == 'isosurface':
            # Isosurface rendering - lightweight alternative
            output_path = render_3d_isosurface_plotly(volume, threshold_percentile=50, cmap=cmap, downsample_factor=2)
        else:
            # Orthogonal slices - default and recommended
            output_path = render_3d_volume_plotly_slices(volume, opacity, cmap)
        
        return send_file(output_path, mimetype='text/html')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Get port from environment variable (for Hugging Face Spaces) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

