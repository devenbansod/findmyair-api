import pandas as pd 
import numpy as np
from textblob import TextBlob
from sklearn.preprocessing import MinMaxScaler
import pickle
import json
import tqdm

reviews = pd.read_csv('../dataset/reviews.csv')
reviews = reviews[['listing_id','comments']]
sentiments = {}

# for review in reviews.itertuples()[:100]:
for index in tqdm.tqdm(range(reviews.shape[0])):
	if isinstance(reviews.loc[index,'comments'], str):
		# blob = TextBlob(review['comments'])
		# sentiments[review['listing_id']] = (blob.sentiment.polarity + 1)/2
		blob = TextBlob(reviews.loc[index,'comments'])
		listings_id = reviews.loc[index,'listing_id']
		sentiment_score = (blob.sentiment.polarity + 1)/2
		pos_review = False
		if sentiment_score >= 0.5:
			pos_review = True

		if sentiments.get(str(listings_id), -1) == -1:
			sentiments[str(listings_id)] = {'average_sentiment':sentiment_score, 'total_pos':0, 'total_neg':0}
		else:
			sentiments[str(listings_id)]['average_sentiment'] += sentiment_score 
		
		if pos_review:
			sentiments[str(listings_id)]['total_pos'] += 1
		else:
			sentiments[str(listings_id)]['total_neg'] += 1	

# Average the sentiment scores
for key, value in sentiments.items():
	sentiments[key]['average_sentiment'] = sentiments[key]['average_sentiment']/(sentiments[key]['total_pos']+sentiments[key]['total_neg'])

# print(sentiments)
# keys = []
# all_scores = []
# for key, value in sentiments.items():
# 	keys.append(key)
# 	all_scores.append(value['average_sentiment'])

# all_scores = np.expand_dims(np.array(all_scores), 1)
# scaler = MinMaxScaler()
# all_scores = scaler.fit_transform(all_scores)

# for index, key in enumerate(keys):
# 	sentiments[key]['average_sentiment'] = all_scores[index,0]

# print(sentiments)

with open('data/review_sentiments.json', 'w') as fp:
	json.dump(sentiments, fp)

# sentiments_scores = []
# for curr_key, sentiment_score in zip(keys, all_scores):
# 	sentiments_scores.append([curr_key, sentiment_score])

# sentiments_scores = np.array(sentiments_scores)
# print(sentiments_scores.shape)
# np.save('data/review_sentiments.npy', sentiments_scores) 