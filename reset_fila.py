import shutil
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_INICIAL = (
    BASE_DIR / "data" / "fila_itens_inicial.csv"
)

ARQUIVO_ATIVO = (
    BASE_DIR / "data" / "fila_itens.csv"
)


def resetar_fila():
    if not ARQUIVO_INICIAL.exists():
        raise FileNotFoundError(
            f"Massa inicial não encontrada: {ARQUIVO_INICIAL}"
        )

    shutil.copyfile(
        ARQUIVO_INICIAL,
        ARQUIVO_ATIVO,
    )

    print("Fila reinicializada com sucesso.")
    print(f"Arquivo atualizado: {ARQUIVO_ATIVO}")


if __name__ == "__main__":
    resetar_fila()