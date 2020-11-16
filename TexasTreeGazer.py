#!/usr/bin/env python
# tweepy-bots/bots/autoreply.py

import tweepy
import logging
import time
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def create_api():
    consumer_key = "abcd"
    consumer_secret = "abcd"
    access_token = "abcd"
    access_token_secret = "abcd"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api

def getPhotoURL(tweet):

	if not tweet.entities['media'][0]:
		return ""

	media_url = tweet.entities['media'][0]['media_url']
	return media_url

def build_tweet(prediction, username):

	names = {
		"american_elm": "American Elm",
		"american_sycamore": "American Sycamore",
		"bald_cypress": "Bald Cypress",
		"bigtooth_maple": "Bigtooth Maple",
		"black_cherry": "Black Cherry",
		"cedar_elm": "Cedar Elm",
		"green_ash": "Green Ash",
		"live_oak": "Live Oak",
		"magnolia": "Magnolia",
		"mexican_white_oak": "Mecixan White Oak",
		"pecan": "Pecan",
		"red_oak": "Red Oak",
		"shumard_oak": "Shumard Oak",
		"texas_ash": "Texas Ash",
		"texas_walnut": "Texas Walnut",
		"yaupon": "Yaupon Holly"
	}

	if prediction == "american_elm" or prediction == "american_sycamore":
		tweet_string = "@{username} I think this is a photo of an {name} #TexasTreeGazer".format(
			username=username,
			name=names[prediction]
		)
	else:
		tweet_string = "@{username} I think this is a photo of a {name} #TexasTreeGazer".format(
			username=username,
			name=names[prediction]
		)

	return tweet_string

def check_mentions(api, keywords, since_id):
	logger.info("Retrieving mentions")
	new_since_id = since_id
	for tweet in tweepy.Cursor(api.mentions_timeline,
		since_id=since_id).items():
		new_since_id = max(tweet.id, new_since_id)
		if tweet.in_reply_to_status_id is not None:
			continue
		if any(keyword in tweet.text.lower() for keyword in keywords):
			logger.info(f"Answering to {tweet.user.name}")

			print(tweet.entities['media'][0]['media_url'])

			url = getPhotoURL(tweet)
			if url:
				prediction = requests.get(
					"https://trees-of-central-texas.onrender.com/classify-url", params={"url": url}
				).json()["result"]

				print(url)
				print(prediction)

				tweet_text = build_tweet(prediction, tweet.user.screen_name)
				print(tweet_text, len(tweet_text))

				api.update_status(tweet_text, in_reply_to_status_id=tweet.id) 

			if not tweet.user.following:
				tweet.user.follow()

			
	return new_since_id

def main():
	api = create_api()
	since_id = 1
	while True:
		since_id = check_mentions(api, ["id"], since_id)
		logger.info("Waiting...")
		time.sleep(60)

if __name__ == "__main__":
	main()