import discord
from discord.ext import commands
import re
import asyncio
from typing import Set

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Set to track recent jokes to avoid spam
recent_jokes: Set[str] = set()
JOKE_COOLDOWN = 30  # seconds

# Common words ending in -er that are at least 2 syllables
# This is a curated list to avoid false positives
ER_WORDS = {
    'cleaner', 'teacher', 'player', 'builder', 'painter', 'writer', 'speaker',
    'maker', 'taker', 'baker', 'dancer', 'singer', 'fighter', 'driver',
    'rider', 'slider', 'leader', 'reader', 'feeder', 'breeder', 'keeper',
    'sleeper', 'weeper', 'helper', 'killer', 'filler', 'spiller', 'thriller',
    'dealer', 'healer', 'stealer', 'sealer', 'peeler', 'wheeler', 'reeler',
    'planner', 'scanner', 'banner', 'manner', 'dinner', 'winner', 'sinner',
    'spinner', 'beginner', 'runner', 'gunner', 'cunner', 'stunner',
    'corner', 'warner', 'mourner', 'burner', 'turner', 'learner', 'earner',
    'owner', 'loner', 'stoner', 'cloner', 'moaner', 'groaner',
    'power', 'tower', 'flower', 'shower', 'slower', 'lower', 'grower',
    'mower', 'sower', 'bower', 'cower', 'dower',
    'super', 'upper', 'supper', 'copper', 'hopper', 'chopper', 'shopper',
    'stopper', 'dropper', 'popper', 'topper', 'wrapper', 'snapper',
    'clapper', 'flapper', 'mapper', 'rapper', 'tapper', 'zapper',
    'eper', 'paper', 'taper', 'caper', 'draper', 'shaper',
    'finger', 'linger', 'singer', 'ringer', 'bringer', 'stinger',
    'hanger', 'banger', 'ranger', 'danger', 'stranger', 'changer',
    'anger', 'hunger', 'younger', 'longer', 'stronger',
    'other', 'mother', 'father', 'brother', 'bother', 'gather',
    'weather', 'leather', 'feather', 'heather', 'together',
    'water', 'matter', 'latter', 'fatter', 'chatter', 'scatter',
    'platter', 'flatter', 'batter', 'tatter', 'clatter',
    'center', 'enter', 'winter', 'hunter', 'counter', 'pointer',
    'printer', 'splinter', 'painter', 'fainter',
    'offer', 'suffer', 'buffer', 'differ', 'stiffer',
    'server', 'clever', 'never', 'ever', 'fever', 'lever',
    'sever', 'river', 'liver', 'giver', 'silver', 'deliver',
    'computer', 'commuter', 'recruiter', 'shooter', 'looter',
    'rooter', 'hooter', 'footer', 'scooter', 'tutor',
    'color', 'humor', 'tumor', 'rumor', 'manor', 'honor',
    'error', 'terror', 'mirror', 'horror',
    'sugar', 'finger', 'trigger', 'bigger', 'digger', 'figure',
    'zipper', 'dipper', 'skipper', 'chipper', 'flipper', 'slipper',
    'chamber', 'member', 'timber', 'amber', 'umber', 'umber',
    'wonder', 'ponder', 'wander', 'tender', 'render', 'gender',
    'sender', 'lender', 'bender', 'fender', 'mender', 'vendor',
    'spider', 'rider', 'slider', 'wider', 'cider', 'insider',
    'outsider', 'provider', 'divider', 'decider',
    'order', 'border', 'folder', 'holder', 'colder', 'bolder',
    'older', 'shoulder', 'boulder', 'smolder',
    'under', 'thunder', 'wonder', 'plunder', 'blunder', 'sunder',
    'number', 'lumber', 'slumber', 'cucumber', 'remember',
    'october', 'november', 'december', 'september',
    'chapter', 'after', 'laughter', 'daughter', 'slaughter',
    'disaster', 'master', 'faster', 'easter', 'plaster', 'caster',
    'theater', 'sweater', 'greater', 'traitor', 'waiter',
    'feature', 'creature', 'preacher', 'reacher', 'beacher', 'formatter',
    'manufacturer', 'controller', 'amplifier', 'converter', 'analyzer',
    'compiler', 'debugger', 'processor', 'interpreter', 'scheduler',
    'transformer', 'transistor', 'resistor', 'capacitor', 'inductor',
    'cylinder', 'actuator', 'regulator', 'excavator', 'calibrator',
    'zipper', 'dipper', 'skipper', 'chipper', 'flipper', 'slipper',
    'chamber', 'member', 'timber', 'amber', 'umber', 'umber',
    'wonder', 'ponder', 'wander', 'tender', 'render', 'gender',
    'sender', 'lender', 'bender', 'fender', 'mender', 'vendor',
    'spider', 'rider', 'slider', 'wider', 'cider', 'insider',
    'outsider', 'provider', 'divider', 'decider',
    'order', 'border', 'folder', 'holder', 'colder', 'bolder',
    'older', 'shoulder', 'boulder', 'smolder',
    'under', 'thunder', 'wonder', 'plunder', 'blunder', 'sunder',
    'later', 'hater', 'dater', 'gater', 'skater', 'cater', 'structure',
    'fixture', 'texture', 'mixture', 'venture', 'gesture', 'picture',
    'measure', 'pressure', 'exposure', 'procedure'
}

