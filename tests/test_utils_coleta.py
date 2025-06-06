import os
import sys

# Add the src directory to the Python path so tests can import project modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from coleta.utils_coleta import coletar_dados_inpe, COORDENADAS_UF


def test_coletar_dados_inpe_returns_all_ufs():
    df = coletar_dados_inpe("2024-01-01", "2024-01-03")
    assert not df.empty
    assert set(df["uf"].unique()) == set(COORDENADAS_UF.keys())

