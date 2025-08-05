import fitz
import os
import re
from pdf2image import convert_from_path
import tempfile
import camelot
from camelot.core import TableList

def pdf_to_markdown(pdf_path, output_md, image_dir, dpi=500, table_flavor='lattice'):
    os.makedirs(image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    markdown_content = []
    image_count = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir, fmt='png')
        
        for page_num, (page, pil_image) in enumerate(zip(doc, images)):
            markdown_content.append(f"\n# Page {page_num+1}\n")
            
            # 1. 先处理图片
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                image_ext = base_image["ext"]
                image_filename = f"{image_dir}/image_{page_num+1}_{img_index}.{image_ext}"
                with open(image_filename, "wb") as f:
                    f.write(image_bytes)
                
                img_width = base_image["width"]
                img_height = base_image["height"]
                markdown_content.append(f"\n![Image {image_count}]({image_filename}) {{width={img_width}px, height={img_height}px}}\n")
                image_count += 1
            try:
                tables = camelot.read_pdf(
                    pdf_path,
                    pages=str(page_num+1),
                    flavor=table_flavor,
                    suppress_stdout=True
                )
                
                if isinstance(tables, TableList) and len(tables) > 0:
                    markdown_content.append(f"\n## 表格 (共 {len(tables)} 个)\n")
                    for i, table in enumerate(tables, 1):
                        try:
                            markdown_table = table.df.to_markdown(index=False)
                            markdown_content.append(f"\n### 表格 {i}\n")
                            markdown_content.append(f"```markdown\n{markdown_table}\n```\n")
                        except Exception as e:
                            print(f"第 {page_num+1} 页表格 {i} 转换失败: {str(e)}")
                            continue
                    markdown_content.append("\n---\n")
                    continue
            except Exception as e:
                print(f"第 {page_num+1} 页表格提取失败: {str(e)}")
            
            text = page.get_text("text")
            if text.strip():
                text = text.strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                formatted_text = []
                
                for line in lines:
                    # 识别标题
                    if line.isupper() and len(line.split()) < 5: 
                        formatted_text.append(f"## {line}")
                    # 识别列表项
                    elif line.startswith(('•', '-', '◦', '∙')):
                        formatted_text.append(f"- {line[1:].strip()}")
                    # 识别数字列表
                    elif re.match(r'^\d+[\.\)]', line):
                        formatted_text.append(f"1. {line.split(maxsplit=1)[1] if ' ' in line else ''}")
                    else:
                        formatted_text.append(line)
                
                markdown_content.append("\n".join(formatted_text))

                markdown_content = re.sub(r'^# Page \d+$', '', "\n".join(markdown_content), flags=re.MULTILINE)

    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(markdown_content))

pdf_path = './教材/高中教材人教版/高中思想政治必修2_经济与社会.pdf'
output_path = './PDF_to_MD/Books/高中思想政治必修2_经济与社会高中思想政治必修2_经济与社会.md'
image_dir = './PDF_to_MD/Books/高中思想政治必修2_经济与社会/Image'

pdf_to_markdown(pdf_path, output_path, image_dir, dpi=500)


# 副本：
import fitz 
import os
import re
from pdf2image import convert_from_path
import tempfile

def pdf_to_markdown(pdf_path, output_md, image_dir, dpi=300):
    os.makedirs(image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    markdown_content = []
    image_count = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir, fmt='png')
        
        for page_num, (page, pil_image) in enumerate(zip(doc, images)):            
            # 1. 先处理图片
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                image_ext = base_image["ext"]
                image_filename = f"{image_dir}/image_{page_num+1}_{img_index}.{image_ext}"
                with open(image_filename, "wb") as f:
                    f.write(image_bytes)
                
                img_width = base_image["width"]
                img_height = base_image["height"]
                markdown_content.append(f"\n![Image {image_count}]({image_filename}) {{width={img_width}px, height={img_height}px}}\n")
                image_count += 1
            
            # 2. 处理文本内容
            text = page.get_text("text")
            if text.strip():
                text = text.strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                formatted_text = []
                
                for line in lines:
                    # 识别标题
                    if line.isupper() and len(line.split()) < 5: 
                        formatted_text.append(f"## {line}")
                    # 识别列表项
                    elif line.startswith(('•', '-', '◦', '∙')):
                        formatted_text.append(f"- {line[1:].strip()}")
                    # 识别数字列表
                    elif re.match(r'^\d+[\.\)]', line):
                        formatted_text.append(f"1. {line.split(maxsplit=1)[1] if ' ' in line else ''}")
                    else:
                        formatted_text.append(line)
                
                markdown_content.append("\n".join(formatted_text))

    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(markdown_content))

pdf_path = './教材/高中教材人教版/高中思想政治必修2_经济与社会.pdf'
output_path = './PDF_to_MD/Books/高中思想政治必修2_经济与社会高中思想政治必修2_经济与社会.md'
image_dir = './PDF_to_MD/Books/高中思想政治必修2_经济与社会/Image'

pdf_to_markdown(pdf_path, output_path, image_dir, dpi=500)



