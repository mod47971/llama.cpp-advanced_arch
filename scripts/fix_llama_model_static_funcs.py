import re
import sys

# Использование: py fix_llama_model_static_funcs.py llama.cpp/src/llama-model.cpp

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_llama_model_static_funcs.py <путь_к_llama-model.cpp>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Переместить все static-функции на уровень файла (после закрывающей скобки функции, если они внутри)
    # 2. Закрыть все незакрытые фигурные скобки после default: ... return ...;

    # Перемещение static-функций на уровень файла
    # Найти static-функции, которые идут сразу после закрывающей скобки функции
    code, n1 = re.subn(r'(\}\s*)static ([^\(]+\([^\)]*\)\s*\{)', r'\1\nstatic \2', code)

    # Исправить случаи, когда static-функция идёт без \n после }
    code, n2 = re.subn(r'(\}\s*)\nstatic ', r'\1\nstatic ', code)

    # Закрыть скобки после default: ... return ...;
    code, n3 = re.subn(r'(default:[^;]+;\s*)\}(static )', r'\1\n}\n\2', code)
    code, n4 = re.subn(r'(default:[^;]+;\s*)\}\s*static ', r'\1\n}\nstatic ', code)
    code, n5 = re.subn(r'(default:[^;]+;\s*)\}(static const std::map)', r'\1\n}\n\2', code)
    code, n6 = re.subn(r'(default:[^;]+;\s*)\}\s*static const std::map', r'\1\n}\nstatic const std::map', code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f'Файл успешно исправлен. Перемещено static-функций: {n1 + n2}, закрыто скобок: {n3 + n4 + n5 + n6}')

if __name__ == '__main__':
    main()
