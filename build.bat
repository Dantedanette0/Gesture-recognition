pyinstaller ^
    --clean ^
    --onefile ^
    --noconsole ^
    --workpath build ^
    --specpath build ^
    --distpath build ^
    --add-data "../audio/*;audio" ^
    --hidden-import "msvc-runtime" ^
    --collect-data "mediapipe" ^
    main.py