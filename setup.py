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
        "pandas>=2.0.0",  # Atualizado para versão mais recente
        "numpy>=1.22.0,<2.0.0",
        "plotly>=5.13.0,<6.0.0",
        "folium>=0.14.0,<1.0.0",
        "streamlit-folium>=0.11.0,<1.0.0",
        "weasyprint>=58.0,<61.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "Pillow>=10.0.0",
        "requests>=2.28.0,<3.0.0",
        "markdown-it-py>=2.2.0,<4.0.0",
        "rich>=13.0.0,<15.0.0",
        "mdurl>=0.1.0,<0.2.0",
        "pygments>=2.15.0,<3.0.0"
    ],
)
