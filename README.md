# Panda Technic Tasks

Starter repo: Flask backend, Aiogram Telegram bot, React admin panel.

## Quick local run (backend)
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# set ADMIN_TOKEN in backend/.env or export env var
python app.py

## Run bot
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# set TELEGRAM_BOT_TOKEN in bot/.env
python bot.py

## Run admin frontend
cd admin-frontend
npm install
npm start
# set REACT_APP_BACKEND_URL and REACT_APP_ADMIN_TOKEN in .env

## GitHub
# from repository root:
git init
git add .
git commit -m "Initial commit - Panda Technic Tasks"
# create repo on GitHub manually or via CLI, then:
git remote add origin git@github.com:YOUR_USERNAME/panda-technic-tasks.git
git push -u origin main
