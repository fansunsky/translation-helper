# 项目背景

专门为考研党或雅思机考党免费开发的一个小工具，用户可以上传词汇表或英汉对照文件。
词汇表省上传去了用户的查单词时间，并且能够在页面上点击单词查看到单词的完整释义；
英汉对照文件上传，用户可以根据中文原文填入对应的英文译文，提交给AI评测，指出英文译文存在
的单词、语法、表达方式等问题，帮助用户提升翻译与写作水平。

# 功能概览

详细信息见飞书文档
[功能概览](https://d59pmlcbus.feishu.cn/docx/WERYdpBdPozfrNxuy5LcPLdEnBb?from=from_copylink)

# 技术栈

| 名称| version
| --- | --- |
| python | >=3.10  |
| nodeJS| v20.15.1 |
| npm | 10.7.0 |

# 本地部署流程

## 后端

在.env文件填写调用模型的key和url

```
cd backend
```

安装必要依赖

```
pip install -r requirements.txt
```

启动后端服务

```
python app.py
```

## 前端

```
cd frontend
```

安装必要依赖

```
npm install
```

启动前端服务

```
npm run dev
```

测试上传单词的示例文件:[词汇表](https://resource-tx-cdn.xiaoeeye.com/appvod604qb9206/file/b_u_ck8n6b6ps1bshnkerp00/m1dtmema9n12qg.pdf?download_name=%E8%AF%8D%E6%B1%87%E8%A1%A8%E7%A4%BA%E4%BE%8B.pdf)

测试上传英汉对照的示例文件:[英汉对照](https://resource-tx-cdn.xiaoeeye.com/appvod604qb9206/file/b_u_ck8n6b6ps1bshnkerp00/xvum17ma9n12r0.pdf?download_name=%E8%8B%B1%E6%B1%89%E5%AF%B9%E7%85%A7%E7%A4%BA%E4%BE%8B.pdf)

文件来源:B站up主"Larry想做技术大佬"在公众号开源下载站提供

# 项目demo地址见以下链接

[回译助手](http://14.103.134.75/)













