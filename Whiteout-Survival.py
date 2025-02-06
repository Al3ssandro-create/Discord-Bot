from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import discord
import random
import os
from discord.ext import commands
from dotenv import load_dotenv
import logging
import json
import re
import time  # For rate limiting
from flask import Flask
from threading import Thread
import requests
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
# ---------------------------
# Logging Configuration
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# ---------------------------
# Environment Variables
# ---------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# ---------------------------
# Required Profile Keys
# ---------------------------
required_profile_keys = [
    "name",
    "dating_me_like",
    "way_to_heart",
    "known_for",
    "spontaneous_thing",
    "geek_out_on",
    "age",
    "job",
    "funny_fact"
]

# ---------------------------
# Initialize and Validate Profile Cache
# ---------------------------
profile_cache = {}
CACHE_FILE = "profile_cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        profile_cache = json.load(f)
    logging.info("Profile cache loaded.")
    
    # Validate and update existing profiles
    updated = False
    for member_id, profile in profile_cache.items():
        for key in required_profile_keys:
            if key not in profile:
                profile[key] = "N/A"  # Add missing key with a default value
                updated = True
                logging.warning(f"Added missing key '{key}' to profile of member ID {member_id}.")
            elif isinstance(profile[key], str) and not profile[key].strip():
                profile[key] = "N/A"  # Replace empty strings with a default value
                updated = True
                logging.warning(f"Updated empty key '{key}' to 'N/A' for member ID {member_id}.")
            elif isinstance(profile[key], int):
                # Ensure integer values are correctly handled; this might depend on your specific needs
                pass  # Do nothing for now, but add logic if needed (e.g., range checks)
    
    if updated:
        with open(CACHE_FILE, "w") as f:
            json.dump(profile_cache, f, indent=4)
        logging.info("Profile cache updated with missing or corrected keys.")

else:
    logging.info("No existing profile cache found. Starting fresh.")

# ---------------------------
# Initialize Likes Cache
# ---------------------------
likes_cache = {}
LIKES_CACHE_FILE = "likes_cache.json"
EVENTS_FILE = "events.json"

if os.path.exists(LIKES_CACHE_FILE):
    with open(LIKES_CACHE_FILE, "r") as f:
        likes_cache = json.load(f)
    logging.info("Likes cache loaded.")
else:
    logging.info("No existing likes cache found. Starting fresh.")

def save_likes_cache():
    with open(LIKES_CACHE_FILE, "w") as f:
        json.dump(likes_cache, f, indent=4)
    logging.info("Likes cache saved.")

# Load events from cache
def load_events():
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save events to cache
def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)
# ---------------------------
# Discord Bot Setup
# ---------------------------
intents = discord.Intents.default()
intents.members = True           # Enables the bot to see server members
intents.message_content = True   # Enables access to message content

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree
# ---------------------------
# Rate Limiting Setup
# ---------------------------
last_called = {}
RATE_LIMIT_SECONDS = 5  # Seconds between calls per user

async def can_generate_profile(user_id):
    current_time = time.time()
    if user_id in last_called:
        elapsed = current_time - last_called[user_id]
        if elapsed < RATE_LIMIT_SECONDS:
            return False, RATE_LIMIT_SECONDS - elapsed
    last_called[user_id] = current_time
    return True, 0




# ---------------------------
# Scheduler Setup
# ---------------------------
scheduler = AsyncIOScheduler()

# -----------------------------------
# Restore scheduled events from cache
# -----------------------------------
def restore_events():
    events = load_events()
    for event_id, data in events.items():
        mode = data["mode"]
        channel_id = data["channel_id"]
        message = data["message"]

        if mode == "weekly":
            trigger = CronTrigger(day_of_week=data["day_of_week"], hour=data["hour"], minute=data["minute"])
        elif mode == "interval":
            last_start = datetime.fromisoformat(data["start_time"])  # Restore the original start time
            now = datetime.utcnow()

            # Adjust the interval so it's aligned with the original start time
            time_passed = (now - last_start).total_seconds()
            interval_seconds = data["interval_value"] * 3600 if data["interval_unit"] == "hours" else data["interval_value"] * 86400
            next_run_seconds = interval_seconds - (time_passed % interval_seconds)

            trigger = IntervalTrigger(seconds=interval_seconds, start_date=now + timedelta(seconds=next_run_seconds))
        
        else:
            continue  # Skip unknown mode
        
        scheduler.add_job(notify_event, trigger, args=[channel_id, message], id=event_id, replace_existing=True)
    print(f"Restored {len(events)} scheduled events.")

