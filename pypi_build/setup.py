from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_directory, 'README.md')

long_description = "A WebAssembly-powered UI framework with Pythonic, indentation-based syntax."
if os.path.exists(readme_path):
    with open(readme_path, encoding='utf-8') as f:
        long_description = f.read()

setup(
    name="tinpyui-ff",
    version="1.7.2",
    author="Barathanandh",
    description="The official compiler and CLI for the TinUI framework, featuring a Pythonic, indentation-based syntax powered by WebAssembly and WebGL.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barathanandh-coder/tinui",
    project_urls={
        "Homepage": "https://github.com/barathanandh-coder/tinui",
        "Documentation": "https://github.com/barathanandh-coder/tinui#readme",
        "Repository": "https://github.com/barathanandh-coder/tinui",
        "Bug Tracker": "https://github.com/barathanandh-coder/tinui/issues",
    },
    keywords=[
        "tinui",
        "tinpyui",
        "zero-dom",
        "python-gui",
        "python-ui-framework",
        "streamlit-alternative",
        "flet-alternative",
        "reflex-alternative",
        "webassembly",
        "rust-wasm",
        "webgl-ui",
        "hardware-accelerated",
        "120fps-gui",
        "cross-platform",
        "android-gui",
        "ios-gui",
        "indentation-syntax-compiler",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "tinpyui=tinpyui.cli:main",
            "tinui=tinpyui.cli:main",
        ]
    },
    package_data={
        "tinpyui": ["__init__.pyi", "py.typed", "app_icon.png", "index.tin", "*.tin", "*.js", "*.wasm", "*.html", "*.dll", "*.so", "*.dylib", "shaders/*"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
