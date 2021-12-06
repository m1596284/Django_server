# -*- coding: UTF-8 -*-
import json
import datetime
from time import sleep, time
from pathlib import Path
from src.py_logging import py_logger, remove_old_log
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound
from .models import *
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, StickerSendMessage, AudioSendMessage, ImagemapSendMessage, TemplateSendMessage, FlexSendMessage, BaseSize, ImageCarouselTemplate, ImageCarouselColumn, PostbackAction, VideoSendMessage, BubbleContainer, ImageComponent, URIAction, CarouselContainer, BoxComponent, TextComponent, SeparatorComponent, messages, ButtonComponent, Background, LinearGradientBackground
import requests
from bs4 import BeautifulSoup, element
import re
import random
from PyDictionary import PyDictionary
from pytube import YouTube
from youtube_search import YoutubeSearch

## the BASE_DIR of this django project
pyPath = Path(__file__).parent.parent
py_name = "IU_line_bot"

## log setting
remove_old_log(dir_path=f"{pyPath}/log",file_name=py_name)
log = py_logger("a",level="INFO", dir_path=f"{pyPath}/log",file_name=py_name)

## Loading the access token and secret for line bot
with open(f"{str(pyPath)}/line_bot_channel.json") as f:
    channel_json = json.load(f)
line_bot_api = LineBotApi(channel_json["iu_fans"]["channel_access_token"])
handler = WebhookHandler(channel_json["iu_fans"]["channel_secret"])

## parameter
with open(f"{str(pyPath)}/line_bot_headers.json") as f:
    headers_json = json.load(f)
headers_IG = headers_json["headers_IG"]
headers_tiktok = headers_json["headers_tiktok"]
headers_hastag = headers_json["headers_hastag"]
headers_postman = headers_json["headers_postman"]

## dictionary
with open(f"{str(pyPath)}/line_bot_dictionary.json") as f:
    dictionary_json = json.load(f)
IU_test = dictionary_json["IU_test"]
IU_fans_club = dictionary_json["IU_fans_club"]
IU_fans_club_chat_room = dictionary_json["IU_fans_club_chat_room"]
permission_dict_chat_room_hometown = dictionary_json["permission_dict_chat_room_hometown"]
line_user_dict = dictionary_json["line_user_dict"]
keyword_dict = dictionary_json["keyword_dict"]
dog_dict = dictionary_json["dog_dict"]
sticker_dict = dictionary_json["sticker_dict"]
horoscope_dict = dictionary_json["horoscope_dict"]
weather_dict = dictionary_json["weather_dict"]
city_encoding = dictionary_json["city_encoding"]
location_to_city = dictionary_json["location_to_city"]

## list
with open(f"{str(pyPath)}/line_bot_list.json") as f:
    list_json = json.load(f)
cityLocations = list_json["cityLocations"]
Language_List = list_json["Language_List"]

## get admin id
admin_id = list(IU_fans_club.keys())[0]

def print_request_detail(request):
    request_dict = json.loads(request.body.decode('utf-8'))
    destination = request_dict.get("destination")
    events = request_dict.get("events")
    events_type = request_dict["events"][0].get("type")
    events_message = request_dict["events"][0].get("message")
    events_timestamp = request_dict["events"][0].get("timestamp")
    events_source = request_dict["events"][0].get("source")
    events_replyToken = request_dict["events"][0].get("replyToken")
    events_mode = request_dict["events"][0].get("mode")
    source_type = request_dict["events"][0]["source"].get('type')
    source_groupId = request_dict["events"][0]["source"].get('groupId',"None")
    source_roomId = request_dict["events"][0]["source"].get('roomId',"None")
    source_userId = request_dict["events"][0]["source"].get('userId')
    message_type = request_dict["events"][0]["message"].get("type")
    message_id = request_dict["events"][0]["message"].get("id")
    message_text = request_dict["events"][0]["message"].get("text")
    print(f"request_dict: {request_dict}")
    print(f"destination:\t{destination}")
    print(f"events_type:\t{events_type}")
    print(f"message_type:\t{message_type}")
    print(f"message_id:\t{message_id}")
    print(f"message_text:\t{message_text}")
    print(f"events_timestamp:\t{events_timestamp}")
    print(f"events_replyToken:\t{events_replyToken}")
    print(f"events_mode:\t{events_mode}")
    print(f"source_type:\t{source_type}")
    print(f"source_groupId:\t{source_groupId}")
    print(f"source_roomId:\t{source_roomId}")
    print(f"source_userId:\t{source_userId}")
    # request sample
    {
    'destination': 'U7b5246f2dcb119442f7fc847c66d8824',
    'events': [
                {
                'type': 'message',
                'message': {
                            'type': 'text',
                            'id': '14957918020461',
                            'text': '1'
                            }, 
                'timestamp': 1634919357482, 
                'source': {
                            'type': 'user', 
                            'userId': 'U898b0be359442b95fabc587d6b9aed9e'
                            }, 
                'replyToken': '35364dee67244dea95ab8b22a3350bc2', 
                'mode': 'active'
                }
            ]
    }
    pass

def DB_update_line_user():
    for num,user_id in enumerate(line_user_dict):
        line_user = user_info_table(id = num+1, user_name = line_user_dict[user_id], user_id = user_id)
        line_user.save()

def DB_update_chat_log(user_id,user_name,chat_room,message_text):
    chat_log_table.objects.create(user_id=user_id,user_name=user_name,chat_room=chat_room,chat_text=message_text)
    pass

def reply_help(reply_token):
    help_message = "IU Line Bot v6.3 2021/12/02 " + "fix tiktok" + "\n" \
        "IU : 隨機IU" + "\n" \
        "OO : 歐美" + "\n" \
        "CC : Cosplay" + "\n" \
        "MM : 台灣妹子" + "\n" \
        "PP : 18禁" + "\n" \
        "9fun : 9gag-funny" + "\n" \
        "9girl : 9gag-girl" + "\n" \
        "9hot : 9gag-nsfw" + "\n" + "\n"\
        "ex:雙子, 巨蟹" + "\n" + "當日運勢短評" + "\n"+ "\n" \
        "ex:來首 張震嶽" + "\n" +"ex:點播 105度的你" + "\n" + "會自動播出Youtube" + "\n\n" \
        "ex:字典 dinner" + "\n" + "提供Key的詞性解釋" + "\n\n"\
        "ex:許願 新增五月天圖庫" + "\n" + "將許願資訊匿名傳送給作者" + "\n\n" \
        "ex:雷達, 雲圖, 溫度, 紫外線, 雨量" + "\n" +"最近時間的天氣資訊" + "\n\n" \
        "ex:台北士林天氣" + "\n" + "高雄天氣" + "\n" + "地點的短期天氣預報" + "\n\n" \
        "ex:我就爛" + "\n" + "觸發關鍵字會自動展圖" + "\n" + "-h keyword 列出關鍵字表"  + "\n\n" \
        "自動展圖: IG, youtube, Ptt(moPtt), 抖音, Twitter, imgur, #tag" + "\n" \
        "Porn keyword ..."
    line_bot_api.reply_message(reply_token,TextSendMessage(text=help_message))

def reply_help_keyword(reply_token):
    help_message = ""
    for key, value in keyword_dict.items():
        help_message = f"{help_message}\n{key}"
    for key, value in dog_dict.items():
        help_message = f"{help_message}\n{key}"
    line_bot_api.reply_message(reply_token,TextSendMessage(text=help_message))

def reply_keyword(reply_token,message_text):
    if message_text in keyword_dict:
        url_keyword = keyword_dict[message_text]
    elif message_text in dog_dict:
        url_keyword = dog_dict[message_text]
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_keyword, preview_image_url=url_keyword))

def reply_dog_card(reply_token):
    url_keyword = random.choice(list(dog_dict.values()))
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_keyword, preview_image_url=url_keyword))

def reply_sticker(reply_token,message_text):
    sitcker_ID = sticker_dict[message_text]
    line_bot_api.reply_message(reply_token, StickerSendMessage(package_id=11537, sticker_id=sitcker_ID))

