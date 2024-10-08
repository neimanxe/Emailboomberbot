from pyrogram import Client, filters
from pymongo import MongoClient
import yagmail
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, MONGO_URI

mongo_client = MongoClient("MONGO_URI")
db = mongo_client["email_bot"]
database = db["users"]
sent_emails_database = db["sent_emails"]

neimanxe = Client(
    "Emailboomberbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=bot_token,
)

@neimanxe.on_message(filters.command("logging"))
async def logging(_, msg):
    user_id = msg.from_user.id
    await msg.reply("Enter your email:")
    email = await _.listen(user_id)
    await msg.reply("Enter your password:")
    password = await _.listen(user_id)
    await msg.reply("Is 2-step verification enabled? (yes/no)")
    two_step_enabled = await _.listen(user_id)
    if two_step_enabled.lower() == "yes":
        await msg.reply("Enter 2-step verification code:")
        two_step_code = await _.listen(user_id)
    database.insert_one({"user_id": user_id, "email": email, "password": password, "two_step_enabled": two_step_enabled, "two_step_code": two_step_code})
    await msg.reply("Email login data stored successfully!")

@neimanxe.on_message(filters.command("run"))
async def run(_, msg):
    user_data = database.find_one({"user_id": user_id})
    if not user_data:
        await msg.reply("Please use /logging command to store your email login data first!")
        return
    await msg.reply("To whom do you want to send the email?")
    recipient_email = await _.listen(user_id)
    await msg.reply("What message do you want to send on this email?")
    email_message = await _.listen(user_id)
    await msg.reply("How many emails do you want to send?")
    num_emails = int(await _.listen(user_id))
    yag = yagmail.SMTP(user_data["email"], user_data["password"])
    if user_data["two_step_enabled"] == "yes":
        yag.login(twofactor=True, otp=user_data["two_step_code"])
    for _ in range(num_emails):
        yag.send(to=recipient_email, subject="neimanxe", contents=email_message)
    sent_emails_database.insert_one({"user_id": user_id, "recipient_email": recipient_email, "num_emails": num_emails})
    await msg.reply("Emails sent successfully!")

@neimanxe.on_message(filters.command("mystatus"))
async def mystatus(_, msg):
    sent_emails_data = sent_emails_database.find({"user_id": user_id})
    sent_emails_message = "You have sent emails to:\n"
    for data in sent_emails_data:
        sent_emails_message += f"{data['recipient_email']}: {data['num_emails']} emails\n"
    await msg.reply(sent_emails_message)

@neimanxe.on_message(filters.command("logout"))
async def logout(_, msg):
    database.delete_one({"user_id": user_id})
    sent_emails_database.delete_many({"user_id": user_id})
    await msg.reply("Email login data cleared successfully!")

neimanxe.run()
