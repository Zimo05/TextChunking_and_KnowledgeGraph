
import re
from Config.Settings import setting
from PDF_to_MD.Check_File_Type import file_judge

class Node:
    def __init__(self, title, level, parent=None):
        self.title = title 
        self.level = level
        self.content = ""
        self.children = []
        self.parent = parent  # Add parent reference
    
    def add_child(self, node):
        node.parent = self  # Set the parent when adding a child
        self.children.append(node)
    
    def add_content(self, text):
        if self.content:
            self.content += "\n" + text
        else:
            self.content = text

class MD_parser:
    def __init__(self):
        self.input_path = setting.Designer['Storage']['PDF_to_MD']['MD_file']
        
    def parse_markdown_to_linked_lists(self):
        with open(self.input_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read() 

        lines = markdown_text.split('\n') 
        roots = []
        stack = [] 
        for line in lines:
            if line.strip() == '':
                continue
            match = re.match(r'^(#+)\s*(.*)', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                node = Node(title, level)
                while stack and stack[-1].level >= level:
                    stack.pop()
                if not stack:  # 根节点
                    roots.append(node)
                else:  # 子节点
                    stack[-1].add_child(node)
                stack.append(node)
            else:
                if stack: 
                    stack[-1].add_content(line)
        return roots

Parser = MD_parser()
BookTree = Parser.parse_markdown_to_linked_lists()