# -*- coding: utf-8 -*-
#功能 ：批量同步halo博客文章到csdn
#日期 ：2021-10-03 
#作者：Dark-Athena
#email ：darkathena@qq.com
#说明：自动从备选ip清单中寻找最低延时IP，设置到本地host中，需要使用管理员权限运行

"""
Copyright DarkAthena(darkathena@qq.com)
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import requests,json,time
import markdown,urllib 
#参数配置
#1.halo博客主站网址,这里改成你自己的
url_halo_main='https://www.darkathena.top'
#2.halo后台配置的api_access_key
halo_key='**********'
#3.提前手动保存好的已登录的csdn的cookie文本文件，可用chrome浏览器F12获得
csdn_cookie_path=r'd:\py\csdn-cookie.txt'
#4.状态： 0发布，2草稿
status=2
#5.要同步的文章完整标题列表，请自行添加
title_list=[]
title_list.append('【python】自动更换本地HOSTS中github.com的ip指向为最低延迟ip')
title_list.append('【云】对象存储服务亚马逊云S3、腾讯云cos、阿里云oss的命令行工具使用方式整理')
title_list.append('【ORACLE】关于多态表函数PTF（Polymorphic Table Functions）的使用')

#csdn保存文章的api，不要动
csdn_url = 'https://blog-console-api.csdn.net/v1/mdeditor/saveArticle'

#获取halo博客文章内容
def get_content(title,key):
    url_search =url_halo_main+'/api/content/posts?keyword='+title+'&api_access_key='+halo_key
    url_get_content =url_halo_main+'/api/content/posts/articleId?&api_access_key='+halo_key
    #查找文章清单
    s =requests.get(url_search)
    t =json.loads(s.text)
    #halo搜索可能找到多篇文章，这里做标题精准匹配以找到唯一的articleId
    for i in t['data']['content'] :
        if i['title']==title:
            id=i['id']
    response =requests.get(url_get_content.replace('articleId',str(id)))
    t =json.loads(response.text)
    #获取原始文章内容
    originalContent=t['data']['originalContent']
    #将文章内相对路径改成绝对路径
    newcontent=originalContent.replace('(/upload/','('+url_halo_main+'/upload/')
    newcontent=newcontent.replace('(/archives/','('+url_halo_main+'/archives/')
    #csdn部分代码块语言类型不识别
    newcontent=newcontent.replace('```plsql','```sql')
    newcontent=newcontent.replace('```HTML','```html')
    return newcontent

#同步到csdn
def push_csdn(title,content):
    data = {"title":title,
            "markdowncontent":content,
            "content":markdown.markdown(content),
            "readType":"public",
            "status":status,
            "not_auto_saved":"1",
            "source":"pc_mdeditor",
            "cover_images":[],
            "cover_type":0,
            "is_new":1,
            "vote_id":0,
            "pubStatus":"draft",
            "type": "original",
            "authorized_status":False,
            "tags":"",
            "categories":""} 

    cookie=open(csdn_cookie_path,"r+",encoding="utf-8").read()
    headers={"content-type": "application/json;charset=UTF-8",
             "cookie": cookie,
             "user-agent": "Mozilla/5.0"}
    response = requests.post(csdn_url,data=json.dumps(data),headers=headers)
    result = json.loads(response.text)
    return result

#执行
try:
    for title in title_list:
        content=get_content(title,halo_key)
        result=push_csdn(title,content)
        if result["code"]==200:
            print(result["code"],result["msg"],result["data"]["title"])
        else:
            print(result["code"],result["msg"])
        time.sleep(30)#csdn设置了两篇文章发布间隔小于30秒会报错
except Exception as e:
        print(e)    
