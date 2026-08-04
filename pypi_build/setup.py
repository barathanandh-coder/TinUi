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
    version="1.5.2",
    author="Barathanandh",
    description="The official Python type stubs and CLI integration for the TinUI framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/barathanandh-coder/tinui",
    packages=find_packages(),
    package_data={
        "tinpyui": ["__init__.pyi", "py.typed"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