def reply_porn(reply_token,message_text):
    input_url = "https://www.xvideos.com/?k=" + message_text + "&sort=relevance&quality=hd"
    r = requests.get(input_url, headers=headers_postman)
    soup = BeautifulSoup(r.text, 'html.parser')
    video_all = soup.find_all('div',class_="thumb")
    video = str(video_all[random.randint(1,27)])
    input_url = "https://www.xvideos.com" + video[video.find('href')+6:video.find('">',20)]
    r = requests.get(input_url, headers=headers_postman)
    video = r.text
    output_url = video[video.find('setVideoUrlHigh')+17:video.find("')",video.find('setVideoUrlHigh'))]
    picture_url = video[video.find('setThumbUrl169')+16:video.find("')",video.find('setThumbUrl169'))]
    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=picture_url))

def reply_xvideos(reply_token,message_text):
    input_url = message_text
    r = requests.get(input_url, headers=headers_postman)
    video = r.text
    output_url = video[video.find('setVideoUrlHigh')+17:video.find("')",video.find('setVideoUrlHigh'))]
    picture_url = video[video.find('setThumbUrl169')+16:video.find("')",video.find('setThumbUrl169'))]
    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=picture_url))

def reply_douyin(reply_token,message_text):
    ## url preprocessing
    if message_text.find("v.douyin.com")!= -1:
        input_url = message_text[message_text.find('http'):message_text.find("/",message_text.find('http')+21)+1]
        redirect_url = requests.get(input_url,headers=headers_hastag).url
        item_ids = redirect_url[redirect_url.find("video")+6:redirect_url.find("?")]
    else:
        redirect_url = message_text[message_text.find('http'):]
        item_ids = redirect_url[redirect_url.find("video")+6:redirect_url.find("?")]
    redirect_url = redirect_url[0:redirect_url.find("?")]
    r = requests.get(redirect_url,headers=headers_hastag)
    input_url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids={item_ids}"
    r = requests.get(input_url,headers=headers_hastag)
    output_url = r.json()['item_list'][0]['video']['play_addr']['url_list'][0]
    picture_url = r.json()['item_list'][0]['video']['cover']['url_list'][0]
    # picture_url = picture_url.replace("300x400","540x960")
    r = requests.get(picture_url)
    if r.text.find("Fail to handle imagesite request")>1:
        picture_url = picture_url.replace("540x960","300x400")
    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=picture_url))

def reply_tiktok(reply_token,message_text):
    r = requests.get(message_text,headers=headers_tiktok)
    r_text = r.text
    video_url = r_text[r_text.find('playAddr')+11:r_text.find('downloadAddr')-3]
    video_url = video_url.encode('utf-8').decode("unicode_escape")
    picture_url = r_text[r_text.find('originCover')+14:r_text.find('dynamicCover')-3]
    picture_url = picture_url.encode('utf-8').decode("unicode_escape")
    headers_tiktok_referer = {"referer":f"{video_url}"}
    r = requests.get(video_url,headers=headers_tiktok_referer)
    ts = str(time()).replace(".","")
    temp_path = f"{pyPath}/media/tiktok/{ts}.mp4"
    with open(temp_path, 'wb') as f: 
        for chunk in r.iter_content(chunk_size = 1024*1024): 
            if chunk: 
                f.write(chunk) 
    warehouse_url = f"https://iufans.club/warehouse/tiktok/{ts}"
    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=warehouse_url,preview_image_url=picture_url))

def reply_IG(reply_token,chat_room,message_text):
    ## url preprocessing
    if message_text[0:22] == "https://instagram.com/":
        message_text = f"https://www.{message_text[8:]}"
    ## picture, video of post
    if  message_text[0:28] == "https://www.instagram.com/p/" or message_text[0:31] == "https://www.instagram.com/reel/": # Instagram
        if message_text[0:31] == "https://www.instagram.com/reel/":
            message_text = message_text.replace("/reel/","/p/")
        shortcode = message_text[28:message_text.find("/",28)]
        sub_page = f"https://www.instagram.com/p/{shortcode}/"
        # log.info(sub_page)
        ## loging test
        Login_test = 0
        print(headers_IG)
        while Login_test != -1:
            try:
                r = requests.get(sub_page,headers=headers_IG)
                Login_test = r.text.find("Login • Instagram")
            except:
                Login_test = 0
        # log.info(r.text)
        ## get IG_post_title
        IG_post_title = r.text[r.text.find("<title>")+7:r.text.find("</title>")]
        if len(IG_post_title) == 0:
            IG_post_title = "_"
        else:
            IG_post_title = IG_post_title[IG_post_title.find(":")+2:].replace("\n","")
        ## get all picture
        url_list =[]
        start = 0
        for _ in range(1,12):
            if start != 13:
                start = r.text.find("display_url",start)+14
            else:
                pass
            if start != 13:
                end = r.text.find("display_resources",start)-3
                url_list.append(r.text[start:end].replace("\\u0026","&"))
            else:
                pass
        ## reply multi-picture
        if len(url_list)>2:
            bubble_container = []
            for i in range(1,len(url_list)):
                if i == 1:
                    container = BubbleContainer(
                        size="giga",
                        body=BoxComponent(
                            layout='vertical',
                            margin="none",
                            padding_all="0px",
                            contents=[
                                ImageComponent(
                                    url=url_list[i],size='full',
                                    aspect_mode='cover',
                                    aspect_ratio="1:1",
                                    action=URIAction(uri=url_list[i])
                                ),
                                BoxComponent(
                                    layout='vertical',
                                    contents=[
                                        TextComponent(
                                            text=IG_post_title,
                                            size="xs",
                                            color="#ffffff",
                                            wrap=True,
                                        )
                                    ],
                                    background=LinearGradientBackground(angle="0deg",start_color="#00000099", end_color="#00000000"),
                                    position="absolute",
                                    width="100%",
                                    height="12%",
                                    offset_bottom="0px",
                                    offset_start="0px",
                                    offset_end="0px",
                                )
                            ]
                        )
                    ) 
                    bubble_container.append(container)
                else:
                    container = BubbleContainer(size="giga",hero=ImageComponent(url=url_list[i],size='full',aspect_mode='cover',action=URIAction(uri=url_list[i])))
                    bubble_container.append(container)
            line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
        ## reply single picture
        else:
            bubble_container = []
            container = BubbleContainer(
                size="giga",
                body=BoxComponent(
                    layout='vertical',
                    margin="none",
                    padding_all="0px",
                    contents=[
                        ImageComponent(
                            url=url_list[0],size='full',
                            aspect_mode='cover',
                            aspect_ratio="1:1",
                            action=URIAction(uri=url_list[0])
                        ),
                        BoxComponent(
                            layout='vertical',
                            contents=[
                                TextComponent(
                                    text=IG_post_title,
                                    size="xs",
                                    color="#ffffff",
                                    wrap=True,
                                )
                            ],
                            background=LinearGradientBackground(angle="0deg",start_color="#00000099", end_color="#00000000"),
                            position="absolute",
                            width="100%",
                            height="12%",
                            offset_bottom="0px",
                            offset_start="0px",
                            offset_end="0px",
                        )
                    ]
                )
            ) 
            bubble_container.append(container)
            line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
        ## get all video
        video = 0
        video = r.text.find('video_url":')
        start = 0
        if video != -1:
            video_count = r.text.count('video_url')
            for _ in range(video_count):
                ## video thumbnail
                pic_start = r.text.find('display_url":"',start) + 14
                pic_end = r.text.find(',"display_resources"',start)-1
                picture_url = r.text[pic_start:pic_end].replace("\\u0026","&")
                ## video url
                start = r.text.find('video_url":',start)+12
                end = r.text.find('"video_view_count"',start)-2
                url_video = r.text[start:end].replace("\\u0026","&")
                line_bot_api.push_message(chat_room,VideoSendMessage(original_content_url=url_video,preview_image_url=picture_url))
    ## picture, video  of story
    elif  message_text[0:34] == "https://www.instagram.com/stories/": # IG time limit
        story_num = message_text[message_text.find("/",34)+1:message_text.find("?")]
        input_url = message_text[0:message_text.find("/",34)+1] + story_num
        r = requests.get(input_url,headers=headers_IG).text
        reel_start = r.find(':{"id":')+8
        reel_end = r.find(',"profile_pic_url":')-1
        reel_ids = str(r[reel_start:reel_end])
        hash_IG = "5ec1d322b38839230f8e256e1f638d5f" #5/20
        query_url = f"https://www.instagram.com/graphql/query/?query_hash={hash_IG}&variables=%7B%22reel_ids%22%3A%5B%22{reel_ids}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%2C%22show_story_viewer_list%22%3Atrue%2C%22story_viewer_fetch_count%22%3A200%2C%22story_viewer_cursor%22%3A%22%22%2C%22stories_video_dash_manifest%22%3Afalse%7D"
        IG_story_finder = -1
        for _ in range(10):
            if IG_story_finder == -1:
                try:
                    r = requests.get(query_url,headers=headers_IG)
                    IG_story_finder = r.text.find("X-UA-Compatible")
                    IG_items = []
                    stories_nums = len(r.json()['data']['reels_media'][0]['items'])
                    for i in range(stories_nums):
                        IG_items.append(r.json()['data']['reels_media'][0]['items'][i]['id'])
                    story_num = IG_items.index(story_num)
                    try:
                        v_or_p = 1
                        output_url = r.json()['data']['reels_media'][0]['items'][story_num]['video_resources'][1]['src']
                        picture_url = r.json()['data']['reels_media'][0]['items'][story_num]['display_url']
                    except:
                        try:
                            v_or_p = 1
                            output_url = r.json()['data']['reels_media'][0]['items'][story_num]['video_resources'][0]['src']
                            picture_url = r.json()['data']['reels_media'][0]['items'][story_num]['display_url']
                        except:
                            v_or_p = 2
                            output_url = r.json()['data']['reels_media'][0]['items'][story_num]['display_url']
                            picture_url = output_url
                    if v_or_p ==1:
                        line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=picture_url))
                    else:
                        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url=output_url,preview_image_url=picture_url))
                except:
                    pass
    ## video of TV
    elif  message_text[0:29] == "https://www.instagram.com/tv/": # IG time limit
        url_num = 5
        Main_page = message_text
        r=requests.get(Main_page,headers=headers_IG)
        start = 0
        ## video thumbnail
        pic_start = r.text.find('display_url":"',start) + 14
        pic_end = r.text.find(',"display_resources"',start)-1
        picture_url = r.text[pic_start:pic_end].replace("\\u0026","&")
        ## video url
        start = r.text.find('video_url":',start)+12
        end = r.text.find('"video_view_count"',start)-2
        url_video = r.text[start:end].replace("\\u0026","&")
        line_bot_api.push_message(chat_room,VideoSendMessage(original_content_url=url_video,preview_image_url=picture_url))
    ## picture of user
    elif  message_text[0:26] == "https://www.instagram.com/":
        url_num = 5
        Main_page = message_text
        r=requests.get(Main_page, headers=headers_IG)
        start_main = r.text.find('content="https://instagram')+9
        end_main = r.text.find('"',start_main)
        main_url = r.text[start_main:end_main]
        start = 0
        bubble_container = []
        tag_num = r.text.count("shortcode")
        post_list = []
        post_codes = []
        likecount_list = []
        likecount_nums =[]
        for _ in range(tag_num):
            start = r.text.find("shortcode",start)+12
            end = start +11
            shortcode = r.text[start:end].replace('"',"")
            post_list.append(shortcode)
            start_like = r.text.find("edge_liked_by",start)+24
            end_like = r.text.find("}",r.text.find("edge_liked_by",start)+24)
            try:
                post_like = int(r.text[start_like:end_like])
            except:
                post_like = 9999999999
            likecount_list.append(post_like)
        for likecount_index, _ in enumerate(likecount_list):
            try:
                if likecount_list[likecount_index] != likecount_list[likecount_index+1]:
                    likecount_nums.append(likecount_list[likecount_index])
                    post_codes.append(post_list[likecount_index])
            except:
                if likecount_list[likecount_index] != likecount_list[0]:
                    likecount_nums.append(likecount_list[likecount_index])
                    post_codes.append(post_list[likecount_index])
        if len(post_codes) > url_num :
            loop_times = url_num
        else:
            loop_times = len(post_codes)
        container = BubbleContainer(size="giga",hero=ImageComponent(url=main_url,size='full',aspect_mode='cover',action=URIAction(uri=main_url)))
        bubble_container.append(container)
        for opt_num in range(loop_times):
            shortcode = post_codes[opt_num]
            sub_page = f"https://www.instagram.com/p/{shortcode}/"
            r_2 =requests.get(sub_page,headers=headers_IG)
            start = 0
            start = r_2.text.find("display_url",start)+14
            end = r_2.text.find(",",start)-1
            url_tag = r_2.text[start:end].replace("\\u0026","&")
            container = BubbleContainer(size="giga",hero=ImageComponent(url=url_tag,size='full',aspect_mode='cover',action=URIAction(uri=url_tag)))
            bubble_container.append(container)
        line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))    

