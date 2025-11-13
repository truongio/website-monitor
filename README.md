# Website Monitor Bot

A free, automated website monitoring service with Telegram notifications. Get notified instantly when your favorite websites change!

## Features

- Monitor any website for changes
- Smart change detection (ignores ads, timestamps, and dynamic content)
- Telegram bot interface for easy subscription management
- Completely free using Supabase, GitHub Actions, and Render
- Runs checks every 30 minutes automatically

## Architecture

- **Database**: Supabase PostgreSQL (free tier, 500MB)
- **Bot Commands**: Python Telegram bot on Render (free tier)
- **Monitoring**: GitHub Actions (scheduled cron job)
- **Notifications**: Telegram Bot API

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Save the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Set up Supabase Database

1. Go to [Supabase](https://supabase.com) and create a free account
2. Create a new project
3. Go to SQL Editor and run the schema from `database/schema.sql`
4. Go to Project Settings > Database and copy:
   - Connection String (URI format)
   - This will be your `DATABASE_URL`

### 3. Deploy Bot to Render

1. Fork this repository to your GitHub account
2. Go to [Render](https://render.com) and sign up
3. Click "New +" and select "Web Service"
4. Connect your GitHub repository
5. Configure:
   - Name: `website-monitor-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m bot.main`
6. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your bot token from step 1
   - `DATABASE_URL`: Your Supabase connection string from step 2
7. Click "Create Web Service"

### 4. Set up GitHub Actions

1. In your forked repository, go to Settings > Secrets and variables > Actions
2. Add repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `DATABASE_URL`: Your Supabase connection string
3. Go to Actions tab and enable workflows
4. The monitor will run automatically every 30 minutes

### 5. Test Your Bot

1. Open Telegram and search for your bot
2. Send `/start` to see available commands
3. Try subscribing to a website:
   ```
   /subscribe https://example.com
   ```
4. Wait for the next scheduled check (or manually trigger the GitHub Action)

## Bot Commands

- `/start` - Welcome message and help
- `/subscribe <url>` - Subscribe to a URL
- `/unsubscribe <url>` - Unsubscribe from a URL
- `/list` - Show your subscriptions
- `/pause <url>` - Pause monitoring a URL
- `/resume <url>` - Resume monitoring a URL
- `/help` - Show help message

## How It Works

1. **Subscription Management**: You use Telegram bot commands to subscribe to websites
2. **Scheduled Checks**: GitHub Actions runs every 30 minutes
3. **Smart Detection**: The monitor fetches pages, removes dynamic content (ads, timestamps)
4. **Change Notification**: If content hash changes, all subscribers get notified via Telegram

## Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd changeio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Fill in your environment variables in `.env`

5. Run the bot locally:
   ```bash
   python -m bot.main
   ```

6. Test monitoring script:
   ```bash
   python run_monitor.py
   ```

## Customization

### Change Check Interval

Edit `.github/workflows/monitor.yml` and modify the cron expression:
```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '*/15 * * * *'  # Every 15 minutes
  # - cron: '0 * * * *'     # Every hour
```

### Adjust Content Cleaning

Edit `monitor/content_cleaner.py` to customize what gets filtered:
- Add more ad selectors
- Add patterns for dynamic content
- Adjust social media widget removal

## Troubleshooting

### Bot doesn't respond
- Check Render logs for errors
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Make sure the web service is running (not sleeping)

### No notifications received
- Check GitHub Actions logs
- Verify `DATABASE_URL` is correct
- Make sure you have active subscriptions (`/list`)
- Trigger workflow manually to test

### Database connection errors
- Verify Supabase credentials
- Check if database schema is properly set up
- Ensure connection string includes `postgresql://` prefix

## Cost Breakdown

- **Supabase**: Free (500MB storage, more than enough)
- **Render**: Free (sleeps after inactivity, wakes on command)
- **GitHub Actions**: Free (2,000 minutes/month for public repos)
- **Telegram Bot API**: Free (unlimited)

**Total Monthly Cost: $0.00**

## Limitations

- Render free tier sleeps after 15 min inactivity (first command takes ~50s)
- GitHub Actions runs every 30 minutes (configurable)
- Supabase free tier: 500MB storage
- Some websites may block automated requests

## License

MIT License - feel free to modify and use as you wish!

## Contributing

Pull requests welcome! Please feel free to improve the bot or add new features.
