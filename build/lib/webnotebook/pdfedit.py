"""Модуль с функциями для работы с пдф"""

from pypdf import PdfMerger
import PyPDF2
from PIL import Image
import os
import pypdfium2 as pdfium


def convert(path):
    """
    Перводит pdf файл в png.

    :param path: (str) путь до исходника pdf.
    :return: (str) путь до полученного png.
    """
    pdf = pdfium.PdfDocument(path)
    path_parts = path.split('/')
    new_path = "/".join(path_parts[:-1]) + "/" + path_parts[-1].split('.')[0]
    os.mkdir(new_path)
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        pil_image = page.render(scale=300 / 72).to_pil()
        pil_image.save(new_path + '/page' + str(page_number + 1) + '.png')

    return new_path


def connect_pdf(path_to_dir):
    """
    Склеивает все pdf файлы, имеющиеся в директории в один.

    :param path_to_dir: (str) путь до директории с pdf файлами.
    :return: путь до полученного pdf.
    """
    path_to_file = os.path.join(path_to_dir, os.path.basename(path_to_dir).split('_')[-1] + "_00.pdf")
    os.remove(path_to_file)

    pdfs = sorted([f for f in os.listdir(path_to_dir) if os.path.isfile(os.path.join(path_to_dir, f))])
    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(os.path.join(path_to_dir, pdf))

    merger.write(path_to_file)
    merger.close()

    return path_to_file


def add_page(path_to_pdf, path_to_pic, num):
    """
    Вставляет страницу в pdf файл.

    :param path_to_pdf: (str) путь до исходника pdf.
    :param path_to_pic: (str) путь до png файла, содержащего вставляемую страницу.
    :param num: (int) номер страницы, на который необходимо вставить png файл.
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


def page_delete(path_to_pdf, num):
    """
    Удаляет страницу из pdf файла.

    :param path_to_pdf: (str) путь до исходника pdf.
    :param num: (int) номер страницы, которую нужно удалить.
    """
    file = open(path_to_pdf, 'rb')
    readpdf = PyPDF2.PdfReader(file)
    totalpages = len(readpdf.pages)
    file.close()

    merger = PdfMerger()
    merger.append(path_to_pdf, pages=(0, num - 1))
    merger.append(path_to_pdf, pages=(num, totalpages))

    os.remove(path_to_pdf)

    merger.write(path_to_pdf)
    merger.close()

    connect_pdf("/".join(path_to_pdf.split('/')[:-1]))
