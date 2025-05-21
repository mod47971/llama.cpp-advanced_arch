import os

TARGET = os.path.join(os.path.dirname(__file__), '../src/llama-model.cpp')

# --- Каркас функции инференса STARVECTOR ---
starvector_impl = '''
// === НАЧАЛО: Инференс STARVECTOR ===
llm_build_starvector::llm_build_starvector(const llama_model & model, const llm_graph_params & params, ggml_cgraph * gf, int mode)
    : llm_graph_context(params), mode(mode) {
    ggml_tensor * cur = nullptr;
    if (mode == 0) {
        // text2svg: вход — токены текста
        // TODO: реализовать forward-pass SVG-трансформера
        // cur = ...
    } else {
        // image2svg: вход — изображение (тензор), затем SVG-трансформер
        // TODO: реализовать vision encoder, затем SVG-трансформер
        // cur = ...
    }
    // TODO: сохранить результат в res->t_logits или аналогично другим архитектурам
    // ggml_build_forward_expand(gf, cur);
}
// === КОНЕЦ: Инференс STARVECTOR ===
'''

# --- Ветка в build_graph ---
build_graph_patch = '''        case LLM_ARCH_©:
            return std::make_shared<llm_build_starvector>(*this, params, gf, /*mode=*/0); // TODO: передавать режим через параметры
'''

def patch_llama_model_cpp():
    with open(TARGET, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. Вставить реализацию llm_build_starvector после последней архитектурной build-функции
    insert_idx = None
    for i, line in enumerate(lines):
        if 'llm_build_starcoder' in line:
            insert_idx = i
    if insert_idx is not None:
        lines.insert(insert_idx + 1, '\n' + starvector_impl + '\n')

    # 2. Добавить ветку в build_graph
    in_build_graph = False
    for i, line in enumerate(lines):
        if 'llama_model::build_graph' in line:
            in_build_graph = True
        if in_build_graph and 'switch (arch)' in line:
            # Найти место после switch (arch) {
            for j in range(i+1, len(lines)):
                if 'default:' in lines[j]:
                    lines.insert(j, build_graph_patch)
                    break
            break

    with open(TARGET, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == '__main__':
    patch_llama_model_cpp()
    print('Патч STARVECTOR успешно применён!')
