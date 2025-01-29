import discord
import random
import os
from discord.ext import commands
from dotenv import load_dotenv
import logging
import json
import re
import time  # For rate limiting

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
            if key not in profile or not profile[key].strip():
                profile[key] = "N/A"
                updated = True
                logging.warning(f"Added missing key '{key}' to profile of member ID {member_id}.")
    
    if updated:
        with open(CACHE_FILE, "w") as f:
            json.dump(profile_cache, f, indent=4)
        logging.info("Profile cache updated with missing keys.")
else:
    logging.info("No existing profile cache found. Starting fresh.")

# ---------------------------
# Initialize Likes Cache
# ---------------------------
likes_cache = {}
LIKES_CACHE_FILE = "likes_cache.json"

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

# ---------------------------
# Expanded Profile Data
# ---------------------------
# Expanded profile prompts
profile_prompts = [
    "Dating me is like...",
    "The way to my heart is...",
    "I’m known for...",
    "Most spontaneous thing I’ve done...",
    "I geek out on...",
    "Age:",
    "Job:",
    "A funny fact about me:",
]

# Expanded personality traits
dating_like_options = [
    "Embarking on a thrilling adventure where every day brings new surprises.",
    "Enjoying cozy nights in with good company and great conversations.",
    "Experiencing a blend of excitement and comfort in every moment.",
    "Exploring new horizons together while cherishing our roots.",
    "Balancing spontaneity with thoughtful planning for unforgettable experiences.",
]

way_to_heart_options = [
    "Heartfelt conversations over a cup of coffee.",
    "Surprising me with small, meaningful gestures.",
    "Sharing your favorite books and music with me.",
    "Being genuine and authentic in every interaction.",
    "Showing kindness and empathy in everyday actions.",
]

known_for_options = [
    "My culinary skills and spontaneous weekend getaways.",
    "Organizing epic game nights and unforgettable parties.",
    "My dedication to fitness and outdoor adventures.",
    "Creating beautiful art pieces and appreciating creativity.",
    "Being the go-to person for tech troubleshooting and innovations.",
]

spontaneous_things_options = [
    "Booking a last-minute flight to Bali.",
    "Joining a flash mob in the middle of the city.",
    "Signing up for an impromptu cooking class abroad.",
    "Participating in a spontaneous road trip across the country.",
    "Surprising friends with unplanned outdoor movie nights.",
]

geek_out_on_options = [
    "Astronomy and the mysteries of the universe.",
    "The latest advancements in technology and gadgets.",
    "Deep dives into fantasy and sci-fi novels.",
    "Innovative video game strategies and developments.",
    "Exploring the intricacies of programming and software development.",
]

age_options = [
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
]

job_options = [
    "Software Developer",
    "Graphic Designer",
    "Digital Marketer",
    "Data Analyst",
    "Project Manager",
    "Content Creator",
    "Mechanical Engineer",
    "Financial Advisor",
    "Healthcare Professional",
    "Entrepreneur",
    "Teacher",
    "Sales Manager",
    "Architect",
    "Photographer",
]

funny_facts = [
    "I can juggle three oranges while riding a unicycle.",
    "I once accidentally sent a text to my boss meant for my friend.",
    "I have a collection of over 100 quirky socks.",
    "I can recite the alphabet backward in under 10 seconds.",
    "I survived a week without any technology—only using a typewriter.",
    "I once won a dance-off in a flash mob.",
    "I can whistle the entire Star Wars theme song.",
    "I built my own mini-golf course in the backyard.",
    "I’ve been to three different continents in a single year.",
    "I can make a perfect pancake flip every single time.",
    "I once met a celebrity at a coffee shop and didn't recognize them.",
    "I can solve a Rubik's cube in under a minute.",
    "I have a knack for finding the best hidden gems in any city.",
    "I once participated in a reality TV show as an extra.",
    "I can speak three languages fluently.",
]

# ---------------------------
# Discord Bot Setup
# ---------------------------
intents = discord.Intents.default()
intents.members = True           # Enables the bot to see server members
intents.message_content = True   # Enables access to message content

bot = commands.Bot(command_prefix="!", intents=intents)

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

