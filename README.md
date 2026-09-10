# Projeto Prático de Hyperautomation

## Conferência automatizada de itens de importação

**Autor:** José Santarém Gomes

## 1. Objetivo

Este projeto demonstra, de maneira simples e reproduzível, os conceitos de estrutura de bot, fila de trabalho, idempotência, validação de dados, tratamento de falhas, logging estruturado, alertas e testes automatizados.

O bot realiza a conferência de uma lista de itens de importação. Cada item possui uma quantidade informada e uma quantidade encontrada. O processamento compara esses valores e registra o resultado individualmente.

Uma falha ou divergência em um item não impede o processamento dos demais registros.

## 2. Cenário

O arquivo CSV possui 12 itens de importação.

Para cada item, o bot compara:

* quantidade informada;
* quantidade encontrada.

Os resultados possíveis são:

* `pendente`: item aguardando processamento;
* `processando`: item reservado pelo bot;
* `concluido`: quantidades conferidas com sucesso;
* `erro`: divergência ou dado inválido encontrado.

Na massa de dados utilizada:

* 8 itens possuem quantidades iguais;
* 4 itens possuem divergências.

## 3. Funcionalidades

O projeto possui as seguintes funcionalidades:

* leitura da fila em arquivo CSV;
* processamento individual dos registros;
* atualização do estado de cada item;
* controle do número de tentativas;
* validação das quantidades;
* tratamento de falhas sem interromper o lote;
* proteção contra reprocessamento;
* logging estruturado em formato JSON;
* alerta simulado baseado em critério;
* resumo consolidado da execução;
* testes automatizados;
* reinicialização da massa de dados.

## 4. Estrutura do projeto

```text
projeto_hyperautomation/
├── bot.py
├── reset_fila.py
├── requirements.txt
├── README.md
├── data/
│   ├── fila_itens.csv
│   └── fila_itens_inicial.csv
├── evidencias/
│   ├── primeira_execucao.txt
│   ├── segunda_execucao.txt
│   ├── resultado_testes.txt
│   └── fila_apos_primeira_execucao.csv
├── logs/
│   └── execucao.log
└── tests/
    └── test_bot.py
```

### Descrição dos arquivos

* `bot.py`: ponto de entrada e código principal da automação;
* `reset_fila.py`: restaura a fila para o estado inicial;
* `requirements.txt`: informa as dependências do projeto;
* `README.md`: contém as instruções de reprodução;
* `data/fila_itens.csv`: fila utilizada pelo bot;
* `data/fila_itens_inicial.csv`: massa original usada para reiniciar o teste;
* `logs/execucao.log`: log estruturado das execuções;
* `evidencias/primeira_execucao.txt`: resultado da primeira execução;
* `evidencias/segunda_execucao.txt`: comprovação da idempotência;
* `evidencias/resultado_testes.txt`: resultado dos testes automatizados;
* `evidencias/fila_apos_primeira_execucao.csv`: estado da fila depois do primeiro processamento;
* `tests/test_bot.py`: testes automatizados do projeto.

## 5. Requisitos

Para executar o projeto, é necessário possuir:

* Python 3.10 ou superior;
* terminal PowerShell, Prompt de Comando ou terminal equivalente;
* permissão para ler e gravar arquivos na pasta do projeto.

## 6. Dependências

O bot utiliza somente bibliotecas nativas do Python. Portanto, não depende de pacotes externos.

O arquivo `requirements.txt` contém:

```text
# Projeto sem dependências externas
```

## 7. Estrutura da fila

O arquivo `data/fila_itens.csv` possui as seguintes colunas:

| Coluna                  | Descrição                                 |
| ----------------------- | ----------------------------------------- |
| `item_id`               | Identificador único do item               |
| `descricao`             | Descrição do componente                   |
| `quantidade_informada`  | Quantidade esperada                       |
| `quantidade_encontrada` | Quantidade conferida                      |
| `status`                | Estado atual do item                      |
| `tentativas`            | Número de vezes que o item foi processado |
| `mensagem`              | Resultado ou motivo do erro               |

