' Создаем объект для взаимодействия с оболочкой Windows
Set WshShell = CreateObject("WScript.Shell")

' Задаем рабочую папку (ту, где лежит сам скрипт vbs)
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Запускаем скрипт через pythonw. Параметр 0 полностью скрывает окно.
WshShell.Run "pythonw main.py", 0, False