def reply_hashtag(reply_token,message_text):
    Main_page = f"https://www.instagram.com/explore/tags/{message_text}/"
    url_num = 10
    r=requests.get(Main_page,headers=headers_hastag)
    start = 0
    bubble_container = []
    tag_num = r.text.count("display_url")
    post_list = []
    display_url_list = []
    likecount_list = []
    if tag_num != 0:
        for i in range(tag_num):
            start = r.text.find("display_url",start)+14
            end = r.text.find("edge_liked_by",start)-3
            display_url = r.text[start:end].replace('"',"").replace('\\u0026',"&")
            display_url_list.append(display_url)
            start_like = r.text.find("edge_liked_by",start)+24
            end_like = r.text.find("}",r.text.find("edge_liked_by",start)+24)
            post_like = int(r.text[start_like:end_like])
            likecount_list.append(post_like)
        for post_index, post_code in enumerate(display_url_list):
            if display_url_list.count(post_code) > 1:
                display_url_list.remove(display_url_list[post_index])
                likecount_list.remove(likecount_list[post_index])
        if len(display_url_list) > url_num :
            loop_times = url_num
        else:
            loop_times = len(display_url_list)
        for opt_num in range(loop_times):
            display_url = display_url_list[likecount_list.index(max(likecount_list))]
            display_url_list.remove(display_url_list[likecount_list.index(max(likecount_list))])
            likecount_list.remove(max(likecount_list))
            container = BubbleContainer(size="giga",hero=ImageComponent(url=display_url,size='full',aspect_mode='cover',action=URIAction(uri=display_url)))
            bubble_container.append(container)
        line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
    else:
        line_bot_api.reply_message(reply_token,TextSendMessage(text="無此Tag"))

def repky_FB(reply_token,message_text):
    r = requests.get(message_text)
    if r.text.find("hd_src") != -1:
        output_url = re.search('hd_src:"(.+?)"', r.text).group(1)
        display_url = re.search('spriteIndexToURIMap:{(.+?)}', r.text)[1]
        display_url = display_url[5:display_url.find(",")].replace(",","").replace('"',"")
        line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=display_url))
    else:
        start = r.text.find("og:image")+19
        end = r.text.find(" />",start+1)-1
        output_url =  r.text[start:end]
        output_url = output_url.replace("&amp;","&")
        display_url = output_url
        print(output_url)
        print(display_url)
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url=output_url,preview_image_url=display_url))

def reply_Youtube(reply_token,message_text):
    input_url = message_text
    yt = YouTube(input_url)
    output_url = yt.streams[0].url
    if input_url.find('youtube') != -1:
        start = input_url.find("v=")+2
        end =start +11
        display_url = f"https://i.ytimg.com/vi/{input_url[start:end]}/0.jpg"
    else:
        start = input_url.find(".be/")+4
        end =start +11
        display_url = f"https://i.ytimg.com/vi/{input_url[start:end]}/0.jpg"
    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=display_url),True)

def reply_ptt(reply_token,message_text):
    if message_text.find('www.ptt.cc') != -1:
        message_text = message_text[message_text.find('https'):message_text.find('.html')+5]
        message_text = message_text.replace(".html","").replace("/",".").replace("https:..www.ptt.cc.bbs.","https://moptt.tw/p/")
    input_url = message_text
    input_url =input_url.replace('/p/','/ptt/')
    bubble_container =[]
    output_url = json.loads(requests.get(input_url).text)
    loop_times = output_url['content'].count('imgur')
    if loop_times >10: 
        loop_times = 10
    start = 0
    for _ in range(loop_times):
        start = output_url['content'].find('http',start+1)
        end = output_url['content'].find('\n',start)
        if output_url['content'][start:end].find('.gif') == -1:
            if output_url['content'][start:end].find('i.imgur') == -1:
                url_out = output_url['content'][start:end].replace("imgur","i.imgur") + ".jpg"
            else:
                url_out = output_url['content'][start:end]
            if url_out.find('https')== -1:
                url_out = url_out.replace('http','https')
            container = BubbleContainer(size="giga",hero=ImageComponent(url=url_out,size='full',aspect_mode='cover',action=URIAction(uri=url_out)))
            bubble_container.append(container)
    line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))

