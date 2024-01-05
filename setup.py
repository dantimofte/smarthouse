from setuptools import find_packages, setup

VERSION = "1.0.1"
# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    "structlog==23.3.0",
    "fastapi==0.108.0",
    "uvicorn==0.25.0",
    "aiohttp==3.9.1",
    "python-dotenv==1.0.0",
    "ewelink@git+ssh://git@github.com/dantimofte/ewelink-api-python.git@1.1.0"
]

setup(
    name="smarthouse",
    version=VERSION,
    description="Smart house automations",
    author="Dan Timofte",
    author_email="github.fragile316@passmail.net",
    url="https://github.com/dantimofte/smarthouse",
    license="",
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    include_package_data=True,
    keywords=[],
    classifiers=[],
    zip_safe=True,
    entry_points={
    },
)
