# 🎬 Heisenberg Film Bot

Telegram bot for searching movies by genre, mood, decade, country and topic. Powered by TMDb API.

## Features

- 🎲 Random movie
- 🎭 Search by genre
- 🎨 Search by mood
- 📅 Search by decade
- 🔑 Search by topic (spies, war, robots, etc.)
- 🌍 Search by country
- 🔄 Find similar movies
- ⚙️ Combined search with multiple filters
- 🌐 Multilingual: Russian, English, Spanish, Chinese

## Setup

1. Get a bot token from [@BotFather](https://t.me/BotFather)
2. Get a free API key from [themoviedb.org](https://www.themoviedb.org/settings/api)
3. Clone this repo and create a `.env` file:

```
TELEGRAM_TOKEN=your_token
TMDB_API_KEY=your_key
```

4. Install dependencies and run:

```bash
pip install python-telegram-bot requests
python movie_bot.py
```

## Deployment

The bot is deployed on [Railway](https://railway.app). Environment variables are set in the Railway dashboard.

## Built with

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [TMDb API](https://www.themoviedb.org/documentation/api)
