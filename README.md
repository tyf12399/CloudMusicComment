# CloudMusicComment
一个对网易云指定歌手的歌曲评论分析的程序，可获取情感趋向饼状图，柱状图，和评论关键词词云
## 使用说明
+ 需要的包有：PyQt5, wordcloud, matplotlib, urllib, numpy, jieba, panda, snownlp, sqliite3等
+ 安装完需求的库之后，执行ui.py即可
+ 有历史记录功能，已搜索过的歌手可以更快获得结果
+ 歌手歌曲过多时会只取200首
+ 所使用的字体为 刻石录颜体，免费可商用
## Todo list
- [ ] 使用vs code执行时，图表输出会异常，待修复

  （尝试用QtChart重写图表生成部分）

- [ ] 运行中途再次点击确定会重复查找，并异常退出，待修复

  （改为点击后直到输出图表前无法再次点击）

- [ ] 输出栏自动滚动

- [ ] 提高歌曲上限

- [ ] 优化词云结果，添加评论相关停止词和常用词

- [ ] 窗体美化
