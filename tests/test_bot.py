import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bot


class TestBot(unittest.TestCase):

    def criar_item(
        self,
        informada="10",
        encontrada="10",
        status="pendente",
        tentativas="0",
    ):
        return {
            "item_id": "TESTE-001",
            "descricao": "Item utilizado no teste",
            "quantidade_informada": informada,
            "quantidade_encontrada": encontrada,
            "status": status,
            "tentativas": tentativas,
            "mensagem": "",
        }

    @patch("bot.registrar_log")
    def test_item_com_quantidades_iguais(self, mock_log):
        item = self.criar_item(
            informada="10",
            encontrada="10",
        )

        resultado = bot.processar_item(item)

        self.assertEqual(resultado, "concluido")
        self.assertEqual(item["status"], "concluido")
        self.assertIn(
            "sucesso",
            item["mensagem"].lower(),
        )

    @patch("bot.registrar_log")
    def test_item_com_divergencia(self, mock_log):
        item = self.criar_item(
            informada="10",
            encontrada="8",
        )

        resultado = bot.processar_item(item)

        self.assertEqual(resultado, "erro")
        self.assertEqual(item["status"], "erro")
        self.assertIn(
            "divergência",
            item["mensagem"].lower(),
        )

    @patch("bot.registrar_log")
    def test_quantidade_negativa(self, mock_log):
        item = self.criar_item(
            informada="10",
            encontrada="-1",
        )

        resultado = bot.processar_item(item)

        self.assertEqual(resultado, "erro")
        self.assertEqual(item["status"], "erro")
        self.assertIn(
            "dados inválidos",
            item["mensagem"].lower(),
        )

    def test_idempotencia(self):
        """
        Executa o bot duas vezes em uma fila temporária
        e verifica se o item concluído não é reprocessado.
        """

        with tempfile.TemporaryDirectory() as pasta:
            csv_temporario = Path(pasta) / "fila_teste.csv"

            itens = [
                self.criar_item(
                    informada="10",
                    encontrada="10",
                )
            ]

            with csv_temporario.open(
                mode="w",
                encoding="utf-8",
                newline="",
            ) as arquivo:
                escritor = csv.DictWriter(
                    arquivo,
                    fieldnames=bot.CAMPOS,
                )

                escritor.writeheader()
                escritor.writerows(itens)

            with patch.object(
                bot,
                "CSV_PATH",
                csv_temporario,
            ):
                with patch("bot.registrar_log"):
                    with patch("builtins.print"):
                        # Primeira execução
                        bot.executar()

                        with csv_temporario.open(
                            mode="r",
                            encoding="utf-8",
                            newline="",
                        ) as arquivo:
                            primeira_execucao = list(
                                csv.DictReader(arquivo)
                            )

                        # Segunda execução
                        bot.executar()

                        with csv_temporario.open(
                            mode="r",
                            encoding="utf-8",
                            newline="",
                        ) as arquivo:
                            segunda_execucao = list(
                                csv.DictReader(arquivo)
                            )

            self.assertEqual(
                primeira_execucao[0]["status"],
                "concluido",
            )

            self.assertEqual(
                segunda_execucao[0]["status"],
                "concluido",
            )

            self.assertEqual(
                primeira_execucao[0]["tentativas"],
                "1",
            )

            self.assertEqual(
                segunda_execucao[0]["tentativas"],
                "1",
            )


if __name__ == "__main__":
    unittest.main()