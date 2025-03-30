from setuptools import setup, find_packages


__version__ = "0.0.6"


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="hackatari",
    version=__version__,
    author="Quentin Delfosse, Jannis Blüml",
    author_email="quentin.delfosse@cs.tu-darmstadt.de",
    packages=find_packages(),
    # package_data={'': extra_files},
    include_package_data=True,
    # package_dir={'':'src'},
    url="https://github.com/k4ntz/HAckAtari",
    description="Extended Atari Learning Environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires="3.11.11",
    install_requires=[
        "ocatari==2.2.1",
        "notebook==7.3.3",
        "voila==0.5.8",
        "ipywidgets==8.1.5",
        "torch==2.6.0",
        "widgetsnbextension==4.0.13",
        "tabulate==0.9.0"
    ],
)

# print("Please install gymnasium atari dependencies, using:\n",
#       "pip install gymnasium[atari, accept-rom-license]")
