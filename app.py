import sqlite3
    # Глобальный объект request для доступа к входящим данным запроса, которые будут подаваться через форму HTML.
    # Функция url_for() для генерирования URL-адресов.
    # Функция flash() для появления сообщения при обработке запроса.
    # Функция redirect() для перенаправления клиента в другое расположение.
from flask import Flask, render_template, request, url_for, flash, redirect

#функция abort нужна для ответа в виде страницы 404
from werkzeug.exceptions import abort

#подключение к базе данных и возвращение данных
def get_db_connection():
# открываем соединение с файлом базы данных database.db
    conn = sqlite3.connect('database.db')
#устанавливаем атрибут row_factory в sqlite3. Row, чтобы получить доступ к столбцам на основе имен.
    conn.row_factory = sqlite3.Row
#функция возвращает объект подключения conn, который нужен для доступа к базе данных
    return conn

#аргумент post_id определяет, какой пост блога предназначен для возврата.
def get_post(post_id):
#получаем пост блога, связанный с указанным значением post_id.
    conn = get_db_connection()
#метод fetchone() нужен для получения результата и хранения его в переменной post
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
#если пост не найден выходит ошибка 404 из функции abort
    if post is None:
        abort(404)
#если пост был найден, вы возвращаете значение переменной post
    return post

#создаём объект класса Flask
# конструктору Flask назначается аргумент __name__.
# Конструктор Flask должен иметь один обязательный аргумент. Им служит название пакета.
# В большинстве случаев значение __name__ подходит.
# Название пакета приложения используется фреймворком Flask, чтобы находить статические файлы, шаблоны и т. д.
app = Flask(__name__)
# для настройки секретного ключа нужно добавить конфигурацию SECRET_KEY в ваше приложение через объект app.config
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/')
# #Функция просмотра index() возвращает результат вызова render_template() с index.html в качестве аргумента.
def index():
#открываем  подключение к базе данных
    conn = get_db_connection()
#метод fetchall() доставляет все строки результата запроса.
    posts = conn.execute('SELECT * FROM posts').fetchall()
#закрываем подключение к базе данных
    conn.close()
# #render_template(), позволяет  поставлять файлы шаблонов HTML, существующих в папке  templates
    return render_template('index.html', posts=posts)

# функция просмотра для отображения отдельного шаблона
# <int:post_id> указывает, что часть после слэша (/) представляет собой положительное целое число
# (отмеченное конвертером int),
# которое вам необходимо в функции просмотра.
@app.route('/<int:post_id>')
#  Flask распознает это и передает его значение аргументу ключевого слова post_id вашей функции просмотра post().
def post(post_id):
# Затем вы используем функцию get_post() для получения поста блога, связанного с заданным ID, и хранения результата в переменной post
    post = get_post(post_id)
    return render_template('post.html', post=post)


# функция просмотра, которая будет отображать шаблон, показывающий форму, которую вы можете заполнить для создания нового поста в блоге.
# маршрут /create, который принимает запросы GET и POST. Запросы GET принимаются по умолчанию.
# Для того чтобы также принимать запросы POST, которые посылаются браузером при подаче форм,
# передаем кортеж с приемлемыми типами запросов в аргумент methods декоратора @app.route().
@app.route('/create', methods=('GET', 'POST'))
def create():
# код выполняется только в случае, если запрос является запросом POST
    if request.method == 'POST':
# затем извлекаем отправленные заголовок и содержание из объекта request.form
        title = request.form['title']
        content = request.form['content']
# Если заголовок не указан, будет выполнено условие
# flash - выводит flash - собщения на странице
        if not title:
            flash('Title is required!')
# если заголовок указан, вы открываем подключение с помощью функции get_db_connection()
# и вставляем полученные заголовок и содержание в таблицу posts.
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
# вносим изменения в базу данных и закрываем подключение
            conn.commit()
            conn.close()
# перенаправляем клиента на страницу индекса с помощью функции redirect(),
# передавая URL, сгенерированный функцией url_for() со значением 'index' в качестве аргумента.
            return redirect(url_for('index'))

    return render_template('create.html')

# редактирование поста
@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

# удаление поста
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

if __name__ == "__main__":
#запуск сервера
    app.run()
