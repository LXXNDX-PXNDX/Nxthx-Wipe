from setuptools import setup, find_packages

setup(
    name="NetherWipe",
    version="1.0.0",
    author="CygnusX",
    description="Netzwerk-Zerstörungstool für macOS",
    packages=find_packages(),
    install_requires=[
        "scapy",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "netherwipe=netherwipe.main:main",
        ]
    },
    python_requires=">=3.7",
)