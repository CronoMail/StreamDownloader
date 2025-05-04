from setuptools import setup, find_packages
import os

with open('VERSION') as f:
    version = f.read().strip()

setup(
    name="stream-downloader",
    version=version,
    packages=find_packages(),
    package_data={
        "src.ui": ["*.qss"],
    },
    install_requires=[
        "PyQt5>=5.15.0",
        "yt-dlp>=2025.04.30",
        "streamlink>=6.0.0",
        "requests>=2.25.0",
        "inquirer>=3.1.3",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "stream-downloader-gui=src.main:main",
            "stream-downloader=src.cli:main",
        ],
    },
    author="Stream Downloader Team",
    author_email="example@example.com",
    description="A modern UI application for downloading Twitch and YouTube livestreams",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CronoMail/StreamDownloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.6",
)
