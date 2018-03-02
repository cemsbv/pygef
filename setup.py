from setuptools import setup

setup(
    name="pygef",
    version="0.2",
    author="Ritchie Vink",
    author_email='ritchie46@gmail.com',
    url="https://www.ritchievink.com",
    license="mit",
    packages=["pygef"],
    install_requires=[
        "pandas",
        "numpy"
    ],
    python_requires=">=3.4"
)
