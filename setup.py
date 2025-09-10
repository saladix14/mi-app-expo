from setuptools import setup, find_packages

setup(
    name="seedaudit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "colorama"
    ],
    entry_points={
        "console_scripts": [
            "seedaudit=seedaudit.cli:cli"
        ]
    },
    author="Riko De la Kika",
    description="Auditoría de RNG y generación de mnemonics en proyectos Web3.",
    license="MIT",
)
