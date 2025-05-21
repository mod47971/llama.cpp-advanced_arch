import re
import sys

# Использование: py fix_llama_model_header.py llama.cpp/src/llama-model.cpp

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_llama_model_header.py <путь_к_llama-model.cpp>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Исправить: default: ... return ...;\n}static ... -> default: ... return ...;\n}\nstatic ...
    code, n = re.subn(r'(default:[^;]+;\s*)\}(static )', r'\1\n}\n\2', code)
    code, n2 = re.subn(r'(default:[^;]+;\s*)\}\s*static ', r'\1\n}\nstatic ', code)
    # Для llama_expert_gating_func_name
    code, n3 = re.subn(r'(default:[^;]+;\s*)\}(static const std::map)', r'\1\n}\n\2', code)
    code, n4 = re.subn(r'(default:[^;]+;\s*)\}\s*static const std::map', r'\1\n}\nstatic const std::map', code)
    if n or n2 or n3 or n4:
        print('Добавлены закрывающие скобки после default: return ...;')
    else:
        print('Не удалось найти место для исправления!')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Файл успешно исправлен.')

if __name__ == '__main__':
    main()
