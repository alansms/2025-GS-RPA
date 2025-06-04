from setuptools import setup, find_packages

setup(
    name="monitoramento-queimadas",
    version="1.0.0",
    description="Sistema de monitoramento de queimadas",
    author="Alan",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.24.0,<2.0.0",
        "pandas>=1.5.0,<2.0.0",
        "numpy>=1.22.0,<2.0.0",
        "plotly>=5.13.0,<6.0.0",
        "folium>=0.14.0,<1.0.0",
        "streamlit-folium>=0.11.0,<1.0.0",
        "weasyprint>=58.0,<61.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "Pillow>=9.0.0,<10.0.0",
        "requests>=2.28.0,<3.0.0"
    ],
)
