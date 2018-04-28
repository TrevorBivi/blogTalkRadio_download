'''
ABOUT:
mass download a blogTalkRadio user's episodes

IMPORTANT METHODS:
download_blogtalkradio -- download episode mp3s from a given user

TO DO:
- make download_blogtalkradio() have option to use start and end dates instead of page numbers
  could find start and end episode positions using a binary search method
- make download_blogtalkradio() have option to download to specific folder using tkinter
- report files the could not be downloaded after multiple tries at the end of excecution
  (prints FAILED TO DOWNLOAD FILE where a failure happened but this isn't as convinient)
'''

from requests_html import HTMLSession
import requests
import time as t
import os

sesh = HTMLSession()

header = {'User-agent': 'Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1'}

def init_download(url,min_size):
    '''
    return (raw returned file, file size)
    start attempt to download the file at url
    url -- the url to download
    min_size -- the minimume size for the  to be valid
    '''
    size = 0
    for i in range(4):
        r = requests.get(url, stream=True)
        print('got return code:',r.status_code)
        size = int(r.headers['Content-length'])
        if r.status_code == 200 and size < min_size: #sometimes checking the status code is not enough this always makes sure the return is a valid file
            continue
        break
    else:
        print('FAILED TO DETECT SIZE OF FILE - ' + url)
        return None
    return (r,size)

def download_file(url,min_size = 10000):
    '''
    attempt to download the file at url
    url -- the url to download
    min_size -- the minimum size for the file to be valid
    '''
    print('downloading', url)
    local_filename = url.split('/')[-1]

    init_result = init_download(url,min_size)
    if init_result:
        r,size = init_result
    else:
        return
    print('file size:',size)
    
    for i in range(3):
        bytes_recieved = 0
        progress = 0

        print('[' + ' ' * 18 + ']')    
        with open(local_filename, 'wb') as f: 
            for chunk in r.iter_content(chunk_size=1024): #files are large so iteravely get and write response
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    
                    bytes_recieved += 1024
                    new_progress = int(20 * (bytes_recieved  / size))
                    if(new_progress > progress):
                        progress = new_progress
                        print('#',end='')
        print('\n')

        if abs(size - os.stat(local_filename).st_size) < 2000:
            break
        print('download fail -- reattempting')
        init_result = init_download(url,minSize)
        if init_result:
            r,size = init_result
        else:
            return
    
    else:
        print('FAILED TO DOWNLOAD FILE')
    #return local_filename

def download_blogtalkradio(user, start_page, end_page):
    '''
    download files from start to end
    '''
    if end_page < start_page:
        next_dir = -1
    else:
        next_dir = 1
    end_page = end_page + next_dir
    for i in range(start_page,end_page,next_dir):
        print('--- page #' + str(i) + ' ---')
        eps_page = sesh.get('http://www.blogtalkradio.com/'+ user + '/' + str(i), headers=header)
        ep_urls = eps_page.html.xpath('//*[@class="episode-container ondemand"]/div[@class="episode-details"]/h3/a/@href')
        ep_urls = ['http://www.blogtalkradio.com' + relative_url + '.mp3' for relative_url in ep_urls]
        [download_file(url) for url in ep_urls]

if __name__ == '__main__':
    usr = input('''Input the user to download episodes from (www.blogtalkradio.com/[user]).
user>''')
    p1 = int(input('''Input a start and end page number. Program can download pages backwords or forwards.
start page>'''))
    p2 = int(input('end page>'))
    download_blogtalkradio(usr,p1,p2)
