from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
import os

PDF_FOLDER = "corpus"
PDFS_A_PROCESAR = [
    "ayudas_20-21.pdf",
    "ayudas_21-22.pdf",
    "ayudas_22-23.pdf",
    "ayudas_23-24.pdf",
    "ayudas_24-25.pdf",
    "ayudas_25-26.pdf"
]

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model
pipeline_options.do_ocr = True


doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# source = r"C:\Users\miria\OneDrive\Documentos\universidad\MASTER\Master 2024-2025\APLN\REPO\APLN2025\corpus\ayudas_24-25.pdf"
for pdf_file in PDFS_A_PROCESAR:
    source = os.path.join(PDF_FOLDER, pdf_file)
    result = doc_converter.convert(source)

    # Guardar texto limpio en un archivo
    output_file = os.path.join(PDF_FOLDER, pdf_file.replace('.pdf', '_docling.txt'))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.document.export_to_markdown())

    print(f"[EXITO] Texto limpio guardado en '{output_file}'")
