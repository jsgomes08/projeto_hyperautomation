import csv
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path


# Caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "fila_itens.csv"
LOG_PATH = BASE_DIR / "logs" / "execucao.log"

CAMPOS = [
    "item_id",
    "descricao",
    "quantidade_informada",
    "quantidade_encontrada",
    "status",
    "tentativas",
    "mensagem",
]


def configurar_logger():
    """Configura o arquivo de log estruturado."""

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("hyperautomation")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(
        LOG_PATH,
        mode="a",
        encoding="utf-8",
    )

    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    return logger


LOGGER = configurar_logger()


def obter_timestamp():
    """Retorna data e horário atual no padrão UTC."""

    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def registrar_log(nivel, item_id, evento, mensagem):
    """Registra um evento estruturado no arquivo de log."""

    registro = {
        "timestamp": obter_timestamp(),
        "nivel": nivel,
        "item_id": item_id,
        "evento": evento,
        "mensagem": mensagem,
    }

    mensagem_json = json.dumps(registro, ensure_ascii=False)

    if nivel == "CRITICAL":
        LOGGER.critical(mensagem_json)
    elif nivel == "ERROR":
        LOGGER.error(mensagem_json)
    elif nivel == "WARNING":
        LOGGER.warning(mensagem_json)
    else:
        LOGGER.info(mensagem_json)

    print(f"[{nivel}] {item_id} - {evento}: {mensagem}")


def carregar_fila():
    """Carrega todos os registros do CSV."""

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo da fila não encontrado: {CSV_PATH}"
        )

    with CSV_PATH.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        campos_encontrados = leitor.fieldnames or []

        if campos_encontrados != CAMPOS:
            raise ValueError(
                "O cabeçalho do CSV não corresponde ao esperado.\n"
                f"Esperado: {CAMPOS}\n"
                f"Encontrado: {campos_encontrados}"
            )

        return list(leitor)


def salvar_fila(itens):
    """
    Salva a fila utilizando um arquivo temporário.
    Isso reduz o risco de corromper o CSV.
    """

    arquivo_temporario = CSV_PATH.with_suffix(".tmp")

    with arquivo_temporario.open(
        mode="w",
        encoding="utf-8",
        newline="",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=CAMPOS,
        )

        escritor.writeheader()
        escritor.writerows(itens)

    os.replace(arquivo_temporario, CSV_PATH)


def processar_item(item):
    """Compara as quantidades e atualiza o estado do item."""

    item_id = item["item_id"]

    try:
        quantidade_informada = int(item["quantidade_informada"])
        quantidade_encontrada = int(item["quantidade_encontrada"])

        if quantidade_informada < 0 or quantidade_encontrada < 0:
            raise ValueError("As quantidades não podem ser negativas.")

        if quantidade_informada == quantidade_encontrada:
            item["status"] = "concluido"
            item["mensagem"] = "Quantidades conferidas com sucesso."

            registrar_log(
                "INFO",
                item_id,
                "ITEM_CONCLUIDO",
                item["mensagem"],
            )

            return "concluido"

        item["status"] = "erro"
        item["mensagem"] = (
            "Divergência encontrada. "
            f"Quantidade informada: {quantidade_informada}; "
            f"quantidade encontrada: {quantidade_encontrada}."
        )

        registrar_log(
            "WARNING",
            item_id,
            "DIVERGENCIA_ENCONTRADA",
            item["mensagem"],
        )

        return "erro"

    except (ValueError, TypeError) as erro:
        item["status"] = "erro"
        item["mensagem"] = f"Dados inválidos: {erro}"

        registrar_log(
            "ERROR",
            item_id,
            "ERRO_DE_VALIDACAO",
            item["mensagem"],
        )

        return "erro"

    except Exception as erro:
        item["status"] = "erro"
        item["mensagem"] = f"Falha inesperada: {erro}"

        registrar_log(
            "ERROR",
            item_id,
            "FALHA_INESPERADA",
            item["mensagem"],
        )

        return "erro"


def verificar_alerta(quantidade_erros):
    """
    O alerta somente será emitido quando existirem
    dois ou mais erros na mesma execução.
    """

    if quantidade_erros >= 2:
        mensagem = (
            f"Foram encontrados {quantidade_erros} itens com erro. "
            "Verificação humana necessária."
        )

        registrar_log(
            "CRITICAL",
            "EXECUCAO",
            "ALERTA_CRITICO",
            mensagem,
        )

        print("\nALERTA SIMULADO")
        print(mensagem)


def executar():
    """Executa o processamento completo da fila."""

    print("\nIniciando o processamento da fila...\n")

    registrar_log(
        "INFO",
        "EXECUCAO",
        "EXECUCAO_INICIADA",
        "Processamento da fila iniciado.",
    )

    itens = carregar_fila()

    processados = 0
    concluidos = 0
    erros = 0
    ignorados_concluidos = 0
    bloqueados_erro = 0

    for item in itens:
        status = item["status"].strip().lower()

        # Garantia de idempotência
        if status == "concluido":
            ignorados_concluidos += 1
            continue

        # Itens com erro exigem correção antes de nova tentativa
        if status == "erro":
            bloqueados_erro += 1
            continue

        if status != "pendente":
            registrar_log(
                "WARNING",
                item["item_id"],
                "STATUS_DESCONHECIDO",
                f"Item ignorado por possuir status '{status}'.",
            )
            continue

        item["status"] = "processando"
        item["tentativas"] = str(
            int(item.get("tentativas") or 0) + 1
        )
        item["mensagem"] = "Item em processamento."

        salvar_fila(itens)

        registrar_log(
            "INFO",
            item["item_id"],
            "ITEM_INICIADO",
            "Processamento do item iniciado.",
        )

        resultado = processar_item(item)
        processados += 1

        if resultado == "concluido":
            concluidos += 1
        else:
            erros += 1

        # Salva o resultado depois de cada item
        salvar_fila(itens)

    verificar_alerta(erros)

    registrar_log(
        "INFO",
        "EXECUCAO",
        "EXECUCAO_FINALIZADA",
        (
            f"Processados: {processados}; "
            f"concluídos: {concluidos}; "
            f"erros: {erros}; "
            f"ignorados por idempotência: {ignorados_concluidos}."
        ),
    )

    print("\nResumo da execução")
    print(f"Itens processados: {processados}")
    print(f"Itens concluídos: {concluidos}")
    print(f"Itens com erro: {erros}")
    print(
        "Itens ignorados por já estarem concluídos: "
        f"{ignorados_concluidos}"
    )
    print(f"Itens bloqueados com erro anterior: {bloqueados_erro}")


if __name__ == "__main__":
    executar()