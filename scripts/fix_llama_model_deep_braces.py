import re
import sys

# Использование: py fix_llama_model_deep_braces.py llama.cpp/src/llama-model.cpp

def is_func_decl(line):
    # Простая эвристика для определения объявления функции на уровне файла
    return bool(re.match(r'^(static |inline |constexpr |)[\w:<>]+\s+[\w:<>]+\s*\([^)]*\)\s*\{', line.strip()))

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_llama_model_deep_braces.py <путь_к_llama-model.cpp>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    brace_balance = 0
    for i, line in enumerate(lines):
        # Считаем баланс скобок
        brace_balance += line.count('{')
        brace_balance -= line.count('}')
        # Если встречаем объявление функции на уровне файла, а баланс > 0, закрываем все открытые скобки
        if is_func_decl(line) and brace_balance > 0:
            new_lines.extend(['}' for _ in range(brace_balance)])
            brace_balance = 0
        new_lines.append(line)
    # В конце файла закрываем все незакрытые скобки
    if brace_balance > 0:
        new_lines.extend(['}' for _ in range(brace_balance)])
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f'Файл успешно исправлен. Закрыто скобок: {brace_balance}')

if __name__ == '__main__':
    main()
