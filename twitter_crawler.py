import sys
import requests
import csv
import os
import time
import json
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor
from pybloom_live import ScalableBloomFilter
import threading
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


class TwitterCrawler:
    def __init__(self, args):

        self.args = args
        self.config = self._load_config()

        if getattr(args, 'queries', None):
            self.config['BASE_QUERIES'] = args.queries

        self._validate_config()

        self.bloom = ScalableBloomFilter(
            mode=ScalableBloomFilter.LARGE_SET_GROWTH,
            initial_capacity=1000000,
            error_rate=0.0001
        )
        self.session = self._create_session()
        self.csv_lock = threading.Lock()
        self.stats = self._init_stats()

        self._init_csv()
        self._setup_logging()

    def _load_config(self):
        config_path = Path('config.json')
        if not config_path.exists():
            raise FileNotFoundError(
                "config.json not found. Please copy config.example.json to config.json and edit it.")

        with open(config_path) as f:
            config = json.load(f)

        # Merge command line arguments
        if self.args.max_tweets is not None:
            config['MAX_TWEETS'] = self.args.max_tweets
        if self.args.output:
            config['OUTPUT_CSV'] = self.args.output

        return config

    def _validate_config(self):
        if not os.getenv('API_KEY'):
            raise ValueError("API_KEY not found in .env file")
        if not self.config.get('API_ENDPOINT'):
            raise ValueError("API_ENDPOINT missing in config.json")
        if len(self.config['BASE_QUERIES']) == 0:
            raise ValueError("No queries configured")

    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            "X-API-Key": os.getenv('API_KEY'),
            "User-Agent": f"TwitterCrawler/2.0 (Python {'.'.join(map(str, sys.version_info[:3]))}"
        })
        return session

    def _init_stats(self):
        return {
            'total_tweets': 0,
            'total_requests': 0,
            'current_query': '',
            'current_page': 0
        }

    def _init_csv(self):
        output_path = Path(self.config['OUTPUT_CSV'])
        if not output_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'id', 'text', 'createdAt', 'userName',
                    'retweetCount', 'likeCount', 'hashtags',
                    'lang', 'urls', 'source'
                ])

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log'),
                logging.StreamHandler()
            ]
        )

    def _save_tweets(self, tweets):
        with self.csv_lock:
            with open(self.config['OUTPUT_CSV'], 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for tweet in tweets:
                    writer.writerow([
                        tweet['id'],
                        tweet['text'],
                        tweet.get('createdAt', ''),
                        tweet.get('author', {}).get('userName', ''),
                        tweet.get('retweetCount', 0),
                        tweet.get('likeCount', 0),
                        ",".join([ht['text'] for ht in tweet.get(
                            'entities', {}).get('hashtags', [])]),
                        tweet.get('lang', 'vi'),
                        ",".join([url['url'] for url in tweet.get(
                            'entities', {}).get('urls', [])]),
                        tweet.get('source', '')
                    ])

    def _log_progress(self, new_tweets):
        logging.info(f"""
        [Progress Update]
        Query: {self.stats['current_query'][:25]}
        Page: {self.stats['current_page']}
        New Tweets: {new_tweets}
        Total Collected: {self.stats['total_tweets']}/{self.config['MAX_TWEETS']}
        API Requests: {self.stats['total_requests']}
        """)

    def fetch_page(self, query, cursor=None):
        params = {
            "query": query,
            "cursor": cursor,
            "precision": "high"
        }

        try:
            response = self.session.get(
                self.config['API_ENDPOINT'],
                params=params,
                timeout=self.config.get('REQUEST_TIMEOUT', 10)
            )
            self.stats['total_requests'] += 1

            if response.status_code != 200:
                logging.warning(
                    f"API returned {response.status_code}: {response.text[:100]}")
                return None

            return response.json()

        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            return None

    def process_query(self, query):
        cursor = None
        self.stats['current_query'] = query

        while self.stats['total_tweets'] < self.config['MAX_TWEETS']:
            data = self.fetch_page(query, cursor)
            if not data or 'tweets' not in data:
                break

            new_tweets = []
            for tweet in data['tweets']:
                tweet_id = str(tweet['id'])
                if not self.bloom.add(tweet_id):
                    continue

                new_tweets.append(tweet)

            if new_tweets:
                self._save_tweets(new_tweets)
                self.stats['total_tweets'] += len(new_tweets)
                self.stats['current_page'] += 1
                self._log_progress(len(new_tweets))

            cursor = data.get('next_cursor')
            if not cursor:
                break

            time.sleep(0.2)

    def start_crawling(self):
        with ThreadPoolExecutor(max_workers=self.config.get('THREAD_WORKERS', 3)) as executor:
            futures = []
            for query in self.config['BASE_QUERIES']:
                if self.stats['total_tweets'] >= self.config['MAX_TWEETS']:
                    break
                futures.append(executor.submit(self.process_query, query))

            while not all(f.done() for f in futures):
                time.sleep(1)
