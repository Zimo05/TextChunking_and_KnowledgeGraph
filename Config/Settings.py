class settings:
    Designer = {
        'DIFY': {
            'DIFY_ENG_Paper_Parser_API': '',
            'DIFY_Entity_Linking_API': '',
            'DIFY_Entity_Book_Linking_API': '',
            'DIFY_Correction_API': '',
            'DIFY_URL': "http://localhost/v1/workflows/run",
            'DIFY_USER': ''
            },
        'MinerU_Token': '', 
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
                    'MD_file':'' 
                },
                'Parser':{
                    'Chunked_paper':'./Data/Updated/Papers/',
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
            'subject':'',
            'question_type':'' # 出题助手
        }
    
setting = settings()


# Graph integration
