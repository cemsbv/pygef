from setuptools import setup

exec(open("pygef/_version.py").read())

setup(
    name="pygef",
    version=__version__,
    author="Ritchie Vink",
    author_email="ritchie46@gmail.com",
    url="https://www.ritchievink.com",
    license="mit",
    packages=["pygef", "pygef.been_jefferies", "pygef.robertson"],
    install_requires=["pandas>= 1.1.5", "matplotlib>= 3.4.2"],
    python_requires=">=3.6",
)
