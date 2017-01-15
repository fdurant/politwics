# Inspired by https://gist.github.com/bonzanini/af0463b927433c73784d

import argparse
from credentials import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from mylistener import MyListener
import time
import string
import json
from yaml import load
import sys

def init():

    parser = argparse.ArgumentParser()
    parser.add_argument('--userIdsFile', dest='userIdsFile',
                        help='YAML file containing a list of (lists of) Twitter User IDs',
                        required=True)
    parser.add_argument('--outFileJson', dest='outFileJson',
                        help='JSON file to store the retrieved tweets',
                        default='out.json')
    parser.add_argument('--outDir', dest='outDir',
                        help='directory containing the outFileJson',
                        default='.')
    global args
    args = vars(parser.parse_args())
    print >> sys.stderr, "args = ", args

    global yamlConfigs
    yamlConfigs = load(open(args['userIdsFile']))
    print >> sys.stderr, "yamlConfigs = ", yamlConfigs

def getUserIds(api, seedlists, seedusers):

    resultUserIds = []

    for memberlist in seedlists:
        print >> sys.stderr, "Retrieving members from %s ..." % memberlist,
        resultUserIds.extend(["%d" % user.id for user in tweepy.Cursor(api.list_members, memberlist['owner_id'], memberlist['slug']).items()])
        print >> sys.stderr, "done"

    # We only retrieve the first 10, in order not to break the rate limit
    for screen_name in seedusers[0:10]:
        print >> sys.stderr, "Retrieving id for screen_name %s ..." % screen_name,
        try:
            user = api.get_user(screen_name)
            resultUserIds.append("%d" % user.id)
        except BaseException as e:
            print >> sys.stderr, "failed: %s" % str(e)
        print >> sys.stderr, "done"

    return resultUserIds

if __name__ == '__main__':
    init()

    auth = OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    api = tweepy.API(auth)

    userIdsToFollow = getUserIds(api, yamlConfigs['seedlists'], yamlConfigs['seedusers'])
    print >> sys.stderr, "userIdsToFollow = ", userIdsToFollow
        
    twitter_stream = Stream(auth, MyListener(args['outDir'], args['outFileJson']))
    twitter_stream.filter(follow=userIdsToFollow)