def reply_twitter(reply_token,message_text):
    url = "https://www.expertsphp.com/instagram-reels-downloader.php"
    data_1 = {'url': message_text}
    r = requests.post(url, data=data_1)
    url_out = r.text[r.text.find('src="http://pbs')+5:r.text.find('.jpg',r.text.find('src="http://pbs'))+4]
    if url_out.find('https')== -1:
        url_out = url_out.replace('http','https')
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))

def reply_imgur(reply_token,message_text):
    # error
    url_out = message_text
    if url_out.find('https') == -1:
        url_out = url_out.replace('http','https')
    if url_out.find('m.imgur.com') != -1:
        url_out = url_out.replace('m.imgur.com','i.imgur.com')
        url_out = url_out + ".jpg"
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))

def IU_call_love_list(reply_token,chat_room):
    iu_love_list = iu_love_table.objects.all().order_by("id")
    bubble_container = []
    for table_id, table_object in enumerate(iu_love_list): # table_id start from 0
        container = BubbleContainer(size="giga",hero=ImageComponent(url=table_object.url,size='full',aspect_mode='cover',action=URIAction(uri=table_object.url)))
        bubble_container.append(container)
        if (table_id % 10) == 9 or table_id == len(iu_love_list)-1:
            line_bot_api.push_message(chat_room,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
            bubble_container =[]

def IU_call_random_pic(reply_token):
    iu_list = iu_table.objects.all().order_by("id")
    chose_id = random.randint(0,len(iu_list))
    url_out = iu_list[chose_id].url
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))
                
def reply_yuyan(reply_token):
    yuyan_list = yuyan_table.objects.all().order_by("id")
    chose_id = random.randint(0,len(yuyan_list))
    url_out = yuyan_list[chose_id].url
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))
    
def reply_double_word_pic(reply_token, message_text):
    if message_text == "MM":
        double_word_table = mm_table
    elif message_text == "OO":
        double_word_table = oo_table
    elif message_text == "CC":
        double_word_table = cc_table
    elif message_text == "PP":
        double_word_table = pp_table
    double_word_list = double_word_table.objects.all().order_by("id")
    package_num = int(double_word_list[0].package)
    if package_num == int(double_word_list[len(double_word_list)-1].package):
        package_num = int(double_word_list[len(double_word_list)-1].package)
        # package_num = 1
    else:
        package_num = package_num + 1
    picture_list = double_word_table.objects.filter(package=package_num).order_by("id")
    bubble_container = []
    for num, picture in enumerate(picture_list):
        picture_text = picture.package_name
        if num == 0 :
            container = BubbleContainer(
                size="giga",
                body=BoxComponent(
                    layout='vertical',
                    margin="none",
                    padding_all="0px",
                    contents=[
                        ImageComponent(
                            url=picture.url,size='full',
                            aspect_mode='cover',
                            aspect_ratio="1:1",
                            action=URIAction(uri=picture.url)
                        ),
                        BoxComponent(
                            layout='vertical',
                            contents=[
                                TextComponent(
                                    text=picture_text,
                                    size="xs",
                                    color="#ffffff",
                                    wrap=True,
                                )
                            ],
                            background=LinearGradientBackground(angle="0deg",start_color="#00000099", end_color="#00000000"),
                            position="absolute",
                            width="100%",
                            height="10%",
                            offset_bottom="0px",
                            offset_start="0px",
                            offset_end="0px",
                        )
                    ]
                )
            )
        else:
            container = BubbleContainer(size="giga",hero=ImageComponent(url=picture.url,size='full',aspect_mode='cover',action=URIAction(uri=picture.url)))
        bubble_container.append(container)
    line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
    double_word_table.objects.filter(id=0).update(package=package_num)

def reply_9gag(reply_token, message_text):
    if message_text == "9FUN":
        ngag_table = ngag_funny_table
    elif message_text == "9GIRL":
        ngag_table = ngag_girl_table
    elif message_text == "9HOT":
        ngag_table = ngag_nsfw_table
    ngag_list = ngag_table.objects.all().order_by("id")
    row_id = int(ngag_list[0].article_id)
    if row_id == int(ngag_list[len(ngag_list)-1].id):
        row_id = int(ngag_list[len(ngag_list)-1].id)
        # package_num = 1
    else:
        row_id = row_id + 1
    ngag_row = ngag_table.objects.get(id=row_id)
    if ngag_row.article_type == "mp4":
        video_url = f"https://img-9gag-fun.9cache.com/photo/{ngag_row.article_id}_460sv.mp4"
        display_url = f"https://img-9gag-fun.9cache.com/photo/{ngag_row.article_id}_700b.jpg"
        line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=video_url,preview_image_url=display_url))
        ngag_table.objects.filter(id=0).update(article_id=row_id)
    else:
        display_url = f"https://img-9gag-fun.9cache.com/photo/{ngag_row.article_id}_460s.jpg"
        display_url = f"https://img-9gag-fun.9cache.com/photo/{ngag_row.article_id}_700b.jpg"
        bubble_container = []
        container = BubbleContainer(
            size="giga",
            body=BoxComponent(
                layout='vertical',
                margin="none",
                padding_all="0px",
                contents=[
                    ImageComponent(
                        url=display_url,
                        size='full',
                        action=URIAction(uri=display_url),
                    ),
                    BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(
                                text=ngag_row.article_title,
                                size="xs",
                                color="#ffffff",
                                wrap=True,
                                offset_start="60px",
                                position="absolute",
                            )
                        ],
                        background=LinearGradientBackground(angle="0deg",start_color="#00000099", end_color="#00000000"),
                        position="absolute",
                        width="100%",
                        height="10%",
                        offset_bottom="0px",
                        offset_start="0px",
                        offset_end="0px",
                    )
                ]
            )
        )
        bubble_container.append(container)
        line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Multiple pictures",contents=CarouselContainer(contents=bubble_container)))
        ngag_table.objects.filter(id=0).update(article_id=row_id)

def reply_for_ccc(reply_token):
    ccc_list = ccc_table.objects.all().order_by("id")
    chose_id = random.randint(0,len(ccc_list))
    url_out = ccc_list[chose_id].url
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))
        
def reply_for_cccc(reply_token):
    cccc_list = cccc_table.objects.all().order_by("id")
    chose_id = random.randint(0,len(cccc_list))
    url_out = cccc_list[chose_id].url
    line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url_out, preview_image_url=url_out))
        
def dict_translator(reply_token, message_text):
    trans_bf = message_text[3:]
    if trans_bf.upper() == "IU":
        trans_bf = "angel"
    dictionary = PyDictionary()
    meaning = dictionary.meaning(trans_bf)
    meaning_list =[]
    try:
        meaning_list.append("名詞 : " + meaning['Noun'][0])
    except:
        pass
    try:
        meaning_list.append("動詞 : " + meaning['Verb'][0])
    except:
        pass
    try:
        meaning_list.append("形容詞 : " + meaning["Adjective"][0])
    except:
        pass
    try:    
        meaning_list.append("副詞 : " + meaning["Adverb"][0])
    except:
        pass
    # print(meaning_list)
    syn_str = "同義詞 : "
    try:
        syn = dictionary.synonym(trans_bf)
        for iii in range(len(syn)):
            syn_str = syn_str + syn[iii] + ", "
            if iii == 5:
                break
    except:
        syn_str =  "同義詞 : 沒有同義詞, "
    syn_str = syn_str[:len(syn_str)-2]
    ant_str = "反義詞 : "
    try:
        ant = dictionary.antonym(trans_bf)
        for iii in range(len(ant)):
            ant_str = ant_str + ant[iii] + ", "
            if iii == 5:
                break
    except:
        ant_str = "反義詞 : 沒有反義詞, "
    ant_str = ant_str[:len(ant_str)-2] 
    out_str = ""
    for ii in range(len(meaning_list)):    
        out_str = out_str + meaning_list[ii] + '\n'
    out_str = trans_bf + '\n' + out_str + syn_str + '\n' + ant_str
    # print(out_str)
    line_bot_api.reply_message(reply_token,TextSendMessage(text=out_str))

