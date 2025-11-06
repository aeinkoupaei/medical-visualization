#!/usr/bin/env python3
"""
Interactive 3D Medical Volume Viewer
Cross-Platform Support: Windows, Linux, and macOS

Features:
- Full interactive 3D visualization (rotate, zoom, pan)
- Automatic GPU acceleration (Metal on macOS, DirectX/OpenGL on Windows/Linux)
- Full resolution support (no downsampling)
- Multiple viewing modes
- Real-time controls
- Export to interactive HTML

Author: Medical Imaging Visualization
Platform: Cross-platform (Windows, Linux, macOS)
Note: Optimized for Apple Silicon on macOS
"""

import numpy as np
import pyvista as pv
import nibabel as nib
import os
import sys
from pathlib import Path

# ============================================================================
# CUSTOM COLORMAPS
# ============================================================================

def get_dark_gray_colormap():
    """
    Create a custom slightly dark gray colormap for PyVista.
    Darker than standard gray but not too dark.
    Returns a list of hex color strings.
    """
    # Create color list: 256 colors from dark gray (0.2) to light gray (0.9)
    n_colors = 256
    gray_values = np.linspace(0.2, 0.9, n_colors)
    # Convert to hex strings
    colors = ['#{:02x}{:02x}{:02x}'.format(int(g*255), int(g*255), int(g*255)) for g in gray_values]
    return colors

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def load_nifti_volume(filepath):
    """
    Load 3D medical volume from NIfTI file.
    
    Parameters:
    -----------
    filepath : str
        Path to .nii or .nii.gz file
        
    Returns:
    --------
    numpy.ndarray : 3D volume data
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if not filepath.endswith(('.nii', '.nii.gz')):
        raise ValueError("File must be .nii or .nii.gz format")
    
    print("="*70)
    print("Loading NIfTI Volume")
    print("="*70)
    
    # Load NIfTI file
    nifti_img = nib.load(filepath)
    volume = nifti_img.get_fdata()
    
    # Display info
    print(f"File: {os.path.basename(filepath)}")
    print(f"Shape: {volume.shape}")
    print(f"Voxels: {volume.size / 1e6:.2f}M")
    print(f"Memory: {volume.nbytes / (1024**2):.2f} MB")
    print(f"Data type: {volume.dtype}")
    print(f"Value range: [{volume.min():.2f}, {volume.max():.2f}]")
    print(f"Voxel spacing: {nifti_img.header.get_zooms()}")
    print("="*70)
    
    return volume


def create_volume_grid(volume, use_cell_data=True):
    """
    Create PyVista ImageData grid from numpy volume.
    
    Parameters:
    -----------
    volume : numpy.ndarray
        3D volume data
    use_cell_data : bool
        If True, use cell_data (for volume rendering)
        If False, use point_data (for isosurface)
        
    Returns:
    --------
    pyvista.ImageData : Grid with volume data
    """
    grid = pv.ImageData()
    
    if use_cell_data:
        # For volume rendering
        grid.dimensions = np.array(volume.shape) + 1
        grid.cell_data["values"] = volume.flatten(order="F")
    else:
        # For isosurface (contour needs point data)
        grid.dimensions = np.array(volume.shape)
        grid.point_data["values"] = volume.flatten(order="F")
    
    return grid


# ============================================================================
# SAVE INTERACTIVE VIEWER
# ============================================================================

def save_interactive_viewer(plotter, filename):
    """
    Save an interactive 3D viewer to HTML file.
    
    The saved HTML file can be opened in any web browser and remains
    fully interactive (rotate, zoom, pan)!
    
    Parameters:
    -----------
    plotter : pyvista.Plotter
        The plotter object to save
    filename : str
        Output filename (e.g., 'my_volume.html')
        
    Example:
    --------
    plotter = pv.Plotter()
    plotter.add_volume(grid)
    save_interactive_viewer(plotter, 'interactive_volume.html')
    """
    import os
    
    # Ensure .html extension
    if not filename.endswith('.html'):
        filename += '.html'
    
    print(f"\n💾 Saving interactive viewer to: {filename}")
    plotter.export_html(filename)
    
    # Get absolute path for display
    abs_path = os.path.abspath(filename)
    
    print(f"✅ Saved successfully!")
    print(f"📂 Location: {abs_path}")
    print(f"🌐 Open in browser: file://{abs_path}")
    print(f"   Or just double-click the file to open")
    print(f"\n   The viewer stays FULLY INTERACTIVE!")
    print(f"   - Rotate with mouse")
    print(f"   - Zoom with scroll")
    print(f"   - Pan with right-click drag")
    

# ============================================================================
# VISUALIZATION MODES
# ============================================================================

def visualize_volume_interactive(volume, 
                                 opacity='sigmoid_3',  # Transparent by default
                                 cmap='gray',
                                 window_size=(1200, 800),
                                 title="Interactive 3D Volume",
                                 save_html=None):
    """
    Interactive 3D volume rendering with automatic GPU acceleration.
    
    Full resolution, smooth rotation/zoom/pan with mouse.
    Automatically uses best GPU backend: Metal (macOS), DirectX/OpenGL (Windows/Linux).
    
    Parameters:
    -----------
    volume : numpy.ndarray
        3D volume data
    opacity : str
        Opacity preset (MUST be string):
        - For TRANSPARENT (see inside): 'sigmoid_1', 'sigmoid_2', 'sigmoid_3'
        - For BALANCED: 'sigmoid' or 'sigmoid_5' (default)
        - For OPAQUE (surface view): 'sigmoid_10', 'sigmoid_15', 'sigmoid_20'
        - Other options: 'linear', 'geom'
        (Lower numbers = MORE transparent!)
    cmap : str
        'gray', 'bone', 'viridis', 'hot', etc.
    window_size : tuple
        (width, height) in pixels
    title : str
        Window title
    save_html : str, optional
        If provided, saves an INTERACTIVE HTML file you can open in browser
        The HTML file stays interactive - you can rotate/zoom!
        Example: 'my_volume_interactive.html'
        
    Controls:
    ---------
    Mouse:
        - Left drag: Rotate
        - Right drag: Pan
        - Scroll: Zoom
    Keyboard:
        - 's': Save screenshot (to 'screenshot.png')
        - 'r': Reset camera
        - 'q': Quit
    """
    print("\n" + "="*70)
    print("INTERACTIVE 3D VOLUME RENDERING")
    print("="*70)
    print(f"Shape: {volume.shape}")
    print(f"Voxels: {volume.size / 1e6:.2f}M")
    print(f"Memory: {volume.nbytes / (1024**2):.2f} MB")
    print(f"Opacity: {opacity}")
    print(f"Colormap: {cmap}")
    print()
    print("FULL RESOLUTION - NO DOWNSAMPLING")
    print("Automatic GPU acceleration (Metal/DirectX/OpenGL)")
    print()
    print("Controls:")
    print("  Mouse Left Drag   : Rotate")
    print("  Mouse Right Drag  : Pan")
    print("  Mouse Scroll      : Zoom")
    print("  'r' key           : Reset camera")
    print("  'q' key           : Quit")
    print("="*70)
    
    # Create grid (use cell data for volume rendering)
    grid = create_volume_grid(volume, use_cell_data=True)
    
    # Calculate intensity range
    vmin, vmax = np.percentile(volume, [5, 95])
    print(f"Intensity range: [{vmin:.2f}, {vmax:.2f}]")
    
    # Create plotter (native window, NOT off_screen)
    plotter = pv.Plotter(window_size=window_size)
    plotter.add_text(title, position='upper_edge', font_size=14, color='white')
    
    # Add volume
    plotter.add_volume(
        grid,
        cmap=cmap,
        clim=(vmin, vmax),
        opacity=opacity,
        shade=False,
        show_scalar_bar=True,
        scalar_bar_args={
            'title': 'Intensity',
            'vertical': True,
            'height': 0.5,
            'position_x': 0.85,
            'position_y': 0.25
        }
    )
    
    # Set camera
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Enable anti-aliasing for smooth rendering
    plotter.enable_anti_aliasing('fxaa')
    
    # Add axes
    plotter.show_axes()
    
    print("\nRendering... (window will open)")
    print("GPU acceleration enabled automatically!")
    
    # Save interactive HTML if requested
    if save_html:
        print(f"\n💾 Saving interactive HTML to: {save_html}")
        try:
            plotter.export_html(save_html)
            print(f"✅ Saved! Open '{save_html}' in any browser to view interactively!")
        except ImportError as e:
            print(f"\n❌ Error: Missing dependencies for HTML export")
            print(f"   Install with: pip install nest-asyncio trame trame-vtk")
            print(f"\n   Continuing without saving HTML...")
            save_html = None  # Don't show save message at end
    
    # Show (interactive!)
    plotter.show()
    
    print("="*70)
    print("Window closed.")
    if save_html:
        print(f"💾 Interactive viewer saved to: {save_html}")
    print("="*70)


def visualize_isosurface_interactive(volume,
                                     threshold_percentile=50,
                                     cmap='viridis',
                                     smooth=True,
                                     window_size=(1200, 800),
                                     title="Interactive 3D Isosurface",
                                     save_html=None):
    """
    Interactive 3D isosurface extraction and visualization.
    
    Faster than volume rendering, good for surfaces.
    
    Parameters:
    -----------
    volume : numpy.ndarray
        3D volume data
    threshold_percentile : float
        Percentile for isosurface threshold (0-100)
    cmap : str
        Colormap
    smooth : bool
        Apply Laplacian smoothing to surface
    window_size : tuple
        (width, height)
    title : str
        Window title
    """
    print("\n" + "="*70)
    print("INTERACTIVE 3D ISOSURFACE")
    print("="*70)
    
    # Calculate threshold
    threshold = np.percentile(volume[volume > 0], threshold_percentile)
    print(f"Threshold: {threshold:.2f} ({threshold_percentile}th percentile)")
    
    # Create grid (use point data for contour)
    grid = create_volume_grid(volume, use_cell_data=False)
    
    # Extract isosurface
    print("Extracting isosurface...")
    surface = grid.contour([threshold], scalars="values")
    
    # Smooth if requested
    if smooth and surface.n_points > 0:
        print("Smoothing surface...")
        surface = surface.smooth(n_iter=50, relaxation_factor=0.1)
    
    print(f"Surface: {surface.n_points:,} points, {surface.n_cells:,} cells")
    
    # Create plotter
    plotter = pv.Plotter(window_size=window_size)
    # plotter.set_background('black')  # Black background
    plotter.add_text(title, position='upper_edge', font_size=14, color='white')
    
    # Add surface
    plotter.add_mesh(
        surface,
        cmap=cmap,
        smooth_shading=True,
        show_scalar_bar=True,
        scalar_bar_args={'title': 'Intensity'}
    )
    
    # Set camera
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Enable anti-aliasing
    plotter.enable_anti_aliasing('fxaa')
    
    # Add axes
    plotter.show_axes()
    
    print("\nControls:")
    print("  Mouse Left Drag : Rotate")
    print("  Mouse Scroll    : Zoom")
    print("  'r' key         : Reset camera")
    print("="*70)
    print("\nRendering...")
    
    # Save interactive HTML if requested
    if save_html:
        print(f"\n💾 Saving interactive HTML to: {save_html}")
        try:
            plotter.export_html(save_html)
            print(f"✅ Saved! Open '{save_html}' in any browser to view interactively!")
        except ImportError as e:
            print(f"\n❌ Error: Missing dependencies for HTML export")
            print(f"   Install with: pip install nest-asyncio trame trame-vtk")
            print(f"\n   Continuing without saving HTML...")
            save_html = None  # Don't show save message at end
    
    # Show
    plotter.show()
    
    print("="*70)
    print("Window closed.")
    if save_html:
        print(f"💾 Interactive viewer saved to: {save_html}")
    print("="*70)


def visualize_multiplanar(volume,
                         cmap='gray',
                         window_size=(1400, 800),
                         title="Multi-Planar Reconstruction",
                         save_html=None):
    """
    Interactive multi-planar reconstruction (MPR).
    
    Shows three orthogonal slice planes in 3D space.
    
    Parameters:
    -----------
    volume : numpy.ndarray
        3D volume data
    cmap : str
        Colormap
    window_size : tuple
        (width, height)
    title : str
        Window title
    """
    print("\n" + "="*70)
    print("MULTI-PLANAR RECONSTRUCTION (MPR)")
    print("="*70)
    
    # Create grid
    grid = create_volume_grid(volume, use_cell_data=True)
    
    # Calculate intensity range
    vmin, vmax = np.percentile(volume, [1, 99])
    
    # Create plotter
    plotter = pv.Plotter(window_size=window_size)
    # plotter.set_background('black')  # Black background
    plotter.add_text(title, position='upper_edge', font_size=14, color='white')
    
    # Add orthogonal slices
    plotter.add_mesh_slice_orthogonal(
        grid,
        generate_triangles=False,
        cmap=cmap,
        clim=(vmin, vmax),
        show_scalar_bar=True
    )
    
    # Set camera
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Enable anti-aliasing
    plotter.enable_anti_aliasing('fxaa')
    
    # Add axes
    plotter.show_axes()
    
    print(f"Intensity range: [{vmin:.2f}, {vmax:.2f}]")
    print("\nControls:")
    print("  Mouse Left Drag : Rotate")
    print("  Mouse Scroll    : Zoom")
    print("="*70)
    print("\nRendering...")
    
    # Save interactive HTML if requested
    if save_html:
        print(f"\n💾 Saving interactive HTML to: {save_html}")
        try:
            plotter.export_html(save_html)
            print(f"✅ Saved! Open '{save_html}' in any browser to view interactively!")
        except ImportError as e:
            print(f"\n❌ Error: Missing dependencies for HTML export")
            print(f"   Install with: pip install nest-asyncio trame trame-vtk")
            print(f"\n   Continuing without saving HTML...")
            save_html = None  # Don't show save message at end
    
    # Show
    plotter.show()
    
    print("="*70)
    print("Window closed.")
    if save_html:
        print(f"💾 Interactive viewer saved to: {save_html}")
    print("="*70)


def visualize_volume_with_slices(volume,
                                 cmap='gray',
                                 window_size=(1400, 800),
                                 title="Volume with Slice Planes",
                                 save_html=None):
    """
    Volume rendering with slice planes overlay.
    Better for HTML export than multiplanar alone.
    
    The volume is transparent and slices show internal structure.
    HTML export: Fully rotatable, slices are fixed but visible.
    
    Parameters:
    -----------
    volume : numpy.ndarray
        3D volume data
    cmap : str
        Colormap
    window_size : tuple
        (width, height)
    title : str
        Window title
    save_html : str, optional
        Save as interactive HTML
    """
    print("\n" + "="*70)
    print("VOLUME WITH SLICE PLANES")
    print("="*70)
    
    # Create grid
    grid = create_volume_grid(volume, use_cell_data=True)
    
    # Calculate intensity range
    vmin, vmax = np.percentile(volume, [5, 95])
    
    # Create plotter
    plotter = pv.Plotter(window_size=window_size)
    # plotter.set_background('black')  # Black background
    plotter.add_text(title, position='upper_edge', font_size=14, color='white')
    
    # Add semi-transparent volume
    plotter.add_volume(
        grid,
        cmap=cmap,
        clim=(vmin, vmax),
        opacity='sigmoid_1',  # Very transparent
        show_scalar_bar=False
    )
    
    # Add orthogonal slices
    plotter.add_mesh_slice_orthogonal(
        grid,
        generate_triangles=False,
        cmap=cmap,
        clim=(vmin, vmax),
        show_scalar_bar=True
    )
    
    # Set camera
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Enable anti-aliasing
    plotter.enable_anti_aliasing('fxaa')
    
    # Add axes
    plotter.show_axes()
    
    print(f"Intensity range: [{vmin:.2f}, {vmax:.2f}]")
    print("\nControls:")
    print("  Mouse Left Drag : Rotate")
    print("  Mouse Scroll    : Zoom")
    print("="*70)
    print("\nNote: Slice planes are fixed in HTML export")
    print("      But you can still rotate/zoom the entire scene")
    print("="*70)
    print("\nRendering...")
    
    # Save interactive HTML if requested
    if save_html:
        print(f"\n💾 Saving interactive HTML to: {save_html}")
        try:
            plotter.export_html(save_html)
            print(f"✅ Saved! Open '{save_html}' in any browser to view interactively!")
        except ImportError as e:
            print(f"\n❌ Error: Missing dependencies for HTML export")
            print(f"   Install with: pip install nest-asyncio trame trame-vtk")
            print(f"\n   Continuing without saving HTML...")
            save_html = None  # Don't show save message at end
    
    # Show
    plotter.show()
    
    print("="*70)
    print("Window closed.")
    if save_html:
        print(f"💾 Interactive viewer saved to: {save_html}")
    print("="*70)


def export_comparison_html(volume1, volume2, titles=["Volume 1", "Volume 2"], 
                           opacity='geom', cmap='gray', use_dark_gray=True,
                           filename_prefix='comparison'):
    """
    Export two volumes as separate HTML files for side-by-side browser viewing.
    Since PyVista subplots don't export well, this creates individual files.
    
    Parameters:
    -----------
    volume1, volume2 : numpy.ndarray
        3D volumes to export
    titles : list of str
        Titles for each volume
    opacity : str
        Opacity mode
    cmap : str
        Colormap
    use_dark_gray : bool
        Use custom dark gray colormap
    filename_prefix : str
        Prefix for output files (creates filename_1.html and filename_2.html)
    """
    print("\n" + "="*70)
    print("EXPORTING VOLUMES FOR SIDE-BY-SIDE COMPARISON")
    print("="*70)
    print("Note: Exporting as separate HTML files since subplots don't export well")
    
    # Use custom dark gray if requested
    if use_dark_gray and cmap == 'gray':
        cmap_to_use = get_dark_gray_colormap()
    else:
        cmap_to_use = cmap
    
    # Export volume 1
    file1 = f"{filename_prefix}_1.html"
    print(f"\nExporting {titles[0]} to {file1}...")
    visualize_volume_interactive(
        volume1,
        opacity=opacity,
        cmap=cmap_to_use if use_dark_gray else cmap,
        title=titles[0],
        save_html=file1
    )
    
    # Export volume 2
    file2 = f"{filename_prefix}_2.html"
    print(f"\nExporting {titles[1]} to {file2}...")
    visualize_volume_interactive(
        volume2,
        opacity=opacity,
        cmap=cmap_to_use if use_dark_gray else cmap,
        title=titles[1],
        save_html=file2
    )
    
    print("\n" + "="*70)
    print("Export Complete!")
    print(f"  {file1}")
    print(f"  {file2}")
    print("\nTo compare side-by-side:")
    print("  1. Open both HTML files in separate browser tabs")
    print("  2. Or use browser's split-screen feature")
    print("="*70)


def compare_volumes_side_by_side(volume1, volume2,
                                  titles=["Volume 1", "Volume 2"],
                                  opacity='geom',
                                  cmap='gray',  # Default gray (can be changed)
                                  window_size=(1600, 800),
                                  save_html=None,
                                  use_dark_gray=True):
    """
    Compare two volumes side-by-side interactively.
    
    Useful for comparing source vs target, before vs after, etc.
    
    Parameters:
    -----------
    volume1, volume2 : numpy.ndarray
        3D volumes to compare
    titles : list of str
        Titles for each volume
    opacity : str
        Opacity mode
    cmap : str
        Colormap
    window_size : tuple
        (width, height)
    save_html : str, optional
        If provided, saves an INTERACTIVE HTML file
    """
    print("\n" + "="*70)
    print("SIDE-BY-SIDE VOLUME COMPARISON")
    print("="*70)
    print(f"Volume 1: {volume1.shape}")
    print(f"Volume 2: {volume2.shape}")
    
    # Create grids
    grid1 = create_volume_grid(volume1, use_cell_data=True)
    grid2 = create_volume_grid(volume2, use_cell_data=True)
    
    # Calculate intensity ranges
    vmin1, vmax1 = np.percentile(volume1, [5, 95])
    vmin2, vmax2 = np.percentile(volume2, [5, 95])
    
    # Use custom dark gray if requested
    if use_dark_gray and cmap == 'gray':
        cmap = get_dark_gray_colormap()
    
    # Create plotter with subplots
    plotter = pv.Plotter(shape=(1, 2), window_size=window_size)
    
    # Left subplot (volume 1)
    plotter.subplot(0, 0)
    plotter.add_text(titles[0], position='upper_edge', font_size=12, color='white')
    plotter.add_volume(grid1, cmap=cmap, clim=(vmin1, vmax1), opacity=opacity)
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Right subplot (volume 2)
    plotter.subplot(0, 1)
    plotter.add_text(titles[1], position='upper_edge', font_size=12, color='white')
    plotter.add_volume(grid2, cmap=cmap, clim=(vmin2, vmax2), opacity=opacity)
    plotter.camera_position = 'xy'
    plotter.camera.elevation = 30
    plotter.camera.azimuth = 45
    
    # Link cameras
    plotter.link_views()
    
    # Enable anti-aliasing
    plotter.enable_anti_aliasing('fxaa')
    
    # Add axes to both subplots
    plotter.subplot(0, 0)
    plotter.show_axes()
    
    plotter.subplot(0, 1)
    plotter.show_axes()
    
    print("\nBoth volumes rendered side-by-side")
    print("Cameras are linked (rotate one, both rotate)")
    print("="*70)
    print("\nRendering...")
    
    # Note about HTML export for subplots
    if save_html:
        print(f"\n⚠️  Note: Subplot layouts don't export well to HTML")
        print(f"   The file will be created but may be empty or broken")
        print(f"\n   Alternative: After viewing, use the export_comparison_html() function")
        print(f"   to create separate HTML files for each volume")
        
        # Try to export anyway (will likely create empty file)
        try:
            plotter.export_html(save_html)
            print(f"\n   Created {save_html} (may be empty due to subplot limitation)")
        except ImportError as e:
            print(f"\n   Error: Missing dependencies for HTML export")
            print(f"   Install with: pip install nest-asyncio trame trame-vtk trame-vuetify")
        except Exception as e:
            print(f"\n   Export failed: {str(e)}")
    
    # Show
    plotter.show()
    
    print("="*70)
    print("Window closed.")
    if save_html:
        print(f"Interactive viewer saved to: {save_html}")
    print("="*70)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function - demonstrates usage with menu.
    """
    import sys
    
    print("\n" + "="*70)
    print("Interactive 3D Medical Volume Viewer")
    print("Cross-Platform: Windows, Linux, macOS")
    print("="*70)
    
    # Check for command line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        # Interactive file selection
        print("\nEnter path to your NIfTI file (.nii or .nii.gz):")
        print("Example: /path/to/img0066.nii.gz")
        print("Or drag and drop the file here: ", end='')
        filepath = input().strip().strip("'\"")
    
    # Load volume
    try:
        volume = load_nifti_volume(filepath)
    except Exception as e:
        print(f"\nError loading file: {e}")
        sys.exit(1)
    
    # Menu
    while True:
        print("\n" + "="*70)
        print("SELECT VISUALIZATION MODE:")
        print("="*70)
        print("1. Volume Rendering (Full 3D, transparent)")
        print("2. Isosurface (Surface extraction)")
        print("3. Multi-Planar Reconstruction (3 orthogonal slices)")
        print("4. Volume + Slices (Best for HTML export)")
        print("5. Compare Two Volumes Side-by-Side")
        print("6. Exit")
        print("="*70)
        print("Enter choice (1-6): ", end='')
        
        choice = input().strip()
        
        if choice == '1':
            # Ask if user wants to save
            print("\n💾 Save as interactive HTML? (yes/no, default=no): ", end='')
            save_choice = input().strip().lower()
            save_file = None
            if save_choice in ['yes', 'y']:
                print("Enter filename (e.g., my_volume.html): ", end='')
                save_file = input().strip()
                if not save_file.endswith('.html'):
                    save_file += '.html'
                print("\n⚠️  Note: Requires trame libraries. If missing, run:")
                print("    pip install nest-asyncio trame trame-vtk")
            
            visualize_volume_interactive(
                volume,
                opacity='geom',
                cmap='gray',
                title="Volume Rendering - Full Resolution",
                save_html=save_file
            )
            
        elif choice == '2':
            print("\nEnter threshold percentile (0-100, default 50): ", end='')
            thresh = input().strip()
            thresh = float(thresh) if thresh else 50.0
            
            # Ask if user wants to save
            print("\n💾 Save as interactive HTML? (yes/no, default=no): ", end='')
            save_choice = input().strip().lower()
            save_file = None
            if save_choice in ['yes', 'y']:
                print("Enter filename (e.g., isosurface.html): ", end='')
                save_file = input().strip()
                if not save_file.endswith('.html'):
                    save_file += '.html'
            
            visualize_isosurface_interactive(
                volume,
                threshold_percentile=thresh,
                cmap='viridis',
                smooth=True,
                title="Isosurface Rendering",
                save_html=save_file
            )
            
        elif choice == '3':
            # Ask if user wants to save
            print("\n💾 Save as interactive HTML? (yes/no, default=no): ", end='')
            save_choice = input().strip().lower()
            save_file = None
            if save_choice in ['yes', 'y']:
                print("Enter filename (e.g., multiplanar.html): ", end='')
                save_file = input().strip()
                if not save_file.endswith('.html'):
                    save_file += '.html'
            
            visualize_multiplanar(
                volume,
                cmap='gray',
                title="Multi-Planar Reconstruction",
                save_html=save_file
            )
            
        elif choice == '4':
            # Ask if user wants to save
            print("\n💾 Save as interactive HTML? (yes/no, default=no): ", end='')
            save_choice = input().strip().lower()
            save_file = None
            if save_choice in ['yes', 'y']:
                print("Enter filename (e.g., volume_slices.html): ", end='')
                save_file = input().strip()
                if not save_file.endswith('.html'):
                    save_file += '.html'
            
            visualize_volume_with_slices(
                volume,
                cmap='gray',
                title="Volume with Slice Planes",
                save_html=save_file
            )
            
        elif choice == '5':
            # Compare two volumes
            print("\nEnter path to second NIfTI file to compare:")
            print("Or drag and drop the file here: ", end='')
            filepath2 = input().strip().strip("'\"")
            
            try:
                print("\nLoading second volume...")
                volume2 = load_nifti_volume(filepath2)
                
                print("\nEnter title for first volume (default='Volume 1'): ", end='')
                title1 = input().strip() or "Volume 1"
                
                print("Enter title for second volume (default='Volume 2'): ", end='')
                title2 = input().strip() or "Volume 2"
                
                # Ask if user wants to save
                print("\nSave as interactive HTML? (yes/no, default=no): ", end='')
                save_choice = input().strip().lower()
                save_file = None
                if save_choice in ['yes', 'y']:
                    print("Enter filename (e.g., comparison.html): ", end='')
                    save_file = input().strip()
                    if not save_file.endswith('.html'):
                        save_file += '.html'
                
                compare_volumes_side_by_side(
                    volume,
                    volume2,
                    titles=[title1, title2],
                    opacity='geom',
                    cmap='gray',
                    use_dark_gray=True,  # Use custom dark gray
                    save_html=save_file
                )
            except Exception as e:
                print(f"\nError loading second volume: {e}")
                print("Returning to menu...")
            
        elif choice == '6':
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()

