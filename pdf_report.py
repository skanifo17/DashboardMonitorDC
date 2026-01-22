from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def generate_pdf(inv, util, filename="Executive_Report.pdf"):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    elements.append(Paragraph("EXECUTIVE CONTROL TOWER REPORT", styles["Title"]))
    elements.append(Paragraph("Inventory Summary", styles["Heading2"]))

    data = [["Barang","Gudang","Stok","Days Cover"]]
    for _,r in inv.iterrows():
        data.append([
            r["Nama Barang"],
            r["Gudang"],
            int(r["Stok Karton"]),
            round(r["Days Cover"],1)
        ])

    elements.append(Table(data))
    doc.build(elements)
