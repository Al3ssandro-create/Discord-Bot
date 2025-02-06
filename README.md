# Discord Matchmaking & Event Scheduling Bot

## 📌 Introduction
This is a **Discord bot** designed for **matchmaking, event scheduling, and automated notifications**. It allows users to create dating profiles, like other profiles, check matches, and manage scheduled events with a persistent cache.

## ✨ Features
- **Matchmaking System:**
  - Generate & view dating profiles
  - Like and unlike user profiles
  - View mutual matches
  - List top-liked profiles
- **Event Scheduling:**
  - Schedule recurring events (weekly or interval-based)
  - List and remove scheduled events
  - Persistent event storage (events are restored on bot restart)
- **Utility Commands:**
  - View bot commands
  - Integrated rate limiting
  - Flask web server for uptime monitoring

---
## 🚀 Setup & Installation
### 1️⃣ Requirements
- Python 3.8+
- A **Discord bot token**
- An `.env` file with the following:
  ```ini
  DISCORD_TOKEN=your_bot_token_here
  GROQ_API_KEY=your_groq_api_key_here
  ```
- Required Python packages:
  ```sh
  pip install discord.py python-dotenv apscheduler flask requests
  ```

### 2️⃣ Running the Bot
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/discord-bot.git
   cd discord-bot
   ```
2. Create an `.env` file and add your **Discord bot token** and **Groq API key**.
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```sh
   python bot.py
   ```

---
## 🎮 Commands
### **Matchmaking Commands**
| Command       | Description |
|--------------|-------------|
| `/profile` | Generate or view a user's dating profile. |
| `/resetprofile @User` | Reset a member's profile (Admins only). |
| `/listprofiles` | List all cached profiles (Admins only). |
| `/like @User` | Like another user's profile. |
| `/unlike @User` | Unlike a previously liked profile. |
| `/likes` | See who has liked your profile. |
| `/mymatches` | View mutual matches. |
| `/findmatches` | Find potential matches. |
| `/toplikes [number]` | View top profiles by likes. |

### **Event Scheduling Commands**
| Command       | Description |
|--------------|-------------|
| `/schedule_event` | Schedule a recurring event (weekly or interval-based). |
| `/list_scheduled_events` | View all scheduled events for the channel. |
| `/remove_event event_name` | Remove a scheduled event. |

### **Utility Commands**
| Command       | Description |
|--------------|-------------|
| `/help` | Display bot instructions. |
| `/sendmessage` | Send a test message. |

---
## 🛠 How Event Scheduling Works
1. **Weekly Events:** Runs on a specific day and time every week.
   ```sh
   /schedule_event event_name="Meeting" mode="weekly" day_of_week="monday" time="14:00" message="Weekly meeting reminder!"
   ```
2. **Interval Events:** Runs every X days/hours starting at a specific time.
   ```sh
   /schedule_event event_name="Reminder" mode="interval" interval_value=2 interval_unit="days" start_time="15:00" message="Time to check in!"
   ```

✅ **Events persist even after a bot restart.**

---
## 📂 Persistent Data Storage
- `profile_cache.json`: Stores user-generated profiles.
- `likes_cache.json`: Stores user likes and matches.
- `events.json`: Stores scheduled events.

---
## 🖥️ Web Server (Flask)
- A **Flask web server** runs alongside the bot to keep it active.
- You can access it at: `http://yourserver:7123/`

---
## 💡 Future Improvements
- Add support for **timezone conversions** in event scheduling.

---
## 📜 License
This bot is open-source. Feel free to modify and expand its capabilities!

---
## 🤝 Contributing
1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Submit a pull request!

---
## ❓ Need Help?
- Open an issue on GitHub.
- Contact the bot owner on Discord.

Happy matchmaking & event scheduling! 🎉

