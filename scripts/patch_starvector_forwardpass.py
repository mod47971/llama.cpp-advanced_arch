import os
import re

TARGET = os.path.join(os.path.dirname(__file__), '../src/llama-model.cpp')

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

def patch_and_lint_llama_model_cpp():
    with open(TARGET, 'r', encoding='utf-8') as f:
        code = f.read()

    # Заменить существующую реализацию llm_build_starvector
    code, n = re.subn(
        r'// === НАЧАЛО: Инференс STARVECTOR ===.*?// === КОНЕЦ: Инференс STARVECTOR ===',
        starvector_impl,
        code,
        flags=re.DOTALL
    )
    if n == 0:
        # Если не найдено — просто вставить перед default: в build_graph
        idx = code.find('default:')
        if idx != -1:
            code = code[:idx] + starvector_impl + '\n' + code[idx:]

    # Базовая авто-правка форматирования (убрать двойные пустые строки)
    code = re.sub(r'\n{3,}', '\n\n', code)
    # Исправить отступы для case LLM_ARCH_STARVECTOR (если нужно)
    code = re.sub(r'(case LLM_ARCH_STARVECTOR:[^\n]*\n)([ \t]*)return', r'\1        return', code)

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.write(code)

if __name__ == '__main__':
    patch_and_lint_llama_model_cpp()
    print('Патч STARVECTOR (forward-pass) и авто-линт успешно применены!')
