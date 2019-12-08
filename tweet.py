from twython import Twython, TwythonError
from auth import (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret    
)

class Tweet():

    def __init__(self):
        self.twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
        self.tweetCount = 0

    def sendTweet(self, message):
        try:
            self.twitter.update_status(status=message)
            self.tweetCount += 1
        except TwythonError as xcp:
            print("Tweet exception: ", xcp.msg)
