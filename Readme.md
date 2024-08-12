## 功能介绍

<p><font color="BlueGreen">1.提供关键词，并且根据关键词在BILIBILI搜索视频，并获得视频的元数据</font></p>
<p><font color="BlueGreen">2.将视频元数据保存为{关键词}.json</font></p>
<p><font color="BlueGreen">3.同时也可以提供作者id,并且获得视频元数据</font></p>
<p><font color="BlueGreen">4.使用作者id爬取时,元数据将保存为<strong>{作者姓名}</strong>.json</font></p>

## 元数据
视频元数据保存为以下格式

```
{
        "id": "BiliBili_BV1zZ42117Sk",
        "title": "\u3010\u4e2d\u82f1\u5b57\u5e55\u3011ASMR-\u4f60\u53d7\u4f24\u4e86  ASMR- VIETNAM MEDIC ROLE PLAY",
        "full_url": "https://www.bilibili.com/video/BV1zZ42117Sk/",
        "author": "homo-popcorn",
        "duration": 5096,
        "categories": [
            "\u70ed\u70b9"
            (理论上来说应当是"热点","关键词","作者"中任选一)
        ],
        "tags": [
            "ASMR",
            "ASMR"
        ],
        "view_count": "null"
},
```
## TODO
- [x] <font color=YellowGreen>修改类的定义，在使用关键词搜索时无须传入关键词</font>
- [x] <font color=YellowGreen>能够流畅执行按作者爬取</font>
- [ ] <font color=YellowGreen>测试下载脚本对于按作者爬取的适配</font>
- [ ] <font color=YellowGreen>为tag过滤做准备</font>
- [ ] <font color=YellowGreen>避免重复爬取作者</font>  
- [ ] <font color=YellowGreen>时长过滤模块放在下载脚本部分</font>
- [ ] <font color=YellowGreen>能够在热点视频上按关键词爬取</font>
- [ ] <font color=YellowGreen>在关键词搜索时过滤掉小up</font>
