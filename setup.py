from setuptools import find_packages, setup

setup(
    name="main",
    version="1.0.0",
    packages=[*find_packages(exclude=["test", "test.*"])],
    url="github url"
    entry_points={"console_scripts": ["main= main.__main__:main"]},
    include_package_data=True,
)
