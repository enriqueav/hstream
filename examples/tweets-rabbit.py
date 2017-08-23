
import socket
import sys
import tweepy
import pika
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("HOST")
parser.add_argument("QUEUE")

args = parser.parse_args()

HOST = args.HOST
TAGS = ['#barcelona']
QUEUE= args.QUEUE

# Twitter credentials
consumer_key="6TmfVYxSmn5MJsahkEQ6jy0aJ"
consumer_secret="ITwmPInEL23xhmjtT4dlMJyPlpiC3mvnrqPgt1bJyAxWBgQU4D"
access_token="124131670-4dfRR9VaK8wqhEZiTHtMRcD6E0BTl3LolcXxXf4M"
access_token_secret="xGAeY9AUKOWIwJA6wQckS5HkWyPLqnu6wdsPaTnpBAGH6"


# Send tweet via socket
class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        text = status.text.encode('utf-8') 
        channel.basic_publish(exchange='', routing_key=QUEUE, body=text)
        print(text)
        


if __name__ == '__main__':
    
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
    channel    = connection.channel()
    channel.queue_declare(queue=QUEUE)
    
    # Authenticate app on twitter 
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    # Start receiving tweets 
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)
    myStream.filter(track=TAGS)


