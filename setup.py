"""Setup configuration for interactive kids device."""

from setuptools import setup, find_packages

setup(
    name="brain-ball",
    version="0.1.0",
    description="Interactive Kids Device - Crawl Phase",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "adafruit-circuitpython-ili9341>=1.2.0",
        "adafruit-blinka>=8.0.0",
        "gpiozero>=1.6.2",
        "pygame>=2.5.0",
        "pytest>=7.4.0",
        "pytest-mock>=3.12.0",
    ],
    entry_points={
        "console_scripts": [
            "brain-ball=src.app.main:main",
        ],
    },
)