def is_multisyllable_er_word(word: str) -> bool:
    """Check if a word ends with -er sound and is at least 2 syllables"""
    word_lower = word.lower().strip('.,!?;:"\'')
    
    # Check if it's in our curated list
    if word_lower in ER_WORDS:
        return True
    
    # Additional pattern matching for common -er endings
    # This catches words that might not be in our list
    if len(word_lower) >= 4:  # At least 4 letters for 2+ syllables
        # Words ending in -er, -or, -ar with common patterns
        patterns = [
            r'.*[aeiou].*er$',  # vowel + consonant(s) + er
            r'.*[aeiou].*or$',  # vowel + consonant(s) + or  
            r'.*[aeiou].*ar$',  # vowel + consonant(s) + ar
            r'.*cker$',         # -cker endings
            r'.*nner$',         # -nner endings
            r'.*pper$',         # -pper endings
            r'.*tter$',         # -tter endings
            r'.*mmer$',         # -mmer endings
            r'.*sser$',         # -sser endings
        ]
        
        for pattern in patterns:
            if re.match(pattern, word_lower):
                # Exclude common single-syllable words
                single_syllable = {'her', 'per', 'for', 'or', 'are', 'ere', 'err', 'our', 'cur', 'fur', 'sir', 'were'}
                if word_lower not in single_syllable:
                    return True
    
    return False

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.event
async def on_message(message):
    # Don't respond to bot messages
    if message.author.bot:
        return
    
    # Process the message for -er words
    words = message.content.split()
    
    for word in words:
        if is_multisyllable_er_word(word):
            # Clean the word for the joke
            clean_word = word.lower().strip('.,!?;:"\'')
            
            # Check cooldown to avoid spam
            cooldown_key = f"{message.channel.id}_{clean_word}"
            if cooldown_key in recent_jokes:
                continue
            
            # Add to recent jokes and set removal timer
            recent_jokes.add(cooldown_key)
            asyncio.create_task(remove_from_recent(cooldown_key))
            
            # Create the dad joke response
            joke = f"{clean_word[0].upper()+clean_word[1:]}? Hardly know her!"
            
            try:
                await message.reply(joke)

                print(f"Responded to '{clean_word}' in {message.guild.name}#{message.channel.name}")
                break  # Only respond to the first word found to avoid spam
            except discord.errors.Forbidden:
                print(f"No permission to send message in {message.guild.name}#{message.channel.name}")
            except Exception as e:
                print(f"Error sending message: {e}")
    
    # Process other bot commands
    await bot.process_commands(message)

async def remove_from_recent(key: str):
    """Remove a joke from recent jokes after cooldown period"""
    await asyncio.sleep(JOKE_COOLDOWN)
    recent_jokes.discard(key)

@bot.command(name='test_er')
async def test_er_command(ctx, *, text: str):
    """Test command to see what -er words the bot would detect"""
    words = text.split()
    detected = []
    
    for word in words:
        if is_multisyllable_er_word(word):
            clean_word = word.lower().strip('.,!?;:"\'')
            detected.append(f"{clean_word} → {clean_word}? Hardly know her!")
    
    if detected:
        response = "I would respond to these words:\n" + "\n".join(detected)
    else:
        response = "No -er words detected in that text."
    
    await ctx.send(response)

@bot.command(name='bot_stats')
async def bot_stats(ctx):
    """Show bot statistics"""
    guild_count = len(bot.guilds)
    total_members = sum(guild.member_count for guild in bot.guilds)
    
    embed = discord.Embed(title="Dad Joke Bot Stats", color=0x3498db)
    embed.add_field(name="Servers", value=guild_count, inline=True)
    embed.add_field(name="Total Members", value=total_members, inline=True)
    embed.add_field(name="Active Cooldowns", value=len(recent_jokes), inline=True)
    
    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    bot.run(open('token.txt').read().strip())