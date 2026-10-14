# Explorar os resumos digitais

Os notebooks em `test/` trabalham diretamente com as tabelas HTML em `extracted/`:

- `01_panorama.ipynb`: inventário, contagens por manifesto, busca por arquivo e checagem do **formato** dos hashes.
- `02_urnas.ipynb`: comparação dos arquivos-base e dos resumos por UF das urnas 2013, 2015, 2020 e 2022.
- `03_midias.ipynb`: comparação dos manifestos das entidades TSE, OAB, MP e CONFEA em 01/09 e 02/09/2026.

**Atenção:** estes são manifestos de hashes SHA-512 em Base64, *não* resultados de votação. Sem os arquivos originais não é possível recalcular os hashes nem atestar a integridade das urnas. Linhas `HASH GERAL` e títulos de seção não são contados como arquivos. As entradas de `__MACOSX/` são metadados de ZIP e são ignoradas.

## Executar e conservar os gráficos

Na raiz do repositório, com Python 3.10+:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r test/requirements.txt
python test/run_notebooks.py
python -m unittest discover -s test -p 'test_*.py'
```

`run_notebooks.py` executa os três notebooks e **salva as imagens PNG dentro das células** (`image/png`), no próprio `.ipynb`. A execução não limpa os outputs depois; se um notebook falhar, sua versão salva anteriormente continua intacta. Os notebooks distribuídos aqui já incluem gráficos executados para leitura sem kernel. Não execute ferramentas de *clear-output*/`nbstripout` antes de salvar as alterações.

Para explorar no navegador, instale opcionalmente `jupyterlab` e execute `jupyter lab test/`. Altere os filtros em maiúsculas (`GRUPO`, `BUSCA`, `UF`, `MODELO`, `ENTIDADE`, `DATA`) e rode a célula correspondente; salve o notebook para manter o novo gráfico ou tabela embutido. Também é possível abrir os `.ipynb` em um editor com suporte a Jupyter. O leitor encontra o repositório tanto ao executar a partir da raiz quanto de `test/`.
