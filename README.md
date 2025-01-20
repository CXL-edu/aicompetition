# 竞x赛  

防检索  

## 配置环境  
```python
# 第一种方式，使用conda配置环境
conda env create -f environment.yml

# 第二种方式，在已有环境中使用pip安装依赖
pip install -r requirements.txt

# 第三种方式，官方推荐，使用poetry配置环境
pip install pipx
pipx install poetry
pipx ensurepath
poetry install
#poetry 环境下运行代码需要在命令行指定，如
poetry run python -m example.ModelingAgent_baseline                         
```

## 数据  
将dataset数据压缩包解压至dataset中  

## 运行baseline  
在`example\ModelingAgent_baseline.py`中写入api key  
在命令行输入`python -m example.ModelingAgent_baseline`指令执行赛道1的baseline