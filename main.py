import argparse
import sys
import time
from pathlib import Path
from twitter_crawler import TwitterCrawler


def check_required_files():
    required_files = {
        'config.json': Path('config.json'),
        '.env': Path('.env')
    }

    missing = [name for name, path in required_files.items()
               if not path.exists()]
    if missing:
        print(f"Missing required files: {', '.join(missing)}")
        print("Please check:")
        print("- Copy .env.example to .env and edit with your API key")
        print("- Create config.json from config.example.json")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Twitter Advanced Search Crawler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-m', '--max-tweets',
        type=int,
        help="Maximum number of tweets to collect"
    )
    parser.add_argument(
        '-q', '--queries',
        nargs='+',
        help="Additional search queries to add"
    )
    parser.add_argument(
        '-o', '--output',
        help="Output CSV file path"
    )
    return parser.parse_args()


def main():
    check_required_files()
    args = parse_args()

    print("\n=== Twitter Advanced Search Crawler ===")
    print("Repository: https://github.com/ThaiG2Pro/twitter-crawler")
    print("---------------------------------------")

    try:
        crawler = TwitterCrawler(args)
        start_time = time.time()

        print("\n[+] Starting crawling process...")
        crawler.start_crawling()

    except KeyboardInterrupt:
        print("\n[!] Crawling interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Fatal error occurred: {str(e)}")
        sys.exit(1)
    finally:
        if 'crawler' in locals():
            duration = time.time() - start_time
            print("\n=== Crawling Summary ===")
            print(f"Total tweets collected: {crawler.stats['total_tweets']}")
            print(f"Total API requests: {crawler.stats['total_requests']}")
            print(f"Execution time: {duration:.2f} seconds")
            print(f"Output file: {crawler.config['OUTPUT_CSV']}")
            print("\nThank you for using Twitter Crawler!")


if __name__ == "__main__":
    main()
