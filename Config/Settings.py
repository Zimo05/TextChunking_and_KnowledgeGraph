class settings:
    Designer = {
        'DIFY': {
            'DIFY_ENG_Paper_Parser_API': 'app-poOfJ4k822C9y4kDOdP8eGLb',
            'DIFY_Entity_Linking_API': 'app-hMrsW6S7ECwARMQORH2tS5oU',
            'DIFY_Entity_Book_Linking_API': 'app-ICVmh2I94iQ6hFxkvJ7wevLX',
            'DIFY_Correction_API': '',
            'DIFY_URL': "http://localhost/v1/workflows/run",
            'DIFY_USER': 'Zimo'
            },
        'MinerU_Token': 'eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI5MDMwOTkwMCIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc1NDQ2OTM0NywiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiYmJmYjA5MjAtYjE2OS00ZmFiLThjYWItZGRkM2RmNzhiYmViIiwiZW1haWwiOiIiLCJleHAiOjE3NTU2Nzg5NDd9.ltjH0meHyflsxezRgr3nKfoT2eRPEsbq04Nl4izynXGaQJ7awEcXBRbioslzsRI3Iqi-EWXewg9a6SX1YdHhog',
        'NEO4J': {
            'NEO4J_URL': '',
            'NEO4J_USERNAME': '',
            'NEO4J_PASSWORD': ''
            },
        'ES': {
            'ES_URL': '',
            'ES_USER': '',
            'ES_PASSWORD': ''
            },
        'DEEPSEEK': {
            'API': 'sk-16528769d4794f44a01c283443c88bec'
            },
        'Storage':{
                'PDF_to_MD':{
                    'MD_file':'/Users/zimoshen/Desktop/Talkweb_intern/KG_Construction/Data/MarkdownFile' # Attention please: if your saving path is ./Data/MarkdownFile/Book/MAT/必修第一册A版/, 
                                    # then you only need to fill ./Data/MarkdownFile in this position!!!
                },
                'Parser':{
                    'Chunked_paper':'./Data/Updated/Papers',
                    'Chunked_book': './Data/Updated/TextBooks' 
                },            
            },
        'Entity_linking':{
            'Edukg_instance_info': '',
            'Entity_Table_Path': '', # 根据用户输入的科目，index to the table corresponding to the subject
            'Entity_level_index': '',
            'Output_path': '' # 用来存更新后的entity linking table
        }
        }
    
    USER = {
            'file_path': '',
            'knowledge': '',
            'interdisciplinary': '', # true or false, if true, choose subject_field, if false, choose subject
            'subject_field': '', 
            'subject':'POL',
            'question_type':'' # 出题助手
        }
    
setting = settings()