import fitz  # PyMuPDF
import os
import re
from typing import List, Dict
from pdf2image import convert_from_path
import tempfile
import camelot
from camelot.core import TableList

def is_math_formula(text: str, font_name: str = "") -> bool:
    """
    判断文本是否为数学公式
    :param text: 待检测文本
    :param font_name: 字体名称（某些PDF用特殊字体表示公式）
    :return: True if it's a math formula
    """
    # 检测LaTeX语法（如 $\frac{a}{b}$）
    if re.search(r'\$[^$]+\$', text):
        return True
    
    # 检测常见数学符号
    math_symbols = r'[∑∫∏√∞∩∪α-ω→⇌∂∇]|\\[a-zA-Z]+'
    if re.search(math_symbols, text):
        return True
    
    # 检测数学字体（如 Cambria Math, STIX）
    if "math" in font_name.lower():
        return True
    
    return False

def extract_math_formulas(page) -> List[Dict]:
    """
    提取页面中的数学公式
    :param page: fitz.Page 对象
    :return: 公式列表，每个公式包含文本和位置信息
    """
    formulas = []
    blocks = page.get_text("dict")["blocks"]  # 获取结构化文本
    
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    font = span["font"]
                    if is_math_formula(text, font):
                        formulas.append({
                            "text": text,
                            "bbox": span["bbox"],  # 公式的位置（用于后续处理）
                            "font": font
                        })
    return formulas

def process_text_content(text: str, formulas: List[Dict] = None) -> str:
    """
    处理文本内容，识别标题、列表项，并处理数学公式
    :param text: 原始文本
    :param formulas: 数学公式列表
    :return: 格式化后的Markdown文本
    """
    if not text.strip():
        return ""
    
    text = text.strip()
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    formatted_text = []
    
    for line in lines:
        # 替换数学公式
        if formulas:
            for formula in formulas:
                if formula["text"] in line:
                    line = line.replace(formula["text"], f" ${formula['text']}$ ")
        
        # 识别标题
        if line.isupper() and len(line.split()) < 5: 
            formatted_text.append(f"## {line}")
        # 识别列表项
        elif line.startswith(('•', '-', '◦', '∙')):
            formatted_text.append(f"- {line[1:].strip()}")
        # 识别数字列表
        elif re.match(r'^\d+[\.\)]', line):
            formatted_text.append(f"1. {line.split(maxsplit=1)[1] if ' ' in line else ''}")
        else:
            formatted_text.append(line)
    
    return "\n".join(formatted_text)

def pdf_to_markdown_with_all_features(pdf_path: str, output_md: str, image_dir: str, dpi: int = 500, table_flavor: str = 'lattice'):
    os.makedirs(image_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    markdown_content = []
    image_count = 0
    
    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(pdf_path, dpi=dpi, output_folder=temp_dir, fmt='png')
        
        for page_num, (page, pil_image) in enumerate(zip(doc, images)):
            markdown_content.append(f"\n# Page {page_num+1}\n")
            
            # 提取数学公式
            formulas = extract_math_formulas(page)
            
            # 处理图片
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                image_ext = base_image["ext"]
                image_filename = f"{image_dir}/image_{page_num+1}_{img_index}.{image_ext}"
                with open(image_filename, "wb") as f:
                    f.write(image_bytes)
                
                img_width = base_image["width"]
                img_height = base_image["height"]
                markdown_content.append(f"\n![Image {image_count}]({image_filename}) {{width={img_width}px, height={img_height}px}}\n")
                image_count += 1
            
            # 3. 处理表格
            try:
                tables = camelot.read_pdf(
                    pdf_path,
                    pages=str(page_num+1),
                    flavor=table_flavor,
                    suppress_stdout=True
                )
                
                if isinstance(tables, TableList) and len(tables) > 0:
                    markdown_content.append(f"\n## 表格 (共 {len(tables)} 个)\n")
                    for i, table in enumerate(tables, 1):
                        try:
                            markdown_table = table.df.to_markdown(index=False)
                            markdown_content.append(f"\n### 表格 {i}\n")
                            markdown_content.append(f"```markdown\n{markdown_table}\n```\n")
                        except Exception as e:
                            print(f"第 {page_num+1} 页表格 {i} 转换失败: {str(e)}")
                            continue
                    markdown_content.append("\n---\n")
            except Exception as e:
                print(f"第 {page_num+1} 页表格提取失败: {str(e)}")
            
            # 4. 处理文本内容
            text = page.get_text("text")
            processed_text = process_text_content(text, formulas)
            if processed_text:
                markdown_content.append(processed_text)
    
    # 清理多余的分页标记
    final_content = re.sub(r'^# Page \d+$', '', "\n".join(markdown_content), flags=re.MULTILINE)
    
    # 写入Markdown文件
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(final_content)

# 使用示例
pdf_path = "./PDF_to_MD/2023广东化学-试题.pdf"
output_path = "./PDF_to_MD/Papers/2023广东化学-试题/2023广东化学-试题.md"
image_dir = "./PDF_to_MD/Papers/2023广东化学-试题/Image"

pdf_to_markdown_with_all_features(pdf_path, output_path, image_dir, dpi=500)