def get_likes(member_id):
    result = []
    for user_id, profile in profile_cache.items():
        if user_id != member_id and member_id in likes_cache.get(user_id, []):
            result += [user_id]
    return result


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
# Profile Generation Function
# ---------------------------
async def generate_profile_content(member):
    member_id = str(member.id)
    # Check if profile exists in cache
    if member_id in profile_cache:
        logging.info(f"Profile for {member.display_name} fetched from cache.")
        return profile_cache[member_id]
    
    # Generate profile by selecting random prompts and traits
    try:
        profile_details = {}
        for prompt in profile_prompts:
            if prompt == "Age:":
                trait = random.choice(age_options)
                profile_details["Age"] = trait
            elif prompt == "Job:":
                trait = random.choice(job_options)
                profile_details["Job"] = trait
            elif prompt == "A funny fact about me:":
                trait = random.choice(funny_facts)
                profile_details["A funny fact about me"] = trait
            else:
                if prompt.startswith("Dating me is like"):
                    trait = random.choice(dating_like_options)
                elif prompt.startswith("The way to my heart is"):
                    trait = random.choice(way_to_heart_options)
                elif prompt.startswith("I’m known for"):
                    trait = random.choice(known_for_options)
                elif prompt.startswith("Most spontaneous thing I’ve done"):
                    trait = random.choice(spontaneous_things_options)
                elif prompt.startswith("I geek out on"):
                    trait = random.choice(geek_out_on_options)
                else:
                    trait = "N/A"
                # Remove trailing colon and ellipsis if present
                if prompt.endswith("..."):
                    prompt_clean = prompt[:-3]
                elif prompt.endswith(":"):
                    prompt_clean = prompt[:-1]
                else:
                    prompt_clean = prompt
                profile_details[prompt_clean] = trait
        
        # Structure the profile data
        profile_data = {
            "name": member.display_name,
            "dating_me_like": profile_details.get("Dating me is like", "N/A"),
            "way_to_heart": profile_details.get("The way to my heart is", "N/A"),
            "known_for": profile_details.get("I’m known for", "N/A"),
            "spontaneous_thing": profile_details.get("Most spontaneous thing I’ve done", "N/A"),
            "geek_out_on": profile_details.get("I geek out on", "N/A"),
            "age": profile_details.get("Age", "N/A"),
            "job": profile_details.get("Job", "N/A"),
            "funny_fact": profile_details.get("A funny fact about me", "N/A"),
        }
        
        # Validate profile data
        profile_data = validate_profile_data(profile_data)
        
        # Store in cache
        profile_cache[member_id] = profile_data
        logging.info(f"Profile for {member.display_name} stored in cache.")
        
        # Save cache to file
        with open(CACHE_FILE, "w") as f:
            json.dump(profile_cache, f, indent=4)
        logging.info("Profile cache updated.")
        
        return profile_data
    except Exception as e:
        logging.error(f"Error generating profile content for {member.display_name}: {e}")
        return None

# ---------------------------
# Discord Bot Events and Commands
# ---------------------------
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    logging.info('------')

