from pypdf import PdfMerger
import PyPDF2
from PIL import Image
import os
import pypdfium2 as pdfium


def convert(path):
    """
    Convert original pdf to png.

    :param path: (str) path to original pdf.
    :return: (str) path to directory with png.
    """
    pdf = pdfium.PdfDocument(path)
    path_parts = path.split('/')
    new_path = "/".join(path_parts[:-1]) + "/" + path_parts[-1].split('.')[0]
    os.mkdir(new_path)
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        pil_image = page.render(scale=300/72).to_pil()
        pil_image.save(new_path + '/page' + str(page_number + 1) + '.png')

    return new_path


def connect_pdf(path_to_dir):
    """
    Combines all the pdf's into one.

    :param path_to_dir: (str) path to directory with pdfs.
    :return: path to new pdf.
    """
    path_to_file = path_to_dir + path_to_dir.split('/')[-2].split("_")[-1] + "_00.pdf"
    os.remove(path_to_file)

    pdfs = [f for f in os.listdir(path_to_dir) if os.path.isfile(os.path.join(path_to_dir, f))]
    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(path_to_dir + pdf)

    merger.write(path_to_file)
    merger.close()

    return path_to_file


def add_page(path_to_pdf, path_to_pic, num):
    """
    Insert page in original pdf.

    :param path_to_pdf: (str) path to original pdf.
    :param path_to_pic: (str) path to the png to be inserted.
    :param num: (int) the number under which you want to insert the png.
    """

    image_1 = Image.open(path_to_pic)
    im_1 = image_1.convert('RGB')
    pdf_path_parts = path_to_pdf.split('/')
    pic_name = path_to_pic.split('/')[-1].split('.')[0]
    pic_pdf_path = "/".join(pdf_path_parts[:-1]) + '/' + pic_name + '.pdf'
    im_1.save(pic_pdf_path)

    file = open(path_to_pdf, 'rb')
    readpdf = PyPDF2.PdfReader(file)
    totalpages = len(readpdf.pages)
    file.close()

    merger = PdfMerger()
    merger.append(path_to_pdf, pages=(0, num - 1))
    merger.append(pic_pdf_path)
    merger.append(path_to_pdf, pages=(num - 1, totalpages))

    os.remove(path_to_pdf)
    os.remove(pic_pdf_path)
    os.remove(path_to_pic)

    merger.write(path_to_pdf)
    merger.close()

    connect_pdf("/".join(path_to_pdf.split('/')[:-1]))
