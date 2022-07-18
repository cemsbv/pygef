from setuptools import setup

exec(open("pygef/_version.py").read())

setup(
    name="pygef",
    version=__version__,
    author="Ritchie Vink",
    author_email="ritchie46@gmail.com",
    url="https://github.com/cemsbv/pygef",
    license="mit",
    packages=["pygef", "pygef.been_jefferies", "pygef.robertson"],
    install_requires=[
        "polars>= 0.13.55",
        "matplotlib>= 3.4.2",
        "lxml==4.9.1",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
