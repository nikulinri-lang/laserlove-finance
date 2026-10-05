from io import BytesIO
from zipfile import ZipFile, BadZipFile
from xml.etree import ElementTree as ET
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
import posixpath


def payroll_xlsx(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Зарплата"
    headers = ["Сотрудник", "Должность", "Начислено", "НДФЛ", "Удержания", "К выплате", "Взносы", "Стоимость работодателя"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(h, "") for h in headers])
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 22
    ws.freeze_panes = "A2"
    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return out


def _safe_zip_name(name: str) -> bool:
    p = name.replace("\\", "/")
    return not (p.startswith("/") or p.startswith("../") or "/../" in p or ":" in p.split("/")[0])


def inspect_1c_archive(data: bytes):
    try:
        with ZipFile(BytesIO(data)) as z:
            names = z.namelist()
            unsafe = [n for n in names if not _safe_zip_name(n)]
            if unsafe:
                raise ValueError("Архив содержит небезопасные пути и не может быть импортирован")
            xml_files = [n for n in names if n.lower().endswith(".xml")]
            summaries = []
            for name in xml_files[:100]:
                raw = z.read(name)
                try:
                    root = ET.fromstring(raw)
                    summaries.append({
                        "file": name,
                        "root": root.tag,
                        "size": len(raw),
                        "children": len(root),
                    })
                except ET.ParseError:
                    summaries.append({"file": name, "root": None, "size": len(raw), "xml_error": True})
            return {
                "type": "zip",
                "files_count": len(names),
                "xml_count": len(xml_files),
                "files": names[:500],
                "xml": summaries,
                "ready_for_mapping": bool(xml_files) and not unsafe,
            }
    except BadZipFile:
        raise ValueError("Файл не является корректным ZIP-архивом 1С")
