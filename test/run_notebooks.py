"""Executa test/*.ipynb e preserva as figuras PNG dentro dos próprios notebooks.

Uso: python test/run_notebooks.py (na raiz; por caminho absoluto de qualquer lugar).
Salva cada notebook somente após uma execução bem-sucedida; uma falha mantém a
versão anterior com seus outputs intactos. Não gera nem apaga arquivos PNG soltos.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_DIR = ROOT / "test"


def main() -> None:
    paths = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if not paths:
        raise SystemExit(f"Nenhum notebook encontrado em {NOTEBOOK_DIR}")

    for path in paths:
        print(f"Executando {path.relative_to(ROOT)} ...", flush=True)
        notebook = nbformat.read(path, as_version=4)
        NotebookClient(
            notebook,
            timeout=120,
            kernel_name="python3",
            resources={"metadata": {"path": str(ROOT)}},
            record_timing=False,
        ).execute()
        nbformat.validate(notebook)
        images = sum(
            "image/png" in output.get("data", {})
            for cell in notebook.cells
            for output in cell.get("outputs", [])
        )
        if images == 0:
            raise RuntimeError(f"Nenhuma figura PNG foi produzida por {path}")

        # A troca atômica impede que um erro de execução limpe os outputs salvos.
        fd, temporary = tempfile.mkstemp(prefix=".notebook-", suffix=".ipynb", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                nbformat.write(notebook, stream)
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)
        print(f"  Salvo com {images} figura(s) embutida(s).", flush=True)


if __name__ == "__main__":
    main()
