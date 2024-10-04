from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters
import project
import time
import os

token = "8107598303:AAHQtgnHx3XiTH8HGLX_O5A47q-kWuIwix8"

async def start_command(update, context):
    await update.message.reply_text("Для проверки выполнения задания отправьте боту pdf файл. \nК сожалению, телеграм устанавливает ограничение для ботов на скачивание файлов.\nМаксимальный размер файла 20мб.\nФайлы большего размера Вы можете проверить с помощью кода, представленного в репозитории.")


async def downloader(update, context):
    print("новый запрос")
    file_id = update.message.document.file_id
    new_file = await context.bot.get_file(file_id)
    file_name = new_file.file_id
    await new_file.download_to_drive(file_name)
    start = time.time()
    project.make_table_of_contents(file_name)
    print(time.time() - start)
    output_file_name = "new.pdf"
    chat_id = update.message.chat_id
    document = open(output_file_name, 'rb')
    await context.bot.send_document(chat_id, document)
    os.remove(output_file_name)
    os.remove(file_name)



application = ApplicationBuilder().token(token).build()
application.add_handler(CommandHandler("start", start_command))
application.add_handler(MessageHandler(filters.ATTACHMENT, downloader))

application.run_polling()
