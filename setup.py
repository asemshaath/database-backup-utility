from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="afterchive",
    version="0.1.0",
    author="Asem Shaath",
    author_email="shaathasem@gmail.com",
    description="Multi-database, multi-cloud backup utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asemshaath/afterchive",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Database",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mysql": ["mysql-connector-python>=8.0.0"],
        "gcs": ["google-cloud-storage>=2.0.0"],
        "s3": ["boto3>=1.26.0"],
        "all": [
            "psycopg2-binary>=2.9.0",
            "mysql-connector-python>=8.0.0",
            "google-cloud-storage>=2.0.0",
            "boto3>=1.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "afterchive=core.cli:main",
        ],
    },
)