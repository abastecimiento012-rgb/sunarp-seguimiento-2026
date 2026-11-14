#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publica la base de consulta SUNARP desde un Excel LOCAL. Requiere Python, openpyxl y GitHub CLI.
NO sube el archivo XLSX ni guarda contraseñas o tokens en el repositorio.
"""
from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

REPO = "abastecimiento012-rgb/sunarp-seguimiento-2026"
DEST = "datos.json"
COLUMNAS = {
    "B": "id", "C": "descripcion", "D": "procedimiento", "E": "pac",
    "F": "itemCMN", "G": "clasificador", "H": "meta", "I": "especialista",
    "J": "area", "K": "cuantia", "L": "inversion", "M": "cui",
    "N": "estado", "O": "fechaEsperada", "P": "observaciones",
    "Q": "relacionHosting", "R": "contratoVigente", "S": "contratista",
    "T": "vencimiento", "U": "naturaleza", "V": "nuevaConvocatoria",
    "W": "estadoNueva", "X": "documentosRequerimiento",
    "Y": "fechaRequerimiento", "Z": "compatibilizacion",
    "AA": "informeSoftware", "AB": "modalidadContratacion",
    "AC": "fechaConvocatoria", "AD": "fechaBuenaPro",
    "AE": "fechaConsentimiento", "AF": "plazoDocumentos",
    "AG": "fechaFirma", "AH": "primerDevengado", "AI": "detallePagos",
    "AJ": "saldoContrato", "AK": "ccp2026", "AL": "montoCCP2026",
    "AM": "prevision2027", "AN": "montoPrevision2027",
    "AO": "prevision2028", "AP": "montoPrevision2028",
    "AQ": "prevision2029", "AR": "montoPrevision2029",
    "AS": "prevision2030", "AT": "montoPrevision2030",
    "AU": "montoAdelanto", "AV": "montoAdjudicado",
    "AW": "numeroContrato", "AX": "fechaSuscripcion", "AY": "fechaInicio",
    "AZ": "montoContratado", "BA": "postor", "BB": "plazo",
    "BC": "estadoContrato", "BD": "diasVencimientoExcel",
    "BE": "semaforoExcel", "BF": "seguimientoExcel",
}
CAMPOS_NO_PUBLICAR = {"detallePagos", "saldoContrato", "primerDevengado", "montoAdelanto"}


def texto(celda):
    value = celda.value
    if value is None:
        return ""
    if isinstance(value, bool):
        return "SÍ" if value else "NO"
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, (float, int, Decimal)):
        try:
            dec = Decimal(str(value))
            if re.fullmatch(r"0+", str(celda.number_format or "").strip()):
                return str(int(dec)).zfill(len(celda.number_format))
            return format(dec, "f").rstrip("0").rstrip(".") if "." in format(dec, "f") else format(dec, "f")
        except (InvalidOperation, ValueError):
            return str(value).strip()
    return str(value).strip()


def seleccionar_archivo():
    if len(sys.argv) >= 2:
        return Path(sys.argv[1]).expanduser().resolve()
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        name = filedialog.askopenfilename(
            title="Selecciona el Excel actualizado de seguimiento SUNARP",
            filetypes=[("Excel", "*.xlsx")]
        )
        root.destroy()
        return Path(name).resolve() if name else None
    except Exception as exc:
        print("No se pudo abrir el selector de archivos:", exc)
        name = input("Ruta completa del Excel (.xlsx): ").strip().strip('"')
        return Path(name).expanduser().resolve() if name else None


def convertir_excel(path):
    try:
        from openpyxl import load_workbook
    except ImportError:
        raise RuntimeError("Falta openpyxl. Ejecuta: py -3 -m pip install openpyxl")
    if not path or not path.is_file() or path.suffix.lower() != ".xlsx":
        raise ValueError("Debes seleccionar un archivo .xlsx existente.")
    libro = load_workbook(path, data_only=True, read_only=False)
    try:
        hoja = libro.worksheets[0]  # Misma hoja utilizada por el aplicativo anterior.
        titulo = texto(hoja["C5"]).upper()
        if "DESCRIPCION" not in titulo and "DESCRIPCIÓN" not in titulo:
            raise ValueError("Formato no reconocido: falta DESCRIPCIÓN en C5 de la primera hoja.")
        rows = []
        for n in range(6, hoja.max_row + 1):
            if not texto(hoja[f"C{n}"]):
                continue
            registro = {k: texto(hoja[f"{col}{n}"]) for col, k in COLUMNAS.items() if k not in CAMPOS_NO_PUBLICAR}
            registro["filaExcel"] = n
            rows.append(registro)
        if len(rows) < 10:
            raise ValueError("Solo se detectaron %d registros. Se bloqueó la publicación para evitar un reemplazo accidental." % len(rows))
        ids = [r["id"] for r in rows]
        if not all(ids) or len(ids) != len(set(ids)):
            raise ValueError("Hay números de registro vacíos o repetidos; corrige la columna B antes de publicar.")
        return rows
    finally:
        libro.close()


def gh_api(endpoint, *, payload=None):
    if shutil.which("gh") is None:
        raise RuntimeError("No está instalado GitHub CLI. Instálalo desde https://cli.github.com/ y ejecuta gh auth login.")
    comando = ["gh", "api", endpoint, "-H", "Accept: application/vnd.github+json"]
    archivo_temporal = None
    try:
        if payload is not None:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json", delete=False) as f:
                json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
                archivo_temporal = f.name
            comando.extend(["--method", "PUT", "--input", archivo_temporal])
        res = subprocess.run(comando, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode:
            raise RuntimeError(res.stderr.strip() or "Error de autenticación GitHub. Ejecuta: gh auth login")
        return json.loads(res.stdout)
    finally:
        if archivo_temporal:
            Path(archivo_temporal).unlink(missing_ok=True)


def main():
    origen = seleccionar_archivo()
    if origen is None:
        print("Operación cancelada; no se modificaron datos.")
        return
    print("Leyendo y comprobando:", origen.name)
    rows = convertir_excel(origen)
    print("Registros válidos:", len(rows))
    actual = gh_api(f"repos/{REPO}/contents/{DEST}?ref=main")
    sha = actual.get("sha")
    if not sha:
        raise RuntimeError("No se encontró la base central en GitHub.")
    # Obtener la cantidad anterior, cuando el archivo es pequeño.
    try:
        previous = json.loads(base64.b64decode(actual["content"]).decode("utf-8"))
        print("Registros publicados anteriormente:", len(previous.get("records", [])))
    except (KeyError, ValueError, UnicodeDecodeError):
        pass
    answer = input("¿Publicar estos datos para todas las personas que consulten el enlace? [s/N]: ").strip().lower()
    if answer not in ("s", "si", "sí"):
        print("Cancelado, sin cambios en el repositorio.")
        return
    documento = {
        "schemaVersion": 1,
        "publishedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "recordCount": len(rows),
        "records": rows,
    }
    content = base64.b64encode(json.dumps(documento, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii")
    payload = {
        "message": f"Publicar seguimiento SUNARP: {len(rows)} registros",
        "content": content,
        "sha": sha,
        "branch": "main",
    }
    gh_api(f"repos/{REPO}/contents/{DEST}", payload=payload)
    print()
    print("PUBLICACIÓN CONFIRMADA EN GITHUB.")
    print("Registros publicados:", len(rows))
    print("La página actualizará su consulta de forma automática cuando esté abierta.")
    print("Enlace: https://abastecimiento012-rgb.github.io/sunarp-seguimiento-2026/")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError) as exc:
        print("\nERROR:", exc)
        sys.exit(1)