# ---------------------------
# Likes Management Functions
# ---------------------------
def like_member(liker_id, likee_id):
    if likee_id not in likes_cache:
        likes_cache[likee_id] = []
        logging.info(f"Initialized likes list for member ID {likee_id}.")
    if liker_id not in likes_cache[likee_id]:
        likes_cache[likee_id].append(liker_id)
        save_likes_cache()
        logging.info(f"Member ID {liker_id} liked Member ID {likee_id}.")
        
        # Check if this creates a mutual match
        if likee_id in likes_cache.get(liker_id, []):
            return True  # Indicate that a new mutual match was created
        return True
    logging.warning(f"Member ID {liker_id} attempted to like Member ID {likee_id} again.")
    return False

# ---------------------------
# Likes Management Functions
# ---------------------------
def unlike_member(liker_id, likee_id):
    if likee_id in likes_cache and liker_id in likes_cache[likee_id]:
        likes_cache[likee_id].remove(liker_id)
        save_likes_cache()
        logging.info(f"Member ID {liker_id} unliked Member ID {likee_id}.")
        
        # Check if the likee had liked the liker, indicating a mutual match
        if likee_id in likes_cache.get(liker_id, []):
            # Since the liker is removing their like, the mutual match is broken
            return 1  # Indicate that a mutual match was broken
        return 2
    logging.warning(f"Member ID {liker_id} attempted to unlike Member ID {likee_id} without a prior like.")
    return 0

# ---------------------------
# get likes
# ---------------------------
def get_likes(member_id):
    result = []
    for user_id, profile in profile_cache.items():
        if user_id != member_id and member_id in likes_cache.get(user_id, []):
            result += [user_id]
    return result

# ---------------------------
# get matches
# ---------------------------
def get_matches(member_id):
    likers = set(likes_cache.get(member_id, []))
    logging.info(f"likers: {likers}")
    liked_members = set(get_likes(member_id))
    logging.info(f"liked: {liked_members}")
    mutual_matches = liked_members.intersection(likers)
    return list(mutual_matches)

# ---------------------------
# Profile Data Validation
# ---------------------------
def validate_profile_data(profile_data):
    for key in required_profile_keys:
        if key not in profile_data or not profile_data[key].strip():
            logging.warning(f"Missing or empty key in profile data: {key}")
            profile_data[key] = "N/A"
    return profile_data

# ---------------------------
# Flask Web Server Setup
# ---------------------------
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

# ---------------------------
# Discord Bot Events and Commands
# ---------------------------
@bot.event
async def on_ready():
    try:
        await tree.sync()  # Force sync all commands
        logging.info(f'✅ Slash commands synced!')
        # check the name of the commands
        commands = [command.name for command in tree.get_commands()]
        logging.info(f'Commands: {commands}')
    except Exception as e:
        logging.error(f'❌ Error syncing commands: {e}')
        
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info('------')
    # Ensure to check if the scheduler is already running before starting it
    if not scheduler.running:
        scheduler.start()
        logging.info("Scheduler started.")
    restore_events()
    

