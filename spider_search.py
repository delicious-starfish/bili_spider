import re
import os
import os.path as osp
import sys
import json
import time
import argparse
import datetime
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from bs4 import BeautifulSoup
from urllib import parse as url_parse
import random
from tqdm import tqdm
import json


from xpinyin import Pinyin

def mkdir_if_missing(dir):

    if not os.path.exists(dir):
        os.mkdir(dir)

def write_json(data, filename):
    try:
        with open(filename, 'w', encoding="utf-8") as json_file:
            json_file.write(json.dumps(data,ensure_ascii=False,indent=4))
        print(f"Data successfully saved to {filename}.")
    except (IOError, TypeError) as e:
        print(f"An error occurred while saving to {filename}: {e}")

class Bilibili_Spider():

    def __init__(self, url,  page_num, o, save_id, key_word=None,save_dir_json='json', save_by_page=False, t=1):
        self.t = t
        self.page_num = page_num
        self.o = o
        self.save_id = save_id
        self.user_url = url
        self.save_dir_json = save_dir_json
        self.save_by_page = save_by_page
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = "127.0.0.1:33210"
        proxy.ssl_proxy = "127.0.0.1:33210"

        options = webdriver.FirefoxOptions()
        options.add_argument('--proxy-server=http://{}:{}'.format("127.0.0.1", "33210"))
        options.add_argument('--headless')
        self.browser = webdriver.Firefox(options=options)
        self.key_word = key_word
        print('spider init done.')



    def close(self):
        # 关闭浏览器驱动
        self.browser.quit()

    def time_convert(self, time_str):
        time_item = time_str.split(':')
        #assert len(time_item) == 2, 'time format error: {}, x:x expected!'.format(time_str)
        if len(time_item) == 1:
            seconds = int(time_item[0])
        if len(time_item) == 2:
            seconds = int(time_item[0])*60 + int(time_item[1])
        if len(time_item) == 3:
            seconds = int(time_item[0])*60*60 + int(time_item[1])*60 + int(time_item[2])
        return seconds

    def date_convert(self, date_str):
        # date_item = date_str.split('-')
        # assert len(date_item) == 2 or len(date_item) == 3, 'date format error: {}, x-x or x-x-x expected!'.format(date_str)
        # if len(date_item) == 2:
        #     year = datetime.datetime.now().strftime('%Y')
        #     date_str = '{}-{:>02d}-{:>02d}'.format(year, int(date_item[0]), int(date_item[1]))
        # else:
        #     date_str = '{}-{:>02d}-{:>02d}'.format(date_item[0], int(date_item[1]), int(date_item[2]))
        return date_str

    def authorMode_get_videos_by_author_pages(self,page_cnt):
        page_url = self.user_url + f"/?tid=0&pn={page_cnt}&keyword=&order=pubdate"
        print(page_url)
        self.browser.get(page_url)
        time.sleep(self.t + random.random())

        html = BeautifulSoup(self.browser.page_source, features="html.parser")
        ul_data = html.find_all('li', attrs = {"class":"small-item fakeDanmu-item"})
        ul_data.extend(html.find_all('li', attrs = {"class":"small-item new fakeDanmu-item"}))
        print(len(ul_data))
        n = 0
        ids = []
        urls = []
        titles = []
        duration = []
        categories = []
        plays = []
        if len(ul_data) == 0:
            print("ERROR")
            # print(self.browser.page_source)
            # return
            return ids, urls, titles, duration, categories, plays, 0.0

        for ul in ul_data:
            dur = ul.find('span', attrs = {"class":"length"})
            dur = dur.text
            dur = self.time_convert(dur)

            title = ul.find('a', attrs = {"class":"title","target":"_blank"}).text

            url = ul.find('a', attrs = {"class":"title","target":"_blank"})
            url = "https:"+url.get("href")        # NOTE:  http -> https:

            ids.append("BiliBili_"+url.split("/")[-2])
            urls.append(url)
            titles.append(title)
            duration.append(dur)
            categories.append(["作者"])
            plays.append("null")
            n += 1
        print(n)
        dur_all = sum(duration) / 3600
        print(dur_all,"hours")
        print(titles[0])
        return ids, urls, titles,duration, categories, plays, dur_all
    def authorMode_get_max_author_pages(self):
        html = BeautifulSoup(self.browser.page_source, features="html.parser")
        max_page_num = html.find("span",attrs={"class":"be-pager-total"}).text
        max_page_num = re.search(r'\d+', max_page_num).group()

        return int(max_page_num)

    def authorMode_get_author(self):
        html = BeautifulSoup(self.browser.page_source, features="html.parser")
        return html.find('span',attrs = {"id":"h-name"}).text

    def get_videos_by_page(self, idx):
        # 获取第 page_idx 页的视频信息
        urls_page, titles_page, plays_page, dates_page, durations_page, tags_page = [], [], [], [], [], []
        page_url = self.user_url + '&page={}&o={}'.format(idx+1,idx*self.o)
        print(page_url)
        self.browser.get(page_url)
        time.sleep(self.t+random.random())
        # try:

        html = BeautifulSoup(self.browser.page_source, features="html.parser")
        ul_data = html.find_all('div', attrs = {"class":"bili-video-card__wrap __scale-wrap"})
        print(len(ul_data))
        import ast
        n = 0
        ids =[]
        urls = []
        titles = []
        authors = []
        duration = []
        categories = []
        tags = []
        plays = []
        if len(ul_data) == 0:
            print("ERROR")
            # print(self.browser.page_source)
            # return
            return ids, urls, titles, authors, duration, categories, tags, plays, 0.0
        for ul in ul_data:
            dur = ul.find('span', attrs = {"class":"bili-video-card__stats__duration"})
            dur = dur.text
            dur = self.time_convert(dur)
            i = ul.find('div', attrs = {"class":"bili-video-card__info __scale-disable"})
            # find title, au, tag, 
            tag = i.find_all('em')
            tag_ = []
            for t in tag:
                tag_.append(t.text)
            au = i.find('span', attrs = {"class":"bili-video-card__info--author"})
            try:
                au = au.text
            except:
                au = None
                print(f"没找到作者,{au}")
            url = i.find('a', attrs = {"data-ext":"click"})
            url = "https:"+url.get("href")        # NOTE:  http -> https:
            tit = i.find("h3", attrs = {"class":"bili-video-card__info--tit"})
            tit = tit.get("title")

            ids.append("BiliBili_"+url.split("/")[-2])
            urls.append(url)
            titles.append(tit)
            authors.append(au)
            duration.append(dur)
            categories.append(["关键词"])
            tags.append(tag_)
            plays.append("null")
            n += 1   
        print(n)
        dur_all = sum(duration) / 3600
        print(dur_all,"hours")
        print(titles[0])
        return ids, urls, titles, authors, duration, categories, tags, plays, dur_all


    def save(self, json_path, ids, urls, titles, authors, duration, categories, tags, play):
        data_list = []
        for i in range(len(urls)):
            result = {}
            result['id'] = ids[i]
            result['title'] = titles[i]
            result["full_url"] = urls[i]
            result['author'] = authors[i]
            result['duration'] = duration[i]
            result['categories'] = categories[i]
            result['tags'] = tags[i] if tags else "null"
            result["view_count"] = play[i]
            data_list.append(result)
        
        print('write json to {}'.format(json_path))
        dir_name = osp.dirname(json_path)
        mkdir_if_missing(dir_name)
        write_json(data_list, json_path)
        print('dump json file done. total {} urls. \n'.format(len(urls)))

    def get_by_keyWords(self):
        # 获取该 up 主的所有基础视频信息
        print('Start ... \n')
        print('Pages Num {}'.format(self.page_num))

        ids_all =[]
        urls_all = []
        titles_all = []
        authors_all = []
        duration_all = []
        categories_all = []
        tags_all = []
        play_all = []
        self.key_word = self.user_url.split("/")[3]
        self.key_word = re.search("keyword=(.*?)&search_source=5",self.key_word).group(1)
        for idx in range(self.page_num):
            print('>>>> page {}/{}'.format(idx+1, self.page_num))
            ids, urls, titles, authors, duration, categories, tags, play, dur_all = self.get_videos_by_page(idx)
            sys.stdout.flush()

            for i in range(len(urls)):
                if urls[i] not in urls_all:
                    ids_all.append(ids[i])
                    urls_all.append(urls[i])
                    titles_all.append(titles[i])
                    authors_all.append(authors[i])
                    duration_all.append(duration[i])
                    categories_all.append(categories[i])
                    tags_all.append(tags[i])
                    play_all.append(play[i])
        p = Pinyin()
        key = p.get_pinyin(self.key_word)
        json_path = osp.join(self.save_dir_json, '{}_{}'.format("bilibili", "关键词"), str(key)+'.json')
        print("Result:", len(urls_all))
        print("Result:", sum(duration_all) / 3600 , "hours")
        self.save(json_path, ids_all, urls_all, titles_all, authors_all, duration_all, categories_all, tags_all, play_all)

    def get_by_authors(self):
        if "search" in self.user_url:
            print("链接提供错误，请提供用户页面")
            return

        ids_all = []
        urls_all = []
        titles_all = []
        authors_all = []
        duration_all = []
        categories_all = []
        tags_all = []
        play_all = []
        author = "unknown"
        page_cnt = 1
        max_page = -1
        while True:
            if max_page != -1 and page_cnt > max_page:
                break

            print('>>>> page {}/{}'.format(page_cnt + 1, max_page if max_page != -1 else "unknown"))

            ids, urls, titles, duration, categories, play, dur_all = self.authorMode_get_videos_by_author_pages(page_cnt)
            if max_page == -1: max_page = self.authorMode_get_max_author_pages()
            if author == 'unknown': author = self.authorMode_get_author()
            page_cnt += 1

            for i in range(len(urls)):
                if urls[i] not in urls_all:
                    ids_all.append(ids[i])
                    urls_all.append(urls[i])
                    titles_all.append(titles[i])
                    authors_all.append(author)
                    duration_all.append(duration[i])
                    categories_all.append(categories[i])
                    tags_all.append(None)
                    play_all.append(play[i])
        p = Pinyin()
        author = p.get_pinyin(author)
        json_path = osp.join(self.save_dir_json, '{}_{}'.format("bilibili", "作者"), str(author) + '.json')
        print("Result:", len(urls_all))
        print("Result:", sum(duration_all) / 3600, "hours")
        self.save(json_path, ids_all, urls_all, titles_all, authors_all, duration_all, categories_all, tags_all,
                      play_all)

def main():
    path = osp.dirname(os.getcwd()) + '\\视频数据'
    mkdir_if_missing(path)
    key_words = ["新番","美食","nasa","流浪地球","哈勃望远镜","中国天眼","这就是中国"]
    for key_word in key_words:

        #每次运行需要更改的参数
        url = f"https://search.bilibili.com/all?keyword={key_word}&search_source=5&duration=4"
        page_num = 40
        o = 36          #点第二页或者第三页会发现url上的o成倍数增长，在这里给1倍的o
        save_id = 3     #每次运行手动加1
        bilibili_spider = Bilibili_Spider(url, page_num, o, save_id,save_dir_json=path)
        bilibili_spider.get_by_keyWords()

    # authors = ["8096990","113362335","297882491","508416316","25503580","297786973","337312411","888465","7481602"]
    # for author in authors:
    #     url = f"https://space.bilibili.com/{author}/video"
    #     page_num = 40
    #     o = 36
    #     save_id = 3
    #     bilibili_spider = Bilibili_Spider(url, page_num, o, save_id, save_dir_json=path)
    #     bilibili_spider.get_by_authors()



if __name__ == '__main__':
    main()