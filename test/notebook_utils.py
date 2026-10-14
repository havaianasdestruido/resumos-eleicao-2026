"""Apresentação compacta de tabelas nos notebooks."""

from html import escape
from typing import Iterable, Sequence

from IPython.display import HTML, display


def show_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    """Exibe uma tabela com texto escapado; limite as linhas antes de chamar."""
    head = "".join(f"<th>{escape(str(value))}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(value))}</td>" for value in row) + "</tr>"
        for row in rows
    )
    display(
        HTML(
            '<div style="overflow-x:auto;max-width:100%">'
            '<table style="border-collapse:collapse;font-size:0.9em;width:100%">'
            '<thead style="background:#dcebe8"><tr>'
            + head
            + '</tr></thead><tbody style="border-top:1px solid #aaa">'
            + body
            + "</tbody></table></div>"
        )
    )
