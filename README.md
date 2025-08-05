# TextChunking_and_KnowledgeGraph

## MinerU configuration(GPU version):
1. Create a virtual environment inside the MinerU folder
2. run the requirement.txt
3. **Confugure torch and torchvision:**
    - link:
       - https://download.pytorch.org/whl/torchvision, **using torch2.7.1 + cu128, and choose the sepcific python version**
       - https://download.pytorch.org/whl/torch, **using torchvision0.22.1 + cu128, and choose the sepcific python version**

## Dify configuration(for MinerU):
1. MinerU FastApi: mineru-api --host 127.0.0.1 --port \<port number\>
2. 

## USING Guidance:
1. Designer:
- Open the Config.Settings to modify the dify, neo4j and elastic search API key and personal settings
- Update the input and output data paths as needed
2. User:
- Open the UserImplementation folder to run the UserCommand.py
- follow the guidance to complete the file uploading and Configure settings
 
## 使用指南： 
1. 后台:
   - 打开Config.Settings设置修改dify， neo4j和elastic搜索API密钥和个人设置
   - 根据需要更新输入和输出数据路径 
3. 用户:
   - 打开“UserImplementation”文件夹，运行“UserCommand.py”
   - 根据界面提示完成文件上传和配置
