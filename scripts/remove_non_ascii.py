import sys

# Использование: py remove_non_ascii.py <путь_к_файлу>

def main():
    if len(sys.argv) != 2:
        print('Использование: py remove_non_ascii.py <путь_к_файлу>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    clean_code = ''.join(c for c in code if ord(c) < 128)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(clean_code)
    print('Все не-ASCII символы удалены.')

if __name__ == '__main__':
    main()
