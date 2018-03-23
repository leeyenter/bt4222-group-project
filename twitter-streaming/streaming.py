#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 13:10:54 2018

@author: hong
"""

from datetime import datetime
import json
import random
import re
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from secret import *

# This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

    def on_data(self, json_data):
        # print(json_data)
        now = str(datetime.now()).rsplit(':',maxsplit=1)[0]
        filename = re.sub(r'\s|\/|:', r'_', '%s.txt' % now)
        fileloc = './twitter_stream_data/' + filename
        
        
        with open(fileloc, 'a') as f:
            f.write(json_data)
        return True

    def on_error(self, status_code):
        '''
        return False disconnects stream
        return True reconnects stream with backoff
        '''
        if status_code==420:
            time.sleep(3)
            return True # disconnect stream


# @retry(wait_exponential_multiplier=1000,wait_exponential_max=10000)
def main():
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=['#GalaxyS9', '#Nokia8', '#Xperia', '#LGV30k'])
    print("exiting main")


if __name__ == '__main__':
    
    try:
        main()
    except Exception as e:
        print(e)
        time.sleep(3)