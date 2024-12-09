import discord, asyncio, os, discord.ui
from discord.ext import commands
from discord import app_commands
import time
import threading
from dotenv import load_dotenv

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)
client.help_command = None

global spc_timeout
spc_timeout = 15

def config():
    load_dotenv()

async def timeout_timer(time):
    await asyncio.sleep(time)
    return "time_up"

@client.event
async def on_ready():
    await client.tree.sync()
    global LOG_CHANNEL
    LOG_CHANNEL = await client.fetch_channel(1295520368609464421) # ID SHOULD BE CHANGED ACCORDING TO THE CHANNEL ID
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Magazinim'))
    print("CaptchaBot Online")
    print("____________________")
    try:
        print(f"Synced command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@client.tree.command(name="create_captcha", description="Generate a CAPTCHA with either text or image.")
@app_commands.choices(captcha_type=[
    app_commands.Choice(name='text_generation', value="text"),
    app_commands.Choice(name='math_generation', value="math"),
    app_commands.Choice(name="image_generation", value="image"),
    app_commands.Choice(name="text_recognition", value="comp_text")
])
async def create_captcha(interaction: discord.Interaction, captcha_type: app_commands.Choice[str]):
    result = ""
    async def text_callback(interaction):
        result = ""
        if int(interaction.data['custom_id']) == chosen_word_index:
            embed = discord.Embed(title="Verification successful!", description="You've completed the Captcha successfully.", color=0x32a881)
            await interaction.response.edit_message(embed=embed, attachments=[], view=None)
            result = "Passed"
        else:
            embed = discord.Embed(title="Verification failed.", description="You've failed the Captcha test.", color=0x32a881)
            await interaction.response.edit_message(embed=embed, attachments=[], view=None)
            result = "Failed"

        embed_color = 0x00FF00
        if result == "Failed": embed_color=0xFD4646
        if result == "Passed": embed_color=0x39c4af
        log_embed = discord.Embed(title="Captcha Result!", color=embed_color)
        log_embed.set_thumbnail(url=interaction.user.avatar.url)
        log_embed.set_author(name="🌐 Captcha System")
        log_embed.add_field(name="Captcha Type", value="Text Generation", inline=True)
        log_embed.add_field(name="User Tested", value=f"{interaction.user}", inline=True)
        log_embed.add_field(name="Captcha Result", value=f"{result}", inline=True)
        log_embed.add_field(name="Edited at", value=f"{time.strftime('%Y-%m-%d %H:%M:%S')}", inline=True)

        await LOG_CHANNEL.send(embed=log_embed)  

    async def math_callback(interaction):
        timeout = threading.Thread(target=timeout_timer, args=(spc_timeout))
        result = ""

        while timeout != "time_up":
            if int(interaction.data['custom_id']) == answer_index:
                embed = discord.Embed(title="Verification successful!", description="You've completed the Captcha successfully.", color=0x32a881)
                await interaction.response.edit_message(embed=embed, attachments=[], view=None)
                result = "Passed"
            else:
                embed = discord.Embed(title="Verification failed.", description="You've failed the Captcha test.", color=0x32a881)
                await interaction.response.edit_message(embed=embed, attachments=[], view=None)
                result = "Failed"

        embed_color = 0x00FF00
        
        if result == "Failed": embed_color=0xFD4646
        if result == "Passed": embed_color=0x39c4af
        log_embed = discord.Embed(title="Captcha Result!", color=embed_color)
        log_embed.set_thumbnail(url=interaction.user.avatar.url)
        log_embed.set_author(name="🌐 Captcha System")
        log_embed.add_field(name="Captcha Type", value="Math Equation", inline=True)
        log_embed.add_field(name="User Tested", value=f"{interaction.user}", inline=True)
        log_embed.add_field(name="Captcha Result", value=f"{result}", inline=True)
        log_embed.add_field(name="Edited at", value=f"{time.strftime('%Y-%m-%d %H:%M:%S')}", inline=True)

        await LOG_CHANNEL.send(embed=log_embed)  


    async def image_callback(interaction):
        result = ""
        global image_counter, image_view, general_count

        if not interaction.response.is_done():
            await interaction.response.defer()

        button_id = interaction.data['custom_id']
        print(f"Button ID pressed: {button_id}")

        button = None
        for child in image_view.children:
            if child.custom_id == button_id:
                button = child
                break

        if button:
            if int(button_id) in index_list:
                button.disabled = True
                image_counter += 1
                general_count += 1

        embed = None
        print(f"Correct Answers: {image_counter}, General Answers: {rnd1}")
        if image_counter == rnd1:
            print("Entered first conditional.")
            embed = discord.Embed(title="Verification successful!", description="You've completed the Captcha successfully.", color=0x32a881)
            original_message = await interaction.original_response()
            await interaction.followup.edit_message(message_id=original_message.id, embed=embed, view=None, attachments=[])
            result = "Passed"

        print(f"General Answers: {general_count}, Number of Cats: {rnd1}")
        if general_count > rnd1:
            print("Entered second conditional.")
            embed = discord.Embed(title="Verification failed.", description="You've failed the Captcha test.", color=0x32a881)
            original_message = await interaction.original_response()
            await interaction.followup.edit_message(message_id=original_message.id, embed=embed, view=None, attachments=[])
            result = "Failed"

        embed_color = 0x00FF00
        
        if result == "Failed": embed_color=0xFD4646
        if result == "Passed": embed_color=0x39c4af
        log_embed = discord.Embed(title="Captcha Result!", color=embed_color)
        log_embed.set_thumbnail(url=interaction.user.avatar.url)
        log_embed.set_author(name="🌐 Captcha System")
        log_embed.add_field(name="Captcha Type", value="Image Generation", inline=True)
        log_embed.add_field(name="User Tested", value=f"{interaction.user}", inline=True)
        log_embed.add_field(name="Captcha Result", value=f"{result}", inline=True)
        log_embed.add_field(name="Edited at", value=f"{time.strftime('%Y-%m-%d %H:%M:%S')}", inline=True)      

        await LOG_CHANNEL.send(embed=log_embed)  


    try:
        if captcha_type.value == "text":
            import random, discord
            with open(r"words_list/words_list.txt", 'r') as file:
                words = [line.strip() for line in file.readlines()]
                random_words = []
                chosen_word = random.choice(words)
                random_words.append(chosen_word)
                
                global chosen_word_index

                while len(random_words) < 9:
                    word = random.choice(words)
                    if word not in random_words:
                        random_words.append(word)

                random.shuffle(random_words)
                chosen_word_index = random_words.index(chosen_word)

                image_list = []
                for i in range(9):
                    image_list.append(lingo_text_to_image(random_words[i], 200, 40))

                files = [discord.File(fp=image, filename=f"captcha_{i+1}.png") for i, image in enumerate(image_list)]
                embed = discord.Embed(title="Captcha: Text Generation", description=f"Please press the correct square that represents the word: `{chosen_word}`.", color=0x32a881)

                from discord.ui import Button, View

                view = View(timeout=spc_timeout)
                BTN_list = []
                divider, row = 0, 0
                for i in range(9):
                    if divider % 3 == 0:
                        row += 1
                    btn = Button(label=f"{i+1}", style=discord.ButtonStyle.green, row=row, custom_id=f"{i}")
                    btn.callback = text_callback
                    view.add_item(btn)
                    BTN_list.append(btn)
                    divider += 1

                await interaction.response.send_message(embed=embed, files=files, view=view, ephemeral=True)

        if captcha_type.value == "math":
            import random, discord.ui
            from discord.ui import Button, View

            timer_task = asyncio.create_task(timeout_timer(spc_timeout))
            
            operations = ['+', '-', '*']
            num_terms = random.randint(2, 4)
            terms = [random.randint(1, 20) for _ in range(num_terms)]
            equation_parts = [str(terms[0])]

            for i in range(1, num_terms):
                operator = random.choice(operations)
                equation_parts.append(operator)
                equation_parts.append(str(terms[i]))

            if random.choice([True, False]):
                start = random.randint(0, num_terms - 1) * 2
                end = start + random.randint(2, 4) * 2
                if end >= len(equation_parts):
                    end = len(equation_parts) - 1

            equation = ' '.join(equation_parts)

            try:
                answer = eval(equation)
            except Exception as e:
                print(f"Error evaluating equation: {e}")
                await interaction.followup.send("An error occurred while generating the CAPTCHA.", ephemeral=True)
                return

            answers_list = [answer]
            
            while len(answers_list) < 9:
                wrong_answer = random.randint(-30, 80)
                if wrong_answer != answer and wrong_answer not in answers_list:
                    answers_list.append(wrong_answer)

            random.shuffle(answers_list)

            global answer_index
            answer_index = answers_list.index(answer)

            image_list = []
            for ans in answers_list:
                image_list.append(create_text_to_image(str(ans)))

            files = [discord.File(fp=image, filename=f"captcha_{i+1}.png") for i, image in enumerate(image_list)]
            embed = discord.Embed(title="Captcha: Math Equation", description=f"Please solve the equation: `{equation}`, and choose the right answer.", color=0x32a881)

            if timer_task.done():
                print("Task done, entered conditional")
                embed = discord.Embed(title="Time's Up!", description="You didn't manage to solve the Captcha in time.", color=0x32a881)
                try:
                    print(embed)
                    interaction.response.edit_message(embed=embed, view=None, attachments=[])
                except Exception as e:
                    print(e)

            view = View(timeout=spc_timeout)
            divider, row = 0, 0
            for i in range(9):
                if divider % 3 == 0:
                    row += 1
                btn = discord.ui.Button(label=str(answers_list[i]), style=discord.ButtonStyle.green, custom_id=f"{i}", row=row)
                btn.callback = math_callback
                view.add_item(btn)
                divider += 1

            await interaction.response.send_message(embed=embed, files=files, view=view, ephemeral=True)

        if captcha_type.value == "image":
            import random, os, discord.ui
            from discord.ui import Button, View

            cat_images = [f for f in os.listdir(r"images\pets") if os.path.isfile(os.path.join(r"images\pets", f)) and 'cat' in f and 'dog' not in f]
            dog_images = [f for f in os.listdir(r"images\pets") if os.path.isfile(os.path.join(r"images\pets", f)) and 'dog' in f and 'cat' not in f]
            both_images = [f for f in os.listdir(r"images\pets") if os.path.isfile(os.path.join(r"images\pets", f)) and 'both' in f]

            pet_dict = {}
            global rnd1

            rnd1 = random.randint(2, 3)
            random_cat_images = random.sample(cat_images, rnd1)
            for idx, image in enumerate(random_cat_images):
                pet_dict[f"cat{idx+1}"] = os.path.join(r"images\pets", image)

            rnd2 = random.randint(1, 4)
            random_dog_images = random.sample(dog_images, rnd2)
            for idx, image in enumerate(random_dog_images):
                pet_dict[f"dog{idx+1}"] = os.path.join(r"images\pets", image)

            rm_img = 9 - rnd1 - rnd2
            random_both_images = random.sample(both_images, rm_img)
            for idx, image in enumerate(random_both_images):
                pet_dict[f"both{idx+1}"] = os.path.join(r"images\pets", image)


            items = list(pet_dict.items())
            random.shuffle(items)
            pet_dict = dict(items)

            global index_list, image_counter, general_count
            image_counter, general_count = 0, 0
            index_list = []
            for idx, key in enumerate(pet_dict):
                if "cat" in key and "dog" not in key:
                    index_list.append(idx)

            files = [discord.File(fp=pet_dict[key], filename=f"captcha_{i+1}.png") for i, key in enumerate(pet_dict)]

            global image_embed
            image_embed = discord.Embed(
                title="Captcha: Image Selection",
                description=f"Please choose every image that contains **only** a `cat`.",
                color=0x32a881
            )

            global image_view
            image_view = View(timeout=spc_timeout)
            divider, row = 0, 0
            for i in range(9):
                if divider % 3 == 0:
                    row += 1
                btn = Button(label = f"{i}", style=discord.ButtonStyle.green, custom_id=f"{i}", row=row)
                btn.callback = image_callback
                image_view.add_item(btn)
                divider += 1

            await interaction.response.send_message(embed=image_embed, files=files, view=image_view, ephemeral=True)

        if captcha_type.value == "comp_text":
            @client.event
            async def on_message(message):
                result = ""
                if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
                    user_response = message.content.strip().lower()
                    if user_response == word:
                        embed = discord.Embed(title="Verification successful!", description="You've completed the Captcha successfully.", color=0x32a881)
                        await message.channel.send(embed=embed)
                        result = "Passed"
                    else:
                        embed = discord.Embed(title="Verification failed.", description="You've failed the Captcha test.", color=0x32a881)
                        await message.channel.send(embed=embed)
                        result = "Failed"

                embed_color = 0x00FF00
                
                if result == "Failed": embed_color=0xFD4646
                if result == "Passed": embed_color=0x39c4af
                log_embed = discord.Embed(title="Captcha Result!", color=embed_color)
                log_embed.set_thumbnail(url=interaction.user.avatar.url)
                log_embed.set_author(name="🌐 Captcha System")
                log_embed.add_field(name="Captcha Type", value="Text Recognition", inline=True)
                log_embed.add_field(name="User Tested", value=f"{interaction.user}", inline=True)
                log_embed.add_field(name="Captcha Result", value=f"{result}", inline=True)
                log_embed.add_field(name="Edited at", value=f"{time.strftime('%Y-%m-%d %H:%M:%S')}", inline=True)

                await LOG_CHANNEL.send(embed=log_embed)  


            import discord.ui, random, os
            from discord.ui import Button, View

            with open(r"words_list/words_list.txt", 'r') as file:
                words = [line.strip() for line in file.readlines()]
                word = random.choice(words)

            DM_CHANNEL = await interaction.user.create_dm()
            img = lingo_text_to_image(word, 800)

            embed = discord.Embed(title="Captcha: Text Recognition", description="Please write the word that is located in the picture above.", color=0x32a881)

            await DM_CHANNEL.send(embed=embed, file=discord.File(fp=img, filename="captcha_image.png"))
            
    except Exception as e:
        print(f"An error occurred: {e}")
        await interaction.followup.send("An error occurred while generating the CAPTCHA.", ephemeral=True)
             
def create_text_to_image(word):
    import PIL, io
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    width, height = 200, 200
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try: font = ImageFont.truetype("arial.ttf", 35)
    except IOError: font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), word, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    position = ((width - text_width) // 2, (height - text_height) // 2)

    draw.text(position, word, fill=(0, 0, 0), font=font)
    
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    return image_buffer

def lingo_text_to_image(word, size, font_size=None):
    import random
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO

    width, height = size, size
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    if font_size is None:
        font_size = random.randint(65, 90)

    try:
        font = ImageFont.truetype("fonts/astigma/ASS.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), word, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    padding = 20 

    temp_image = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (255, 255, 255, 0))
    temp_draw = ImageDraw.Draw(temp_image)

    temp_draw.text((padding, padding), word, font=font, fill=(0, 0, 0))

    rotation_angle = random.uniform(-45, 45)
    rotated_text = temp_image.rotate(rotation_angle, expand=True)

    rotated_bbox = rotated_text.getbbox()
    rotated_width = rotated_bbox[2] - rotated_bbox[0]
    rotated_height = rotated_bbox[3] - rotated_bbox[1]

    position = ((width - rotated_width) // 2, (height - rotated_height) // 2)

    image.paste(rotated_text, position, rotated_text)

    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    return image_buffer

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension(f'cogs.{filename[:-3]}')

async def main():
    config()
    await load()
    await client.start(os.getenv('token'))

if __name__ == "__main__":
    asyncio.run(main())