import os
import argparse
from bs4 import BeautifulSoup
import requests
import re
import subprocess
import pipes


def parser():
    parser = argparse.ArgumentParser(description='Provided a movie or a tv-series url on cinemana gives you the option to download the movie with subtitle files or download all or some episodes', epilog='Send suggestions to yusuf.mohammad@zoho.com')
    parser.add_argument('--movie', action='store_true', help='Add this flag if'
                        ' you are downloading a movie or you want to only'
                        ' download a single episode, by default the this '
                        'option is off')
    parser.add_argument('--no-subtitle', dest='subtitle',
                        action='store_false',
                        help='If you don\'t want the subtitles downloaded')
    parser.add_argument('--pick-res', dest='highest', action='store_false',
                        help='Add this flag if you want to pick a resolution'
                        ' from the available resolutions (note that this means'
                        ' you have to pick a resolution for each episode)')
    parser.add_argument('--res')
    parser.add_argument('--season', dest='custom_seasons', action='append',
                        help='specify the season number you want to download,'
                        ' repeat for more than one')
    parser.add_argument('--concurrent-downloads', default=3,
                        help='pass concurrent downloads option to aria2c')
    parser.add_argument(dest='urls', metavar='URLs', nargs='+',
                        help='one or more cinemana urls')
    return parser.parse_args()


def single_link(url, highest, subtitle, resolution):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    movie_name = soup.title.text.strip()
    links_dict = dict()
    for link in soup.findAll(class_='mp4'):
        links_dict[link.get('data-res')] = link.get('src')

    if not highest:
        for i, res in enumerate(links_dict.keys()):
            print(str(i+1)+')', res)
        res = int(input('Please enter the number for the desired resolution: '))
    else:
        res = len(list(links_dict.keys()))
    if resolution is not None:
        res = [i for i, r in enumerate(links_dict.keys()) if r == resolution]
        if len(res) == 1:
            res = res[0]
        else:
            res = len(list(links_dict.keys()))
    subtitles = dict()
    if subtitle:
        for sub in soup.findAll(kind='captions'):
            subtitles[sub.get('srclang')] = sub.get('src')

    return links_dict[list(links_dict.keys())[res-1]], subtitles, movie_name


def seasons_parser(url, custom_seasons):
    print(custom_seasons)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    tv_series = soup.title.text.strip()
    seasons_objs = soup.select('div[class="seasonconts"] div[class="season"] a')
    if custom_seasons:
        seasons = {season.text.strip(): None for season in seasons_objs if season.text.strip() in custom_seasons}
    else:
        seasons = {season.text.strip(): None for season in seasons_objs}
    for season in seasons.keys():
        selector = 'div[id="myTabContent"] div[id={}] a'.format('\"'+season+'\"')
        episodes = {re.search(r'.*ep\s*(\d+)\s*', episode.text, flags=re.IGNORECASE).group(1): episode.get('href') for episode in soup.select(selector)}
        seasons[season] = episodes
    return seasons, tv_series


def single_download(url, path=os.path.expanduser('~/Downloads'),
                    name='noname', ext='.mp4', split=5):
    path = pipes.quote(path)
    name = pipes.quote(name)
    cmd = (f'aria2c --max-connection-per-server={split} -c -V -s {split} -d '
           f'{path} -o {name+ext} {url}')
    subprocess.Popen(cmd, shell=True)
    aria2_running = subprocess.Popen(
        f"ps -u {os.getenv('USER')} | grep aria", shell=True, text=True,
        stdout=subprocess.PIPE).communicate()[0] != ''
    while aria2_running:
        aria2_running = subprocess.Popen(
            'ps -u yusuf | grep aria', shell=True, text=True,
            stdout=subprocess.PIPE).communicate()[0] != ''


if __name__ == '__main__':
    args = parser()
    downloads_path = os.path.expanduser('~/Downloads/')
    urls_list = []
    if args.movie:
        for url in args.urls:
            link, subs, movie_name = single_link(
                url, args.highest, args.subtitle, args.res)
            print('Starting %s download to %s' %
                  (movie_name, downloads_path+movie_name))
            urls_list.append(link)
            urls_list.append(f'  dir={downloads_path+movie_name}')
            urls_list.append(f'  out={movie_name}.mp4')
            # single_download(link,
            #                 path=downloads_path + movie_name,
            #                 name=movie_name)
            for lang, sub in subs.items():
                print('Starting %s subtitle download for %s' %
                      (lang, movie_name))
                urls_list.append(sub)
                urls_list.append(f'  dir={downloads_path+movie_name}')
                urls_list.append(f'  out={movie_name+lang.strip()}.vtt')
                urls_list.append('  split=1')
    else:
        for url in args.urls:
            seasons, tv_series = seasons_parser(url, args.custom_seasons)
            print('The following will be downloaded')
            for season, episodes in seasons.items():
                print('Season:', season)
                print('  Episodes:', ', '.join(list(episodes.keys())))
            for season, episodes in seasons.items():
                for episode_num, episode_url in episodes.items():
                    link, subs, _ = single_link(episode_url, args.highest, args.subtitle, args.res)
                    season_path = os.path.join(
                        downloads_path, tv_series, season)
                    print('Starting %s download to %s' % ('S'+season+' - E'+episode_num, season_path))
                    urls_list.append(link)
                    urls_list.append(f'  dir={season_path}')
                    urls_list.append(f'  out={episode_num}.mp4')
                    for lang, sub in subs.items():
                        print('Starting %s %s subtitle download to %s' %
                              ('S'+season+' - E'+episode_num, lang, season_path))
                        urls_list.append(sub)
                        urls_list.append(f'  dir={season_path}')
                        urls_list.append(f'  out={episode_num+lang.strip()}.vtt')
                        urls_list.append('  split=1')
    with open('temp_urls', 'w+') as f_obj:
        for row in urls_list:
            f_obj.write(row + '\n')
    download_cmd = (f'aria2c --max-concurrent-downloads={args.concurrent_downloads} '
                    '--continue=true --check-integrity=true --split=5 '
                    '--input-file=temp_urls --deferred-input=true'
                    ' --file-allocation=falloc')
    subprocess.Popen(download_cmd, shell=True)

