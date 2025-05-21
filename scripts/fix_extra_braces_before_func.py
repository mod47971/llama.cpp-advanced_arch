import re
import sys

# Использование: py fix_extra_braces_before_func.py <путь_к_файлу>

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_extra_braces_before_func.py <путь_к_файлу>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    # Удаляем лишние закрывающие скобки перед объявлением функции (оставляем одну)
    code, n = re.subn(r'(\}\}\})\s*([a-zA-Z_][\w:<> ]*\([^\)]*\)\s*\{)', r'}\n\2', code)
    code, n2 = re.subn(r'(\}\})\s*([a-zA-Z_][\w:<> ]*\([^\)]*\)\s*\{)', r'}\n\2', code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f'Лишние скобки перед функциями удалены: {n + n2}')

if __name__ == '__main__':
    main()
