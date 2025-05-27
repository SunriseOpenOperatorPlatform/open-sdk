from setuptools import setup, find_packages

setup(
    name="OpenSDK",
    version="0.1.0",
    description="SDK para interactuar con EdgeCloud",
    author="Tu Nombre",
    author_email="tuemail@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    install_requires=[
        "annotated-types==0.7.0",
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "colorlog==6.8.2",
        "exceptiongroup==1.2.2",
        "idna==3.10",
        "iniconfig==2.0.0",
        "packaging==24.2",
        "pluggy==1.5.0",
        "pydantic==2.10.6",
        "pydantic_core==2.27.2",
        "pytest==8.3.2",
        "requests==2.32.3",
        "tomli==2.2.1",
        "typing_extensions==4.12.2",
        "urllib3==2.3.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)