# ---------------------------
# Generate Profile using Groq
# ---------------------------
async def generate_profile_with_groq(member_name):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    prompt = f"""
    Create a dating profile for {member_name} with the following fields:
    - Dating me is like...
    - The way to my heart is...
    - I'm known for...
    - Most spontaneous thing I’ve done...
    - I geek out on...
    - Age (random between 22-35)
    - Job
    - A funny fact about me...
    Format the response in JSON with these exact keys: name, dating_me_like, way_to_heart, known_for, spontaneous_thing, geek_out_on, age, job, funny_fact.
    """
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        try:
            content = response_data["choices"][0]["message"]["content"]
            # Regex to match content enclosed in triple backticks, json part optional
            json_str = re.search(r"```(?:json\n)?(.+?)\n```", content, re.DOTALL).group(1)
            profile_data = json.loads(json_str)
            return profile_data
        except IndexError as e:
            logging.error(f"Index error when accessing response data: {e}. Content may not be properly formatted.")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding failed: {e}. Check the formatting of the JSON string.")
            return None
        except AttributeError as e:
            logging.error(f"Attribute error during regex search: {e}. Possible incorrect or missing JSON boundaries.")
            return None
    else:
        logging.error(f"API call failed with status {response.status_code}: {response.text}")
        return None


    
def save_cache():
    with open(CACHE_FILE, "w") as f:
        json.dump(profile_cache, f, indent=4)
    logging.info("Profile cache saved.")

# ---------------------------
# Slash Commands to Generate Profile
# ---------------------------
@tree.command(name="profile", description="Generate or view your dating profile")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user
    if member.bot:
        await interaction.response.send_message("Cannot generate profiles for bots.")
        return

    member_id = str(member.id)
    if member_id not in profile_cache:
        profile_data = await generate_profile_with_groq(member.display_name)
        if not isinstance(profile_data, dict):
            await interaction.response.send_message("Failed to generate a valid profile. Please try again.")
            return
        profile_cache[member_id] = profile_data
        save_cache()

    profile_data = profile_cache.get(member_id, {})
    embed = discord.Embed(title=f"{member.display_name}", color=discord.Color.blue())
    # Define a mapping of field keys to their corresponding emojis and titles
    field_emojis = {
        "name": "🔖 **Name:**",
        "dating_me_like": "💡 **Dating me is like:**",
        "way_to_heart": "✨ **The way to my heart is:**",
        "known_for": "🏆 **I’m known for:**",
        "spontaneous_thing": "🚀 **Most spontaneous thing I’ve done:**",
        "geek_out_on": "🎮 **I geek out on:**",
        "age": "🎂 **Age:**",
        "job": "💼 **Job:**",
        "funny_fact": "😂 **A funny fact about me:**"
    }

    for key, value in profile_data.items():
        # Use get to return the default title if key is not found in field_emojis
        title = field_emojis.get(key, key.replace('_', ' ').title())
        embed.add_field(name=title, value=value, inline=False)

    embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://via.placeholder.com/128")
    await interaction.response.send_message(embed=embed)

# ---------------------------
# Slash Command to Reset a Member's Profile (Admins Only)
# ---------------------------
@tree.command(name="resetprofile", description="Reset a member's dating profile")
@commands.has_permissions(administrator=True)
async def reset_profile_command(interaction: discord.Interaction, member: discord.Member):
    member_id = str(member.id)
    
    if member_id in profile_cache:
        del profile_cache[member_id]
        save_cache()
        logging.info(f"Profile for {member.display_name} has been reset.")
        await interaction.response.send_message(f"Profile for {member.display_name} has been reset.")
    else:
        await interaction.response.send_message(f"No existing profile found for {member.display_name}.")