def weather(reply_token, message_text):
    Authorization = "CWB-7DBEB9CD-CC73-4483-8615-B05C5CE54979"
    if len(message_text) == 6:
        message_text = message_text.replace("台","臺")
        city_message_text = message_text[:2]
        loc_message_text = message_text[2:4]
        print(city_message_text)
        print(loc_message_text)
        for item in cityLocations:
            if city_message_text == "宜蘭" and loc_message_text == "宜蘭":
                city = "宜蘭縣"
                location = "宜蘭市"
                city_code = city_encoding[city]
                break
            elif city_message_text in item and loc_message_text in item:
                city_code = city_encoding[item[:3]]
                city = item[:3]
                location = item[3:]
                break
    else:
        message_text = message_text[:2].replace("台","臺")
        print(message_text)
        city_counter = 0
        city_start = 0
        for item in cityLocations:
            if item[:3].find(message_text) == 0:
                city_counter = city_counter + 1
        for item in cityLocations:
            if message_text in item:
                if item.find(message_text) < 2:
                    print(item)
                    city_code = city_encoding[item[:3]]
                    city = item[:3]
                    print(city_start,city_counter)
                    location = cityLocations[city_start+random.randint(0,city_counter-1)][3:]
                    print(item,city,location,city_code)
                else:
                    print(item)
                    city_code = city_encoding[item[:3]]
                    city = item[:3]
                    location = item[3:]
                break
            city_start = city_start + 1
    w_page = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/{city_code}?Authorization={Authorization}&locationName={location}"
    # print(w_page)
    r = json.loads(requests.get(w_page).text)
    rain_1_start = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][0]['startTime'][11:13])
    if int(rain_1_start) > 11:
        rain_1_daytime = "晚上"
        rain_2_daytime = "白天"
        rain_3_daytime = "晚上"
        rain_4_daytime = "早上"
    else:
        rain_1_daytime = "早上"
        rain_2_daytime = "晚上"
        rain_3_daytime = "早上"
        rain_4_daytime = "晚上"
    if rain_1_start == "00":
        rain_1_daytime = "凌晨"
        rain_2_daytime = "早上"
        rain_3_daytime = "晚上"
        rain_4_daytime = "早上"
    rain_1_day = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][0]['startTime'][5:10])
    rain_1_day = f"{rain_1_day[0:2]}/{rain_1_day[3:]}"
    rain_2_day = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][1]['startTime'][5:10])
    rain_2_day = f"{rain_2_day[0:2]}/{rain_2_day[3:]}"
    rain_3_day = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][2]['startTime'][5:10])
    rain_3_day = f"{rain_3_day[0:2]}/{rain_3_day[3:]}"
    rain_4_day = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][3]['startTime'][5:10])
    rain_4_day = f"{rain_4_day[0:2]}/{rain_4_day[3:]}"
    rain_1_po = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][0]['elementValue'][0]['value'])
    rain_2_po = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][1]['elementValue'][0]['value'])
    rain_3_po = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][2]['elementValue'][0]['value'])
    rain_4_po = str(r['records']['locations'][0]['location'][0]['weatherElement'][0]['time'][3]['elementValue'][0]['value'])
    temp_1 = str(r['records']['locations'][0]['location'][0]['weatherElement'][1]['time'][0]['elementValue'][0]['value'])
    temp_2 = str(r['records']['locations'][0]['location'][0]['weatherElement'][1]['time'][1]['elementValue'][0]['value'])
    temp_3 = str(r['records']['locations'][0]['location'][0]['weatherElement'][1]['time'][2]['elementValue'][0]['value'])
    temp_4 = str(r['records']['locations'][0]['location'][0]['weatherElement'][1]['time'][3]['elementValue'][0]['value'])
    wind_1 = str(r['records']['locations'][0]['location'][0]['weatherElement'][4]['time'][0]['elementValue'][0]['value'])
    wind_2 = str(r['records']['locations'][0]['location'][0]['weatherElement'][4]['time'][1]['elementValue'][0]['value'])
    wind_3 = str(r['records']['locations'][0]['location'][0]['weatherElement'][4]['time'][2]['elementValue'][0]['value'])
    wind_4 = str(r['records']['locations'][0]['location'][0]['weatherElement'][4]['time'][3]['elementValue'][0]['value'])
    wind_1_d = str(r['records']['locations'][0]['location'][0]['weatherElement'][13]['time'][0]['elementValue'][0]['value'])
    wind_2_d = str(r['records']['locations'][0]['location'][0]['weatherElement'][13]['time'][1]['elementValue'][0]['value'])
    wind_3_d = str(r['records']['locations'][0]['location'][0]['weatherElement'][13]['time'][2]['elementValue'][0]['value'])
    wind_4_d = str(r['records']['locations'][0]['location'][0]['weatherElement'][13]['time'][3]['elementValue'][0]['value'])
    wx_1 = str(r['records']['locations'][0]['location'][0]['weatherElement'][6]['time'][0]['elementValue'][0]['value'])
    wx_2 = str(r['records']['locations'][0]['location'][0]['weatherElement'][6]['time'][1]['elementValue'][0]['value'])
    wx_3 = str(r['records']['locations'][0]['location'][0]['weatherElement'][6]['time'][2]['elementValue'][0]['value'])
    wx_4 = str(r['records']['locations'][0]['location'][0]['weatherElement'][6]['time'][3]['elementValue'][0]['value'])
    if len(wx_1)<6:
        wx_1_1 = wx_1[0:3]
        wx_1_2 = wx_1[3:]
        wx_1_3 = " "
        wx_1_4 = " "
    else:
        wx_1_1 = wx_1[0:3]
        wx_1_2 = wx_1[3:6]
        wx_1_3 = wx_1[6:]
        if len(wx_1_3) > 3:
            wx_1_3 = wx_1[6:9]
            wx_1_4 = wx_1[9:]
        else:
            wx_1_4=" "
    if len(wx_2)<6:
        wx_2_1 = wx_2[0:3]
        wx_2_2 = wx_2[3:]
        wx_2_3 = " "
        wx_2_4 = " "
    else:
        wx_2_1 = wx_2[0:3]
        wx_2_2 = wx_2[3:6]
        wx_2_3 = wx_2[6:]
        if len(wx_2_3) > 3:
            wx_2_3 = wx_2[6:9]
            wx_2_4 = wx_2[9:]
        else:
            wx_2_4=" "
    if len(wx_3)<6:
        wx_3_1 = wx_3[0:3]
        wx_3_2 = wx_3[3:]
        wx_3_3 = " "
        wx_3_4 = " "
    else:
        wx_3_1 = wx_3[0:3]
        wx_3_2 = wx_3[3:6]
        wx_3_3 = wx_3[6:]
        if len(wx_3_3) > 3:
            wx_3_3 = wx_3[6:9]
            wx_3_4 = wx_3[9:]
        else:
            wx_3_4=" "
    if len(wx_4)<6:
        wx_4_1 = wx_4[0:3]
        wx_4_2 = wx_4[3:]
        wx_4_3 = " "
        wx_4_4 = " "
    else:
        wx_4_1 = wx_4[0:3]
        wx_4_2 = wx_4[3:6]
        wx_4_3 = wx_4[6:]
        if len(wx_4_3) > 3:
            wx_4_3 = wx_4[6:9]
            wx_4_4 = wx_4[9:]
        else:
            wx_4_4=" "
    bubble_container=[]
    container = BubbleContainer(
        size="giga",
        body=BoxComponent(
            layout='vertical',
            margin="none",
            contents=[
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"{city}", size='sm',margin="none"),
                        TextComponent(text=f"{rain_1_day}", size='sm'),
                        TextComponent(text=f"{rain_2_day}", size='sm'),
                        TextComponent(text=f"{rain_3_day}", size='sm'),
                        TextComponent(text=f"{rain_4_day}", size='sm'),

                    ]
                ),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                    TextComponent(text=f"{location}", size='sm',margin="none"),
                        TextComponent(text=f"{rain_1_daytime}", size='sm'),
                        TextComponent(text=f"{rain_2_daytime}", size='sm'),
                        TextComponent(text=f"{rain_3_daytime}", size='sm'),
                        TextComponent(text=f"{rain_4_daytime}", size='sm'),

                    ]
                ),
                SeparatorComponent(margin="sm"),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"降雨機率", size='sm'),
                        TextComponent(text=f"{rain_1_po}%", size='sm'),
                        TextComponent(text=f"{rain_2_po}%", size='sm'),
                        TextComponent(text=f"{rain_3_po}%", size='sm'),
                        TextComponent(text=f"{rain_4_po}%", size='sm'),
                    ]
                ),
                SeparatorComponent(margin="sm"),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"氣溫", size='sm'),
                        TextComponent(text=f"{temp_1}℃", size='sm'),
                        TextComponent(text=f"{temp_2}℃", size='sm'),
                        TextComponent(text=f"{temp_3}℃", size='sm'),
                        TextComponent(text=f"{temp_4}℃", size='sm'),
                    ]
                ),
                SeparatorComponent(margin="sm"),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"風力", size='sm'),
                        TextComponent(text=f"{wind_1}", size='sm'),
                        TextComponent(text=f"{wind_2}", size='sm'),
                        TextComponent(text=f"{wind_3}", size='sm'),
                        TextComponent(text=f"{wind_4}", size='sm'),
                    ]
                ),
                SeparatorComponent(margin="sm"),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"風向", size='sm'),
                        TextComponent(text=f"{wind_1_d}", size='sm'),
                        TextComponent(text=f"{wind_2_d}", size='sm'),
                        TextComponent(text=f"{wind_3_d}", size='sm'),
                        TextComponent(text=f"{wind_4_d}", size='sm'),
                    ]
                ),
                SeparatorComponent(margin="sm"),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f" ", size='sm'),
                        TextComponent(text=f"{wx_1_1} ", size='sm'),
                        TextComponent(text=f"{wx_2_1} ", size='sm'),
                        TextComponent(text=f"{wx_3_1} ", size='sm'),
                        TextComponent(text=f"{wx_4_1} ", size='sm'),
                    ]
                ),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f"概況", size='sm'),
                        TextComponent(text=f"{wx_1_2} ", size='sm'),
                        TextComponent(text=f"{wx_2_2} ", size='sm'),
                        TextComponent(text=f"{wx_3_2} ", size='sm'),
                        TextComponent(text=f"{wx_4_2} ", size='sm'),
                    ]
                ),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f" ", size='sm'),
                        TextComponent(text=f"{wx_1_3} ", size='sm'),
                        TextComponent(text=f"{wx_2_3} ", size='sm'),
                        TextComponent(text=f"{wx_3_3} ", size='sm'),
                        TextComponent(text=f"{wx_4_3} ", size='sm'),
                    ]
                ),
                BoxComponent(
                    layout='baseline',
                    margin="sm",
                    contents=[
                        TextComponent(text=f" ", size='sm'),
                        TextComponent(text=f"{wx_1_4} ", size='sm'),
                        TextComponent(text=f"{wx_2_4} ", size='sm'),
                        TextComponent(text=f"{wx_3_4} ", size='sm'),
                        TextComponent(text=f"{wx_4_4} ", size='sm'),
                    ]
                ),
            ],
        )
    )
    bubble_container.append(container)
    line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text="Weather",contents=CarouselContainer(contents=bubble_container)))
    # line_bot_api.push_message(to,FlexSendMessage(alt_text="Weather",contents=CarouselContainer(contents=bubble_container)))

