import re
import json
import os
import random
import hashlib
from pprint import pprint
from googleapiclient.discovery import build
from dotenv import load_dotenv
from tqdm import tqdm

random.seed('chorus-quiz')
load_dotenv()
youtube = build('youtube', 'v3', developerKey=os.getenv('API_KEY'))
channel_handle = '@NTUChorus'


def md5_to_int(s, m):
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % m


def get_channel_id(handle):
    if handle.startswith('@'):
        handle = handle[1:]

    response = youtube.channels().list(
        part='id',
        forHandle=handle,
    ).execute()['items'][0]['id']

    return response


def get_channel_videos(channel_id, page_token=None):
    response = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50,
        order='date',
        type='video',
        pageToken=page_token,
    ).execute()

    videos = []
    for item in response['items']:
        video_id = item['id']['videoId']
        videos.append(video_id)

    if 'nextPageToken' in response:
        videos += get_channel_videos(channel_id, response['nextPageToken'])

    return videos



def get_video_info(video_id):
    response = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id,
    ).execute()

    if response['items']:
        return response['items'][0]
    return None



def download_json():

    channel_id = get_channel_id(channel_handle)
    videos = get_channel_videos(channel_id)

    video_infos = {}
    for video_id in tqdm(videos):
        video_info = get_video_info(video_id)
        if video_info:
            video_infos[video_id] = video_info

    with open('video_infos.json', 'w') as f:
        json.dump(video_infos, f, indent=4)


def parse():
    with open('video_infos.json', 'r') as f:
        video_infos = json.load(f)

    parsed_data = {
        video_id: {
            'title': info['snippet']['title'],
            'description': info['snippet']['description'],
            'viewCount': int(info['statistics']['viewCount']),
        }
        for video_id, info in video_infos.items()
    }

    # filter top 200 by viewCount
    parsed_data = dict(sorted(parsed_data.items(), key=lambda item: item[1]['viewCount'], reverse=True)[:200])

    language_map = {line.split('->')[0].strip(): line.split('->')[1].strip() for line in open('language.txt', 'r').readlines()}
    category_map = {line.split('->')[0].strip(): line.split('->')[1].strip() for line in open('category.txt', 'r').readlines()}
    atmosphere_map = {line.split('->')[0].strip(): line.split('->')[1].strip() for line in open('atmosphere.txt', 'r').readlines()}
    language_chinese_map = {line.split('->')[0].strip(): line.split('->')[1].strip() for line in open('language-chinese.txt', 'r').readlines()}
    polygon_map = ['圓形', '三角形', '菱形', '長方形', '七角星', '雲朵']
    sorcerer_map = ['讀心術', '情緒操控術', '幻術', '心靈護盾']

    assert all(l in ('中文', '英文', '歐洲', '其他語言') for l in language_map.values())
    assert all(c in ('古典宗教作品', '流行編曲', '民謠與傳統歌謠', '藝術歌曲或現代合唱作品', '音樂劇或動畫或電影配樂') for c in category_map.values())
    assert all(a in ('溫柔安靜或抒情', '熱鬧快樂或輕快', '莊嚴神聖或神秘壯闊', '創意或新體驗') for a in atmosphere_map.values())
    assert all(l in ('華語', '台語', '客語', '無') for l in language_chinese_map.values())

    table = {}
    for video_id, info in parsed_data.items():
        title = info['title'].removesuffix(
            '- National Taiwan University Chorus'
        ).removesuffix(
            ' - NTU Chorus & KMU Singers'
        ).removesuffix(
            '-National Taiwan University Chorus'
        ).removesuffix(
            'NTUChorus & University of Utah Chamber Choir and A Cappella Choir'
        ).removesuffix(
            '@TwincussionDuo & National Taiwan University Chorus'
        ).removesuffix(
            'National Taiwan University Chorus'
        ).removesuffix(
            'National Taiwan University Chorus in Libby Gardner Concert Hall, U. of Utah'
        ).removesuffix('- ').strip()

        description = info['description']
        description = re.sub(r'.*?委託編曲.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'.*?委託創作.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Commissioned.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Performed .*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Debut .*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'樂譜訂購：.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'\u3000', ' ', description, flags=re.DOTALL).strip()
        description = re.sub(r'Conductor.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Piano.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Pianist.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Solo.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Soli.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Violin.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Poem.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Percussion.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Composer.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Lyric.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Arrangement.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Audio recording engineer.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Published by.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'e-mail*?\n', '', description, flags=re.DOTALL | re.IGNORECASE).strip()
        description = re.sub(r'email*?\n', '', description, flags=re.DOTALL | re.IGNORECASE).strip()
        description = re.sub(r'出版發行.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'YouTube.*?\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Social Links：.*', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'Facebook：.*', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'\nNational Taiwan University Chorus 台大合唱團\n', '', description, flags=re.DOTALL).strip()
        description = re.sub(r'(─|—|-|\n| )+', ' ', description, flags=re.DOTALL).strip()

        table[video_id] = {
            'title': title,
            # 'description': description,
            'quiz': {
                'language': language_map[title],
                'category': category_map[title],
                'atmosphere': atmosphere_map[title],
                'language_chinese': language_chinese_map[title],
                'polygon': polygon_map[md5_to_int(description, 6)],
                'sorcerer': sorcerer_map[md5_to_int(title, 4)],
                'viewCount': info['viewCount'],
            }
        }
        # print(f'{title} -> {table[video_id]["quiz"]["polygon"]}')
        # print(title)
        # print(repr(description))
        # print()

    # print(*sorted(d['title'] for d in table.values()), sep='\n')

    with open('table.json', 'w') as f:
        json.dump(table, f, indent=4, ensure_ascii=False)
        # json.dump(table, f, ensure_ascii=False)


def check_table():
    with open('table.json', 'r') as f:
        table = json.load(f)

    counter = {}

    for d in table.values():
        lang = d['quiz']['language']
        cat = d['quiz']['category']
        atm = d['quiz']['atmosphere']
        lang_c = d['quiz']['language_chinese']
        poly = d['quiz']['polygon']
        sor = d['quiz']['sorcerer']
        if (lang, cat, atm, lang_c, poly, sor) not in counter:
            counter[(lang, cat, atm, lang_c, poly, sor)] = []

        counter[(lang, cat, atm, lang_c, poly, sor)].append(d)

    for (lang, cat, atm, lang_c, poly, sor), lst in counter.items():
        assert len(lst) <= 3
        # if len(lst) >= 1:
        if len(lst) > 1:
            print(f'[{lang} | {cat} | {atm} | {lang_c} | {poly} | {sor} ] -> {len(lst)}')
            # for d in lst:
            #     print(f' - {d["title"]}')
            #     print(repr(d['description']))
            # print()


if __name__ == '__main__':
    parse()
    check_table()
