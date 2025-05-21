import sys
import re

# Использование: py fix_llama_model_braces.py llama.cpp/src/llama-model.cpp

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_llama_model_braces.py <путь_к_llama-model.cpp>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Закрыть скобки после switch-case и default, если после них идёт static-функция или объявление переменной
    # 2. Проверить, чтобы static-функции были только на уровне файла

    # Закрыть скобки после default: ... return ...; если после идёт не скобка, а код
    code, n1 = re.subn(r'(default:[^;]+;\s*)\n(?![\}\n])', r'\1\n}\n', code)

    # Закрыть скобки после switch-case, если после идёт static или объявление переменной
    code, n2 = re.subn(r'(\s+break;\s*)\n(?![\}\n])', r'\1\n}\n', code)

    # Исправить случаи, когда static-функция идёт сразу после закрывающей скобки функции
    code, n3 = re.subn(r'(\}\s*)\nstatic ', r'\1\nstatic ', code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f'Файл успешно исправлен. Закрыто скобок: {n1 + n2}, перемещено static-функций: {n3}')

if __name__ == '__main__':
    main()
