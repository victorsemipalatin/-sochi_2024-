# Nuclear IT Hack 2024. T1 TABLE OF CONTENT

## Содержание

1. Состав команды
2. Описание работы программы
3. Описание файлов репозитория
4. Способы улучшения программы

## Состав команды

- **Завидов Егор Николаевич**
- **Кораблев Денис Андреевич**
- **Панфилов Павел Андреевич**
- **Петров Григорий Евгеньевич**

## Описание работы программы
- **Ввиду ограничений по времени и железу, было выбрано отказаться от использования LLM и свести задачу к тривиальной.
- **Среднее время работы программы для 150 страниц:** 2 минуты на CPU
- **Рекомендуемое оборудование:** NVIDIA карты с поддержкой CUDA ядер (2 GB) для более быстрой обработки. Скорость обработки с помощью модели можно увеличить до 10 раз.

### Рабочий процесс:

1. **Оцифровка:** Начальный этап включает оцифровку документов.
2. **Извлечение текста:** Извлечение текста в *.txt файл, содержащий оцифрованные строки.
3. **Обработка текста:** Обработка строк с помощью дообученной модели ruBERTa. Датасет для этой модели был собран и размечен вручную.
4. **Дополнительные шаги:** Дополнительные шаги обработки по мере необходимости.

## Описание файлов репозитория

- **app.py:** Реализует API составляющую проекта.
- **bert.py:** Обрабатывает *.txt файл с помощью LM модели.
- **bert_fine_tuning_for_cls.ipynb:** Содержит процесс обучения и обработки датасета.
- **bert_context_tuning.ipynb:** Попытки научить контексту оказались хуже, чем классика.
- **pdfoutline.py, project.py:** Отвечают за оцифровку и разметку PDF файлов.
- **upload_form.html**: Содержит форму для отправки PDF на обработку.

## Способы улучшения программы

1. **Проверка на правописание:** Добавление функции проверки на правописание. Текущие open-source spell-checker'ы не удовлетворили наши ожидания, поэтому можно дообучить небольшую модель.
2. **Оцифровка документов:** Улучшение процесса оцифровки. Текущий метод имеет небольшие недочеты.
3. **Управление заголовками:** Добавление или удаление цифр в заголовках и создание иерархии.
![BARSIK](https://github.com/victorsemipalatin/-sochi_2024-/blob/main/293046_O.png)
