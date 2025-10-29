"""
路径规划与轨迹跟踪课程 - 安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="path-planning-course",
    version="1.0.0",
    author="Path Planning Team",
    author_email="team@example.com",
    description="4节课系统学习路径规划与轨迹跟踪",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/path-planning-course",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "cvxpy>=1.2.0",
        "osqp>=0.6.2",
        "manim>=0.17.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lesson1=examples.lesson1_demo:main",
            "lesson2=examples.lesson2_demo:main",
            "lesson3=examples.lesson3_demo:main",
            "lesson4=examples.lesson4_demo:main",
            "full-demo=examples.full_system_demo:main",
        ],
    },
)

