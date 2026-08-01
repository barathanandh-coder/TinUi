from setuptools import setup, find_packages

setup(
    name="tinpyui-ff",
    version="1.5.1",
    author="Barathanandh",
    description="The official Python type stubs and CLI integration for the TinUI framework.",
    long_description="A WebAssembly-powered UI framework with Pythonic, indentation-based syntax.",
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
