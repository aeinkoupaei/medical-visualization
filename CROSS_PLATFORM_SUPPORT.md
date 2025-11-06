# Cross-Platform Support

This document summarizes the cross-platform capabilities of the Interactive 3D Medical Volume Viewer.

## Supported Platforms

- **Windows** (Windows 10/11, 64-bit)  
- **Linux** (Ubuntu, Fedora, Arch, and other modern distributions)  
- **macOS** (macOS 10.13+, including Apple Silicon M1/M2/M3/M4)

## GPU Acceleration

The viewer automatically detects and uses the best available GPU backend for your platform:

| Platform | GPU Backend | Auto-Detection | Performance |
|----------|-------------|----------------|-------------|
| **Windows** | DirectX 11/12 or OpenGL | Automatic | Very Good |
| **Linux** | OpenGL | Automatic | Very Good |
| **macOS (Apple Silicon)** | Metal | Automatic | Excellent |
| **macOS (Intel)** | Metal/OpenGL | Automatic | Very Good |

**No configuration needed** - PyVista handles GPU backend selection automatically!

## Installation

### Quick Install (All Platforms)

```bash
# Clone repository
git clone https://github.com/aeinkoupaei/medical-visualization.git
cd medical-visualization

# Install dependencies
pip install -r requirements.txt

# Test installation
python scripts/medical_interactive_viewer.py data/nii/img0006.nii.gz
```

### Platform-Specific Prerequisites

#### Windows
- Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Git for Windows (optional)

#### Linux
- Python 3.8+ (usually pre-installed)
- System packages:
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-tk libgl1-mesa-glx
  
  # Fedora
  sudo dnf install python3-tkinter mesa-libGL
  
  # Arch
  sudo pacman -S tk mesa
  ```

#### macOS
- Python 3.8+ (pre-installed on macOS 10.15+)
- Command Line Tools: `xcode-select --install`
- Homebrew (optional): `brew install python@3.11`

## Features Working on All Platforms

- Full-resolution volume rendering  
- Interactive 3D rotation, zoom, and pan  
- Isosurface extraction  
- Multi-planar reconstruction (MPR)  
- Volume + slice visualization  
- Side-by-side volume comparison  
- Interactive HTML export  
- Screenshot capture  
- All colormaps and opacity settings  

## Python Dependencies (Cross-Platform)

All dependencies work on Windows, Linux, and macOS:

- **NumPy** (≥1.20.0) - Numerical computing
- **PyVista** (≥0.40.0) - 3D visualization (handles GPU backends)
- **NiBabel** (≥3.2.0) - NIfTI file handling
- **Trame** libraries - Interactive HTML export (optional)

## Performance Notes

### Best Performance
- **macOS Apple Silicon** (M1/M2/M3/M4) - Native Metal acceleration
- Close GPU-intensive apps during rendering
- Use dedicated GPU if available

### Good Performance
- **Windows** with DirectX 11/12 capable GPU
- **Linux** with modern OpenGL drivers (NVIDIA/AMD)
- **macOS Intel** with Metal support

### Performance Optimization Tips
1. Update your graphics drivers
2. Use isosurface mode for very large datasets
3. Adjust opacity settings (more transparent = faster)
4. Close other GPU-intensive applications
5. Consider downsampling extremely large volumes

## Platform-Specific Considerations

### Windows
- Uses `\` for file paths (auto-handled by Python)
- Windows Defender may scan first run
- Multiple Python installations: use `py -3` instead of `python`

### Linux
- Requires X11 server running (default on desktop environments)
- For headless servers: use HTML export or Xvfb
- SSH with X11 forwarding: `ssh -X user@host`
- NVIDIA proprietary drivers recommended for best performance

### macOS
- Metal GPU provides best performance
- Apple Silicon: Native ARM64 performance
- Intel Macs: Rosetta not needed, native x86_64

## Testing Cross-Platform

All features have been tested on:
- macOS 13+ (Ventura/Sonoma) - Apple Silicon & Intel
- Windows 10/11 - AMD and NVIDIA GPUs
- Ubuntu 20.04/22.04 - NVIDIA GPUs
- Fedora 36+ - AMD GPUs

## Known Platform Limitations

### Windows
- None identified - all features work

### Linux
- Requires X11 display (use HTML export for headless)
- Wayland: Works with XWayland compatibility layer

### macOS
- None identified - all features work

## Troubleshooting by Platform

### Windows Issues

**Problem:** `python` command not found  
**Solution:** Add Python to PATH or use `py -3` command

**Problem:** Missing Visual C++ redistributables  
**Solution:** Install [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Linux Issues

**Problem:** "Cannot connect to X server"  
**Solution:** Ensure X11 is running or use `xvfb-run` for headless

**Problem:** OpenGL errors  
**Solution:** Update graphics drivers:
```bash
# Ubuntu/Debian
sudo ubuntu-drivers autoinstall

# Fedora
sudo dnf install akmod-nvidia
```

### macOS Issues

**Problem:** "Application not responding"  
**Solution:** Use Python with framework support:
```bash
brew install python-tk@3.11
```

## HTML Export (Cross-Platform)

The HTML export feature works identically on all platforms:

```python
visualize_volume_interactive(
    volume,
    save_html='output.html'  # Works on Windows, Linux, macOS
)
```

Exported HTML files:
- Work in any modern browser
- Fully interactive (rotate, zoom, pan)
- No installation needed for viewers
- Cross-platform compatible
- Can be shared via email or web

## Support

For platform-specific issues:
- **GitHub Issues:** [Report bugs or request features](https://github.com/aeinkoupaei/medical-visualization/issues)
- **Discussions:** [Ask questions](https://github.com/aeinkoupaei/medical-visualization/discussions)

---

**The Interactive 3D Medical Volume Viewer is truly cross-platform!**

All core features work identically across Windows, Linux, and macOS with automatic GPU acceleration.

