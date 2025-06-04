from setuptools import setup, find_packages
import os

def read_requirements():
    # Tenta ler o requirements.txt da raiz primeiro
    if os.path.exists("requirements.txt"):
        req_file = "requirements.txt"
    # Se não encontrar, tenta na pasta do projeto
    elif os.path.exists("monitoramento-queimadas/requirements.txt"):
        req_file = "monitoramento-queimadas/requirements.txt"
    else:
        return []

    with open(req_file) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="monitoramento-queimadas",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
)
