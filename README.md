# WebNotebook

Данный проект представляет собой веб-приложение на языке Python, позволяющее студентам хранить свои конспекты лекций и семинаров в виде сканов, преобразованных в формат pdf.

## Установка и настройка

Для запуска проекта необходимо установить следующие компоненты:

- Python 3
- Flask (фреймворк для веб-приложений на Python)
- Flask-WTF (расширение Flask для работы с формами)
- Flask-Login (расширение Flask для аутентификации пользователей)

## Использование

Приложение предоставляет следующие функциональные возможности:

 - Регистрация нового пользователя
 - Аутентификация пользователя
 - Добавление новых тетрадей
 - Добавление конспектов в существующие тетради
 - Группировка тетрадей по предметам
 - Хранение всех тетрадей в облаке

## База данных

Приложение использует SQLite базу данных, которая хранит следующую информацию:

 - Пользователи (id, имя пользователя, email, хеш пароля)
 - Тетради (id, название, дата создания, id пользователя, id предмета)
 - Конспекты (id, название, дата создания, id тетради)

## Разработчик

Проект разработан студентами 321 группы факультета ВМК МГУ:

 - Сагалевич Виталий Дмитриевич
 - Путилов Георгий Константинович