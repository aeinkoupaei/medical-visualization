#!/usr/bin/env python3
"""
Setup script for Interactive 3D Medical Volume Viewer (Cross-Platform)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="medical-visualization",
    version="1.0.0",
    author="aein koupaei",
    author_email="aeinkoupaei@gmail.com",
    description="Cross-platform GPU-accelerated 3D medical imaging visualization tool (Windows, Linux, macOS)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aeinkoupaei/medical-visualization",
    project_urls={
        "Bug Reports": "https://github.com/aeinkoupaei/medical-visualization/issues",
        "Source": "https://github.com/aeinkoupaei/medical-visualization",
        "Documentation": "https://github.com/aeinkoupaei/medical-visualization#readme",
    },
    packages=find_packages(where="scripts"),
    package_dir={"": "scripts"},
    py_modules=["medical_interactive_viewer"],
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        
        # Topic
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Image Processing",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Python Versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        
        # Operating System
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
        
        # Natural Language
        "Natural Language :: English",
    ],
    keywords=[
        "medical imaging",
        "3D visualization",
        "NIfTI",
        "MRI",
        "CT scan",
        "volume rendering",
        "cross-platform",
        "GPU acceleration",
        "Metal",
        "DirectX",
        "OpenGL",
        "PyVista",
        "medical visualization",
        "Windows",
        "Linux",
        "macOS",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pyvista>=0.40.0",
        "nibabel>=3.2.0",
    ],
    extras_require={
        "html": [
            "nest-asyncio>=1.5.6",
            "trame>=2.5.0",
            "trame-vtk>=2.5.0",
            "trame-vuetify>=2.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "all": [
            "nest-asyncio>=1.5.6",
            "trame>=2.5.0",
            "trame-vtk>=2.5.0",
            "trame-vuetify>=2.3.0",
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "medviz=medical_interactive_viewer:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "LICENSE"],
    },
    zip_safe=False,
    platforms=["Windows", "Linux", "MacOS"],
)