def wish(reply_token,user_id,user_name,message_text):
    pray_table.objects.create(user_id=user_id,user_name=user_name,pray_text=message_text)
    line_bot_api.reply_message(reply_token,TextSendMessage(text="願望收到囉 敬請期待"))

def hometown(reply_token,chat_room,message_text):
    try:
        point_num_request = int(message_text[9:])
    except:
        point_num_request = "error"
    if message_text[8:] == "":
        hometown_day_info_list = hometown_day_info_table.objects.get(id=0)
        line_bot_api.reply_message(reply_token,TextSendMessage(text=hometown_day_info_list.day_info))
    elif message_text[9:] == "早班" or message_text[9:] == "中班" or message_text[9:] == "晚班" or message_text[9:] == "新進":
        shift_request = message_text[9:]
        hometown_info_list = hometown_info_table.objects.all().order_by("id")
        hometown_history_list = hometown_history_table.objects.all().order_by("id")
        bubble_container=[]
        for item in hometown_info_list:
            image = item.url
            shift = item.shift
            point_num = item.id_num
            real_working_time = item.time
            body_language = item.body
            introduction = item.info
            history_exp = " "
            for item in hometown_history_list:
                id_num = item.id_num
                history = item.history
                if str(point_num) == str(id_num):
                    history_exp = f"exp: {history}"
            introduction_1 = " "
            introduction_2 = " "
            introduction_3 = " "
            if len(introduction[:18])>0:
                introduction_1 = introduction[:18]
            if len(introduction[18:36])>0:
                introduction_2 = introduction[18:36]
            if len(introduction[36:])>0:
                introduction_3 = introduction[36:]
            if shift in shift_request:
                container = BubbleContainer(
                    size="giga",
                    hero=ImageComponent(
                        url=image,
                        size='full',
                        aspect_mode='cover',
                        action=URIAction(
                            uri=image
                        )
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        margin="none",
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{point_num}", size='sm'),
                                ]
                            ),
                            SeparatorComponent(margin="md"),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{body_language}", size='sm'),
                                ]
                            ),
                            SeparatorComponent(margin="md"),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{introduction}", size='sm',wrap=True),
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{history_exp}", size='sm',wrap=True),
                                ]
                            ),
                        ],
                    )
                )
                bubble_container.append(container)
        working_total_num = len(bubble_container)
        quo = int(working_total_num / 10)
        remain = int(working_total_num % 10)
        for i in range(quo):
            if i == 0 :
                reply_bubble_container = bubble_container[i*10:i*10+10]
                line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text=shift_request,contents=CarouselContainer(contents=reply_bubble_container)))
            else:
                push_bubble_container = bubble_container[i*10:i*10+10]
                line_bot_api.push_message(chat_room,FlexSendMessage(alt_text=shift_request,contents=CarouselContainer(contents=push_bubble_container)))
        if remain != 0:
            push_bubble_container = bubble_container[quo*10:]
            line_bot_api.push_message(chat_room,FlexSendMessage(alt_text=shift_request,contents=CarouselContainer(contents=push_bubble_container)))
    elif str(point_num_request) != "error" and point_num_request <10000:
        try:
            point_num_request = int(message_text[9:])
            try:
                hometown_info_list = hometown_info_table.objects.get(id_num=point_num_request)
            except:
                hometown_info_list = "None"
            try:
                hometown_history_list = hometown_history_table.objects.get(id_num=point_num_request)
                hometown_history = hometown_history_list.history
            except:
                hometown_history= ""
            if hometown_info_list != "None":
                bubble_container=[]
                image = hometown_info_list.url
                shift = hometown_info_list.shift
                point_num = hometown_info_list.id_num
                real_working_time = hometown_info_list.time
                body_language = hometown_info_list.body
                introduction = hometown_info_list.info
                history_exp = f"exp: {hometown_history}"
                introduction_1 = " "
                introduction_2 = " "
                introduction_3 = " "
                if len(introduction[:18])>0:
                    introduction_1 = introduction[:18]
                if len(introduction[18:36])>0:
                    introduction_2 = introduction[18:36]
                if len(introduction[36:])>0:
                    introduction_3 = introduction[36:]
                container = BubbleContainer(
                    size="giga",
                    hero=ImageComponent(
                        url=image,
                        size='full',
                        aspect_mode='cover',
                        action=URIAction(
                            uri=image
                        )
                    ),
                    body=BoxComponent(
                        layout='vertical',
                        margin="none",
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{point_num}", size='sm'),
                                ]
                            ),
                            SeparatorComponent(margin="md"),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{body_language}", size='sm'),
                                ]
                            ),
                            SeparatorComponent(margin="md"),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{introduction}", size='sm'),
                                ]
                            ),
                            BoxComponent(
                                layout='baseline',
                                margin="md",
                                contents=[
                                    TextComponent(text=f"{history_exp}", size='sm',wrap=True),
                                ]
                            ),
                        ],
                    )
                )
                bubble_container.append(container)
                reply_bubble_container = bubble_container
                line_bot_api.reply_message(reply_token,FlexSendMessage(alt_text=point_num,contents=CarouselContainer(contents=reply_bubble_container)))
            else:
                reply_text = "Number not exist !"
                line_bot_api.reply_message(reply_token,TextSendMessage(text=reply_text))
        except:
            pass
    else:
            pass

