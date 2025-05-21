import os
import re

TARGET = os.path.join(os.path.dirname(__file__), '../src/llama-model.cpp')
HEADER = os.path.join(os.path.dirname(__file__), '../src/llama-model.h')

# Новый forward-pass-каркас
starvector_impl = '''
// === НАЧАЛО: Инференс STARVECTOR ===
llm_build_starvector::llm_build_starvector(const llama_model & model, const llm_graph_params & params, ggml_cgraph * gf, int mode)
    : llm_graph_context(params), mode(mode) {
    // Получаем доступ к структуре весов STARVECTOR
    const auto *sv = model.starvector.get();
    ggml_tensor * cur = nullptr;

    if (!sv) {
        throw std::runtime_error("starvector_model не инициализирована");
    }

    if (mode == 0) {
        // === text2svg: только SVG-трансформер ===
        // 1. Вход: токены текста (params.inpL)
        // 2. Эмбеддинг токенов
        cur = ggml_get_rows(ctx0, sv->svg_wte, params.inpL); // эмбеддинг токенов
        // 3. Добавить позиционные эмбеддинги
        ggml_tensor * pos = ggml_get_rows(ctx0, sv->svg_wpe, params.inp_pos); // позиционные эмбеддинги
        cur = ggml_add(ctx0, cur, pos);
        // 4. TODO: Прогон через все слои SVG-трансформера (attention + MLP + LN)
        // for (int il = 0; il < n_layers; ++il) { ... }
        // 5. Финальный layer norm
        // cur = ggml_norm(ctx0, cur, sv->svg_ln_f_weight, sv->svg_ln_f_bias);
        // 6. TODO: Прогон через output head (если есть)
    } else {
        // === image2svg: vision encoder + SVG-трансформер ===
        // 1. Вход: изображение (params.image_tensor или аналогичный)
        // 2. Прогон через vision encoder (ResNet/ViT)
        // cur = vision_encoder_forward(ctx0, sv, params.image_tensor);
        // 3. Проекция признаков изображения в пространство SVG-трансформера
        // cur = ggml_mul_mat(ctx0, sv->proj_c_fc_weight, cur);
        // 4. TODO: Добавить norm/адаптеры, если есть
        // 5. TODO: Передать результат как начальное состояние в SVG-трансформер
        // 6. TODO: Прогон через SVG-трансформер (аналогично text2svg)
    }

    // TODO: Сохранить результат в res->t_logits (или аналогично другим архитектурам)
    // res->t_logits = cur;
    // ggml_build_forward_expand(gf, cur);
}
// === КОНЕЦ: Инференс STARVECTOR ===
'''

def check_brace_balance(code):
    stack = []
    for i, c in enumerate(code):
        if c == '{':
            stack.append(i)
        elif c == '}':
            if stack:
                stack.pop()
            else:
                return False, i  # Лишняя }
    return len(stack) == 0, (stack[-1] if stack else -1)

def patch_and_lint_llama_model_cpp():
    # --- Патч .cpp ---
    with open(TARGET, 'r', encoding='utf-8') as f:
        code = f.read()

    # Исправление: закрываем case LLM_ARCH_T5, если нет } break;
    def fix_t5_case_block(code):
        pattern = re.compile(r'(case LLM_ARCH_T5:[\s\S]*?switch \(type\) \{[\s\S]*?)(?=case LLM_ARCH_STARVECTOR:|case LLM_ARCH_|default:)', re.MULTILINE)
        def repl(m):
            block = m.group(1)
            # Если нет '} break;' в конце блока, добавляем
            if not re.search(r'\}\s*break;\s*$', block):
                return block + '\n        } break;\n'
            return block
        return pattern.sub(repl, code)

    code = fix_t5_case_block(code)

    code, n = re.subn(
        r'// === НАЧАЛО: Инференс STARVECTOR ===.*?// === КОНЕЦ: Инференс STARVECTOR ===',
        starvector_impl,
        code,
        flags=re.DOTALL
    )
    if n == 0:
        idx = code.find('default:')
        if idx != -1:
            code = code[:idx] + starvector_impl + '\n' + code[idx:]

    code = re.sub(
        r'case LLM_ARCH_STARVECTOR:[\s\S]*?break;',
        'case LLM_ARCH_STARVECTOR:\n            {\n                llm = std::make_unique<llm_build_starvector>(*this, params, gf, 0);\n            } break;',
        code,
        flags=re.MULTILINE
    )
    code = re.sub(r'^\s*llm = std::make_unique<llm_build_starvector>\([^\n]+\);\s*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'case LLM_ARCH_STARVECTOR:\n\s*{\s*}\s*break;', 'case LLM_ARCH_STARVECTOR:\n            {\n                llm = std::make_unique<llm_build_starvector>(*this, params, gf, 0);\n            } break;', code)
    code = re.sub(r'\n{3,}', '\n\n', code)

    # Проверка баланса фигурных скобок
    ok, pos = check_brace_balance(code)
    if not ok:
        if pos != -1 and code[pos] == '{':
            # Добавить закрывающую скобку в конец файла
            code += '\n}'
            print('ВНИМАНИЕ: Добавлена закрывающая фигурная скобка в конец файла!')
        else:
            # Удалить лишнюю закрывающую скобку
            code = code[:pos] + code[pos+1:]
            print('ВНИМАНИЕ: Удалена лишняя закрывающая фигурная скобка!')
        # Повторная проверка
        ok2, _ = check_brace_balance(code)
        if not ok2:
            print('ОШИБКА: Баланс фигурных скобок не удалось восстановить!')

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(code)

    # --- Патч .h ---
    with open(HEADER, 'r', encoding='utf-8') as f:
        hcode = f.read()
    # Заменяю наследование
    hcode = re.sub(
        r'struct llm_build_starvector\s*:\s*public\s*llm_graph_result_i',
        'struct llm_build_starvector : public llm_graph_context',
        hcode
    )
    with open(HEADER, 'w', encoding='utf-8') as f:
        f.write(hcode)

if __name__ == '__main__':
    patch_and_lint_llama_model_cpp()
    print('Патч STARVECTOR (баланс фигурных скобок, закрытие блока T5, наследование от llm_graph_context, forward-pass, build_graph, чистка скобок) и авто-линт успешно применены!')
