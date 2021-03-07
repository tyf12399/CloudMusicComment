import requests
import urllib
import math
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import jieba
from snownlp import SnowNLP
from wordcloud import WordCloud
import pandas as pd
import sqlite3
import math

class calculator:
    find_artist=''
    my_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'music.163.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }

    def __init__(self,artist_name):
        self.find_artist=artist_name


    def run(self):   #调用接口
        print("判断是否有过搜索记录")
        self.f=open('history.txt','r+')
        b=True
        while True:
            line=self.f.readline()
            if not line:
                break
            if line==self.find_artist+'\n':
                b=False
                break
        self.conn = sqlite3.connect(self.find_artist+'_netease_cloud_music.db')
        if(b):#判断是否有过搜索记录
            self.pachong()
        else:
            self.load()
        sql = '''
                    SELECT *
                    FROM comment
                    WHERE song_id IN (
                        SELECT song_id
                        FROM song
                        WHERE artists LIKE artists
                    )
                '''
        self.comment = pd.read_sql(sql, con=self.conn)  # 读取库
        #self.draw()


    def pachong(self):   #未搜索过该歌手
        print("未搜索过该歌手，正在爬取数据...")
        fdb=open(self.find_artist+'_netease_cloud_music.db','w+')
        fdb.truncate()   #清空数据库文件
        self.comment_num_list=[]
        name=['评论数','歌曲']

        song_df = self.getSongList(self.find_artist)
        song_df = song_df[song_df['artists'].str.contains(self.find_artist)] #筛选记录
        song_df.drop_duplicates(subset=['song_id'], keep='first', inplace=True) #去重
        song_df.to_sql(name='song', con=self.conn, if_exists='append', index=False)
        sql = '''
            SELECT song_id
            FROM song
            WHERE artists LIKE artists
        '''
        song_id = pd.read_sql(sql, con=self.conn)
        comment_df = pd.DataFrame()
        for index, id in zip(song_id.index, song_id['song_id']):
            print('0开始爬取第 {0}/{1} 首, {2}'.format(index+1, len(song_id['song_id']), id))
            tmp_df = self.getSongComment(id)
            comment_df = pd.concat([comment_df, tmp_df])
        comment_df.drop_duplicates(subset=['comment_id'], keep='first', inplace=True)
        comment_df.to_sql(name='comment', con=self.conn, if_exists='append', index=False)
        print('已成功保存至数据库！')

        self.comment_num=pd.DataFrame(columns=name,data=self.comment_num_list) #生成评论数的表格
        self.comment_num.to_csv(self.find_artist+'的歌曲评论数.csv')  #保存评论数的表格
        self.f.write(self.find_artist+'\n')    #再搜索历史文件中加入该歌手


    def load(self): #已搜索过该歌手
        print("已搜索过该歌手，正在加载本地数据...")
        self.comment_num=pd.read_csv(self.find_artist+'的歌曲评论数.csv') #读取评论数的表格


    def draw(self):# 各类图形的绘制
        print("数据加载完毕，正在计算...")
        plt.style.use('ggplot')
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False

        #歌手歌曲评论数前十图
        data_list=self.comment_num.values.tolist()
        data=np.array(data_list)
        data=data[:,1:3]
        data=np.sort(data,axis=0)
        num_data=data[-1:-11:-1,0]

        plt.bar(np.arange(10),height=num_data)
        plt.title("评论数前十的歌曲")
        plt.savefig('评论数前十的歌曲.jpg')
        plt.show()

        #情感倾向扇形图
        self.comment['semiscore'] = self.comment['content'].apply(lambda x: SnowNLP(x).sentiments)
        self.comment['semilabel'] = self.comment['semiscore'].apply(lambda x: 1 if x > 0.5 else -1)
        semilabel = self.comment['semilabel'].value_counts()
        semilabel = semilabel.loc[[1, -1]]
        plt.pie(semilabel.values,labels=['积极评论','消极评论'],colors=['green','red'],autopct='%3.2f%%')
        plt.title("评论的情感倾向")
        plt.savefig('评论的情感倾向.jpg')
        plt.show()
        
        # 词云图
        text = ''.join(str(s) for s in self.comment['content'] if s not in [None]) #将所有评论合并为一个长文本
        word_list = jieba.cut(text, cut_all=False) #分词
        stopwords = [line.strip() for line in open('stopwords.txt',encoding='UTF-8').readlines()] #加载停用词列表
        clean_list = [seg for seg in word_list if seg not in stopwords] #去除停用词
        clean_text=''.join(str(s+'\n') for s in clean_list)#合成去除停用词后的长文本
        cloud = WordCloud(
            font_path = 'SIMLI.TTF',
            background_color = 'white',
            max_words = 1000,
            max_font_size = 64
        )
        word_cloud = cloud.generate(clean_text)
        plt.figure(figsize=(16, 16))
        plt.imshow(word_cloud)
        plt.axis('off')
        plt.savefig('词云图.jpg')
        plt.show()


    def getJSON(self,url, headers):
        """ Get JSON from the destination URL
        @ param url: destination url, str
        @ param headers: request headers, dict
        @ return json: result, json
        """
        res = requests.get(url, headers=headers)
        res.raise_for_status()  # 抛出异常
        res.encoding = 'utf-8'
        json = res.json()
        return json


    def countPages(self,total, limit):
        """ Count pages
        @ param total: total num of records, int
        @ param limit: limit per page, int
        @ return page: num of pages, int
        """
        page = math.ceil(total / limit)
        return page


    def parseSongInfo(self,song_list):
        """ Parse song info
        @ param song_list: list of songs, list
        @ return song_info_list: result, list
        """
        song_info_list = []
        for song in song_list:
            song_info = []
            song_info.append(song['id'])
            song_info.append(song['name'])
            artists_name = ''
            artists = song['artists']
            for artist in artists:
                artists_name += artist['name'] + ','
            song_info.append(artists_name)
            song_info.append(song['album']['name'])
            song_info.append(song['album']['id'])
            song_info.append(song['duration'])
            song_info_list.append(song_info)
        return song_info_list


    def getSongList(self,key,limit=30):
        """ Get a list of songs
        @ param key: key word, str
        @ param limit: limit per page, int, default 30
        @ return result: result, DataFrame
        """
        total_list = []
        key = urllib.parse.quote(key)  # url编码
        url = 'http://music.163.com/api/search/get/web?csrf_token=&hlpretag=&hlposttag=&s=' + key + '&type=1&offset=0&total=true&limit='
        # 获取总页数
        first_page = self.getJSON(url, self.my_headers)
        song_count = first_page['result']['songCount']
        page_num = self.countPages(song_count, limit)
        if page_num > 20:
            page_num = 20
        # 爬取所有符合条件的记录
        for n in range(page_num):
            url = 'http://music.163.com/api/search/get/web?csrf_token=&hlpretag=&hlposttag=&s=' + key + '&type=1&offset=' + str(
                n * limit) + '&total=true&limit=' + str(limit)
            tmp = self.getJSON(url, self.my_headers)
            song_list = self.parseSongInfo(tmp['result']['songs'])
            total_list += song_list
            print('第 {0}/{1} 页爬取完成'.format(n + 1, page_num,10))
            #time.sleep(random.randint(2, 4))
        df = pd.DataFrame(data=total_list,
                          columns=['song_id', 'song_name', 'artists', 'album_name', 'album_id', 'duration'])
        return df


    def parseComment(self,comments):
        """ Parse song comment
            @ param comments: list of comments, list
            @ return comments_list: result, list
        """
        comments_list = []
        for comment in comments:
            comment_info = []
            comment_info.append(comment['commentId'])
            comment_info.append(comment['user']['userId'])
            comment_info.append(comment['user']['nickname'])
            comment_info.append(comment['user']['avatarUrl'])
            comment_info.append(comment['content'])
            comment_info.append(comment['likedCount'])
            comments_list.append(comment_info)
        return comments_list

    def getSongComment(self,id,limit=20):
        """ Get Song Comments
        @ param id: song id, int
        @ param limit: limit per page, int, default 20
        @ return result: result, DataFrame
        """
        total_comment = []
        url = 'http://music.163.com/api/v1/resource/comments/R_SO_4_' + str(id) + '?limit=20&offset=0'
        # 获取总页数
        first_page = self.getJSON(url, self.my_headers)
        total = first_page['total']
        page_num = self.countPages(total, limit)
        self.comment_num_list.append([total, str(id)])
        # 爬取该首歌曲下的所有评论
        for n in range(min(page_num,10)):
            url = 'http://music.163.com/api/v1/resource/comments/R_SO_4_' + str(id) + '?limit=' + str(
                limit) + '&offset=' + str(n * limit)
            tmp = self.getJSON(url, self.my_headers)
            comment_list = self.parseComment(tmp['comments'])
            total_comment += comment_list
            print('第 {0}/{1} 页爬取完成'.format(n + 1, min(page_num,10)))
            # time.sleep(random.randint(2, 4))

        df = pd.DataFrame(data=total_comment,
                          columns=['comment_id', 'user_id', 'user_nickname', 'user_avatar', 'content', 'likeCount'])
        df['song_id'] = str(id)  # 添加 song_id 列
        return df