# Command to generate a profile for a tagged member or yourself
@bot.command(name="profile")
async def generate_profile_command(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Default to the command issuer
    elif member.bot:
        await ctx.send("Cannot generate profiles for bots.")
        return
    
    can_proceed, wait_time = await can_generate_profile(ctx.author.id)
    if not can_proceed:
        await ctx.send(f"Please wait {int(wait_time)} more seconds before generating another profile.")
        return

    logging.info(f'Generating profile for {member.display_name}')
    
    profile_data = await generate_profile_content(member)
    
    if profile_data is None:
        await ctx.send("Sorry, I couldn't generate a profile at this time.")
        return
    
    # Create profile description with enhanced formatting
    profile_description = (
        f"💡 **Dating me is like:** *{profile_data.get('dating_me_like', 'N/A')}*\n\n"
        f"✨ **The way to my heart is:** *{profile_data.get('way_to_heart', 'N/A')}*\n\n"
        f"🏆 **I’m known for:** *{profile_data.get('known_for', 'N/A')}*\n\n"
        f"🚀 **Most spontaneous thing I’ve done:** *{profile_data.get('spontaneous_thing', 'N/A')}*\n\n"
        f"🎮 **I geek out on:** *{profile_data.get('geek_out_on', 'N/A')}*\n\n"
        f"🎂 **Age:** *{profile_data.get('age', 'N/A')}*\n\n"
        f"💼 **Job:** *{profile_data.get('job', 'N/A')}*\n\n"
        f"😂 **A funny fact about me:** *{profile_data.get('funny_fact', 'N/A')}*"
    )
    
    embed = discord.Embed(
        title=f"📍 {member.display_name}'s Hinge Profile",
        description=profile_description,
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://via.placeholder.com/128")
    await ctx.send(embed=embed)

# Command to manually generate a profile for yourself
@bot.command(name="myprofile")
async def my_profile_command(ctx):
    await generate_profile_command(ctx)  # Reuse the generate_profile_command function

# Command to reset a member's profile (Admins only)
@bot.command(name="resetprofile")
@commands.has_permissions(administrator=True)
async def reset_profile_command(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Default to the command issuer
    
    member_id = str(member.id)
    if member_id in profile_cache:
        del profile_cache[member_id]
        # Update the cache file
        with open(CACHE_FILE, "w") as f:
            json.dump(profile_cache, f, indent=4)
        logging.info(f"Profile for {member.display_name} has been reset.")
        await ctx.send(f"Profile for {member.display_name} has been reset.")
    else:
        await ctx.send(f"No existing profile found for {member.display_name}.")

# Command to list all cached profiles (Admins only)
@bot.command(name="listprofiles")
@commands.has_permissions(administrator=True)
async def list_profiles_command(ctx):
    if not profile_cache:
        await ctx.send("No profiles have been generated yet.")
        return
    
    embed = discord.Embed(
        title="📄 Cached Hinge Profiles",
        color=discord.Color.green()
    )
    
    for member_id, profile in profile_cache.items():
        member = ctx.guild.get_member(int(member_id))
        if member:
            embed.add_field(
                name=f"{member.display_name}",
                value=f"**Age:** {profile.get('age', 'N/A')}, **Job:** {profile.get('job', 'N/A')}",
                inline=False
            )
    
    await ctx.send(embed=embed)

# Command to like a member's profile
@bot.command(name="like")
async def like_command(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Please mention a member to like their profile.")
        return
    if member.bot:
        await ctx.send("You cannot like bots.")
        return
    if member == ctx.author:
        await ctx.send("You cannot like yourself.")
        return
    
    liker_id = str(ctx.author.id)
    likee_id = str(member.id)
    
    if like_member(liker_id, likee_id):
        await ctx.send(f"{ctx.author.display_name} liked {member.display_name}'s profile! ❤️")
        logging.info(f"{ctx.author.display_name} liked {member.display_name}'s profile.")
        
        # Check if this creates a new mutual match
        if likee_id in likes_cache.get(liker_id, []):
            likee_member = ctx.guild.get_member(int(likee_id))
            liker_member = ctx.guild.get_member(int(liker_id))
            if likee_member and liker_member:
                try:
                    await likee_member.send(f"🎉 You have a new match! {ctx.author.display_name} liked your profile and you liked theirs.")
                    await liker_member.send(f"🎉 You have a new match! {member.display_name} liked your profile and you liked theirs.")
                    logging.info(f"Notified {likee_member.display_name} of a new match with {ctx.author.display_name}.")
                    logging.info(f"Notified {liker_member.display_name} of a new match with {member.display_name}.")
                except Exception as e:
                    logging.error(f"Failed to send DM to {likee_member.display_name}: {e}")
    else:
        await ctx.send(f"You have already liked {member.display_name}'s profile.")
        logging.info(f"{ctx.author.display_name} attempted to like {member.display_name}'s profile again.")

# Command to unlike a member's profile
@bot.command(name="unlike")
async def unlike_command(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Please mention a member to unlike their profile.")
        return
    if member.bot:
        await ctx.send("You cannot unlike bots.")
        return
    if member == ctx.author:
        await ctx.send("You cannot unlike yourself.")
        return
    
    liker_id = str(ctx.author.id)
    likee_id = str(member.id)
    
    if unlike_member(liker_id, likee_id) > 0:
        await ctx.send(f"{ctx.author.display_name} unliked {member.display_name}'s profile.")
        logging.info(f"{ctx.author.display_name} unliked {member.display_name}'s profile.")
        
        # Notify the likee about the match being broken
        # Check if a mutual match existed before unliking
        if likee_id in likes_cache.get(liker_id, []):
            likee_member = ctx.guild.get_member(int(likee_id))
            if likee_member:
                try:
                    await likee_member.send(f"💔 {ctx.author.display_name} has unliked your profile. Your match is no longer mutual.")
                    logging.info(f"Notified {likee_member.display_name} of the broken match with {ctx.author.display_name}.")
                except Exception as e:
                    logging.error(f"Failed to send DM to {likee_member.display_name}: {e}")
    else:
        await ctx.send(f"You have not liked {member.display_name}'s profile.")
        logging.info(f"{ctx.author.display_name} attempted to unlike {member.display_name}'s profile without a prior like.")

# Command to show who has liked your profile
@bot.command(name="likes")
async def likes_command(ctx):
    member_id = str(ctx.author.id)
    likers_ids = get_likes(member_id)
    
    if not likers_ids:
        await ctx.send("No one has liked your profile yet.")
        return
    
    likers = [ctx.guild.get_member(int(liker_id)) for liker_id in likers_ids]
    likers = [member for member in likers if member]  # Filter out None values
    
    description = "\n".join([member.mention for member in likers])
    
    embed = discord.Embed(
        title=f"❤️ Likes for {ctx.author.display_name}",
        description=description,
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://via.placeholder.com/128")
    await ctx.send(embed=embed)

# Command to show mutual matches
@bot.command(name="mymatches")
async def mymatches_command(ctx):
    member_id = str(ctx.author.id)
    matches_ids = get_matches(member_id)
    
    if not matches_ids:
        await ctx.send("You have no matches yet.")
        return
    
    matches = [ctx.guild.get_member(int(match_id)) for match_id in matches_ids]
    matches = [member for member in matches if member]  # Filter out None values
    
    description = "\n".join([member.mention for member in matches])
    
    embed = discord.Embed(
        title=f"💞 Your Matches",
        description=description,
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://via.placeholder.com/128")
    await ctx.send(embed=embed)

# Command to find potential matches
@bot.command(name="findmatches")
async def findmatches_command(ctx):
    member_id = str(ctx.author.id)
    likers_ids = set(get_likes(member_id))
    liked_ids = set(likes_cache.get(member_id, []))
    
    # Potential matches: Members who haven't liked you and whom you haven't liked
    # Also, exclude yourself
    potential_matches_ids = set(likes_cache.keys()) - likers_ids - liked_ids - {member_id}
    
    if not potential_matches_ids:
        await ctx.send("No potential matches found at the moment.")
        return
    
    # Limit the number of suggestions to 5
    potential_matches_ids = list(potential_matches_ids)[:5]
    potential_matches = [ctx.guild.get_member(int(match_id)) for match_id in potential_matches_ids]
    potential_matches = [member for member in potential_matches if member]  # Filter out None values
    
    if not potential_matches:
        await ctx.send("No potential matches found at the moment.")
        return
    
    description = "\n".join([member.mention for member in potential_matches])
    
    embed = discord.Embed(
        title=f"🔍 Potential Matches for {ctx.author.display_name}",
        description=description,
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "https://via.placeholder.com/128")
    await ctx.send(embed=embed)

# Command to list top profiles by likes
@bot.command(name="toplikes")
async def toplikes_command(ctx, number: int = 5):
    if number <= 0:
        await ctx.send("Please enter a positive number.")
        return
    
    # Calculate like counts
    like_counts = {member_id: len(likers) for member_id, likers in likes_cache.items()}
    
    # Sort members by like counts in descending order
    sorted_likes = sorted(like_counts.items(), key=lambda item: item[1], reverse=True)
    
    if not sorted_likes:
        await ctx.send("No profiles have been liked yet.")
        return
    
    # Limit the number of top profiles
    sorted_likes = sorted_likes[:number]
    
    description = ""
    for idx, (member_id, count) in enumerate(sorted_likes, start=1):
        member = ctx.guild.get_member(int(member_id))
        if member:
            description += f"{idx}. {member.mention} - {count} like{'s' if count != 1 else ''}\n"
    
    embed = discord.Embed(
        title=f"🏆 Top {len(sorted_likes)} Profiles by Likes",
        description=description,
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://via.placeholder.com/128")  # Optional: Use a trophy icon or relevant image
    await ctx.send(embed=embed)

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

# Run the bot
bot.run(TOKEN)
