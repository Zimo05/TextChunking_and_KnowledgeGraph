# TextChunking_and_KnowledgeGraph
This program is used to chunk textbook and papers and then structurize them into a DAG using neo4j, we silmutaneously conbine the data you input with knowledge instance offered by THU.
- for Textbook: we chunked the textbook into -> text content chunks with length between 600 and 1000, title to which it belongs and parent title to which it belongs, knowledge instance, relationships
- for Papers: we chunked the Papers into -> question, answer and analysis, knowledge

## MinerU configuration:
1. Inside the TextChunking_and_KnowledgeGraph folder, pull the MinerU repositpry
   - git clone https://github.com/opendatalab/MinerU.git
2. **Create a virtual environment, run the requirement.txt：** pip install -r requirements.txt
3. **(API version)Confugure:** Apply MinerU API om the official website: https://mineru.net/apiManage

## USING Guidance:
- Open the Config.Settings：
     - Dify Confuguration: Upload Dify DSL in Entity Data and configure the API keys
     - NEO4J API key
     - MinerU token
     - Deepseek API
- Update the input and output data paths (MD_file, Chunked_paper, Chunked_book) as needed(**If you are Mac user, do not modify, just skip this**)
  - (**For windows user**): Complete the file path prefix, for example: from ***./Data/Updated/Papers*** to ***D://USER/..../TextChunking_and_KnowledgeGraph/Data/Updated/Papers***
- Open the UserImplementation folder to run the UserCommand.py
- follow the guidance to complete the file uploading and Configure settings
- **For input data**:
     - For textbook: No specific requirement
     - For papers: Only special requirements for English, **Do not input a paper, Only one pdf of collection of question type within \['阅读理解', '完形填空', '语法填空'， '七选五'\] is acceptable**
 
- Lastly, follow the guidance within the instructions during code execution



Acknowledgement:
1. Thanks for **[MinerU](https://github.com/opendatalab/MinerU)** for offering fundamental pdf transformation tool.
2. Thanks for **[DeepSeek](https://github.com/deepseek-ai)** for offering advanced AI models and open-source resources.
