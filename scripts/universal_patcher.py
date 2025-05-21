import os
import re
import argparse

"""
Пример использования:
python universal_patcher.py \
  --file llama.cpp/src/llama-model.cpp \
  --replace-block "// === НАЧАЛО: Инференс STARVECTOR ===" "// === КОНЕЦ: Инференс STARVECTOR ===" new_code.txt \
  --insert-before "default:" insert_code.txt \
  --move-constructor-out llm_build_starvector \
  --lint
"""

def read_code(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_code(path, code):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

def replace_block(code, start_marker, end_marker, new_block):
    pattern = re.compile(re.escape(start_marker) + r'.*?' + re.escape(end_marker), re.DOTALL)
    if pattern.search(code):
        code = pattern.sub(new_block, code)
    else:
        print(f'Блок между {start_marker} и {end_marker} не найден!')
    return code

def insert_before(code, before_str, insert_block):
    idx = code.find(before_str)
    if idx != -1:
        code = code[:idx] + insert_block + '\n' + code[idx:]
    else:
        print(f'Строка для вставки перед ({before_str}) не найдена!')
    return code

def insert_after(code, after_str, insert_block):
    idx = code.find(after_str)
    if idx != -1:
        idx += len(after_str)
        code = code[:idx] + '\n' + insert_block + code[idx:]
    else:
        print(f'Строка для вставки после ({after_str}) не найдена!')
    return code

def lint_code(code):
    # Удалить лишние пустые строки
    code = re.sub(r'\n{3,}', '\n\n', code)
    # Убрать пробелы в конце строк
    code = re.sub(r'[ \t]+\n', '\n', code)
    # Привести отступы к 4 пробелам (минимально)
    code = re.sub(r'^(    )+', lambda m: ' ' * (len(m.group(0))), code, flags=re.MULTILINE)
    return code

def move_constructor_out(code, class_name):
    # Находит реализацию конструктора внутри функции и перемещает её в конец файла
    # Пример сигнатуры: llm_build_starvector::llm_build_starvector(...)
    pattern = re.compile(r'(// === НАЧАЛО: Инференс STARVECTOR ===\s*)(%s::%s\s*\([^\)]*\)\s*:[^\{]*\{.*?\n\s*\}// === КОНЕЦ: Инференс STARVECTOR ===)' % (class_name, class_name), re.DOTALL)
    match = pattern.search(code)
    if not match:
        # fallback: ищем просто конструктор между двумя маркерами
        pattern2 = re.compile(r'(// === НАЧАЛО: Инференс STARVECTOR ===)(.*?%s::%s\s*\([^\)]*\)\s*:[^\{]*\{.*?\n\s*\}// === КОНЕЦ: Инференс STARVECTOR ===)' % (class_name, class_name), re.DOTALL)
        match = pattern2.search(code)
    if match:
        block = match.group(2)
        # Удаляем из текущего места
        code = code.replace(block, '')
        # Вставляем в конец файла
        code = code.rstrip() + '\n\n' + block.strip() + '\n'
        print(f'Конструктор {class_name} перемещён в конец файла.')
    else:
        print(f'Конструктор {class_name} не найден для перемещения!')
    return code

def main():
    parser = argparse.ArgumentParser(description='Универсальный автопатчер для C/C++ файлов.')
    parser.add_argument('--file', required=True, help='Путь к целевому файлу')
    parser.add_argument('--replace-block', nargs=3, metavar=('START', 'END', 'BLOCK'), help='Заменить блок между маркерами на содержимое файла BLOCK')
    parser.add_argument('--insert-before', nargs=2, metavar=('BEFORE', 'BLOCK'), help='Вставить BLOCK перед строкой BEFORE')
    parser.add_argument('--insert-after', nargs=2, metavar=('AFTER', 'BLOCK'), help='Вставить BLOCK после строки AFTER')
    parser.add_argument('--move-constructor-out', metavar='CLASS', help='Переместить реализацию конструктора CLASS в конец файла')
    parser.add_argument('--lint', action='store_true', help='Автоматически исправить базовые ошибки форматирования')
    args = parser.parse_args()

    code = read_code(args.file)

    if args.replace_block:
        start_marker, end_marker, block_path = args.replace_block
        new_block = read_code(block_path)
        code = replace_block(code, start_marker, end_marker, new_block)

    if args.insert_before:
        before_str, block_path = args.insert_before
        insert_block = read_code(block_path)
        code = insert_before(code, before_str, insert_block)

    if args.insert_after:
        after_str, block_path = args.insert_after
        insert_block = read_code(block_path)
        code = insert_after(code, after_str, insert_block)

    if args.move_constructor_out:
        code = move_constructor_out(code, args.move_constructor_out)

    if args.lint:
        code = lint_code(code)

    write_code(args.file, code)
    print('Патч успешно применён!')

if __name__ == '__main__':
    main()
