import re
from Config.Settings import setting
import requests
import json
from PDF_to_MD.Check_File_Type import file_name, file_judge
from PDF_to_MD.MinerU_Transform import mineru_zip_path
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class correction:
    def __init__(self):
        self.api = setting.Designer['DIFY']['DIFY_Correction_API']
        self.user = setting.Designer['DIFY']['DIFY_USER']
        self.url = setting.Designer['DIFY']['DIFY_URL']
        self.file_judge = file_judge
        self.file_name = file_name
        self.mineru_zip_path = mineru_zip_path
        self.extract_dir_base = setting.Designer['Storage']['PDF_to_MD']['MD_file']
        self.subject = setting.USER['subject']

    def pre_processing(self):
        file_type = self.file_judge['file_type']
        file_name_base = self.file_name
        file_name_base = file_name_base.replace('.pdf', '')
        extract_dir = f'{self.extract_dir_base}/{file_type}/{self.subject}/{file_name_base}/'
        with zipfile.ZipFile(self.mineru_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        md_content_path = f'{extract_dir}/full.md'
        with open(md_content_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content, md_content_path
    
    def correct_markdown_files(self, content):
        headers = {
            "Authorization": f"Bearer {self.api}",
            "Content-Type": 'application/json'
        }
        request_data = {
                    "inputs": {
                        "Chunk": content, 
                    },
                    "user": self.user
                }
        
        response = requests.post(self.url, headers=headers, json=request_data)
        response_text = response.text
        response_json = json.loads(response_text)
        text = response_json['data']['outputs']['Corrected']

        return text
    
    def main(self):
        corrected_md_file = ''
        if self.file_judge['file_type'] == 'Book':
            if self.subject in ['POL', 'HIS', 'BIO', 'GEO']:
                corrected_md_file, md_content_path = self._process_book()
            else:
                corrected_md_file, md_content_path = self._process_book()

        else:
            corrected_md_file, md_content_path = self._process_paper(corrected_md_file)

        with open(md_content_path, 'w', encoding='utf-8') as file:
            file.write(corrected_md_file)

        return corrected_md_file, md_content_path
    def _process_book(self):      
        content, md_content_path = self.pre_processing()
        content = content.replace(' ', '')   
        content = content.replace('# 人民教育出版社', '')
        book_structure = self._process_index(content)
        last_chapter = list(book_structure.keys())[-1]
        last_section = book_structure[last_chapter][-1]
        last_section_pos = content.rfind(last_section)
        last_char_pos = last_section_pos + len(last_section) - 1
        left_content = content[last_char_pos:]

        lesson_titles = []
        for key, value in book_structure.items():
            for item in value:
                if re.search(r'^第([一二三四五六七八九十\d]+)(?:节|课)\b', item):
                    lesson_titles.append(item.strip())

        chapter_pattern = re.compile(
            r'^#\s*第[一二三四五六七八九十\d]+(?:单元|章)[\s　]*[^\s]', 
            re.UNICODE
        )
        lesson_titles = []
        for key, value in book_structure.items():
            for item in value:
                if re.search(r'^第([一二三四五六七八九十\d]+)(?:节|课)\b', item):
                    lesson_titles.append(item.strip())

        modified_lines = []
        for line in left_content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                heading_text = re.sub(r'^#+\s*', '', line)
                is_chapter = bool(chapter_pattern.match(line))
                is_lesson = False
                if lesson_titles:
                    vectorizer = TfidfVectorizer(analyzer='char')
                    corpus = lesson_titles + [heading_text]
                    vectorizer.fit(corpus)
                    lesson_vec = vectorizer.transform(lesson_titles)
                    heading_vec = vectorizer.transform([heading_text])
                    similarities = cosine_similarity(heading_vec, lesson_vec)[0]
                    is_lesson = similarities.max() > 0.7

                if is_chapter:
                    modified_lines.append(line)
                elif is_lesson:
                    if line.startswith('# '):
                        modified_lines.append(line.replace('# ', '## ', 1))
                    elif not line.startswith('##'):
                        modified_lines.append('## ' + heading_text)
                    else:
                        modified_lines.append(line)
                else:
                    if line.startswith('# '):
                        modified_lines.append(line.replace('# ', '### ', 1))
                    elif line.startswith('## '):
                        modified_lines.append(line.replace('## ', '### ', 1))
                    else:
                        modified_lines.append('### ' + heading_text)
            else:
                modified_lines.append(line)

        modified_text = '\n'.join(modified_lines)

        with open(md_content_path, 'w', encoding='utf-8') as f:
            f.write(modified_text)

        return modified_text, md_content_path

    def _process_paper(self, corrected_md_file):

        content, md_content_path = self.pre_processing()
        content = content.replace('．', '.')
        content = content.replace('（', '(')
        content = content.replace('）', ')')
        
        processed_text = re.sub(r'(\d+\.)(\S)', r'\1 \2', content)
        processed_text = re.sub(r'^(\d+\.)', r'## \1', processed_text, flags=re.MULTILINE)

        sections = re.split(r'(# [一二三四五六七八九十]+、)', processed_text)

        result = []
        for i in range(0, len(sections), 2):
            if i + 1 < len(sections):
                result.append(sections[i] + sections[i+1])
            else:
                result.append(sections[i])
        for idx, sec in enumerate(result, 1):
            modified_md = self.correct_markdown_files(sec.strip(), md_content_path)
            corrected_md_file = corrected_md_file + '\n' + modified_md

        return corrected_md_file, md_content_path
    
    def _process_index(self, book):
        book_structure = {}
        prev_chapter_num = 0
        chapter_pattern = re.compile(
            r'^(?:#\s*)?(第[一二三四五六七八九十\d]+(?:单元|章)\s*[^\n]+)(?:\s|$)', 
            re.MULTILINE
        )
        def mixed_to_arabic(num_str):
            chinese_map = {'一':1, '二':2, '三':3, '四':4, '五':5,
                        '六':6, '七':7, '八':8, '九':9, '十':10}
            if num_str.isdigit():
                return int(num_str)
            elif all(c in chinese_map for c in num_str):
                if len(num_str) == 1:
                    return chinese_map[num_str]
                elif num_str == '十一':
                    return 11
                else:
                    return sum(chinese_map[c] for c in num_str)
            return 
        chapter_matches = list(chapter_pattern.finditer(book))
        for i, match in enumerate(chapter_matches):
            chapter_title = match.group(1).strip()
            num_match = re.search(r'第([一二三四五六七八九十\d]+)(?:单元|章)', chapter_title)
            if num_match:
                chapter_num = mixed_to_arabic(num_match.group(1))
            else:
                chapter_num = prev_chapter_num + 1
            if chapter_num <= prev_chapter_num:
                break
            prev_chapter_num = chapter_num
            start_pos = match.end()
            end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(book)
            chapter_content = book[start_pos:end_pos].strip()
            sections = [
                line.strip() for line in chapter_content.split('\n') 
                if line.strip() and not line.strip().startswith(('![', '<img'))
            ]
            book_structure[chapter_title] = sections
        for chapter, sections in book_structure.items():
            new_sections = []
            for section in sections:
                section_no_digits = re.sub(r'\d', '', section).strip()
                new_sections.append(section_no_digits)
            book_structure[chapter] = new_sections
        return book_structure
        

# 做出可以识别出
correction = correction()
content, md_content_path = correction.main()
