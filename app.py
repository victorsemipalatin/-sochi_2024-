from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import threading
import time
import logging
import shutil

app = Flask(__name__)
CORS(app)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)

# Настройка папки для загрузки и результатов обработки файлов
UPLOAD_FOLDER = 'upload'
PROCESSED_FOLDER = 'processed'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

# Настройка логирования
logging.basicConfig(filename='processing.log', level=logging.INFO)


# Модель базы данных
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), default='Идет обработка', nullable=False)
    status_final = db.Column(db.Boolean, default=False, nullable=False)
    result_final = db.Column(db.String(255), nullable=True)  # Добавлено для хранения имени обработанного файла


with app.app_context():
    db.create_all()

_processed_filename = ''
# Функция обработки файла (эмуляция длительной обработки)
def process_file(file_id):
    global _processed_filename
    with app.app_context():
        logging.info(f"process_file -  {file_id}")
        try:
            file = db.session.get(File, file_id)
            if file:
                logging.info(f"process_file start - {file.name} с ID {file_id}")
                time.sleep(10)  # Эмуляция длительной обработки

                # Путь к исходному и обработанному файлу
                original_filepath = os.path.join(UPLOAD_FOLDER, file.name)
                processed_filename = f"processed_{file.name}"
                _processed_filename = processed_filename
                processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)

                # Копируем оригинальный PDF файл в папку processed
                shutil.copyfile(original_filepath, processed_filepath)

                # Обновляем информацию о файле
                file.status = 'Обработка завершена'
                file.result_final = processed_filename
                file.status_final = True
                db.session.commit()

                logging.info(f"Обработка файла {file.name} завершена. Результат сохранён в {processed_filename}.")
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

    logging.info(f"Запуск потока обработки - ID {new_file.id}")

    # Запуск обработки в отдельном потоке
    thread = threading.Thread(target=process_file, args=(new_file.id,))
    thread.start()
    logging.info(f"Файл - ID {new_file.id} загружен и начата обработка")

    return jsonify({'id': new_file.id}), 200


# Второй эндпоинт для проверки статуса обработки
@app.route('/status/<int:file_id>', methods=['GET'])
def check_status(file_id):
    file = File.query.get(file_id)
    if not file:
        return jsonify({'error': 'Файл не найден'}), 404
    return jsonify({
        'id': file.id,
        'status': file.status,
        'status_final': file.status_final,
        'result_final': file.result_final
    }), 200


# Эндпоинт для скачивания обработанного файла
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(PROCESSED_FOLDER, _processed_filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': 'Файл не найден'}), 404


if __name__ == '__main__':
    app.run(debug=True)
