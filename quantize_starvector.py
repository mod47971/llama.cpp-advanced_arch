import subprocess
import sys
import os

def quantize_model(llama_cpp_dir, model_dir, output_dir, quantization_types):
    """
    Конвертирует модель из формата Hugging Face в GGUF и квантизирует ее.

    Args:
        llama_cpp_dir (str): Путь к директории репозитория llama.cpp.
        model_dir (str): Путь к директории с моделью Hugging Face (например, star-vector-main/starvector-1b-im2svg).
        output_dir (str): Директория для сохранения выходных GGUF файлов.
        quantization_types (list): Список типов квантизации (например, ["Q4_K_M", "Q8_0"]).
    """

    print(f"Отладочное сообщение: llama_cpp_dir = {llama_cpp_dir}")
    print(f"Отладочное сообщение: model_dir = {model_dir}")
    print(f"Отладочное сообщение: output_dir = {output_dir}")
    print(f"Отладочное сообщение: quantization_types = {quantization_types}")

    os.makedirs(output_dir, exist_ok=True)

    # Шаг 1: Конвертация из Hugging Face в формат, совместимый с llama.cpp (ggml)
    # convert.py создает файл .gguf, который затем можно квантизовать далее.
    # Используем f16 в качестве промежуточного формата для сохранения точности перед квантизацией.
    intermediate_gguf = os.path.join(output_dir, "model_f16.gguf")
    # Исправлено: Путь к скрипту конвертации теперь указывает на convert_hf_to_gguf.py в текущей директории llama.cpp
    convert_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'convert_hf_to_gguf.py'))

    if not os.path.exists(convert_script):
        print(f"Ошибка: Скрипт конвертации не найден: {convert_script}")
        print("Убедитесь, что вы склонировали репозиторий llama.cpp и указали правильный путь.")
        return

    print(f"Начинается конвертация модели из {model_dir} в {intermediate_gguf}...")
    try:
        subprocess.run([
            "py", convert_script,
            model_dir,
            "--outfile", intermediate_gguf,
            "--outtype", "f16" # Используем f16 для промежуточного формата
        ], check=True)
        print("Конвертация успешно завершена.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении конвертации: {e}")
        return

    # Шаг 2: Квантизация GGUF файла
    # Исправлено: Путь к скомпилированной утилите квантизации в директории сборки
    quantize_exe = os.path.join(llama_cpp_dir, 'llama-quantize.exe')

    if not os.path.exists(quantize_exe):
        print(f"Ошибка: Утилита квантизации не найдена: {quantize_exe}")
        print("Убедитесь, что вы скомпилировали llama.cpp (выполнили make в директории llama.cpp).")
        # Попробуем найти утилиту в поддиректориях, если базовая компиляция создает их там
        for root, dirs, files in os.walk(llama_cpp_dir):
            if "llama-quantize.exe" in files:
                quantize_exe = os.path.join(root, "llama-quantize.exe")
                print(f"Найдена утилита квантизации по пути: {quantize_exe}")
                break
        if not os.path.exists(quantize_exe):
             print("Не удалось найти утилиту квантизации.")
             return


    for q_type in quantization_types:
        output_gguf = os.path.join(output_dir, f"starvector_{q_type}.gguf")
        print(f"Начинается квантизация в формат {q_type} -> {output_gguf}...")
        try:
            subprocess.run([
                quantize_exe,
                intermediate_gguf,
                output_gguf,
                q_type
            ], check=True)
            print(f"Квантизация в {q_type} успешно завершена.")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при выполнении квантизации {q_type}: {e}")
            # Продолжаем с другими типами квантизации даже при ошибке одного

    # Опционально: Удалить промежуточный файл f16
    # try:
    #     os.remove(intermediate_gguf)
    #     print(f"Удален промежуточный файл: {intermediate_gguf}")
    # except OSError as e:
    #     print(f"Ошибка при удалении промежуточного файла {intermediate_gguf}: {e}")

if __name__ == "__main__":
    print("=== Запуск quantize_starvector.py: MAIN ===")
    # Здесь укажите пути к вашим директориям
    # ВНИМАНИЕ: Замените эти пути на актуальные на вашем компьютере!
    # Убрана переменная llama_cpp_directory, так как пути к скрипту и утилите теперь разные
    # llama_cpp_directory = "./llama.cpp/build/bin/Release/" # Убедитесь, что llama.cpp находится в корне проекта
    # Исправлено: Путь к модели StarVector relative к директории запуска скрипта
    starvector_model_directory = r"C:\Users\PC\Desktop\_Проекты\starvector\star-vector-main\starvector-1b-im2svg" # Путь к вашей модели
    output_gguf_directory = "./quantized_gguf" # Директория для сохранения результатов

    # Выберите типы квантизации. Q4_K_M - один из наиболее распространенных и сбалансированных.
    # Полный список доступен в документации llama.cpp.
    quantization_formats = ["Q4_K_M", "Q8_0"] # Пример: 4-bit и 8-bit квантизация

    # Пропускаем проверку llama_cpp_directory, так как пути к скрипту и утилите проверяются отдельно
    # if not os.path.exists(llama_cpp_directory):
    #     print(f"Ошибка: Директория llama.cpp не найдена по пути: {llama_cpp_directory}")
    #     print("Пожалуйста, склонируйте llama.cpp и обновите переменную llama_cpp_directory в скрипте.")
    # elif not os.path.exists(starvector_model_directory):
    if not os.path.exists(starvector_model_directory):
         print(f"Ошибка: Директория модели StarVector не найдена по пути: {starvector_model_directory}")
         print("Пожалуйста, обновите переменную starvector_model_directory в скрипте.")
         print("=== ВЫХОД: директория модели не найдена ===")
    else:
        # Передаем None вместо llama_cpp_directory, так как пути теперь заданы внутри функции
        llama_cpp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../llama.cpp/build/bin/Release'))
        print(f"DEBUG: llama_cpp_dir = {llama_cpp_dir}")
        quantize_model(
            llama_cpp_dir, # Здесь используется
            starvector_model_directory,
            output_gguf_directory,
            quantization_formats
        ) 