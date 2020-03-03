from setuptools import setup

setup(
    name="cobe_hubbot",
    version="1.0.0",
    author="HubbeKing",
    description="Markov chain based text generator library",
    packages=["cobe_hubbot"],
    install_requires=[
        "Cython"
        "PyStemmer"
    ]
)
