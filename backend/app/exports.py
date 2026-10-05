from io import BytesIO
from openpyxl import Workbook
from zipfile import ZipFile,BadZipFile
from xml.etree import ElementTree as ET
def payroll_xlsx(rows):
    wb=Workbook(); ws=wb.active; ws.title="Зарплата"
    headers=["Сотрудник","Должность","Начислено","НДФЛ","Удержания","К выплате","Взносы работодателя"]
    ws.append(headers)
    for r in rows: ws.append([r.get(h,"") for h in headers])
    out=BytesIO(); wb.save(out); out.seek(0); return out
def inspect_1c_archive(data):
    try:
        with ZipFile(BytesIO(data)) as z:
            names=z.namelist(); xml_files=[n for n in names if n.lower().endswith(".xml")]; summaries=[]
            for name in xml_files[:50]:
                raw=z.read(name)
                try: root=ET.fromstring(raw); summaries.append({"file":name,"root":root.tag,"size":len(raw)})
                except ET.ParseError: summaries.append({"file":name,"root":None,"size":len(raw),"xml_error":True})
            return {"type":"zip","files":names,"xml":summaries}
    except BadZipFile: raise ValueError("Файл не является корректным ZIP-архивом 1С")
