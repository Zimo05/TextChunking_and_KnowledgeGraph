import re
from Config.Settings import setting
import requests
import json
import zipfile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class correction:
    def __init__(self, mineru_zip_path, file_name, file_judge):
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
        extract_dir = f'{self.extract_dir_base}/{file_type}/{self.subject}/{file_name_base}'
        with zipfile.ZipFile(self.mineru_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        md_content_path = f'{extract_dir}/Updated_MD.md'
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
            elif self.subject == 'MAT':
                modified_content, md_content_path = self._process_math()
                

        else:
            corrected_md_file, md_content_path = self._process_paper(corrected_md_file)

        with open(md_content_path, 'w', encoding='utf-8') as file:
            file.write(corrected_md_file)

        return corrected_md_file, md_content_path
    
    def _process_book(self):      
        content, md_content_path = self.pre_processing()
        content = content.replace('# 人民教育出版社', '')
        book_structure, left_content = self._process_index(content)
        lesson_titles = []
        for key, value in book_structure.items():
            for item in value:
                if re.search(r'第\s*([一二三四五六七八九十\d]+)\s*(?:节|课)', item):
                    lesson_titles.append(item.strip())
        chapter_pattern = re.compile(
            r'^(?:#\s*)?(第[一二三四五六七八九十\d]+(?:单元|章)\s*[^\n]+)(?:\s|$)',
            re.MULTILINE
        )
        lesson_titles = []
        for key, value in book_structure.items():
            for item in value:
                if re.search(r'第\s*([一二三四五六七八九十\d]+)\s*(?:节|课)', item):
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
                    is_lesson = similarities.max() > 0.5
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
    
    def _process_index(self, text):
        book_structure = {}
        prev_chapter_num = 0
        chapter_pattern = re.compile(
            r'^(?:#\s*)?(第[一二三四五六七八九十百千万\d]+(?:单元|章)\s*[^\n]+)(?:\s|$)',
            re.MULTILINE
        )
        def chinese_to_arabic(chinese_num):
            mapping = {'一':1, '二':2, '三':3, '四':4, '五':5,
                    '六':6, '七':7, '八':8, '九':9, '十':10, 
                     '十一': 11, '十二':12, '十三':13 }
            if chinese_num in mapping:
                return mapping[chinese_num]
            try:
                return int(chinese_num)
            except ValueError:
                return 0
        processed_text = re.sub(r'(第[\d一二三四五六七八九十百千万]+章)', r'\n\1', text)
        chapter_matches = list(chapter_pattern.finditer(processed_text))
        print(f"Found {len(chapter_matches)} chapter matches")
        for i, match in enumerate(chapter_matches):
            chapter_title = match.group(1).strip()
            print(f"Processing chapter: {chapter_title}")
            chapter_num_match = re.search(r'第([一二三四五六七八九十百千万\d]+)(?:单元|章)', chapter_title)
            if chapter_num_match:
                chapter_num_str = chapter_num_match.group(1)
                chapter_num = chinese_to_arabic(chapter_num_str)
            else:
                chapter_num = prev_chapter_num + 1
            if chapter_num <= prev_chapter_num:
                break
            prev_chapter_num = chapter_num
            start_pos = match.end()
            end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(processed_text)
            chapter_content = processed_text[start_pos:end_pos].strip()
            lines = [
                line.strip() 
                for line in chapter_content.split('\n') 
                if line.strip() and not line.strip().startswith('![')
            ]
            copy_lines = []
            for entry in lines:
                if len(entry) < 30:
                    copy_lines.append(entry)
            book_structure[chapter_title] = copy_lines
        if book_structure:
            last_chapter = list(book_structure.keys())[-1]
            last_content = book_structure[last_chapter][-1]
            last_content_pos = processed_text.rfind(last_content)
            if last_content_pos != -1:
                last_char_pos = last_content_pos + len(last_content)
            else:
                last_char_pos = len(processed_text)
        else:
            last_char_pos = len(processed_text)
        left_book = text[last_char_pos-5:]

        return book_structure, left_book

    def _process_math(self):
        text, md_content_path = self.pre_processing()
        text = text.replace('# 人民教育出版社', '')
        text = text.replace('．', '.')
        def extract_chapters(text):
            def chinese_to_arabic(chinese_num):
                num_map = {'一':1, '二':2, '三':3, '四':4, '五':5,
                        '六':6, '七':7, '八':8, '九':9, '十':10}
                return num_map.get(chinese_num, 0)
            lines = text.split('\n')
            chapters = []
            current_chapter = None
            chapter_pattern = re.compile(r'第([一二三四五六七八九十]+)章')
            section_pattern = re.compile(r'^#\s*([0-9]+\.[0-9]+|本章小结|.*小结)') 
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                match = chapter_pattern.search(line)
                if match:
                    chapter_num = chinese_to_arabic(match.group(1))
                    if current_chapter is None or chapter_num > current_chapter['number']:
                        if current_chapter:
                            chapters.append(current_chapter)
                        current_chapter = {
                            'number': chapter_num,
                            'title': line,
                            'content': []
                        }
                    else:
                        break
                elif current_chapter is not None:
                    if line.startswith('#'):
                        is_section = section_pattern.search(line) is not None
                        is_chapter = chapter_pattern.search(line) is not None
                        if not (is_section or is_chapter):
                            break
                    current_chapter['content'].append(line)
            if current_chapter:
                chapters.append(current_chapter)
            result = []
            for chap in chapters:
                result.append(chap['title'])
                result.extend(chap['content'])
            return result

        def group_by_chapter(content_list):
            chapters = []
            current_chapter = []
            for item in content_list:
                if re.match(r'第[一二三四五六七八九十]+章', item):
                    if current_chapter:
                        chapters.append(current_chapter)
                    current_chapter = [item]
                else:
                    if not item.startswith('!['):
                        current_chapter.append(item)
            if current_chapter:
                chapters.append(current_chapter)
            return chapters
        result = extract_chapters(text)
        chapter_info = group_by_chapter(result)
        lesson_list = []
        for list in chapter_info:
            lesson_list.extend(list[1:])
        last_content = lesson_list[-1]
        last_content_pos = text.rfind(last_content)
        last_char_pos = last_content_pos + len(last_content)
        left_content = text[last_char_pos:]
        modified_content = adjust_headings(left_content, chapter_info)

        def adjust_headings(left_content, chapter_info):
            left_content = left_content.replace('# \n', '')
            level1_lessons = []
            level2_lessons = []
            special_lessons = []
            for chapter in chapter_info:
                for lesson in chapter[1:]:
                    if re.match(r'^\d+\.\d+\.\d+', lesson): 
                        level2_lessons.append(lesson)
                    elif re.match(r'^\d+\.\d+', lesson):
                        level1_lessons.append(lesson)
                    elif '小结' in lesson or '复习' in lesson:
                        special_lessons.append(lesson)
            vectorizer = TfidfVectorizer(analyzer='char')
            all_lessons = level1_lessons + level2_lessons + special_lessons
            if all_lessons: 
                lesson_vectors = vectorizer.fit_transform(all_lessons)
            lines = left_content.split('\n')
            new_lines = []
            for line in lines:
                line = line.strip()
                if not line.startswith('#'):
                    new_lines.append(line)
                    continue
                if '第' in line and '章' in line:
                    new_lines.append(line)
                    continue
                is_special = False
                if ('小结' or '复习') in line:
                    is_special = True
                if is_special:
                    new_lines.append(f"## {line.replace('#', '')}")
                    continue
                if all_lessons:
                    line_vector = vectorizer.transform([line])
                    similarities = cosine_similarity(line_vector, lesson_vectors)
                    max_sim = similarities.max()
                    max_index = similarities.argmax()
                    
                    if max_sim > 0.5:
                        matched_lesson = all_lessons[max_index]
                        if matched_lesson in level2_lessons:
                            new_line = f"### {line.replace('#', '')}"
                        elif matched_lesson in level1_lessons:
                            new_line = f"## {line.replace('#', '')}"
                        else:
                            new_line = f"## {line.replace('#', '')}" 
                        if re.search(r'^\d+\.\d+\.\d+', new_line.replace('#', '').strip()):
                            new_line = f"### {line.replace('#', '')}"
                        new_lines.append(new_line)
                        continue
                    if re.search(r'^\d+\.\d+\.\d+', line):
                        new_lines.append(f"### {line.replace('#', '')}")
                        continue
                    new_lines.append(f"#### {line.replace('#', '')}")
            return '\n'.join(new_lines)

        return modified_content, md_content_path
    
correction = correction()
content, md_content_path = correction.main()
