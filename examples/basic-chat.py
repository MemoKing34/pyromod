import logging

from pyromod import Client, helpers, exceptions
import pyrogram

bot = Client("memobot")

@bot.on_message(pyrogram.filters.command(['start', 'test1']))
async def start(client, message):
    chat = message.chat
    response = await chat.ask("Oh hey! What is your name?")
    name = response.text
    response = await chat.ask(f"Hello {name}! Please tell me your age.")
    age = response.text
    response = await chat.ask(f"So you are {age} years old. Now i wanna know your hobby. What do you like to do?")
    hobby = response.text
    await message.reply(f"Oh, i see. Okay, so your name is {name}, you are {age} years old and you like to {hobby}. Nice to meet you!")

markup = helpers.ikb([['PAGE 1', 'PAGE 2'], ['PAGE 3', 'PAGE 4', 'PAGE 5']])

@bot.on_message()
async def handler(client, message):
    msg = await message.reply_text("Hello world!", reply_markup=markup)
    try:
        query = await msg.wait_for_click(message.from_user.id, timeout=13)
        await msg.edit_text(f'You pressed {query.data!r}')
    except exceptions.ListenerTimeout:
        await msg.edit_text("You're so slow man")


bot.run()