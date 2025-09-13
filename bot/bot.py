import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND = os.getenv("BACKEND_URL", "http://localhost:5000")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "5419054691"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    tg_id = str(message.from_user.id)
    username = message.from_user.username or ""
    await message.reply(f"Welcome to Panda Technic Tasks!\nYour telegram id: {tg_id}\nUse /tasks to view tasks.")
    # optionally register user to backend by making a dummy submit-less create (or backend creates on submit)

# /tasks -> fetch tasks from backend
@dp.message_handler(commands=['tasks'])
async def tasks_cmd(message: types.Message):
    res = requests.get(f"{BACKEND}/api/tasks")
    if res.status_code != 200:
        await message.reply("Failed to fetch tasks.")
        return
    tasks = res.json()
    if not tasks:
        await message.reply("No tasks right now.")
        return
    # show tasks with inline buttons to open link and to submit
    for t in tasks:
        text = f"*{t['name']}*\n{t.get('description','')}\nLink: {t.get('link','-')}"
        kb = types.InlineKeyboardMarkup()
        if t.get('link'):
            kb.add(types.InlineKeyboardButton("Open Link", url=t['link']))
        kb.add(types.InlineKeyboardButton("Submit Proof", callback_data=f"submit_{t['id']}"))
        await message.reply(text, reply_markup=kb, parse_mode='Markdown')

# callback to start submission: ask user to send proof + optional note
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('submit_'))
async def process_submit_cb(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split("_",1)[1]
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"Please send your proof (photo or file) for task {task_id}.\nAlso you can add a text note. When ready, send it together with the file or as text and attach file separately. After sending, reply with /done {task_id}")

# user sends /done <task_id> after uploading files or text
@dp.message_handler(commands=['done'])
async def done_cmd(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Usage: /done <task_id>")
        return
    task_id = parts[1]
    # check if user has recently sent a photo/file — for simplicity, if message is replying to a photo/file, handle it
    proof_file_id = None
    note = message.caption or ""
    # If the /done is sent in reply to a message with file/photo, get file_id
    if message.reply_to_message:
        if message.reply_to_message.photo:
            proof_file_id = message.reply_to_message.photo[-1].file_id
        elif message.reply_to_message.document:
            proof_file_id = message.reply_to_message.document.file_id
        note = message.reply_to_message.caption or message.reply_to_message.text or note

    # If no file attached, allow text-only proof
    files = {}
    if proof_file_id:
        file = await bot.get_file(proof_file_id)
        file_path = file.file_path
        f = await bot.download_file(file_path)
        # send to backend via multipart
        files = {'file': ('proof.jpg', f.read())}

    data = {
        'telegram_id': str(message.from_user.id),
        'username': message.from_user.username or "",
        'task_id': task_id,
        'note': note
    }
    try:
        resp = requests.post(f"{BACKEND}/api/submit", data=data, files=files if files else None)
        if resp.status_code == 200:
            js = resp.json()
            sub_id = js.get("submission_id")
            await message.reply(f"Submission received (id: {sub_id}). Admin will review soon.")
            # Forward proof to admin chat (if we have file)
            if proof_file_id:
                # forward the original message to admin chat so admin sees user and file
                await bot.forward_message(ADMIN_CHAT_ID, from_chat_id=message.from_user.id, message_id=message.reply_to_message.message_id)
            else:
                # no file: send text summary to admin
                await bot.send_message(ADMIN_CHAT_ID, f"New submission #{sub_id}\nUser: {message.from_user.id}\nTask: {task_id}\nNote: {note}")
        else:
            await message.reply("Failed to submit. Try again later.")
    except Exception as e:
        await message.reply("Error submitting: " + str(e))

# Optionally handle direct photo uploads without /done by instructing user to reply with /done
@dp.message_handler(content_types=['photo','document'])
async def handle_media(message: types.Message):
    await message.reply("Received your file. Now reply to this message with `/done <task_id>` to complete submission (so we know which task).")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
