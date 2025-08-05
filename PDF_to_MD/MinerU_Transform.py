from Config.Settings import setting
from openai import OpenAI
import os
import time
import requests

class PDFProcessor:
    def __init__(self, token):
        self.token = setting.Designer['MinerU']['API']
        self.headers = {
            'Authorization': f'Bearer {token}'
        }
        self.file_path = setting.USER['file_path']
        self.subject = setting.USER['subject']

    def upload_file(self):
        print(f"Uploading: {os.path.basename(self.file_path)}")

        try:
            with open(self.file_path, 'rb') as f:
                response = requests.post(
                    'https://tmpfiles.org/api/v1/upload',
                    files={'file': f}
                )
            if response.status_code == 200:
                result = response.json()
                url = result['data']['url']
                direct_url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                print(f"Successfully upload: {direct_url}")
                return direct_url
        except Exception as e:
            print(f"X Upload failed: {e}")
            return None

    def process_pdf(self):
        pdf_url = self.upload_file(self.file_path)
        if not pdf_url:
            return None

        print("Creating compiling task...")
        task_url = 'https://mineru.net/api/v4/extract/task'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        if self.subject == 'ENG':
            lag = 'en'
        else:
            lag = 'cn'

        data = {
            'url': pdf_url,
            'is_ocr': True,
            'enable_formula': True,
            'enable_table': True,
            'language': lag
        }

        response = requests.post(task_url, headers=headers, json=data)
        result = response.json()
        if result['code'] != 0:
            print(f"X Failed to create task: {result['msg']}")
            return None
        task_id = result['data']['task_id']
        print(f"V task id: {task_id}")
        print("Z Waiting to process...")
        while True:
            time.sleep(5)
            status_url = f'https://mineru.net/api/v4/extract/task/{task_id}'
            status_response = requests.get(status_url, headers=headers)
            status_data = status_response.json()
            state = status_data['data']['state']
            
            if state == 'done':
                zip_url = status_data['data']['full_zip_url']
                print(f"V 处理完成！")
                print(f"@ 下载地址: {zip_url}")
                self.download_result(zip_url, task_id)
                return status_data
            
            elif state == 'failed':
                print(f"X 处理失败: {status_data['data']['err_msg']}")
                return None
            
            elif state == 'running':
                progress = status_data['data'].get('extract_progress', {})
                extracted = progress.get('extracted_pages', 0)
                total = progress.get('total_pages', 0)
                print(f"T Processing page: {extracted}/{total}")


    def download_result(self, zip_url, task_id):
        save_path = f''



