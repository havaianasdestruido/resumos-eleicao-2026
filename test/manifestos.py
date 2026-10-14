"""Leitura dos manifestos HTML em extracted/ (somente biblioteca padrão)."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    path: str
    digest: str
    kind: str  # "file" ou "aggregate"; cabeçalhos de seção não são entradas
    section: str = ""


@dataclass(frozen=True)
class Manifest:
    source: Path  # caminho relativo à raiz do repositório
    family: str
    title: str
    subtitle: str
    entries: tuple[Entry, ...]


class _ManifestParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: dict[str, str] = {}
        self.entries: list[Entry] = []
        self._heading: str | None = None
        self._heading_text: list[str] = []
        self._row: list[tuple[str, str]] | None = None
        self._row_classes: set[str] = set()
        self._cell: list[str] | None = None
        self._cell_tag: str | None = None
        self._section = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2"}:
            self._heading = tag
            self._heading_text = []
        elif tag == "tr":
            self._row = []
            self._row_classes = set((dict(attrs).get("class") or "").split())
        elif tag in {"th", "td"} and self._row is not None:
            self._cell_tag = tag
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._heading is not None:
            self._heading_text.append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading:
            self.headings[tag] = "".join(self._heading_text).strip()
            self._heading = None
        if tag in {"th", "td"} and self._cell is not None and self._row is not None:
            self._row.append((self._cell_tag or tag, "".join(self._cell).strip()))
            self._cell = None
            self._cell_tag = None
        if tag == "tr" and self._row is not None:
            if self._row and self._row[0][0] == "td":
                values = [text for _, text in self._row]
                if "section" in self._row_classes and len(values) == 1:
                    self._section = values[0]
                elif len(values) == 2:
                    kind = (
                        "aggregate"
                        if "hash" in self._row_classes or values[0].upper().startswith("HASH GERAL")
                        else "file"
                    )
                    self.entries.append(Entry(values[0], values[1], kind, self._section))
                else:
                    raise ValueError(f"Linha inesperada no manifesto: {values!r}")
            self._row = None


def _family(folder: str) -> str:
    if folder.startswith("path1u"):
        return "urnas"
    if folder.startswith("itnm1"):
        return "sistemas_itnm"
    if folder.startswith("pc1"):
        return "sistemas_pc"
    if folder.startswith("hash_"):
        return "midias"
    return "outros"


def load_manifests(root: Path) -> list[Manifest]:
    """Lê os HTMLs originais; ignora os metadados __MACOSX e inclui as duas datas das mídias."""
    extracted = root / "extracted"
    if not extracted.is_dir():
        raise FileNotFoundError(f"Diretório não encontrado: {extracted}")
    paths = sorted(extracted.glob("*/*.html"))  # não entra em __MACOSX/
    if not paths:
        raise FileNotFoundError(f"Nenhum manifesto HTML encontrado em {extracted}")
    manifests = []
    for path in paths:
        parser = _ManifestParser()
        parser.feed(path.read_text(encoding="utf-8-sig"))
        parser.close()
        manifests.append(
            Manifest(
                source=path.relative_to(root),
                family=_family(path.parent.name),
                title=parser.headings.get("h1", ""),
                subtitle=parser.headings.get("h2", ""),
                entries=tuple(parser.entries),
            )
        )
    return manifests


def is_sha512_base64(value: str) -> bool:
    """Verifica APENAS a forma (Base64 de 64 bytes), não a integridade de nenhum arquivo."""
    try:
        return len(base64.b64decode(value, validate=True)) == 64
    except (binascii.Error, ValueError):
        return False
