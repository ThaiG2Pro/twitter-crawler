# 🐦 Twitter(X) Advanced Search Crawler

A powerful and flexible Twitter data crawler with advanced search capabilities, CLI support, configuration via file and arguments, and real-time logging.

## 📦 Installation

```bash
# Clone the repository
git clone git@github.com:ThaiG2Pro/twitter-crawler.git
cd twitter-crawler

# Install dependencies
pip install -r requirements.txt

# Prepare environment and config files
cp .env.example .env
cp config.example.json config.json
```

    ⚠️ Ensure you are using Python 3.8+ and running this in a virtual environment (`venv` recommended).

    To create a virtual environment, refer to the official Python documentation: [Creating and using virtual environments](https://docs.python.org/3/library/venv.html).

## ⚙️ Configuration

1. Edit `.env`:

```env
API_KEY=your_api_key_here
```

    This key is obtained from [TwitterAPI.io](https://twitterapi.io/), which currently offers a free $5 bonus.

2. Edit `config.json`:

- `MAX_TWEETS`: Max tweets to fetch (across queries)
- `OUTPUT_CSV`: Output file path
- `THREAD_WORKERS`: Number of concurrent query threads
- `BASE_QUERIES`: List of search queries

## 🚀 Usage

Basic usage:

```bash
python main.py
```

With CLI arguments:

```bash
python main.py \
  --max-tweets 1000 \
  --output "data/travel_tweets.csv" \
  --queries "#VietnamTravel" "Đà Lạt"
```

You can override any config file value with CLI args:

- `--max-tweets`: Overrides `MAX_TWEETS`
- `--output`: Overrides `OUTPUT_CSV`
- `--queries`: Overrides `BASE_QUERIES`

  For advanced query writing, refer to [this guide](https://github.com/igorbrigadir/twitter-advanced-search).

## 🧪 Example Queries

```bash
python main.py --queries "Hội An lang:vi" "Đà Lạt lang:vi"
```

## 📌 Features

- ✅ Checks required files (.env, config.json) before execution
- 🔧 Configuration via file and command-line args
- ⚡ Fast with multi-threaded crawling
- 📊 Real-time logging and stats
- 🧠 Duplicate tweet filtering with Bloom filter
- 🛑 Graceful error handling and API retry logic
- ⏱️ Delay between requests to respect rate limits

## 📁 Output Format

CSV file with columns:

- `id`, `text`, `createdAt`, `userName`
- `retweetCount`, `likeCount`, `hashtags`
- `lang`, `urls`, `source`

Example row:

```bash
1645678901234567890,"Exploring Hội An ancient town...",2024-02-15T13:20:45Z,User123,12,53,"du lịch, Hội An",vi,https://bit.ly/abc123,"Twitter for iPhone"
```

## 🛠 Troubleshooting

- **Missing .env or config**: The program will alert and exit. Copy from example files.
- **Missing modules**: Run `pip install -r requirements.txt`
- **No tweets collected?**: Try refining queries or testing with fewer tweets.
- **Permission denied for CSV output?**: Ensure the output folder exists and is writable.

## 📜 License

MIT License

## 🙌 Author

Maintained by [ThaiG2Pro](https://github.com/ThaiG2Pro)
