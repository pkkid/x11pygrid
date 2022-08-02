import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="x11pygrid",
    author="Hilary Jendrasiak",  # AFAIK it's foreseen for the package author; That's the awkward field I was talking about;/
    author_email="sylogista@sylogista.pl",
    description="Easily organize your open windows by tiling, resizing and positioning them. It supports multiple monitors!",
    keywords="X11, tilt, resize",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/x11pygrid/",
    project_urls={  # These urls are IMHO going to fix the aforementioned awkwardness.
        "Documentation": "https://github.com/pkkid/pygrid/blob/master/README.md",
        "Bug Reports": "https://github.com/pkkid/pygrid/issues",
        "Source Code": "https://github.com/pkkid/pygrid",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        # see https://pypi.org/classifiers/
        "Development Status :: 5 - Production/Stable",
        "Topic :: Desktop Environment",
        "Topic :: Desktop Environment :: Window Managers",
        "Topic :: Utilities",
        "Intended Audience :: End Users/Desktop",
        "Environment :: X11 Applications",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Xlib",
        "single_process",
        "PyGObject",  # this is "gi" requirement
        "pycairo",  # this is "gi" requirement
    ],
    scripts=['src/bin/x11pygrid'],
)
