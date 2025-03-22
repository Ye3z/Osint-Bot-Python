import discord
from discord.ext import commands
from discord.ui import Button, View
import aiohttp
import asyncio
import phonenumbers
import json
from phonenumbers import geocoder, carrier
from datetime import datetime

GUILD_ID = 'Id du discord'
WELCOME_CHANNEL_ID = # Id du channel Welcome ☢️
staff_role_id = # Id du rôle Staff ☢️
INVITES_FILE = 'invites.json'

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='&', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot On 💫 {bot.user}')

def load_invites():
    try:
        with open(INVITES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_invites(invites):
    with open(INVITES_FILE, 'w') as f:
        json.dump(invites, f, indent=4)

async def send_welcome_message(member, inviter_name, inviter_invites, is_invited_by_link=False):
    invites = load_invites()

    if is_invited_by_link:
        invite_message = f"<@{member.id}> vient de nous rejoindre pour la 1e fois, Il/Elle a été invité(e) par le **lien d'invitation personnalisé du serveur**. Nous sommes désormais {len(member.guild.members)} !"
    else:
        invite_message = f"<@{member.id}> vient de nous rejoindre pour la 1e fois, Il/Elle a été invité(e) par **{inviter_name}** Nous sommes désormais {len(member.guild.members)} !"
    
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(invite_message)

async def check_username_on_platforms(username):
    platforms = {
        "Instagram": f"https://www.instagram.com/{username}",
        "Twitter": f"https://twitter.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Facebook": f"https://www.facebook.com/{username}",
        "PayPal": f"https://www.paypal.me/{username}",
        "Spotify": f"https://open.spotify.com/user/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "LinkedIn": f"https://www.linkedin.com/in/{username}",
        "YouTube": f"https://www.youtube.com/c/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}"
    }

    results = []
    async with aiohttp.ClientSession() as session:
        for platform, url in platforms.items():
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        results.append((platform, True, url))
                    else:
                        results.append((platform, False, None))
            except:
                results.append((platform, False, None))
    return results

# Userinfo

@bot.command()
async def userinfo(ctx, user: discord.User, check_platforms: bool = False):
    """
    Displays user info. Optionally checks for social media profiles if `check_platforms` is True.
    """
    is_bot = "✅" if user.bot else "❌"
    
    embed = discord.Embed(title=f"__Informations sur {user.name}__", color=discord.Color.from_rgb(255, 255, 255))
    
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Nom global", value=user.global_name or "Aucun", inline=True)
    embed.add_field(name="Nom d'utilisateur", value=user.name, inline=True)
    embed.add_field(name="Compte créé le", value=user.created_at.strftime("`%d/%m/%Y à %H:%M`"), inline=True)
    embed.add_field(name="Est-ce un bot ?", value=is_bot, inline=True)
    
    avatar_url = user.avatar.url if user.avatar else "https://www.example.com/default_avatar.png"
    embed.add_field(name="Bannière :", value=" ", inline=False)

    embed.set_thumbnail(url=avatar_url)

    if user.banner:
        embed.set_image(url=user.banner.url)
    else:
        embed.add_field(name="", value="`Aucune bannière disponible`", inline=False)

    button = Button(label="Voir le profil", url=f"https://discord.com/users/{user.id}", style=discord.ButtonStyle.link)

    view = View()
    view.add_item(button)

    if check_platforms and user.global_name:
        platform_results = await check_username_on_platforms(user.global_name)

        for platform, found, url in platform_results:
            if found:
                embed.add_field(name=platform, value=f"✅ Profil trouvé: [Voir le profil]({url})", inline=False)
            else:
                embed.add_field(name=platform, value="❌ Aucun profil trouvé", inline=False)

    await ctx.send(embed=embed, view=view)

# Username Lookup

@bot.command()
async def username(ctx, *, username: str):
    await ctx.send(f"Recherche des informations pour l'utilisateur: **{username}** 🔎")

    platform_results = await check_username_on_platforms(username)

    embed = discord.Embed(title=f"Résultats de recherche pour: {username}", description="Voici les résultats trouvés sur différentes plateformes:", color=discord.Color.from_rgb(255, 255, 255))

    for platform, found, url in platform_results:
        if found:
            embed.add_field(name=platform, value=f"✅ Profil trouvé: [Voir le profil]({url})", inline=False)
        else:
            embed.add_field(name=platform, value="❌ Aucun profil trouvé", inline=False)

    await ctx.send(embed=embed)

# Ip Lookup

@bot.command()
async def ipinfo(ctx, ip: str):
    await ctx.send(f"Recherche des informations pour l'IP: **{ip}** 🔎")

    url = f"http://ip-api.com/json/{ip}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "fail":
                        await ctx.send("❌ Impossible de trouver des informations pour cette IP.")
                        return
                    
                    city = data.get("city", "Non spécifié")
                    region = data.get("regionName", "Non spécifié")
                    country = data.get("country", "Non spécifié")
                    zip_code = data.get("zip", "Non spécifié")
                    lat = data.get("lat", 0)
                    lon = data.get("lon", 0)
                    isp = data.get("isp", "Non spécifié")
                    org = data.get("org", "Non spécifié")
                    as_name = data.get("as", "Non spécifié")
                    
                    embed = discord.Embed(title=f"Informations sur l'IP: {ip}", color=discord.Color.from_rgb(255, 255, 255))
                    embed.add_field(name="Ville", value=city, inline=True)
                    embed.add_field(name="Région", value=region, inline=True)
                    embed.add_field(name="Pays", value=country, inline=True)
                    embed.add_field(name="Code Postal", value=zip_code, inline=True)
                    embed.add_field(name="ISP", value=isp, inline=True)
                    embed.add_field(name="Organisation", value=org, inline=True)
                    embed.add_field(name="AS", value=as_name, inline=True)
                    embed.add_field(name="Latitude", value=lat, inline=True)
                    embed.add_field(name="Longitude", value=lon, inline=True)

                    button = Button(label="Voir sur Google Maps", url=f"https://www.google.com/maps?q={lat},{lon}", style=discord.ButtonStyle.link)
                    view = View()
                    view.add_item(button)

                    await ctx.send(embed=embed, view=view)
                else:
                    await ctx.send("❌ Une erreur s'est produite lors de la récupération des informations pour cette IP.")
        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue: {str(e)}")

# Num Lookup

@bot.command()
async def numinfo(ctx, phone_number: str):
    try:
        number = phonenumbers.parse(phone_number, 'FR')
        country = geocoder.description_for_number(number, 'fr')
        carrier_name = carrier.name_for_number(number, 'fr')
        
        if phonenumbers.is_valid_number(number):
            embed = discord.Embed(title=f"Informations sur le numéro: {phone_number}", color=discord.Color.from_rgb(255, 255, 255))
            embed.add_field(name="Pays", value=country or "Inconnu", inline=True)
            embed.add_field(name="Opérateur", value=carrier_name or "Inconnu", inline=True)
            embed.add_field(name="Numéro valide", value="✅ Oui", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Le numéro {phone_number} n'est pas valide.")
    except phonenumbers.phonenumberutil.NumberParseException:
        await ctx.send(f"❌ Le numéro {phone_number} est mal formaté.")

# Welcome

@bot.event
async def on_member_join(member):
    invites = load_invites()
    
    guild = member.guild
    invite_used = None
    inviter_name = "un inconnu"
    is_invited_by_link = False

    for invite in await guild.invites():
        if invite.uses > invites.get(str(invite.inviter.id), 0):
            invite_used = invite
            break
    
    if invite_used:
        inviter_name = invite_used.inviter.name
        inviter_invites = invites.get(str(invite_used.inviter.id), 0) + 1
        invites[str(invite_used.inviter.id)] = inviter_invites
    else:
        is_invited_by_link = True
    
    save_invites(invites)
    
    await send_welcome_message(member, inviter_name, inviter_invites if not is_invited_by_link else 0, is_invited_by_link)

# Clear

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount > 100:
        await ctx.send("**Vous ne pouvez pas supprimer plus de 100 messages. ❌**")
        return

    member = ctx.author
    staff_role = discord.utils.get(member.roles, id=staff_role_id)

    if not staff_role:
        await ctx.send("**Ta pas de perm Bouuuuuu ✨**")
        return

    deleted = await ctx.channel.purge(limit=amount)

    embed = discord.Embed(
        title="Messages supprimés",
        description=f"{len(deleted)} messages ont été supprimés.",
        color=discord.Color(0xffffff)
    )

    await ctx.send(embed=embed, delete_after=5)

# Bot Token

bot.run('Bot Token')