Antes da primeira execução, todos os itens devem estar com:

```text
status = pendente
tentativas = 0
mensagem = vazia
```

## 8. Reinicialização da fila

Para restaurar todos os itens ao estado inicial, execute na raiz do projeto:

```powershell
python reset_fila.py
```

O resultado esperado é:

```text
Fila reinicializada com sucesso.
Arquivo atualizado: caminho_do_projeto\data\fila_itens.csv
```

O programa copia o conteúdo de `data/fila_itens_inicial.csv` para `data/fila_itens.csv`.

A reinicialização apaga os resultados presentes somente na fila ativa. Ela não altera os logs nem os arquivos da pasta `evidencias`.

## 9. Configuração de caracteres no PowerShell

Antes de salvar as saídas, recomenda-se configurar o terminal para UTF-8:

```powershell
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

Isso evita que palavras com acentos sejam armazenadas com caracteres incorretos.

## 10. Primeira execução

Primeiro, reinicialize a fila:

```powershell
python reset_fila.py
```

Depois, execute o bot e armazene a saída:

```powershell
$primeiraExecucao = python bot.py
$primeiraExecucao | Set-Content -Path evidencias\primeira_execucao.txt -Encoding utf8
$primeiraExecucao
```

O resultado esperado é:

```text
Itens processados: 12
Itens concluídos: 8
Itens com erro: 4
Itens ignorados por já estarem concluídos: 0
Itens bloqueados com erro anterior: 0
```

Depois da primeira execução, preserve uma cópia da fila processada:

```powershell
Copy-Item data\fila_itens.csv evidencias\fila_apos_primeira_execucao.csv
```

O CSV deverá apresentar:

* 8 itens com status `concluido`;
* 4 itens com status `erro`;
* todos os itens com uma tentativa;
* uma mensagem de sucesso ou divergência em cada item.

## 11. Alerta simulado

O alerta segue o seguinte critério:

> Um alerta crítico deve ser emitido quando dois ou mais itens apresentarem erro na mesma execução.

Como a massa de teste possui quatro divergências, a primeira execução gera:

```text
ALERTA SIMULADO
Foram encontrados 4 itens com erro. Verificação humana necessária.
```

O alerta também é registrado no arquivo `logs/execucao.log` com nível `CRITICAL`.

Um erro isolado seria registrado no log, mas não geraria o alerta. Isso evita notificações excessivas e representa o conceito de interrupção com propósito.

## 12. Segunda execução e idempotência

Sem reinicializar a fila, execute o bot novamente:

```powershell
$segundaExecucao = python bot.py
$segundaExecucao | Set-Content -Path evidencias\segunda_execucao.txt -Encoding utf8
$segundaExecucao
```

O resultado esperado é:

```text
Itens processados: 0
Itens concluídos: 00
Itens com erro: 0
Itens ignorados por já estarem concluídos: 8
Itens bloqueados com erro anterior: 4
```

Na segunda execução:

* os itens concluídos não são processados novamente;
* os itens com erro permanecem bloqueados;
* o número de tentativas permanece igual a 1;
* nenhuma operação é duplicada;
* nenhum novo alerta é emitido.

Esse comportamento comprova a idempotência do bot.

## 13. Logging estruturado

Cada evento é registrado em `logs/execucao.log` no formato JSON.

Exemplo de item concluído:

```json
{
  "timestamp": "2026-09-10T10:30:15Z",
  "nivel": "INFO",
  "item_id": "IMP-001",
  "evento": "ITEM_CONCLUIDO",
  "mensagem": "Quantidades conferidas com sucesso."
}
```

Exemplo de divergência:

```json
{
  "timestamp": "2026-09-10T10:30:16Z",
  "nivel": "WARNING",
  "item_id": "IMP-002",
  "evento": "DIVERGENCIA_ENCONTRADA",
  "mensagem": "Divergência encontrada."
}
```

Os principais eventos registrados são:

* `EXECUCAO_INICIADA`;
* `ITEM_INICIADO`;
* `ITEM_CONCLUIDO`;
* `DIVERGENCIA_ENCONTRADA`;
* `ERRO_DE_VALIDACAO`;
* `FALHA_INESPERADA`;
* `STATUS_DESCONHECIDO`;
* `ALERTA_CRITICO`;
* `EXECUCAO_FINALIZADA`.

Cada entrada contém:

* timestamp;
* nível de severidade;
* identificador;
* evento;
* mensagem.

## 14. Testes automatizados

Os testes estão no arquivo:

```text
tests/test_bot.py
```

Primeiro, verifique a sintaxe:

```powershell
python -m py_compile bot.py reset_fila.py tests\test_bot.py
```

Para executar os testes:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

O resultado esperado é:

```text
test_idempotencia ... ok
test_item_com_divergencia ... ok
test_item_com_quantidades_iguais ... ok
test_quantidade_negativa ... ok

