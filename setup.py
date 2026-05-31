from setuptools import setup, find_packages

setup(
    name="kefu-z",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "gradio>=4.0.0",
        "structlog>=23.0.0",
        "httpx>=0.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    python_requires=">=3.10",
)
