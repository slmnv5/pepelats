
set ENV_ROOT_DIR=%~dp0
cd "%ENV_ROOT_DIR%\src" || goto stop

::exit if already running, search for cmd window title
title no_title
tasklist /v /fo csv | find "start_looper_cmd" && goto stop


:loop
title start_looper_cmd
taskkill /F /IM python.exe
%ENV_ROOT_DIR%\.saved_env.bat
python.exe ./start_looper.py %*
timeout 10

goto loop

title no_title

:stop