def IU_fans_info(reply_token):
    url = "https://drive.google.com/file/d/0B7BRqa5AOBuHSlR1YWZiMVFONXM/view?usp=sharing"
    line_bot_api.reply_message(reply_token,TextSendMessage(text=url))

def reply_horoscope(reply_token,message_text):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    Main_page = f"https://astro.click108.com.tw/daily_{horoscope_dict[message_text]}.php?iAcDay={today}&iAstro={horoscope_dict[message_text]}"
    r = requests.get(Main_page,headers=headers_hastag)
    soup = BeautifulSoup(r.text, 'html.parser')
    today_content = soup.find('div',class_="TODAY_CONTENT")
    msg = ""
    for thing in today_content:
        if str(type(thing)) != "<class 'bs4.element.NavigableString'>":
            msg = f"{msg}{thing.text}\n"
    line_bot_api.reply_message(reply_token,TextSendMessage(text=msg))

def reply_weather(reply_token,message_text):
    if message_text == "radar":
        timestamp = datetime.datetime.now().timestamp()-60*10
        date_time = datetime.datetime.fromtimestamp(timestamp)
        hour_now = date_time.strftime('%H')
        mins_now = date_time.strftime('%M')
        mins_now = f"{mins_now[:1]}0"
        today = date_time.strftime('%Y%m%d')
        today = f"{today}{hour_now}{mins_now}"
        url = f"https://www.cwb.gov.tw/Data/radar/CV1_TW_3600_{today}.png"
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url, preview_image_url=url))
    elif message_text == "cloud":
        timestamp = datetime.datetime.now().timestamp()-60*30
        date_time = datetime.datetime.fromtimestamp(timestamp)
        hour_now = date_time.strftime('%H')
        mins_now = date_time.strftime('%M')
        mins_now = f"{mins_now[:1]}0"
        today = date_time.strftime('%Y-%m-%d')
        today = f"{today}-{hour_now}-{mins_now}"
        url = f"https://www.cwb.gov.tw/Data/satellite/TWI_VIS_TRGB_1375/TWI_VIS_TRGB_1375-{today}.jpg"
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url, preview_image_url=url))
    elif message_text == "rain":
        timestamp = datetime.datetime.now().timestamp()-60*20
        date_time = datetime.datetime.fromtimestamp(timestamp)
        hour_now = date_time.strftime('%H')
        mins_now = date_time.strftime('%M')
        mins_now = int(mins_now[:1])
        if mins_now > 3:
            mins_now = 3
        else:
            mins_now = 0
        mins_now = f"{mins_now}0"
        today = date_time.strftime('%Y-%m-%d')
        today = f"{today}_{hour_now}{mins_now}"
        url = f"https://www.cwb.gov.tw/Data/rainfall/{today}.QZT8.jpg"
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url, preview_image_url=url))
    elif message_text == "UV":
        url = "https://www.cwb.gov.tw/Data/UVI/UVI.png"
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url, preview_image_url=url))
    elif message_text == "temperature":
        timestamp = datetime.datetime.now().timestamp()-60*30
        date_time = datetime.datetime.fromtimestamp(timestamp)
        hour_now = date_time.strftime('%H')
        mins_now = f"00"
        today = date_time.strftime('%Y-%m-%d')
        today = f"{today}_{hour_now}{mins_now}"
        url = f"https://www.cwb.gov.tw/Data/temperature/{today}.GTP8.jpg"
        line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url= url, preview_image_url=url))

def yt_one(reply_token,message_text):
    results = YoutubeSearch(message_text, max_results=10).to_dict()
    video_url = f"https://www.youtube.com/watch?v={results[0]['id']}"
    line_bot_api.reply_message(reply_token,TextSendMessage(text=video_url))

def reply_password_info(reply_token, message_text):
    ## Loading the access token and secret for line bot
    with open(f"{str(pyPath)}/notion_secrets.json") as f:
        notion_secrets = json.load(f)
    notion_token = notion_secrets["token"]

    # set header
    headers = {
        "Authorization": "Bearer " + notion_token,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }
    db_name = "password_database"
    with open(f"{str(pyPath)}/notion_ID.json") as f:
        notion_ID_json = json.load(f)
        notion_ID = notion_ID_json[f"{db_name}"]
    readUrl = f"https://api.notion.com/v1/databases/{notion_ID}/query"
    r = requests.request("POST", readUrl, headers=headers)
    # log.info(r.text)
    r_json = r.json()
    service = []
    account = []
    password = []
    link= []
    if message_text == "ALL":
        line_bot_api.reply_message(reply_token,TextSendMessage(text=message_text))
    else:
        for item in r_json["results"]:
            if message_text in item["properties"]["service"]["title"][0]["text"]["content"].upper():
                service.append(item["properties"]["service"]["title"][0]["text"]["content"])
                account.append(item["properties"]["account"]["rich_text"][0]["text"]["content"])
                password.append(item["properties"]["password"]["rich_text"][0]["text"]["content"])
                link.append(item["properties"]["link"]["rich_text"][0]["text"]["content"])
                # log.info(item)
        if len(service) != 0:
            reply_text = ""
            for num, thing in enumerate(service):
                # print(link[num])
                reply_text = f"{reply_text}{service[num]}\n{account[num]}\n{password[num]}\n{link[num]}\n\n"
            line_bot_api.reply_message(reply_token,TextSendMessage(text=reply_text))
        else:
            reply_text = "empty"
            line_bot_api.reply_message(reply_token,TextSendMessage(text=reply_text))