----------------------------------------------------------------------
Ran 4 tests

OK
```

Os quatro testes verificam:

1. conclusão de um item com quantidades iguais;
2. identificação de uma divergência;
3. rejeição de uma quantidade negativa;
4. não reprocessamento de um item concluído.

Os testes utilizam uma fila temporária. Portanto, não modificam o arquivo `data/fila_itens.csv`.

### Salvando o resultado dos testes

Para armazenar corretamente o resultado, utilize via PowerShell:

```powershell
cmd.exe /d /c 'python -m unittest discover -s tests -p "test_*.py" -v > evidencias\resultado_testes.txt 2>&1'
```

Depois, visualize o arquivo:

```powershell
Get-Content evidencias\resultado_testes.txt -Encoding UTF8
```

A execução está correta quando:

* os quatro testes aparecem;
* todos apresentam `ok`;
* a linha final apresenta `OK`;
* não aparece `FAILED`.

## 15. Tratamento de falhas

Cada item é processado individualmente.

Quando ocorre uma divergência ou falha:

1. o item recebe status `erro`;
2. a mensagem explica o motivo;
3. o evento é registrado no log;
4. o processamento continua com o próximo item.

Isso evita que um único registro defeituoso interrompa todo o lote.

Os itens com erro não são reprocessados automaticamente. Para uma nova tentativa, é necessário corrigir os dados e alterar o status do item para `pendente`.

## 16. Fluxo completo de reprodução

Para reproduzir o projeto do início:

```powershell
python reset_fila.py
```

Configure o UTF-8:

```powershell
$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
```

Faça a primeira execução:

```powershell
$primeiraExecucao = python bot.py
$primeiraExecucao | Set-Content -Path evidencias\primeira_execucao.txt -Encoding utf8
$primeiraExecucao
```

Preserve o CSV processado:

```powershell
Copy-Item data\fila_itens.csv evidencias\fila_apos_primeira_execucao.csv
```

Faça a segunda execução:

```powershell
$segundaExecucao = python bot.py
$segundaExecucao | Set-Content -Path evidencias\segunda_execucao.txt -Encoding utf8
$segundaExecucao
```

Execute os testes:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Ao final, verifique:

* `data/fila_itens.csv`;
* `logs/execucao.log`;
* `evidencias/primeira_execucao.txt`;
* `evidencias/segunda_execucao.txt`;
* `evidencias/resultado_testes.txt`;
* `evidencias/fila_apos_primeira_execucao.csv`.

## 17. Resultado esperado

O projeto demonstra que:

* a fila é processada item por item;
* uma divergência não interrompe o lote;
* itens concluídos não são processados novamente;
* os erros ficam registrados para análise;
* cada evento gera um log estruturado;
* alertas possuem um critério definido;
* os resultados podem ser comprovados por evidências;
* a massa de dados pode ser restaurada;
* a execução pode ser reproduzida em outra máquina.