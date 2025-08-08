import re
class Node:
    def __init__(self, title, level, parent=None):
        self.title = title 
        self.level = level
        self.content = ""
        self.children = []
        self.parent = parent
    
    def add_child(self, node):
        node.parent = self
        self.children.append(node)
    
    def add_content(self, text):
        if self.content:
            self.content += "\n" + text
        else:
            self.content = text

class MD_parser:
    def __init__(self, md_content_path):
        # setting.Designer['Storage']['PDF_to_MD']['MD_file']
        self.input_path = md_content_path
        
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
                if not stack:
                    roots.append(node)
                else:
                    stack[-1].add_child(node)
                stack.append(node)
            else:
                if stack: 
                    stack[-1].add_content(line)
        return roots
