from discord.ext import commands, tasks
from datetime import datetime, timedelta
import discord
import feedparser
import asyncio, datetime
from random import choice
from random import randint
from replies import stfu_alba
from html import unescape

class RickAnswers(commands.Cog, ):
    def __init__(self, bot: commands.Bot, daily_verse_channel_id):
        self.bot = bot

        self.replies = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes – definitely',
                        'You may rely on it', 'As I see it, yes', 'Most likely', 'Outlook good',
                        'Yes Signs point to yes', 'Reply hazy', 'try again', 'Ask again later',
                        'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                        'Dont count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                        'Very doubtful', 'No', 'Yes', 'Cock and balls', "Who's to say"]

        self.advice_list = advice_list
        self.unit_list_many = unit_list_many
        self.unit_list_long = unit_list_long
        self.daily_verse.start()
        self.daily_verse_channel_id = daily_verse_channel_id

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if stfu_alba(message):
            await message.channel.send("stfu alba")
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        else:
            message_lower = message.content.lower()
            if (message_lower[0:13] == "rick how much" or message_lower[0:13] == "rick how many") and message_lower[
                -1] == "?":
                reply = str(randint(0, 123))
                reply = reply + " " + choice(self.unit_list_many)
                await message.channel.send(reply)

            elif message_lower[0:13] == "rick how long" and message_lower[-1] == "?":
                reply = str(randint(0, 210))
                reply = reply + " " + choice(self.unit_list_long)
                await message.channel.send(reply)

            elif message_lower[0:4] == "rick" and message_lower[-1] == "?":
                reply = choice(self.replies)
                await message.channel.send(reply)

    @commands.command(name='advice')
    async def ship(self, ctx):
        if ctx.message.author.bot:
            return

        else:
            reply = choice(self.advice_list)
            await ctx.reply(reply)

    @commands.command(name="verse")
    async def verse(self, ctx):
        feed = feedparser.parse("https://www.biblegateway.com/votd/get/?format=atom")
        entry = feed.entries[0]

        daily_verse = entry.summary[7:-7]
        daily_verse = unescape(''.join(('"', daily_verse, '"')))

        embed = discord.Embed(title="Verse of the Day", url=entry.link,
                              color=0xb4d9e0)
        embed.add_field(name=entry.title, value=daily_verse,
                        inline=False)
        embed.set_thumbnail(url="https://jesuschristsavior.net/Savior.jpeg")
        if ctx is None:
            channel = await self.bot.fetch_channel(self.daily_verse_channel_id)
            await channel.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    @tasks.loop(hours=24)
    async def daily_verse(self):
        await self.verse(ctx=None)

    @daily_verse.before_loop
    async def before(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(24*60*60)





unit_list_many = ["million", "tons", "kg", "liters", "thousand", "cocks", "km/h",
                  ]

unit_list_long = ["meters", "cm", "mm", "meters", "seconds", "hours", "days", "years",
                  ]

advice_list = [
    ' Ignore 1-star and 5-star reviews of books, hotels and products. The 3-star reviews will answer all your questions.',
    ' When you’re a host, use that experience to learn how to be a better guest, and vice-versa.',
    ' If you want to be fit, become someone who doesn’t skip or reschedule workouts. Skipping workouts is always the beginning of the end.',
    ' Learn keyboard shortcuts. If you don’t know what CTRL + Z does, your life is definitely harder than it has to be.',
    ' Become a stranger’s secret ally, even for a few minutes. Your perception of strangers in general will change.',
    ' Get over the myth that philosophy is boring — it has a history of changing lives. It’s only as boring as the person talking about it.',
    ' If you’re about to put down a boring a non-fiction book, skim the rest of it before you move on. Read the bits that still appeal to you.',
    ' Ask yourself if you’ve become a relationship freeloader. Initiate the plans about half the time.',
    ' Notice how much you talk in your head, and experiment with listening to your surroundings instead. You can’t do both at the same time.',
    ' Reach out to people you know are shy. It’s hard for them to get involved in social things without somebody making a point of including them.',
    ' Learn the difference between something that makes you feel bad, and something that’s wrong. A thing can feel bad and be right, and it can feel good and be wrong.',
    ' If you need to stop for any reason in a public place, move off to the side first.',
    ' Before you share an interesting “fact” on Facebook, take thirty seconds to Google it first, to see if you’re spreading made-up bullshit.',
    ' Clean things up right away, unless your messes tend to improve with age.',
    ' Consciously plan your life, or others will do it for you.',
    ' Be suspicious when someone uses the words “Justice” and “Deserve” a lot. Be suspicious when you use them yourself.',
    ' Get rid of stuff you don’t use. Unused and unappreciated things make us feel bad.',
    ' Expect people to get offended sometimes when you try to tell them what to do. Even if you think it’s good advice :)',
    ' Once in a while, imagine what it would be like if you really did lose all your data and had only your current backups.',
    ' Spend as long as it takes — five or ten years even — to move towards a line of work that feels well-suited to you.',
    ' Rediscover board games. They’re still tons of fun.',
    ' Try making small, humble presents instead of buying big ones, and see how different it feels for both you and the recipient.',
    ' To eat fewer calories, eat a lot slower than normal and see what changes.',
    ' Watch experts peform their chosen art whenever you get a chance. There’s something really grounding about it.',
    ' Avoid arguing about politics, except for entertainment value. By the time it’s an argument, nobody’s listening.',
    ' Ledger all your income, purchases and expenses, at least for a whole month. You can’t help but discover wasteful spending. It’s like giving yourself a raise.',
    ' When someone disagrees with you, try to understand what needs and fears are behind their stance. Yours probably aren’t much different.',
    ' When driving, pretend the other drivers are all friends and relatives. It makes the driving experience friendlier, and often hilarious.',
    ' Don’t act while you’re still angry. Anger makes the wrong things seem right, and remorse lasts way longer than anger.',
    ' Understand that what’s dangerous and what’s illegal are always going to be different, and need to be. It doesn’t always make sense to criminalize something just because it can be harmful.',
    ' Don’t be late. Everyone hates waiting for late people.',
    ' Read Richard Carlson’s classic Don’t Sweat the Small Stuff.  Or read it again if it’s been a while. Fifteen years  after I first read it, I can’t think of a more helpful book.',
    ' Be aware of the complex, systemic nature of the world’s biggest problems, and our habit of framing them as simple ones with clear villains and victims.',
    ' When you’re with a loved one, pretend momentarily that they’re actually gone from your life, and that you’re just remembering this ordinary moment with them.',
    ' Make a point of sitting and chatting with at least one local whenever you travel. It will transform your view of the place.',
    ' Experiment with meditation. It gives you tools to mitigate nearly every thing human beings complain about — fear, boredom, loss, envy, pain, sadness, confusion, and doubt — yet remains unpopular in the West.',
    ' Give classical music another shot every few years.',
    ' Read a bit about some of the “isms” you normally dismiss — socialism, capitalism, conservatism, feminism, anarchism. There are probably more good ideas there than you thought.',
    ' Be wary of declaring yourself a “_____ist” though. Making an identity out of your beliefs is bound to make you less objective.',
    ' Picture yourself at your own funeral. Imagine what they are thinking.',
    ' Donate clothes that you don’t feel good wearing.',
    ' Practice opening up to minor discomfort when it happens — really letting yourself feel it instead of resisting it. Everything becomes easier to handle.',
    ' Listen to Dolly Parton’s “Jolene” slowed down to 33 rpm, at least once in your life.',
    ' Don’t make jokes about people’s names or bodies, even if you think they would laugh.',
    ' Make a point of enjoying the walk across the parking lot.',
    ' Understand the concept of “privilege,” but don’t use it as a slur. Use your privilege for good.',
    ' Don’t limit your compassion to people who don’t cause any harm (because there are none.)',
    ' Be aware of the intoxicating effect of bad moods. A bad mood usually means things are better than they look.',
    ' Once in a while, imagine that this moment is the very first moment of your life, and then build a future from there.',
    ' Go to your city’s low-key ethnic restaurants instead of flashy chain establishments — not to “help out the little guy” but because they’re better and cheaper.',
    ' Avoid being the least sober person in the room, unless you’re the only person in the room.',
    ' Go to New York, at least once.',
    ' Consider keeping a bucket list that you take seriously. They stave off complacency.',
    ' Remember that you’re essentially no different from prehistoric humans, except that you have tools and advantages they would find ridiculous.',
    ' If life ever feels like it’s too loud and busy, go hang out at the library.',
    ' Never hide from truths about your financial position. If you’re afraid to know your bank balance, you have a problem bigger than money problems.',
    ' If you think dancing isn’t for you, try it again sometime.',
    ' When you’re about to buy something, think about what feeling you’re actually after. Ultimately we only want things because of how they promise to make us feel.',
    ' Floss every day. You can fool yourself but you can’t fool your dentist, or your teeth.',
    ' Be extra kind to people while they are at work, especially servers, clerks, and tech support staff.',
    ' Whenever you’re being contradicted, try not to get caught up in being defensive. You’re either right, or you get to learn something new today.',
    ' At least consider taking religion’s five central no-no’s seriously: don’t steal, don’t lie, don’t kill, don’t harm people with your reproductive urges, and don’t drink so much that you forget the other four.',
    ' Own at least one plant. They’ll never judge you, but they’ll let you know if you’re being careless.',
    ' Try not to let a week go by without having lunch or coffee with a friend.',
    ' Do 30-day experiments for fun and sport — try out a new way of doing something for a while. Even if they’re train wrecks you always learn something about yourself.',
    ' Appeal to your friends for their expertise. You get good advice, they feel valued.',
    ' Write people letters. Everyone loves getting letters.']
