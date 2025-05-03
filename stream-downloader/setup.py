from setuptools import setup, find_packages

setup(
    name="stream-downloader",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        "stream_downloader": ["style.qss"],
    },
    install_requires=[
        "PyQt5>=5.15.0",
        "yt-dlp>=2022.7.18",
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "stream-downloader=stream_downloader.main:main",
        ],
    },
    author="Stream Downloader Team",
    author_email="example@example.com",
    description="A modern UI application for downloading Twitch and YouTube livestreams",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stream-downloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.6",
)
