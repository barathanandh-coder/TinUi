from setuptools import setup, find_packages

setup(
    name="tinpyui-cli",
    version="1.5.0",
    description="The Zero-DOM Wasm Engine CLI",
    author="barathanandh-coder",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "tinpyui_cli": ["bin/*", "*.pyi"],
    },
    entry_points={
        "console_scripts": [
            "tinpy = tinpyui_cli.main:run",
        ],
    },
)
