# 🏥 Medical Visualization Platform

A professional Flask-based web application for visualizing 3D medical imaging data, fully containerized with Docker.

👉 **Live Demo**: Try the app directly in your browser on Hugging Face Spaces [here](https://huggingface.co/spaces/AeinKoupaei/medical-visualization-platform).

## ✨ Features

- 📁 **File Upload**: Support for NIfTI (.nii, .nii.gz) and NumPy (.npy) formats
- 🔬 **2D Slice Viewing**: Visualize axial, coronal, and sagittal slices
- 📊 **3D Volume Rendering**: Interactive volume visualization with customizable opacity
- 🎨 **Multiple Colormaps**: Gray, Bone, Viridis, Hot, Cool, Plasma
- 🐳 **Docker Ready**: Fully containerized for deployment on Hugging Face Spaces or anywhere
- ⚡ **Fast & Stable**: Pure Flask backend with custom frontend

## 🚀 Quick Start on Hugging Face Spaces

This Space is ready to use! Just click on the application above.

### Upload and Visualize
1. **Upload** a medical imaging file (.nii, .nii.gz, or .npy)
2. **Select** visualization mode:
   - 2D Slice View (Axial, Coronal, or Sagittal)
   - 3D Volume Rendering
3. **Adjust** settings (colormap, opacity, slice index)
4. **Generate** visualization

## 💻 Local Development

### Using Docker Compose

```bash
# Clone the repository
git clone [your-repo-url]
cd medical-visualization-platform

# Build and start
docker-compose up --build
```

Visit http://localhost:5000

### Using Docker Manually

```bash
# Build the Docker image
docker build -t medical-viz .

# Run the container
docker run -p 5000:5000 medical-viz
```

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

## 📁 Project Structure

```
medical-visualization-platform/
├── Dockerfile              # Container configuration
├── app.py                  # Flask application
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/style.css      # Styling
│   └── js/app.js          # Frontend logic
├── uploads/               # Uploaded files (auto-created)
└── outputs/               # Generated visualizations (auto-created)
```

## 🔧 Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- PyVista - 3D visualization
- nibabel - Medical imaging I/O
- NumPy - Numerical computing
- Matplotlib - 2D plotting

**Frontend:**
- Pure HTML5/CSS3/JavaScript
- Modern responsive design

**Deployment:**
- Docker containerized
- Hugging Face Spaces ready

## 🔒 Security Notes

- Maximum file size: 500MB
- Supported formats: .nii, .nii.gz, .npy only
- Files are temporarily stored and should be cleaned periodically