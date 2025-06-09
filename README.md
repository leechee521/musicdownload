# **私有音乐库搭建** | 自动下载/元数据刮削/歌单生成
## 展示成果：
![screenshot-1749442765816](images/screenshot-1749442765816.png)

## 🌟 核心功能
- [x] 双平台音乐检索（某Q/某芸）
- [x] 智能元数据嵌入（ID3v2标准）
- [x] 自动化路径生成：`艺术家/专辑/歌曲名.格式`
- [x] 双语歌词内嵌（LRC+翻译）
- [x] 下载歌单并且生成 Navidrome 歌单
- [x] Docker 一键部署
- [x] 音乐下载只下载文件文件最大的（根据歌名-歌手匹配）
- [x] 适配手机端
- [ ] 本地下载
- [ ] 排行榜查看更多歌曲
- [ ] jellyfin歌单生成
- [ ] 某芸搜索更多歌曲（目前只实现固定页，未实现翻页功能）

## 🚀 快速开始

### 前置要求
- 飞牛NAS（或任意支持Docker的Linux设备）
- 获取到音乐平台cookie
- Python 3.11+

### 本地部署
```cmd
pip install -r requirement.txt
#配置好mysql后就可以运行
python app.py
```
修改config.py
```python
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://root:root@localhost/music_download')
```
### Docker部署
```bash
sudo docker run -d \
  -p 5000:5000 \
  --restart always \
  -v /path/to/downloads:/app/downloads \
  -v /path/to/config:/app/app/config \
  -v /path/to/log:/app/app/log \
  -e EVN=production \
  -e DATABASE_URL=mysql+pymysql://root:root.@localhost/music_download \
  --name musicdownload \
  crpi-g2vqp6cspcljbor7.cn-hangzhou.personal.cr.aliyuncs.com/leechee_ii/musicdownload:latest
```
需要修改数据库，建议使用mysql
### 配置文件示例
创建 `config/config.json`：
```json
{
    "qqMusic": {
        "COOKIE": ""
    },
    "wyyMusic": {
        "COOKIE": ""
    }
}
```

## 🛠️ 使用指南
### 搜索歌曲

![QQ20250609-130004](images/QQ20250609-130004.png)

### 下载单曲

![QQ20250609-122407](images/QQ20250609-122407.png)

## 下载歌单

![QQ20250609-122253](images/QQ20250609-122253.png)


### 歌单处理流程
1. 获取平台歌单ID（分享链接中提取）

2. 将链接粘贴到下载页面

3. 生成文件：`/downloads/playlist/我的歌单.m3u`

## 项目启动后也可以通过下载页面右上角设置修改cookie

![QQ20250609-130647](images/QQ20250609-130647.png)


## 🤝 参与贡献
欢迎通过以下方式改进项目：
1. 提交Issue报告问题
2. Fork仓库后提交PR
3. 补充音乐平台API适配

## 📜 免责声明
**支持正版音乐！！！**本项目仅用于学习交流，都是汇聚各牛人在GitHub上提供的的方法。

## ☕ 支持作者
如果觉得有帮助，可以给个Star⭐~
