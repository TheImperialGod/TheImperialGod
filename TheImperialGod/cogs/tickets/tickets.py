import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import json
import asyncio

class Tickets(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tickets are ready!")

    @commands.command(aliases = ['createticket', 'ticketnew'])
    @cooldown(1, 10, BucketType.user)
    async def new(self, ctx, *, reason = None):
        em = discord.Embed(title = "Confirm New Ticket", color =  ctx.author.color)
        em.add_field(name = "Reason:", value = "We don't want people to spam!")
        em.add_field(name = "Steps to do:", value = "Type `confirm` in the chat to confirm this ticket!")
        em.set_footer(text = "Bot Made By NightZan999#0194")
        msg = await ctx.send(embed = em)

        def msg_check(m):
            return m.author == ctx.author and m.channel  == ctx.channel

        try:
            msg = await self.client.wait_for('message', timeout = 15.0, check= msg_check)
        except:
            em = discord.Embed(title = "<:fail:761292267360485378> New Ticket Failed!", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "You took too long!")
            em.add_field(name = "Cooldown", value = "1 minute more!")
            await ctx.send(embed = em)
        else:
            if msg.content != "confirm":
                em = discord.Embed(title = "<:fail:761292267360485378> New Ticket Failed!", color = ctx.author.color)
                em.add_field(name = "Reason:", value = "You did not want to create one!")
                em.add_field(name = "Cooldown", value = "1 minute more!")
                await ctx.send(embed = em)

            else:
                channelname = "ticket-{}".format(ctx.author.name)
                for _channel in ctx.guild.channels:
                    if _channel.name == channelname:
                        return await ctx.channel.send(f"You already have a ticket! Please contact staff in {_channel.mention}!")

                warning = f"""{ctx.author.mention} it is good to provide a reason for your inquires with the EMPIRE\nNext time try `imp new <reason>`
                """
                tickets = await self.get_tickets()
                guild = ctx.guild
                author = ctx.author
                # Logic
                if str(ctx.guild.id) not in tickets:
                    em = discord.Embed(title = "<:fail:761292267360485378> New Failed",color = ctx.author.color)
                    em.add_field(name = "Reason:", value = "Tickets are not setup!")
                    em.add_field(name ="Usage:", value = "Usage for an admin:\n```diff\n+ imp addticketrole <@role> [reason]\n- imp new [reason]\n```")
                    await ctx.send(embed = em)
                    return
                # Getting the role made!
                ticketrole = tickets[str(ctx.guild.id)]["ticketrole"]
                role_id = int(ticketrole)
                helper_role = ctx.guild.get_role(role_id)
                # Setting up the Channel
                channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}')
                # Creating the embed
                em = discord.Embed(title = f"<:success:761297849475399710> New ticket", color = ctx.author.color)
                em.add_field(name = "Ticket Channel:", value= f"{channel.mention}")
                em.add_field(name = "Description:", value = "Staff will be with your shortly")
                em.add_field(name = "Member:", value = f"{ctx.author.mention}")
                em.add_field(name = "Reason:", value = f"`{reason}`")
                em.set_footer(text="Bot Made By NightZan999#0194")
                # Perms
                # Make sure the author can type!
                await channel.set_permissions(ctx.author, read_messages = True, send_messages = True)
                # Make sure everyone else should not be able to see anything, cause it should be private
                await channel.set_permissions(ctx.guild.default_role, read_messages = False, send_messages = False)
                # And now make sure the helper_role should see this, incase the owner is busy
                await channel.set_permissions(helper_role, read_messages = True, send_messages = True)
                """
                and before you ask, how are we gonna set our Perms
                if we can manage_channels (create a channel), then hell ye
                we can speak, we dont need to actually set perms for ourselves
                """
                # Sending the embed
                await channel.send(embed = em)
                if reason == None:
                    await channel.send(warning)
                await ctx.send(f"Created the ticket! Check {channel.mention}")

                # send the mod log
                try:
                    channelId = int(tickets[str(ctx.guild.id)]["ticketchannel"])
                    for channel_ in ctx.guild.channels:
                        if channel_.id == channelId:
                            em = discord.Embed(title = "<:success:761297849475399710> Ticket Opened!", color = ctx.author.color)
                            em.add_field(name = "Member:", value = f"{ctx.author.mention}")
                            em.add_field(name ="Reason:", value = f"`{reason}`")
                            em.add_field(name= "Channel / Access Point", value = f'{channel.mention}')
                            em.set_thumbnail(url = ctx.author.avatar_url)
                            await channel_.send(embed = em)
                            break
                except:
                    pass

    @new.error
    async def new_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(title = "<:fail:761292267360485378> New Error", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "If your trying to spam the server then get off!")
            em.add_field(name = "Try again in:", value = "`{:.2f}s`".format(error.retry_after))
            em.set_footer(text="Bot Made By NightZan999#0194")
            await ctx.send(embed = em)

    @commands.command(aliases = ['setticketrole', 'ticketrole'])
    @commands.has_permissions(manage_guild = True)
    async def addticketrole(self, ctx, role : discord.Role = None, *,reason = None):
        if role == None:
            await ctx.send("You need to provide a valid role!")
            return

        tickets = await self.get_tickets()
        em = discord.Embed(title= "<:success:761297849475399710> Added ticketrole", color = ctx.author.color)
        guild = ctx.guild
        author = ctx.author
        if str(ctx.guild.id) not in tickets:
            em.add_field(name = "Switch:", value = f"`None` => {role.mention}")
            tickets[str(guild.id)] = {}
            tickets[str(guild.id)]["ticketrole"] = int(role.id)
        else:
            role_id = tickets[str(guild.id)]["ticketrole"]
            tickets[str(guild.id)]["ticketrole"] = int(role.id)
            em.add_field(name = "Role:", value = f"{role.mention}")
        em.add_field(name = "Features:", value = "Users can now type `imp new <reason>`")
        em.add_field(name = "Reason:", value = f"`{reason}`")
        em.set_footer(text="Bot Made By NightZan999#0194")
        await ctx.send(embed = em)
        
        # send the mod log
        try:
            channelId = int(tickets[str(ctx.guild.id)]["ticketchannel"])
            for channel_ in ctx.guild.channels:
                if channel_.id == channelId:
                    em = discord.Embed(title = "<:success:761297849475399710> Ticket Role Set!", color = ctx.author.color)
                    em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
                    em.add_field(name ="Reason:", value = f"`{reason}`")
                    em.add_field(name= "Ticket Role", value = f'{role.mention}')
                    em.set_thumbnail(url = ctx.author.avatar_url)
                    await channel_.send(embed = em)
                    break
        except:
            pass

        # Updating the database
        with open("./data/tickets.json", "w") as f:
            json.dump(tickets, f)
        

    @addticketrole.error
    async def addticketrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            em = discord.Embed(title = "<:fail:761292267360485378> Ticket Error", color = ctx.author.color)
            em.add_field(name = "Reason:", value = "You don't have the perms")
            em.add_field(name = "Perms:", value = "`Manage Server permission missing!`")
            em.set_footer(text="Bot Made By NightZan999#0194")
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title=  "<:fail:761292267360485378> Ticket Error", color = ctx.author.color)
            em.add_field(name ="Reason:", value = f"{ctx.author.mention}, you need to provide a valid role!")
            em.add_field(name = "Usage:", value = '```diff\n+ imp addticketrole <@role> [reason]\n- imp addticketrole bruh\n```')
            em.set_footer(text = "Read the docs, heheboi!")
            await ctx.send(embed = em)

    @commands.command(aliases = ['addticketlogs', 'atl', 'stl'])
    @commands.has_permissions(manage_guild = True)
    async def setticketlogs(self, ctx, channel : discord.TextChannel = None, *, reason = None):
        if channel is None:
            await ctx.send("You need to provide a valid channel!")            
        
        em = discord.Embed(title ="<:success:761297849475399710> Ticket Logs Set", color = ctx.author.color)
        em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
        em.add_field(name = "Channel:", value = f"{channel.mention}")
        em.add_field(name = "Reason:", value = f"`{reason}`", inline = False)
        em.set_footer(text = "Invite me with imp invite ;)")
        await ctx.send(embed = em)

        tickets = await self.get_tickets()
        guild = ctx.guild

        if str(ctx.guild.id) not in tickets:
            tickets[str(guild.id)] = {}
            tickets[str(guild.id)]["ticketchannel"] = int(channel.id)
        else:
            tickets[str(guild.id)]["ticketchannel"] = int(channel.id)

        with open("./data/tickets.json", "w") as f:
            json.dump(tickets, f)

    @setticketlogs.error
    async def setticketlogs_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            em = discord.Embed(title = '<:fail:761292267360485378> Setticketlogs Failed', color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Manage Server permission is missing!`")
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_footer(text="Smh, imagine thinking you have the perms!")
            await ctx.send(embed = em)
        if isinstance(error, commands.BadArgument):
            em = discord.Embed(title = '<:fail:761292267360485378> Setticketlogs Failed', color = ctx.author.color)
            em.add_field(name = "Reason:", value = "Mention a channel properly, like {}".format(ctx.channel.mention))
            em.add_field(name= "Usage:", value = "```diff\n+ imp setticketlogs #ticket-logs better ticket logs\n- imp setticketlogs @NightZan999 setting a member as logs\n```")
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_footer(text="Smh, imagine being bad!")
            await ctx.send(embed = em)

    @commands.command(aliases = ['closeticket', "ticketclose"])
    @commands.has_permissions(manage_channels = True)
    async def close(self, ctx, *, reason = None):
        channel = ctx.channel
        name = channel.name

        if name.startswith("ticket-"):
            messageEmbed = discord.Embed(title = "<:success:761297849475399710> Ticket Will Close!", color = ctx.author.color,
            description = "This ticket will close in ten seconds. Thanks for your time!")
            seconds = 10
            messageEmbed.add_field(name= "Time remaining:", value = f"`{seconds}`")
            messageEmbed.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
            messageEmbed.add_field(name = "Reason:", value = f"`{reason}`")
            messageEmbed.add_field(name = "Mod Logs:", value = "Sending logs in 5 seconds!")
            messageEmbed.set_footer(text = "Wanna invite me eh? `imp invite`)")
            await ctx.send(embed = messageEmbed)
            # sleep and delete channel
            await asyncio.sleep(10)
            # now delete the channel
            await channel.delete()
            # send mod log
            try:
                channelId = int(tickets[str(ctx.guild.id)]["ticketchannel"])
                for ticketChannel in ctx.guild.channels:
                    if ticketChannel.id == channelId:
                        em = discord.Embed(title = "<:fail:761292267360485378> Ticket Closed!", color = ctx.author.color)
                        em.add_field(name = "Moderator:", value = f"{ctx.author.mention}")
                        em.add_field(name ="Reason:", value = f"`{reason}`")
                        em.add_field(name = "Channel Closing:", value = f"{channel.mention}")
                        em.set_thumbnail(url = ctx.author.avatar_url)
                        await ticketChannel.send(embed = em)
                        break
            except:
                pass
        else:
            em = discord.Embed(title = "<:fail:761292267360485378> Closing Failed!", color= ctx.author.color)
            em.add_field(name = "Reason:", value = f'This channel ({ctx.channel.mention}) is not a ticket channel!')
            em.add_field(name = "Try again later!", value = "Only a channel which has been a ticket can be closed!")
            em.set_footer(text="Bot Made By NightZan999#0194")
            await ctx.send(embed = em)

    @close.error
    async def close_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            em = discord.Embed(title = '<:fail:761292267360485378> Close Failed', color = ctx.author.color)
            em.add_field(name = "Reason:", value = "`Manage Channels permission is missing!`")
            em.set_thumbnail(url = ctx.author.avatar_url)
            em.set_footer(text="Smh, imagine thinking you have the perms!")
            await ctx.send(embed = em)

    async def get_tickets(self):
        with open("./data/tickets.json", "r") as f:
            data = json.load(f)        
        return data
    
    """
    @param guild : discord.Guild object!
    """
    async def get_logs(self, guild):
        guild_id = guild.id
        tickets = await self.get_tickets()

        if str(guild_id) not in tickets:
            return False
        return int(tickets[str(guild.id)]["ticketchannel"])
    
    """
    @param guild : discord.Guild object!
    """
    async def get_role(self, guild):
        guild_id = guild.id
        tickets = await self.get_tickets()

        if str(guild_id) not in tickets:
            return False
        return int(tickets[str(guild_id)]["ticketrole"])
    
    """
    @param guild : discord.Guild object!
    @param ticketrole : discord.Role object
    @param ticketchannel : discord.Channel object
    """
    async def open_guild(self, guild, ticketrole : discord.Role, ticketchannel: discord.TextChannel):
        tickets = await self.get_tickets()
        if not str(guild.id) in tickets:
            tickets[str(guild.id)] = {}
            tickets[str(guild.id)]["ticketchannel"] = int(ticketchannel.id)
            tickets[str(guild.id)]["ticketrole"] = int(ticketrole.id)
        else:
            tickets[str(guild.id)]["ticketchannel"] = int(ticketchannel.id)
            tickets[str(guild.id)]["ticketrole"] = int(ticketrole.id)
        
        with open("./data/tickets.json", "w") as f:
            json.dump(tickets, f)
        
        return [self.get_logs(guild), self.get_role(guild)]

def setup(client):
    client.add_cog(Tickets(client))
