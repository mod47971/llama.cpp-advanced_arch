import re
import sys

# Использование: py fix_starvector_constructor.py llama.cpp/src/llama-model.cpp

def main():
    if len(sys.argv) != 2:
        print('Использование: py fix_starvector_constructor.py <путь_к_llama-model.cpp>')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Вынести конструктор STARVECTOR в конец файла
    pattern = re.compile(
        r'(// === НАЧАЛО: Инференс STARVECTOR ===[\s\S]*?// === КОНЕЦ: Инференс STARVECTOR ===)',
        re.MULTILINE
    )
    match = pattern.search(code)
    block = match.group(1) if match else None
    if block:
        code = code.replace(block, '')
        code = code.rstrip() + '\n\n' + block.strip() + '\n'
        print('Конструктор STARVECTOR перемещён в конец файла.')
    else:
        print('Блок конструктора STARVECTOR не найден!')

    # 2. Удалить case LLM_ARCH_© (с недопустимым символом)
    code, n_subs = re.subn(r'case LLM_ARCH_©:[\s\S]*?break;?\s*', '', code)
    if n_subs:
        print('Удалён case LLM_ARCH_©.')

    # 3. Исправить структуру фигурных скобок после switch/case
    # Найти конец switch/case (после default: GGML_ABORT...)
    # и убедиться, что далее нет лишних закрывающих/открывающих скобок
    # Попробуем закрыть функцию ровно одной скобкой
    code = re.sub(r'(default:\s*GGML_ABORT\([^)]+\);\s*)\}', r'\1\n    }', code, count=1)
    # Удалить лишние закрывающие скобки после switch/case
    code = re.sub(r'\}\s*\}\s*\n', '\n}', code)

    # 4. Удалить лишние пустые строки
    code = re.sub(r'\n{3,}', '\n\n', code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Все основные ошибки исправлены!')

if __name__ == '__main__':
    main()
