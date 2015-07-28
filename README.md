### Скрипт Poster

Основная цель скрипта -- упростить набор формул. Скрипт собирает все доллары, разбросанные по тексту и выделяет по ним формулы. Формулы преобразуются в картинки через сервисы [codecogs](https://www.codecogs.com/latex/eqneditor.php) или [tex.s2cms](http://tex.s2cms.ru/).

Кроме того, скрипт преобразует стандартный markdown к html + немного выправляет переводы строк.

По своему опыту я знаю, что сервисы с картинками могут сильно тупить, а то и умирать от хабраэффекта, помноженного на число формул в статье. Я сделал автоматический загрузчик картинок. Исключение составляют svg.

### Подготовка

1. Ставим [Python 2.7](https://www.python.org/downloads/) если нет.
2.  Ставим [curl](http://curl.haxx.se/) если нет. Если ставите под Windows, не забудьте добавить путь к переменной PATH.
3. Качаем [скрипт с GitHub-а](https://github.com/vsevolod-oparin/habratex).
4. Запускаем скрипт init.py. 

Почти готово. Под линуксом или маком, вы можете вызвать init.py через sudo с флагом -l. Скрипт добавит софт-линк /usr/bin/poster на скрипт poster.py.

В файле default.json вы можете поменять источник формул: texsvg, texpng для tex.s2cms или codecogs.


### Как можно использовать

```bash
> poster clipboard
```
Преобразует содержимое буфера к хабрачитаемому виду и записывает обратно в буфер.

```bash
> poster <filename.md>
```
Преобразует содержимое файла filename.md и записывает результат в filename.txt

```bash
> poster -c <filename.md>
```
Тоже самое, но результат при этом копируется в буфер. Есть возможность указать, куда записывать результат через флаг -o.

### Нюансы

1. При загрузке картинок, скрипт запрашивает habrasid и сохраняет его в default.json. Один раз вы должны решить, насколько для вас важно, что habrasid будет валяться у вас в открытом виде. Если согласны, то его надо будет периодически обновлять. Как добывать, смотрите в этом [посте](http://habrahabr.ru/post/214347/).
2. Чтобы сделать кат, наберите 
```
<!-- cut [Cut title] -->
```

### Пост

Этот пост я написал в [stackedit.io](stackedit.io). Исходник можно найти в [гитхабе](https://github.com/vsevolod-oparin/habratex).

Надеюсь, что смогу облегчить своим небольшим вкладом оформление математических статей здесь и на других ресурсах, не поддерживающих ![LaTeX](http://tex.s2cms.ru/svg/%5Cinline%20%5CLaTeX).
