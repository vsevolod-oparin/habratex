### Скрипт Poster

Цель скрипта -- упростить набор формул. Скрипт собирает все доллары, разбросанные по тексту и выделяет по ним формулы. Формулы преобразуются в картинки через сервисы [codecogs](https://www.codecogs.com/latex/eqneditor.php) или [tex.s2cms](http://tex.s2cms.ru/).

Кроме того, скрипт преобразует стандартный markdown к html + немного выправляет переводы строк.

По своему опыту я знаю, что сервисы с картинками могут сильно тупить, а то и умирать от хабраэффекта, помноженного на число формул в статье. Я сделал автоматический загрузчик картинок, который грузит все за исключением составляют svg с tex.s2cms.

### Подготовка

1. Ставим [Python 2.7](https://www.python.org/downloads/) если нет.
2.  Ставим [curl](http://curl.haxx.se/) если нет. Если ставите под Windows, не забудьте добавить путь к переменной PATH.
3. Качаем [скрипт с GitHub-а](https://github.com/vsevolod-oparin/habratex).
4. Запускаем скрипт init.py. 

Почти готово. Под линуксом или маком, вы можете вызвать init.py через sudo с флагом -l. Скрипт добавит софт-линк /usr/bin/poster на скрипт poster.py.

В файле default.json вы можете поменять источник формул: texsvg, texpng для tex.s2cms или codecogs, а также кодировку.


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

1. При загрузке картинок, скрипт запрашивает habrasid и сохраняет его в default.json. Один раз вы должны решить, насколько для вас важно, что habrasid будет находиться в открытом виде. Если согласны, то его надо будет периодически обновлять. Как добывать, смотрите в этом [посте](http://habrahabr.ru/post/214347/).
2. Подгрузка картинок требует времени. Поэтому скрипт кэширует ссылки. Если указан путь к файлу, в той же папке появится папка links с картинками по ссылкам и файл links.json c информацией о загруженных картинках. Если вы преобразуете через буфер, файлы будут скачиваться в папку, где находится скрипт. 

### Особенности синтаксиса

- Чтобы сделать кат, наберите 
```
<!-- cut [Cut title] -->
```

- Чтобы сделать спойлер, введите сначала
```
<!-- spoiler [spoiler title] -->
```
а затем
```
<!-- /spoiler -->
```

- Используйте ключевые слова left, center, right, чтобы обозначить выравнивание картинки
```
![left][beautiful.png]
```


### Плюшка в конце

Пользователи Windows могут воспользоваться программкой [AutoHotKey](http://www.autohotkey.com/). Например, ahk-скрипт
```
^j::
  Send, ^a
  Send, ^c
  Run, <path to poster.py> clipboard
Return
```
позволит по нажатию сочетания Ctrl+J одновременно выделить текущий текст, скопировать в буфер обмена и преобразовать.

Надеюсь, что я смогу облегчить своим небольшим вкладом оформление математических статей здесь и на других ресурсах, не поддерживающих ![LaTeX](http://tex.s2cms.ru/svg/%5Cinline%20%5CLaTeX). 

Удачи!
