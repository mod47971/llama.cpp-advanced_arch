import sys

# Использование: py remove_unmatched_braces.py <путь_к_файлу>

def main():
    if len(sys.argv) != 2:
        print('Использование: py remove_unmatched_braces.py <путь_к_файлу>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Удаляем одиночные строки с } в диапазоне 170-200
    new_lines = []
    for i, line in enumerate(lines):
        if 170 <= i+1 <= 200 and line.strip() == '}':
            continue
        new_lines.append(line)
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print('Лишние одиночные } в диапазоне 170-200 удалены.')

if __name__ == '__main__':
    main()
