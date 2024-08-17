# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="file_auto_expiry", 
    version="0.0.1", 
    description="WATCloud project containing scripts to check if directories / files are expired",  # Optional

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},  
    packages=find_packages(where="src"), 
   
    python_requires=">=3.7, <4",
    extras_require={ 
        "dev": ["check-manifest"],
        "test": ["coverage"],
    }
)