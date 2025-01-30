
# 📘 Discord Matchmaking Bot

Welcome to the **Discord Matchmaking Bot**! This bot is designed to enhance user interaction within your Discord server by facilitating matchmaking features inspired by dating platforms. Users can create profiles, like/unlike other members, and discover mutual matches seamlessly.

---

## 📖 Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Bot Commands](#bot-commands)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)
12. [Support](#support)

---

## Introduction

The **Discord Matchmaking Bot** is a feature-rich bot built with Python using the `discord.py` library. It allows users to create detailed profiles, like or unlike other members, and discover mutual matches within your Discord server. Whether you're managing a community or a group of friends, this bot enhances engagement and connectivity.

---

## Features

- **Profile Management**
  - Generate and view user profiles with detailed attributes.
  - Store profiles persistently using JSON files.

- **Likes System**
  - Like or unlike other users' profiles.
  - Track likes and manage mutual matches.

- **Matchmaking**
  - Identify and notify users of mutual matches.
  - View personal likes and matches.

- **Administrative Tools**
  - Reset user profiles.
  - List all cached profiles.

- **User-Friendly Commands**
  - Comprehensive `!help` command with detailed instructions.

- **Uptime Maintenance**
  - Integrated Flask web server to prevent bot from sleeping.
  - Compatibility with uptime monitoring services like UptimeRobot.

---

## Prerequisites

Before setting up the Discord Matchmaking Bot, ensure you have the following:

- **Discord Account:** To create and manage the bot within Discord.
- **Discord Server:** Where the bot will be deployed.
- **Python 3.8+ Installed:** The bot is built using Python and requires version 3.8 or higher.
- **Git Installed:** For version control and deployment purposes.
- **Hosting Platform Account:** Such as Render, Replit, or any other platform supporting Python applications.
- **Basic Knowledge of Command-Line Operations:** Familiarity with terminal or command prompt usage.

---

## Installation

### 1. Clone the Repository

Clone the bot's repository from GitHub to your local machine:

```bash
git clone https://github.com/your_username/discord-matchmaking-bot.git
cd discord-matchmaking-bot
```

*Replace `your_username` with your actual GitHub username.*

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

*Ensure your `requirements.txt` contains:*

```plaintext
discord.py==2.3.2
python-dotenv==1.0.0
Flask==2.3.2
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory to securely store your Discord bot token:

```bash
touch .env
```

Open `.env` with your preferred text editor and add:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

*Replace `your_discord_bot_token_here` with your actual Discord bot token.*

**Important:** Ensure `.env` is added to your `.gitignore` to prevent accidental exposure.

### 5. Initialize Cache Files

Create empty JSON files for caching profiles and likes:

```bash
touch profile_cache.json
touch likes_cache.json
```

Initialize them with empty JSON objects:

```json
{}
```

*You can do this by opening each file in a text editor and adding `{}`.*

---

## Configuration

### 1. Discord Developer Portal Setup

1. **Create a New Application:**
   - Visit the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click on "New Application" and provide a name.

2. **Add a Bot to Your Application:**
   - Navigate to the "Bot" tab.
   - Click "Add Bot" and confirm.

3. **Enable Privileged Gateway Intents:**
   - Under the "Bot" tab, scroll to "Privileged Gateway Intents."
   - Enable "Server Members Intent" and "Message Content Intent" if your bot requires them.

4. **Copy the Bot Token:**
   - Under the "Bot" tab, click "Copy" to get your bot token.
   - **Securely store this token**; do not share it publicly.

### 2. Inviting the Bot to Your Server

Generate an OAuth2 invite link:

1. **Navigate to the "OAuth2" Tab:**
   - Go to the "URL Generator" section.

2. **Select Scopes:**
   - Check the `bot` scope.

3. **Select Bot Permissions:**
   - Based on your bot's functionality. For matchmaking, consider:
     - `Send Messages`
     - `Manage Messages`
     - `Embed Links`
     - `Read Message History`
     - `Add Reactions`

4. **Generate and Copy the URL:**
   - Use the generated link to invite the bot to your Discord server.

---

## Deployment

You can deploy the Discord Matchmaking Bot on various platforms. Below is a guide for deploying on **Render**, leveraging its free tier.

### Deploying on Render

1. **Sign Up and Log In:**
   - Visit [Render](https://render.com/) and create a free account.

2. **Create a New Web Service:**
   - From the Render dashboard, click "New" > "Web Service."

3. **Connect to Your Repository:**
   - Select your GitHub repository containing the bot's code.

4. **Configure the Service:**
   - **Name:** Choose a descriptive name (e.g., `discord-matchmaking-bot`).
   - **Environment:** Python.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`

5. **Set Environment Variables:**
   - In the Render service settings, add the `DISCORD_TOKEN` variable with your bot token.

6. **Deploy:**
   - Render will automatically build and deploy your service. Monitor the logs to ensure successful deployment.

7. **Set Up Uptime Monitoring:**
   - Use a service like [UptimeRobot](https://uptimerobot.com/) to ping your bot's web server URL every 5 minutes to keep it active.

### Additional Hosting Options

- **Replit:** User-friendly and suitable for beginners.
- **Heroku:** Popular platform with a free tier.
- **DigitalOcean:** Offers scalable VPS solutions.

*Refer to individual platform documentation for detailed deployment steps.*

---

## Bot Commands

The Discord Matchmaking Bot offers a variety of commands to manage profiles, likes, and matches. Below is a comprehensive list of available commands along with their descriptions.

### 📌 **!profile [@User]**

**Description:** Generate or view a user's profile. If no user is mentioned, it defaults to your own profile.

**Usage:**
- `!profile` – View your profile.
- `!profile @Username` – View another user's profile.

**Example:**
```
!profile @JohnDoe
```

---

### 📌 **!myprofile**

**Description:** Manually generate or view your own profile.

**Usage:**
- `!myprofile`

**Example:**
```
!myprofile
```

---

### 👍 **!like @User**

**Description:** Like another user's profile. If both users like each other, a mutual match is created!

**Usage:**
- `!like @Username`

**Example:**
```
!like @JaneDoe
```

---

### 👎 **!unlike @User**

**Description:** Unlike a user you have previously liked, potentially breaking a mutual match.

**Usage:**
- `!unlike @Username`

**Example:**
```
!unlike @JaneDoe
```

---

### 💞 **!mymatches**

**Description:** View all your mutual matches.

**Usage:**
- `!mymatches`

**Example:**
```
!mymatches
```

---

### ❤️ **!likes**

**Description:** See who has liked your profile.

**Usage:**
- `!likes`

**Example:**
```
!likes
```

---

### 🔍 **!findmatches**

**Description:** Find potential matches based on existing likes.

**Usage:**
- `!findmatches`

**Example:**
```
!findmatches
```

---

### 🏆 **!toplikes [number]**

**Description:** View the top profiles ranked by the number of likes they have received. You can specify the number of top profiles to display (default is 5).

**Usage:**
- `!toplikes` – Displays top 5 profiles.
- `!toplikes 10` – Displays top 10 profiles.

**Example:**
```
!toplikes 10
```

---

### 📖 **!help**

**Description:** Provides detailed instructions on how to use all available commands of the bot.

**Usage:**
- `!help`

**Example:**
```
!help
```

---

## Best Practices

To ensure the bot operates smoothly and securely within your Discord server, consider the following best practices:

### 1. **Secure Your Bot Token**

- **Never Share Your Token:** The `DISCORD_TOKEN` is sensitive and grants full control over your bot. Keep it confidential.
- **Use Environment Variables:** Store tokens and other secrets in environment variables or secure storage solutions.
- **Regenerate If Compromised:** If you suspect your token has been exposed, regenerate it immediately from the Discord Developer Portal.

### 2. **Manage Permissions Wisely**

- **Least Privilege Principle:** Grant your bot only the permissions it absolutely needs to function.
- **Avoid Excessive Permissions:** Avoid granting administrative permissions unless necessary.

### 3. **Regularly Update Dependencies**

- **Stay Current:** Keep your Python packages updated to benefit from security patches and new features.
  
  ```bash
  pip install --upgrade -r requirements.txt
  ```

### 4. **Monitor Bot Activity**

- **Check Logs:** Regularly review `bot.log` to monitor bot performance and identify issues.
- **Use Uptime Monitoring:** Ensure your bot remains online using services like UptimeRobot.

### 5. **Backup Data**

- **Cache Files:** Regularly back up `profile_cache.json` and `likes_cache.json` to prevent data loss.
- **Version Control:** Use Git to track changes and maintain history.

### 6. **Handle Errors Gracefully**

- **Implement Error Handling:** Ensure your bot can handle unexpected inputs or errors without crashing.
- **Provide User Feedback:** Inform users when commands fail or when errors occur.

---

## Troubleshooting

If your Discord bot is experiencing issues, refer to the following troubleshooting steps to identify and resolve common problems.

### 1. **Bot Goes Offline After Changing the Icon**

**Possible Causes:**
- **Code Errors:** Recent changes to the bot's code may contain syntax or runtime errors.
- **Deployment Issues:** Errors during deployment may prevent the bot from starting correctly.
- **Environment Variable Misconfiguration:** Incorrect or missing `DISCORD_TOKEN`.

**Solutions:**
- **Check Logs:** Review `bot.log` and deployment logs on your hosting platform for error messages.
- **Revert Recent Changes:** Undo recent code modifications to identify the culprit.
- **Verify Environment Variables:** Ensure `DISCORD_TOKEN` is correctly set in the `.env` file and on the hosting platform.

### 2. **Command Registration Error**

**Error Message:**
```
discord.ext.commands.errors.CommandRegistrationError: The command help is already an existing command or alias.
```

**Cause:**
- Attempting to create a custom `!help` command without disabling the default one provided by Discord.py.

**Solution:**
- **Disable Default Help Command:** Initialize the bot with `help_command=None`.
  
  ```python
  bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
  ```
  
- **Ensure Proper Order:** Define the custom `!help` command after disabling the default one.

### 3. **Bot Token Issues**

**Symptoms:**
- Bot fails to connect.
- Authentication errors in logs.

**Solutions:**
- **Verify Token:** Ensure the token in `.env` matches the one in the Discord Developer Portal.
- **Regenerate Token:** If compromised or invalid, regenerate the token and update `.env`.
- **Restart Bot:** After updating the token, restart the bot to apply changes.

### 4. **Missing Dependencies**

**Symptoms:**
- Import errors in logs.
- Bot fails to start.

**Solutions:**
- **Install Dependencies:** Ensure all packages in `requirements.txt` are installed.
  
  ```bash
  pip install -r requirements.txt
  ```
  
- **Check Versions:** Verify that the installed package versions match those specified.

### 5. **Cache File Issues**

**Symptoms:**
- Bot crashes when accessing cache files.
- Data not being stored or retrieved correctly.

**Solutions:**
- **Validate JSON:** Ensure `profile_cache.json` and `likes_cache.json` contain valid JSON (`{}` if empty).
- **Check File Permissions:** Ensure the bot has read/write permissions for these files.
- **Initialize If Missing:** If cache files are corrupted or missing, recreate them as empty JSON objects.

### 6. **Bot Sleeping/Inactivity**

**Cause:**
- Hosting platform marks the bot as inactive due to lack of activity.

**Solutions:**
- **Implement Web Server:** Use a simple Flask server within `bot.py` to respond to HTTP requests.
- **Set Up Uptime Monitoring:** Configure services like UptimeRobot to ping the bot's web server URL periodically.

---

## Contributing

Contributions are welcome! If you'd like to enhance the Discord Matchmaking Bot, follow these guidelines:

1. **Fork the Repository:**
   - Click the "Fork" button on the GitHub repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/your_username/discord-matchmaking-bot.git
   cd discord-matchmaking-bot
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes:**
   - Implement your desired features or fixes.

5. **Commit Your Changes:**

   ```bash
   git add .
   git commit -m "Add feature: Your Feature Description"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request:**
   - Navigate to your forked repository on GitHub.
   - Click "Compare & pull request" and provide a description of your changes.

8. **Await Review:**
   - Repository maintainers will review your contribution and provide feedback or merge your changes.

**Please ensure that your contributions adhere to the project's coding standards and include appropriate documentation and testing.**

---

## License

This project is licensed under the [MIT License](LICENSE).

*Feel free to modify and distribute the code as per the license terms.*

---

## Support

If you encounter any issues or have questions regarding the Discord Matchmaking Bot, feel free to reach out:

- **Email:** [alessandro.martinolli@live.com](mailto:alessandro.martinolli@live.com)

---

---

**Happy Matchmaking! 🎉**