## main reply function
def line_bot_receive(request):
    # print(request.body)
    # request_dict = request
    request_dict = json.loads(request.body.decode('utf-8'))
    # print_request_detail(request)
    reply_token = request_dict["events"][0].get("replyToken")
    group_id = request_dict["events"][0]["source"].get('groupId',"None")
    room_id = request_dict["events"][0]["source"].get('roomId',"None")
    user_id = request_dict["events"][0]["source"].get('userId')
    destination = request_dict.get("destination")
    events = request_dict.get("events")
    events_type = request_dict["events"][0].get("type")
    events_message = request_dict["events"][0].get("message")
    events_timestamp = request_dict["events"][0].get("timestamp")
    events_source = request_dict["events"][0].get("source")
    events_mode = request_dict["events"][0].get("mode")
    source_type = request_dict["events"][0]["source"].get('type')
    source_groupId = request_dict["events"][0]["source"].get('groupId',"None")
    source_roomId = request_dict["events"][0]["source"].get('roomId',"None")
    source_userId = request_dict["events"][0]["source"].get('userId')
    message_type = request_dict["events"][0]["message"].get("type")
    message_id = request_dict["events"][0]["message"].get("id")
    message_text = request_dict["events"][0]["message"].get("text","None")
    if message_text == "None":
        message_text = message_type
    if group_id != "None":
        chat_room = group_id
    elif room_id != "None":
        chat_room = room_id
    else:
        chat_room = user_id
    user_name = user_info_table.objects.get(user_id=user_id).user_name
    print(f"{user_name} : {message_text}")
    DB_update_chat_log(user_id,user_name,chat_room,message_text)

    ### if text message
    if message_type == "text":
        ### Call back start
        ## Help information
        if message_text.upper() == "HELP" or message_text.upper() == "-H": # Help for IU 
            reply_help(reply_token)
        ## keyword list
        elif message_text.upper() == "-H KEYWORD":
            reply_help_keyword(reply_token)
        ## sticker by keyword https://developers.line.biz/media/messaging-api/sticker_list.pdf
        elif message_text.upper() in sticker_dict:
            message_text = message_text.upper()
            reply_sticker(reply_token,message_text)
        ## picture by keyword
        elif message_text.upper() in keyword_dict or message_text.upper() in dog_dict:
            message_text = message_text.upper()
            if message_text == "???" or message_text == "？？？":
                if chat_room == "C6508e069898b95c1ab12da89894f595e":
                    message_text = "ball?"
            reply_keyword(reply_token,message_text)
        ## picture by dog keyword
        elif message_text == "色色":
            reply_dog_card(reply_token)
        ## video by porn keyword
        elif message_text[0:5].upper() == "PORN ":
            message_text = message_text[5:]
            reply_porn(reply_token,message_text)
        ## reply xvideos
        elif message_text[0:23] == "https://www.xvideos.com":
            reply_xvideos(reply_token,message_text)
        ## douyin
        elif message_text.find("douyin.com") != -1:
            reply_douyin(reply_token,message_text)
        ## tiktok
        elif message_text.find("tiktok.com") != -1:
            reply_tiktok(reply_token,message_text)
        ## instagram
        elif message_text.find("instagram") != -1:
            # if user_id == admin_id:
            reply_IG(reply_token,chat_room,message_text)

        ## 5 picture of hasgtag on IG
        elif message_text[0:1] == "#" and message_text[1:] != "":
            message_text = message_text[1:]
            reply_hashtag(reply_token,message_text)
        ## Facebook
        elif message_text[0:25] == "https://www.facebook.com/":
            message_text = message_text.strip('\n')
            repky_FB(reply_token,message_text)
        ## Youtube
        elif message_text.find("youtu") != -1:
            reply_Youtube(reply_token,message_text)
        ## MoPtt or Ptt image
        elif message_text.find('moptt') != -1 or message_text.find('www.ptt.cc') != -1 : 
            reply_ptt(reply_token,message_text)
        ## Twitter
        elif message_text.find('twitter.com')!= -1:
            reply_twitter(reply_token,message_text)
        ## Imgur
        elif message_text.find('imgur.com') != -1:
            reply_imgur(reply_token,message_text)
        ## call IU love list
        elif message_text.upper() == "IUU" or message_text.upper() == "UUU": 
            IU_call_love_list(reply_token,chat_room)
        ## call IU random list
        elif message_text.upper() == "IU" or message_text.upper() == "UU":
            IU_call_random_pic(reply_token)
        ## yuyan
        elif message_text == "彭于晏": 
            reply_yuyan(reply_token)
        ## double word picture
        elif message_text.upper() == "MM" or message_text.upper() == "PP" or message_text.upper() == "OO" or message_text.upper() == "CC": 
            message_text = message_text.upper()
            if message_text == "PP" and user_id not in IU_fans_club:
                message_text = "MM"
            reply_double_word_pic(reply_token,message_text)
        ## 9gag
        elif message_text.upper() == "9FUN" or message_text.upper() == "9GIRL" or message_text.upper() == "9HOT" or message_text.upper() == "99":
            message_text = message_text.upper()
            if message_text == "9GIRL" and user_id not in IU_fans_club:
                message_text ="9FUN"
            if message_text == "9HOT" and user_id not in IU_fans_club:
                message_text ="9FUN"
            if message_text == "99" and user_id in IU_fans_club:
                message_text = "9GIRL"
            reply_9gag(reply_token, message_text)
        ## call ccc
        elif message_text.upper() == "CCC":
            reply_for_ccc(reply_token,message_text)
        ## call cccc
        elif message_text.upper() == "CCCC": 
            reply_for_cccc(reply_token)
        ## call google translater
        elif message_text[0:2] == "字典" and message_text[2] == " ": 
            dict_translator(reply_token,message_text)
        ## IU Weather
        elif len(message_text) <= 6 and "天氣" in message_text: 
            weather(reply_token, message_text)
        ## youtube song
        elif message_text[:3] == "來一首" or message_text[:3] == "點一首" or message_text[:2] == "點播" or message_text[:2] == "點首" or message_text[:2] == "點歌" or message_text[:2] == "來首":
            if message_text[:3] == "來一首" or message_text[:3] == "點一首":
                message_text = message_text[3:]
            else:
                message_text = message_text[2:]
            yt_one(reply_token,message_text)
        ## 12 horoscope
        elif message_text in horoscope_dict:
            reply_horoscope(reply_token,message_text)
        ## weather report
        elif message_text in weather_dict:
            message_text = weather_dict[message_text]
            reply_weather(reply_token,message_text)
        ## wish list
        elif message_text[0:2] == "許願" and message_text[2:] != "":
            message_text = message_text[2:]
            wish(reply_token,user_id,user_name,message_text)
        ## hometown list
        elif message_text[0:8].upper() == "HOMETOWN":
            if user_id in IU_fans_club and chat_room in permission_dict_chat_room_hometown:
                hometown(reply_token,chat_room,message_text)
            else:
                pass
        ## IU fans club function
        elif message_text.upper() == "IU粉汁":
            if user_id in IU_fans_club and chat_room in IU_fans_club_chat_room:
                IU_fans_info(reply_token)
        ## password table from notion
        elif message_text[0:2].upper() == "PW":
            if user_id == admin_id and chat_room in IU_test:
                message_text = message_text[3:].upper()
                reply_password_info(reply_token, message_text)
        ## test mode 
        elif message_text[0:4].upper() == "TEST":
            if user_id == admin_id and chat_room in IU_test:
                if len(message_text) == 4:
                    # output_url = f"{pyPath}/media/tiktok/test1.mp4"
                    output_url = "https://iufans.club/warehouse/tiktok/1"
                    picture_url = "https://i.imgur.com/4sDRcxn.jpg"
                    # reply_9gag(reply_token, chat_room, message_text)
                    # output_url = ""
                    # picture_url = ""
                    line_bot_api.reply_message(reply_token,VideoSendMessage(original_content_url=output_url,preview_image_url=picture_url))
                    # line_bot_api.reply_message(reply_token,ImageSendMessage(original_content_url=output_url, preview_image_url=picture_url))
                    # line_bot_api.reply_message(reply_token,TextSendMessage(text="Test Ok"))
                    ### https://github.com/line/line-bot-sdk-python
                    ## user name
                    # user_id = ""
                    # group_id = ""
                    # profile = line_bot_api.get_profile('')
                    # print(profile.display_name)
                    # print(profile.user_id)
                    # print(profile.picture_url)
                    # print(profile.status_message)
                    # profile = line_bot_api.get_group_member_profile(group_id, user_id)
                    # print(profile.display_name)
                    # print(profile.user_id)
                    # print(profile.picture_url)
                    # profile = line_bot_api.get_room_member_profile(room_id, user_id)
                    # print(profile.display_name)
                    # print(profile.user_id)
                    # print(profile.picture_url)
                else:
                    message_text = message_text[5:]
                    if message_text == ".":
                        reply_text = ""
                        for i in range(50):
                            reply_text = f"{reply_text}.\n"
                        line_bot_api.reply_message(reply_token,TextSendMessage(text=reply_text))
            elif len(message_text) == 4:
                line_bot_api.reply_message(reply_token,TextSendMessage(text="Test Ok"))
            elif message_text[5:] == ".":
                reply_text = ""
                for i in range(50):
                    reply_text = f"{reply_text}.\n"
                line_bot_api.reply_message(reply_token,TextSendMessage(text=reply_text))
            else:
                pass
        else:
            pass
    ### if image message
    elif message_type == "image":
        message_time = events_timestamp
        print(f'{user_name} : image {message_time}')
        chat_text = f"image {message_time}"
        message_content = line_bot_api.get_message_content(message_id)
        with open(f"{pyPath}/media/{events_timestamp}.jpg", 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

    ### if video message
    elif message_type == "video":
        message_time = events_timestamp
        print(f'{user_name} : video {message_time}')
        chat_text = f"video {message_time}"
        message_content = line_bot_api.get_message_content(message_id)
        with open(f"{pyPath}/media/{message_time}.mp4", 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)

    ### if audio message
    elif message_type == "audio":
        message_time = events_timestamp
        print(f'{user_name} : audio {message_time}')
        chat_text = f"audio {message_time}"
        message_content = line_bot_api.get_message_content(message_id)
        with open(f"{pyPath}/media/{message_time}.m4a", 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
    
    ### any other message
    else:
        print(f"message_type: {message_type}")
    return HttpResponse(status=200)

    