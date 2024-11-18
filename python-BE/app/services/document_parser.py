from unstructured.partition.pdf import partition_pdf

def parse_document(file_path):
    elements = partition_pdf(filename=file_path)
    text_content = "\n".join([element.text for element in elements])
    return text_content
