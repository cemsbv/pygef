from setuptools import setup

setup(
    name="pygef",
    version="0.3.3",
    author="Ritchie Vink",
    author_email="ritchie46@gmail.com",
    url="https://www.ritchievink.com",
    license="mit",
    packages=["pygef", "pygef.been_jefferies", "pygef.robertson"],
    install_requires=["pandas", "numpy", "matplotlib"],
    python_requires=">=3.6",
)
