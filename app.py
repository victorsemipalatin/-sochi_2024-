from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import threading
import time
import logging

app = Flask(__name__)
CORS(app)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)

# Настройка папки для загрузки файлов
UPLOAD_FOLDER = 'upload'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Настройка логирования
logging.basicConfig(filename='processing.log', level=logging.INFO)

# Модель базы данных
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), default='Обработка не начата', nullable=False)
    status_final = db.Column(db.Boolean, default=False, nullable=False)
    result_final = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()

# Функция обработки файла (эмуляция длительной обработки)
def process_file(file_id):
    # Устанавливаем контекст приложения
    with app.app_context():
        logging.info(f"process_file -  {file_id}")
        try:
            file = db.session.get(File, file_id)
            if file:
                logging.info(f"process_file start - {file.name} с ID {file_id}")
                # Эмуляция длительной обработки
                time.sleep(10)
                file.status = 'process_file - time 10 second'
                db.session.commit()
                logging.info(f"FINISH FILE {file.name} с ID {file_id} завершена")
        except Exception as e:
            logging.error(f"ERROR FILE -  {file_id}: {str(e)}")

# Первый эндпоинт для загрузки файла
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Файл не является PDF'}), 400

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    new_file = File(name=filename, result_final="")
    db.session.add(new_file)
    db.session.commit()

    # Лог перед запуском потока
    logging.info(f"Start potok - ID {new_file.id}")

    # Запуск обработки в отдельном потоке
    thread = threading.Thread(target=process_file, args=(new_file.id,))
    thread.start()
    logging.info(f"File -  ID {new_file.id} start")

    return jsonify({'id': new_file.id}), 200

# Второй эндпоинт для проверки статуса обработки
@app.route('/status/<int:file_id>', methods=['GET'])
def check_status(file_id):
    file = File.query.get(file_id)
    if not file:
        return jsonify({'error': 'Файл не найден'}), 404
    return jsonify({'id': file.id, 'status': file.status}), 200

if __name__ == '__main__':
    app.run(debug=True)
