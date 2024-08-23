import discord
from discord.ext import commands
import asyncio
import time
import BCSFE_Python_Discord as BCSFE_Python
from BCSFE_Python_Discord import *
from BCSFE_Python_Discord import game_data_getter
from discord.ui import View, Button, Modal, InputText
from discord import ButtonStyle, Interaction
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
from io import BytesIO
import sqlite3

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

required_role_id = 1274254529818263581

source_channel_id = 1274640900701556746
target_channel_id = 1274627424214192209

FONT_PATH = "C:\\Users\\USER1\\Downloads\\DiscordBot\\saves\\LINESeedKR-Bd.ttf"
BACKGROUND_PATH = "C:\\Users\\USER1\\Downloads\\DiscordBot\\saves\\배경.png"

conn = sqlite3.connect("user_data.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                level INTEGER,
                xp INTEGER
            )''')
conn.commit()

class WarningCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

class PersistentView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # 버튼 정의 및 custom_id 설정 (역할 지급 버튼)
        b1 = Button(label='확인했습니다.', style=ButtonStyle.secondary, custom_id='role_grant_button')
        b1.callback = self.button_callback
        self.add_item(b1)

    async def button_callback(self, interaction: Interaction):
        role_id = 1274253653607317514  # 지급할 역할의 ID
        role = interaction.guild.get_role(role_id)

        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(content=f'{role.mention} 역할이 지급되었습니다.', ephemeral=True)
        else:
            await interaction.response.send_message(content='역할을 찾을 수 없습니다.', ephemeral=True)


class perkView(View):
    def __init__(self):
        super().__init__(timeout=None)

        # 버튼 정의 및 custom_id 설정 (혜택 버튼)
        b1 = Button(label='혜택', style=ButtonStyle.secondary, custom_id='perk_check_button')
        b1.callback = self.button_callback
        self.add_item(b1)

    async def button_callback(self, interaction: Interaction):
        role_ids = {
            "MVP": 1274254351036059649,
            "SVIP": 1274254238251225098,
            "VVIP": 1274254058437345291,
            "VIP": 1274254004632686643,
            "구매자": 1274253788386955335,
        }

        discounts = {
            "MVP": 25,   # 25% 할인
            "SVIP": 20,  # 20% 할인
            "VVIP": 15,  # 15% 할인
            "VIP": 10,   # 10% 할인
            "구매자": 5,  # 5% 할인
        }

        colors = {
            "MVP": 0xFF4500,   # 금색 (Gold)
            "SVIP": 0xFF4500,  # 은색 (Silver)
            "VVIP": 0xFFD700,  # 오렌지 (OrangeRed)
            "VIP": 0xFFD700,   # 파랑 (DeepSkyBlue)
            "구매자": 0x32CD32, # 초록 (LimeGreen)
        }

        guild = interaction.guild
        roles = {
            "MVP": guild.get_role(role_ids["MVP"]),
            "SVIP": guild.get_role(role_ids["SVIP"]),
            "VVIP": guild.get_role(role_ids["VVIP"]),
            "VIP": guild.get_role(role_ids["VIP"]),
            "구매자": guild.get_role(role_ids["구매자"]),
        }

        user_roles = interaction.user.roles
        discount_message = "해당 유저는 지정된 역할이 없습니다."

        for role_name in ["MVP", "SVIP", "VVIP", "VIP", "구매자"]:
            role = roles[role_name]
            if role and role in user_roles:
                discount = discounts[role_name]
                color = colors[role_name]

                embed = discord.Embed(
                    title="혜택 확인",
                    description=f'{interaction.user.mention}님은 {role.mention} 역할이 있습니다!',
                    color=color  # 각 역할별 색상 적용
                )
                embed.add_field(name="할인율", value=f'{discount}% 할인 적용됩니다.', inline=False)
                break
        else:
            # 역할이 없는 경우의 임베드
            embed = discord.Embed(
                title="혜택 확인",
                description="해당 유저는 지정된 역할이 없습니다.",
                color=0xff0000  # 기본 색상 (레드)
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class CannedFoodModal(Modal):
    def __init__(self):
        super().__init__(title="통조림")
        self.add_item(InputText(label="통조림", placeholder="통조림 갯수를 입력해 주세요."))

    async def callback(self, interaction: Interaction):
        response = self.children[0].value  # 유저가 입력한 값
        await interaction.response.send_message(f"DM을 확인해 주세요.", ephemeral=True)

class ExperienceModal(Modal):
    def __init__(self):
        super().__init__(title="경험치")
        self.add_item(InputText(label="경험치", placeholder="경험치 갯수를 입력해 주세요."))

    async def callback(self, interaction: Interaction):
        response = self.children[0].value  # 유저가 입력한 값
        await interaction.response.send_message(f"DM을 확인해 주세요.", ephemeral=True)

class vending(View):
    def __init__(self):
        super().__init__(timeout=None)

        b1 = Button(label='통조림', style=ButtonStyle.secondary, custom_id='canned_food')
        b2 = Button(label='경험치', style=ButtonStyle.secondary, custom_id='experience')
        b1.callback = self.button_callback
        b2.callback = self.button_callback
        self.add_item(b1)
        self.add_item(b2)

    async def button_callback(self, interaction: Interaction):
        button_label = interaction.data['custom_id']  # 눌린 버튼의 custom_id

        if button_label == 'canned_food':
            modal = CannedFoodModal()
            await interaction.response.send_modal(modal)
        elif button_label == 'experience':
            modal = ExperienceModal()
            await interaction.response.send_modal(modal)
        
@bot.event
async def on_ready():
    bot.add_view(PersistentView())
    bot.add_view(perkView())
    bot.add_view(vending())
    print(f'봇이 로그인되었습니다. {bot.user}')

@bot.event
async def on_message(message: discord.Message):
    # 봇 자신의 메시지나 다른 채널에서의 메시지는 무시합니다
    if message.author == bot.user:
        return

    if message.channel.id == source_channel_id:
        target_channel = bot.get_channel(target_channel_id)
        if target_channel:

            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            embed = discord.Embed(
                title="공지",
                description=f'보낸 사람: {message.author.mention}',
                color=0x565656
            )
            embed.add_field(name="메시지 내용", value=message.content, inline=False)
            embed.set_footer(text=f'보낸 시간: {current_time}')

            await target_channel.send(content="@everyone", embed=embed)


            
            await target_channel.send(embed=embed)
        else:
            print(f"채널 ID {target_channel_id}에 해당하는 채널을 찾을 수 없습니다.")

    # 명령어 처리를 위한 필요 코드
    await bot.process_commands(message)

@bot.slash_command(name="규칙", description="규칙보내기")
@commands.has_role(required_role_id)
async def 규칙(ctx):
    embed = discord.Embed(color=0x565656, title="가이드")
    embed.add_field(name="입장 한 뒤", value="입장 후 계정 백업 채널로 이동 후 계정 백업을 진행해 줍니다. (기종변경)", inline=False)
    embed.add_field(name="구매하는 법", value="백업을 하였다면 구매 채널로 가서 원하시는 옵션을 선택해 작업을 진행합니다.", inline=False)
    embed.add_field(name="작업 진행 도중 발생한 오류", value="담당자에게 문의해주시면 재빠르게 계정을 복구해드립니다.", inline=False)
    embed.add_field(name="문의", value="문의는 <#1274336346399313920> 여기를 클릭하여 원하는 문의주시면 됩니다.\n허위,장난 문의 시 1일 탐아", inline=False)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1274252440782504029/1274330450403397652/DISCORD_GARIS.png?ex=66c1dc37&is=66c08ab7&hm=2cdeee1e63fac0fc5b22b7a40218b829a20eaaab78e6bd29548f52e8b48d1475&")
    await ctx.send(embed=embed, view=PersistentView())

@규칙.error
async def 규칙_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(color=0x565656)
        embed.add_field(name="에러", value="이 명령어는 특정 역할이 있는 사용자만 사용 가능합니다.", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(guild_ids = [1272185394162831421], name="혜택", description="혜택확인하기")
@commands.has_role(required_role_id)
async def 혜택(ctx):
    embed = discord.Embed(color=0x565656, title="혜택")
    embed.add_field(name="", value="아래 버튼을 눌러 자신의 혜택을 확인하세요.", inline=False)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1274252440782504029/1274330450403397652/DISCORD_GARIS.png?ex=66c1dc37&is=66c08ab7&hm=2cdeee1e63fac0fc5b22b7a40218b829a20eaaab78e6bd29548f52e8b48d1475&")
    await ctx.send(embed=embed, view=perkView())

@혜택.error
async def 혜택_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(color=0x565656)
        embed.add_field(name="에러", value="이 명령어는 특정 역할이 있는 사용자만 사용 가능합니다.", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

@bot.slash_command(guild_ids = [1272185394162831421], name="도움말", description="도움말을 확인해요")
async def 도움말(ctx):
    embed = discord.Embed(color=0x565656, title="HYPER BC SAVE")
    embed.add_field(name="도움말", value="Hyper BC SAVE 공식 디스코드봇 소개")
    embed.add_field(name="명령어", value="**`/젠`** 특정 채널에서 이 명령어를 사용하면 디엠으로 랜덤 계정이 생성됩니다!", inline=False)
    embed.add_field(name="", value="**`/경험치`** 채팅 및 소통을 하여 레벨을 올릴 수 있습니다! ~~쉿~ 상품이 있을지 누가 알아요?~~", inline=False)
    embed.set_footer(text = "명령어가 별로 없어 아쉬우신가요? 괜찮습니다! 봇은 매주 업데이트 되기 때문입니다.")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1274640900701556746/1274681576868806747/Purple_Modern_Software_Company_Logo_2.png?ex=66c3233a&is=66c1d1ba&hm=72d4bec963d02a1c1f3bde56f14025adc41667f0093e75c0a30dbc791df3f59c&")
    await ctx.respond(embed=embed)

@bot.event
async def on_member_join(member):
    # 유저 정보 가져오기
    username = member.name
    user_id = member.id

    # 유저가 데이터베이스에 없으면 추가
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (user_id, username, level, xp) VALUES (?, ?, 1, 0)", (user_id, username))
        conn.commit()

    # 프로필 사진 가져오기
    avatar_url = member.avatar.url
    response = requests.get(avatar_url)
    avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
    avatar_img = avatar_img.resize((100, 100))

    mask = Image.new("L", avatar_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, 100, 100), fill=255)  # 원형 마스크 그리기

    avatar_img = ImageOps.fit(avatar_img, (100, 100), Image.LANCZOS)
    avatar_img.putalpha(mask)

    # 배경 이미지 불러오기
    background = Image.open(BACKGROUND_PATH).convert("RGB")
    draw = ImageDraw.Draw(background)
    
    # 글꼴 설정
    font_large = ImageFont.truetype(FONT_PATH, 50)
    font_small = ImageFont.truetype(FONT_PATH, 30)

    # 상단 텍스트 추가 (환영 메시지)
    draw.text((50, 20), "환영합니다!", font=font_large, fill=(255, 255, 255))

    # 유저 정보 텍스트 추가 (이름, ID)
    draw.text((170, 120), f"Name: {username}", font=font_small, fill=(255, 255, 255))
    draw.text((170, 160), f"ID: {user_id}", font=font_small, fill=(255, 255, 255))

    # 초기 경험치 및 레벨 텍스트 추가
    draw.text((50, 270), "0 XP", font=font_small, fill=(255, 255, 255))

    # 경험치 바 추가 (타원형 형태)
    bar_width = 300  # 경험치 바의 전체 길이
    bar_height = 40   # 경험치 바의 높이 (타원형의 세로 길이)
    xp = 0  # 초기 XP 값
    max_xp = 100  # 레벨업에 필요한 최대 XP
    xp_ratio = xp / max_xp
    fill_length = int(bar_width * xp_ratio)

    # 경험치 바 배경 그리기 (빈 바)
    draw.rounded_rectangle([50, 300, 50 + bar_width, 300 + bar_height], radius=bar_height//2, outline=(255, 255, 255), width=2)

    # 경험치 바 채우기 (현재 XP)
    if fill_length > 0:
        draw.rounded_rectangle([50, 300, 50 + fill_length, 300 + bar_height], radius=bar_height//2, fill=(0, 255, 0))

    # 프로필 사진 추가
    background.paste(avatar_img, (50, 100), avatar_img)

    # 이미지 파일로 저장
    image_path = "output_image.png"
    background.save(image_path)

    # 이미지 Discord로 전송
    channel = bot.get_channel(1275066691642064896)  # 이미지를 보낼 채널의 ID를 넣어야 함
    with open(image_path, "rb") as file:
        await channel.send(file=discord.File(file, "output_image.png"))

# 유저가 메시지를 보낼 때 경험치 업데이트
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    username = message.author.name
    
    # 유저가 데이터베이스에 없으면 추가
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (user_id, username, level, xp) VALUES (?, ?, 1, 0)", (user_id, username))
        conn.commit()

    # 유저의 현재 경험치와 레벨을 가져옴
    c.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result:
        xp, level = result
        xp += 10  # 채팅당 10 XP 추가

        # 레벨업에 필요한 경험치 계산 (레벨^2 * 100)
        max_xp = 100 * (level ** 2)

        # 레벨업 조건
        if xp >= max_xp:
            xp -= max_xp
            level += 1
            await message.channel.send(embed=discord.Embed(description=f"🎉 @{message.author.name} 님이 {level} 레벨이 되었습니다! 🎉"))

        # 데이터베이스 업데이트
        c.execute("UPDATE users SET xp = ?, level = ? WHERE user_id = ?", (xp, level, user_id))
        conn.commit()

    await bot.process_commands(message)

@bot.slash_command(guild_ids=[1272185394162831421], name="경험치", description="현재 경험치와 레벨을 확인합니다.")
async def 경험치(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = member.id
    c.execute("SELECT xp, level FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()

    if result:
        xp, level = result
        
        # 프로필 사진 가져오기
        avatar_url = member.avatar.url
        response = requests.get(avatar_url)
        avatar_img = Image.open(BytesIO(response.content)).convert("RGBA")
        avatar_img = avatar_img.resize((100, 100))

        mask = Image.new("L", avatar_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 100, 100), fill=255)  # 원형 마스크 그리기

        avatar_img = ImageOps.fit(avatar_img, (100, 100), Image.LANCZOS)
        avatar_img.putalpha(mask)

        # 배경 이미지 불러오기
        background = Image.open(BACKGROUND_PATH).convert("RGB")
        draw = ImageDraw.Draw(background)
        
        # 글꼴 설정
        font_large = ImageFont.truetype(FONT_PATH, 50)
        font_small = ImageFont.truetype(FONT_PATH, 30)

        # 상단 텍스트 추가 (레벨 및 경험치 정보)
        draw.text((50, 20), f"{member.name}님의 현재 레벨", font=font_large, fill=(255, 255, 255))

        # 유저 정보 텍스트 추가 (레벨 및 경험치)
        draw.text((170, 120), f"Level: {level}", font=font_small, fill=(255, 255, 255))
        draw.text((170, 160), f"XP: {xp}", font=font_small, fill=(255, 255, 255))

        # 경험치 바 추가 (타원형 형태)
        bar_width = 300  # 경험치 바의 전체 길이
        bar_height = 40   # 경험치 바의 높이 (타원형의 세로 길이)
        max_xp = 100 * (level ** 2)  # 레벨업에 필요한 최대 XP 계산
        xp_ratio = xp / max_xp
        fill_length = int(bar_width * xp_ratio)

        # 경험치 바 배경 그리기 (빈 바)
        draw.rounded_rectangle([50, 300, 50 + bar_width, 300 + bar_height], radius=bar_height//2, outline=(255, 255, 255), width=2)

        # 경험치 바 채우기 (현재 XP)
        if fill_length > 0:
            draw.rounded_rectangle([50, 300, 50 + fill_length, 300 + bar_height], radius=bar_height//2, fill=(0, 255, 0))

        # 프로필 사진 추가
        background.paste(avatar_img, (50, 100), avatar_img)

        # 이미지 파일로 저장
        image_path = "output_image_xp.png"
        background.save(image_path)

        # 이미지 Discord로 전송
        with open(image_path, "rb") as file:
            await ctx.respond(file=discord.File(file, "output_image_xp.png"))

    else:
        await ctx.respond("데이터가 없습니다. 먼저 채팅을 쳐보세요!")

@bot.slash_command(guild_ids=[1272185394162831421], name="자판기", description="자판기를 생성합니다.")
@commands.has_role(required_role_id)
async def 자판기(ctx):
        embed = discord.Embed(color=0x565656, title="")
        embed.add_field(name="자판기", value="원하는 버튼을 눌러주세요.", inline=False)
        embed.set_footer(text = "[!] 꼭 세이브 채널에서 세이브를 진행해주세요!")
        await ctx.respond(embed=embed, view=vending())

@자판기.error
async def 자판기_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        embed = discord.Embed(color=0x565656)
        embed.add_field(name="에러", value="이 명령어는 특정 역할이 있는 사용자만 사용 가능합니다.", inline=False)
        embed.set_footer(text = "[!] 관리자 이신가요? 문의해주세요!")
        await ctx.respond(embed=embed, ephemeral=True)

# 봇 실행 (토큰은 본인의 것으로 교체)
bot.run('')