# ---------------------------
# Slash Command to List All Cached Profiles (Admins Only)
# ---------------------------
@tree.command(name="listprofiles", description="List all cached dating profiles")
@commands.has_permissions(administrator=True)
async def list_profiles_command(interaction: discord.Interaction):
    if not profile_cache:
        await interaction.response.send_message("No profiles have been generated yet.")
        return
    
    embed = discord.Embed(
        title="📄 Cached Hinge Profiles",
        color=discord.Color.green()
    )
    
    for member_id, profile in profile_cache.items():
        member = interaction.guild.get_member(int(member_id))
        if member:
            embed.add_field(
                name=f"{member.display_name}",
                value=f"**Age:** {profile.get('age', 'N/A')}, **Job:** {profile.get('job', 'N/A')}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)
# ---------------------------
# Slash Command to see scheduled Event
# ---------------------------
@tree.command(name="list_scheduled_events", description="View all scheduled events for this channel")
async def list_scheduled_events(interaction: discord.Interaction):
    event_list = []
    channel_id = interaction.channel_id
    guild_id = interaction.guild_id

    for job in scheduler.get_jobs():
        if job.id.startswith(f"{guild_id}_"):  # Ensure it's an event from this server
            trigger = job.trigger
            event_name = job.id.split("_", 1)[1]  # Extract event name

            if isinstance(trigger, CronTrigger):
                # Weekly event
                event_type = "Weekly"
                schedule_info = f"Every {trigger.fields[4]} at {trigger.fields[2]}:{trigger.fields[1]}"
            elif isinstance(trigger, IntervalTrigger):
                # Interval-based event
                event_type = "Interval"
                schedule_info = f"Every {trigger.interval_length} {trigger.interval}"
            else:
                continue  # Skip unknown trigger types
            # Extract message argument from job
            job_args = job.args
            if len(job_args) > 1 and job_args[0] == channel_id:  # Ensure message is for the same channel
                event_message = job_args[1]
                event_list.append(f"**{event_name}**\n> **Type:** {event_type}\n> **Schedule:** {schedule_info}\n> **Message:** {event_message}")

    if event_list:
        event_display = "\n\n".join(event_list)
        await interaction.response.send_message(f"### 🗓 Scheduled Events for this Channel:\n{event_display}", ephemeral=True)
    else:
        await interaction.response.send_message("No scheduled events found for this channel.", ephemeral=True)



# ---------------------------
# Slash Command to Schedule a Weekly Event
# ---------------------------
@tree.command(name="schedule_event", description="Schedule a recurring event with a unique name and custom notification message")
@discord.app_commands.describe(
    event_name="Name of the event",
    mode="Choose 'weekly' (specific day & time) or 'interval' (every X time units)",
    day_of_week="(For 'weekly' mode) Day of the week (e.g., monday, tuesday, etc.)",
    time="(For 'weekly' mode) Time of the event (HH:MM format, 24-hour)",
    interval_value="(For 'interval' mode) Number of units between notifications",
    interval_unit="(For 'interval' mode) Unit: minutes, hours, or days",
    start_time="(For 'interval' mode) Time when the first occurrence should start (HH:MM 24-hour format)",
    message="Custom message to send when notifying"
)
async def schedule_event(
    interaction: discord.Interaction,
    event_name: str,
    mode: str,
    day_of_week: str = None,
    time: str = None,
    interval_value: int = None,
    interval_unit: str = None,
    start_time: str = None,
    message: str = None
):
    event_id = f"{interaction.guild_id}_{event_name}"
    events = load_events()

    try:
        if mode.lower() == "weekly":
            if not day_of_week or not time:
                await interaction.response.send_message("For weekly scheduling, provide `day_of_week` and `time` (HH:MM).", ephemeral=True)
                return

            hour, minute = map(int, time.split(":"))
            trigger = CronTrigger(day_of_week=day_of_week.lower(), hour=hour, minute=minute)

            events[event_id] = {
                "mode": "weekly",
                "channel_id": interaction.channel_id,
                "day_of_week": day_of_week.lower(),
                "hour": hour,
                "minute": minute,
                "message": message
            }

            scheduler.add_job(notify_event, trigger, args=[interaction.channel_id, message], id=event_id, replace_existing=True)
            await interaction.response.send_message(f"Scheduled event '{event_name}' for every {day_of_week} at {time}.")

        elif mode.lower() == "interval":
            if not interval_value or not interval_unit or not start_time:
                await interaction.response.send_message("For interval scheduling, provide `interval_value`, `interval_unit`, and `start_time` (HH:MM).", ephemeral=True)
                return

            hour, minute = map(int, start_time.split(":"))
            now = datetime.utcnow()
            first_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            if first_run < now:
                first_run += timedelta(days=1)

            unit_mapping = {"minutes": "minutes", "hours": "hours", "days": "days"}
            if interval_unit.lower() not in unit_mapping:
                await interaction.response.send_message("Invalid `interval_unit`. Choose 'minutes', 'hours', or 'days'.", ephemeral=True)
                return

            trigger = IntervalTrigger(**{unit_mapping[interval_unit.lower()]: interval_value}, start_date=first_run)

            events[event_id] = {
                "mode": "interval",
                "channel_id": interaction.channel_id,
                "interval_value": interval_value,
                "interval_unit": interval_unit.lower(),
                "start_time": first_run.isoformat(),
                "message": message
            }

            scheduler.add_job(notify_event, trigger, args=[interaction.channel_id, message], id=event_id, replace_existing=True)
            await interaction.response.send_message(f"Scheduled event '{event_name}' to repeat every {interval_value} {interval_unit} starting at {start_time}.")

        else:
            await interaction.response.send_message("Invalid mode. Choose 'weekly' or 'interval'.", ephemeral=True)

        save_events(events)

    except Exception as e:
        logging.error(f"Failed to schedule event: {str(e)}")
        await interaction.response.send_message(f"Failed to schedule event: {str(e)}", ephemeral=True)

# ---------------------------
# Slash Command to Remove a Scheduled Event
# ---------------------------
@tree.command(name="remove_event", description="Remove a scheduled weekly event by name")
@discord.app_commands.describe(event_name="Name of the event")
async def remove_event(interaction: discord.Interaction, event_name: str):
    event_id = f"{interaction.guild_id}_{event_name}"   
    if scheduler.get_job(event_id):
        scheduler.remove_job(event_id)
        await interaction.response.send_message(f"Event '{event_name}' has been removed.")
    else:
        await interaction.response.send_message(f"No event found with name '{event_name}'.")

async def notify_event(channel_id, message):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(message)

# ---------------------------
# Slash Command to Like a Member's Profile
# ---------------------------
@tree.command(name="like", description="Like another user's dating profile")
async def like_command(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        await interaction.response.send_message("You cannot like bots.")
        return
    if member == interaction.user:
        await interaction.response.send_message("You cannot like yourself.")
        return
    
    liker_id = str(interaction.user.id)
    likee_id = str(member.id)
    
    if likee_id not in likes_cache:
        likes_cache[likee_id] = []
    
    if liker_id in likes_cache[likee_id]:
        await interaction.response.send_message(f"You have already liked {member.display_name}'s profile.")
        logging.info(f"{interaction.user.display_name} attempted to like {member.display_name}'s profile again.")
        return
    
    likes_cache[likee_id].append(liker_id)
    save_cache()
    await interaction.response.send_message(f"{interaction.user.display_name} liked {member.display_name}'s profile! ❤️")
    logging.info(f"{interaction.user.display_name} liked {member.display_name}'s profile.")
    
    if likee_id in likes_cache.get(liker_id, []):
        likee_member = interaction.guild.get_member(int(likee_id))
        liker_member = interaction.guild.get_member(int(liker_id))
        if likee_member and liker_member:
            try:
                await likee_member.send(f"🎉 You have a new match! {interaction.user.display_name} liked your profile and you liked theirs.")
                await liker_member.send(f"🎉 You have a new match! {member.display_name} liked your profile and you liked theirs.")
                logging.info(f"Notified {likee_member.display_name} of a new match with {interaction.user.display_name}.")
                logging.info(f"Notified {liker_member.display_name} of a new match with {member.display_name}.")
            except Exception as e:
                logging.error(f"Failed to send DM to {likee_member.display_name}: {e}")
# ---------------------------
# Slash Command to Unlike a Member's Profile
# ---------------------------
@tree.command(name="unlike", description="Unlike a user's dating profile")
async def unlike_command(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        await interaction.response.send_message("You cannot unlike bots.")
        return
    if member == interaction.user:
        await interaction.response.send_message("You cannot unlike yourself.")
        return
    
    liker_id = str(interaction.user.id)
    likee_id = str(member.id)
    
    if liker_id in likes_cache.get(likee_id, []):
        likes_cache[likee_id].remove(liker_id)
        save_cache()
        await interaction.response.send_message(f"{interaction.user.display_name} unliked {member.display_name}'s profile.")
        logging.info(f"{interaction.user.display_name} unliked {member.display_name}'s profile.")
        
        if likee_id in likes_cache.get(liker_id, []):
            likee_member = interaction.guild.get_member(int(likee_id))
            if likee_member:
                try:
                    await likee_member.send(f"💔 {interaction.user.display_name} has unliked your profile. Your match is no longer mutual.")
                    logging.info(f"Notified {likee_member.display_name} of the broken match with {interaction.user.display_name}.")
                except Exception as e:
                    logging.error(f"Failed to send DM to {likee_member.display_name}: {e}")
    else:
        await interaction.response.send_message(f"You have not liked {member.display_name}'s profile.")
        logging.info(f"{interaction.user.display_name} attempted to unlike {member.display_name}'s profile without a prior like.")

# ---------------------------
# Slash Command to View Who Liked Your Profile
# ---------------------------
@tree.command(name="likes", description="View who has liked your dating profile")
async def likes_command(interaction: discord.Interaction):
    member_id = str(interaction.user.id)
    likers_ids = [user_id for user_id in likes_cache if member_id in likes_cache[user_id]]
    
    if not likers_ids:
        await interaction.response.send_message("No one has liked your profile yet.")
        return
    
    likers = [interaction.guild.get_member(int(liker_id)) for liker_id in likers_ids]
    likers = [member for member in likers if member]  # Filter out None values
    
    description = "\n".join([member.mention for member in likers])
    
    embed = discord.Embed(
        title=f"❤️ Likes for {interaction.user.display_name}",
        description=description,
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else "https://via.placeholder.com/128")
    await interaction.response.send_message(embed=embed)


# ---------------------------
# Slash Command to View Mutual Matches
# ---------------------------
@tree.command(name="mymatches", description="View your mutual matches")
async def mymatches_command(interaction: discord.Interaction):
    member_id = str(interaction.user.id)
    matches_ids = [user_id for user_id in likes_cache.get(member_id, []) if member_id in likes_cache.get(user_id, [])]
    
    if not matches_ids:
        await interaction.response.send_message("You have no matches yet.")
        return
    
    matches = [interaction.guild.get_member(int(match_id)) for match_id in matches_ids]
    matches = [member for member in matches if member]  # Filter out None values
    
    description = "\n".join([member.mention for member in matches])
    
    embed = discord.Embed(
        title=f"💞 Your Matches",
        description=description,
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else "https://via.placeholder.com/128")
    await interaction.response.send_message(embed=embed)


# ---------------------------
# Slash Command to Find Potential Matches
# ---------------------------
@tree.command(name="findmatches", description="Find random potential matches")
async def findmatches_command(interaction: discord.Interaction):
    all_profiles = list(profile_cache.values())
    
    if len(all_profiles) < 5:
        potential_matches = all_profiles  # Show all if less than 5 exist
    else:
        potential_matches = random.sample(all_profiles, 5)  # Pick 5 random profiles
    
    if not potential_matches:
        await interaction.response.send_message("No potential matches found at the moment.")
        return
    
    embed = discord.Embed(
        title=f"🔍 Potential Matches for {interaction.user.display_name}",
        color=discord.Color.gold()
    )
    
    for profile in potential_matches:
        embed.add_field(
            name=f"{profile['name']}",
            value=f"💡 **Dating me is like:** {profile['dating_me_like']}\n💼 **Job:** {profile['job']}\n🎂 **Age:** {profile['age']}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# ---------------------------
# Command to show bot instructions
# ---------------------------
@tree.command(name="help", description="Show bot instructions")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 Bot Instructions",
        description="Welcome to the Discord Matchmaking Bot! Here's how you can interact with me:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📌 **/profile [@User]**",
        value="Generate or view a user's profile. If no user is mentioned, it defaults to your own profile.",
        inline=False
    )

    embed.add_field(
        name="🔄 **/resetprofile @User**",
        value="Reset a user's profile. Only administrators can use this command.",
        inline=False
    )
    embed.add_field(
        name="📋 **/listprofiles**",
        value="List all cached profiles. Only administrators can use this command.",
        inline=False
    )
    embed.add_field(
        name="/schedule_event",
        value="Schedule a weekly event. Only administrators can use this command. (e.g schedule_event event_name day_of_week time message)",
        inline=False
    )
    embed.add_field(
        name="/remove_event",
        value="Remove a scheduled weekly event. Only administrators can use this command. (e.g remove_event event_name)",
        inline=False
    )   

    

    embed.add_field(
        name="👍 **/like @User**",
        value="Like another user's profile. If both users like each other, a mutual match is created!",
        inline=False
    )

    embed.add_field(
        name="👎 **/unlike @User**",
        value="Unlike a user you have previously liked, potentially breaking a mutual match.",
        inline=False
    )

    embed.add_field(
        name="💞 **/mymatches**",
        value="View all your mutual matches.",
        inline=False
    )

    embed.add_field(
        name="❤️ **/likes**",
        value="See who has liked your profile.",
        inline=False
    )

    embed.add_field(
        name="🔍 **/findmatches**",
        value="Find potential matches based on existing likes.",
        inline=False
    )

    embed.add_field(
        name="🏆 **/toplikes [number]**",
        value="View the top profiles ranked by the number of likes they have received. Default is 5.",
        inline=False
    )

    embed.set_footer(text="Use these commands to interact with the bot and enhance your Discord experience!")

    await interaction.response.send_message(embed=embed)  # ✅ Fixed sending method


@tree.command(name="sendmessage")
async def send_message(interaction: discord.Interaction):
    await interaction.response.send_message("I am the new leader of the server, this is going to be the POTATO server")

@tree.command(name="toplikes", description="View top profiles by likes")
async def toplikes_command(interaction: discord.Interaction, number: int = 5):
    if number <= 0:
        await interaction.response.send_message("Please enter a positive number.")
        return
    
    # Calculate like counts
    like_counts = {member_id: len(likers) for member_id, likers in likes_cache.items()}
    
    # Sort members by like counts in descending order
    sorted_likes = sorted(like_counts.items(), key=lambda item: item[1], reverse=True)
    
    if not sorted_likes:
        await interaction.response.send_message("No profiles have been liked yet.")
        return
    
    # Limit the number of top profiles
    sorted_likes = sorted_likes[:number]
    
    description = ""
    for idx, (member_id, count) in enumerate(sorted_likes, start=1):
        member = interaction.guild.get_member(int(member_id))  # ✅ Fix ctx.guild -> interaction.guild
        if member:
            description += f"{idx}. {member.mention} - {count} like{'s' if count != 1 else ''}\n"
    
    embed = discord.Embed(
        title=f"🏆 Top {len(sorted_likes)} Profiles by Likes",
        description=description,
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://via.placeholder.com/128")  # Optional: Use a trophy icon or relevant image
    
    await interaction.response.send_message(embed=embed)  # ✅ Fix ctx.send -> interaction.response.send_message


# Handle command errors gracefully
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Sorry, I didn't understand that command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param.name}")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command.")
    else:
        logging.error(f'An error occurred: {error}')
        await ctx.send("An unexpected error occurred. Please try again later.")

# Save cache on shutdown
@bot.event
async def on_disconnect():
    save_likes_cache()
    with open(CACHE_FILE, "w") as f:
        json.dump(profile_cache, f, indent=4)
    logging.info("Profile and likes cache saved on disconnect.")

# ---------------------------
# Running Flask and Discord Bot
# ---------------------------
def keep_alive():
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

def run_flask():
    app.run(host='0.0.0.0', port=7123)

# Start the web server before running the bot
keep_alive()

# Run the Discord bot
bot.run(TOKEN)