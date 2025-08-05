class settings:
    Designer = {
        'DIFY': {
            'DIFY_ENG_Paper_Parser_API': 'app-j0NdoLnzwvbpQcMVO79XckIZ',
            'DIFY_Entity_Linking_API': 'app-hMrsW6S7ECwARMQORH2tS5oU',
            'DIFY_Entity_Book_Linking_API': 'app-ICVmh2I94iQ6hFxkvJ7wevLX',
            'DIFY_Correction_API': 'app-iwGbYYWNZ1aK9TgXSLU9uIJq',
            'DIFY_URL': "http://localhost/v1/workflows/run",
            'DIFY_USER': 'Zimo'
            },
        'NEO4J': {
            'NEO4J_URL': 'bolt://localhost:7474',
            'NEO4J_USERNAME': 'neo4j',
            'NEO4J_PASSWORD': 'neo4j20227'
            },
        'ES': {
            'ES_URL': 'http://localhost:9200',
            'ES_USER': 'elastic',
            'ES_PASSWORD': 'Shenzimo123456'
            },
        'DEEPSEEK': {
            'API': 'sk-16528769d4794f44a01c283443c88bec'
            },
        'Storage':{
                'PDF_to_MD':{
                    'MD_file':'./Data/Original/教材/高中数学必修第一册A版/高中数学必修第一册A版.md' 
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