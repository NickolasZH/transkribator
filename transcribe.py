"""
Транскрибация аудиозаписей в текст с сохранением результата в .md файл.

Использует faster-whisper (модель Whisper, ускоренная реализация на ctranslate2).
Декодирование аудио выполняется библиотекой PyAV (пакет av), у которой ffmpeg
встроен внутри — отдельно устанавливать системный ffmpeg не требуется.

Использование:
    python transcribe.py records/запись.aac
    python transcribe.py records/запись.aac --model small --language ru
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# На рабочем ноутбуке в системе включён локальный SOCKS-прокси (реестр Windows,
# Internet Settings), а библиотеки для скачивания моделей (httpx/huggingface_hub)
# не умеют работать с SOCKS без дополнительного пакета pysocks. Отключаем прокси
# для этого процесса на Windows — на скачивание моделей с Hugging Face он не нужен.
# На других ОС (например, на Linux-сервере) прокси не трогаем: если он там
# настроен, значит, нужен для доступа в интернет.
if os.name == "nt":
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""
    os.environ["ALL_PROXY"] = ""
    os.environ["NO_PROXY"] = "*"

from faster_whisper import WhisperModel

# Форматы, которые PyAV умеет читать "из коробки" (аудио-контейнеры/кодеки).
SUPPORTED_SUFFIXES = {
    ".aac", ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".wma", ".mp4",
}

# Файл, куда пишется журнал времени транскрибации (в корне проекта, рядом со скриптом).
# Имя совпадает с уже существующей записью в .gitignore.
LOG_PATH = Path(__file__).resolve().parent / "transcribe_log.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Транскрибация аудио в текст (.md)")
    parser.add_argument("audio_path", type=Path, help="путь к аудиофайлу")
    parser.add_argument(
        "--model", default="medium",
        help="размер модели Whisper: tiny/base/small/medium/large-v3 (по умолчанию medium)",
    )
    parser.add_argument(
        "--language", default=None,
        help="код языка (ru, en, ...). По умолчанию — автоопределение",
    )
    parser.add_argument(
        "--device", default="cpu", choices=["cpu", "cuda"],
        help="устройство для вычислений (по умолчанию cpu)",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help="путь к результирующему .md файлу (по умолчанию рядом с аудио)",
    )
    return parser.parse_args()


def transcribe(audio_path: Path, model_size: str, language: str | None, device: str):
    compute_type = "int8" if device == "cpu" else "float16"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(str(audio_path), language=language, vad_filter=True)
    return segments, info


def format_timestamp(seconds: float) -> str:
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def format_duration(seconds: float) -> str:
    """Человекочитаемая длительность процесса транскрибации, например '1м 23.4с'."""
    minutes, sec = divmod(seconds, 60)
    if minutes:
        return f"{int(minutes)}м {sec:04.1f}с"
    return f"{sec:.1f}с"


def log_run(
    audio_path: Path,
    model_size: str,
    device: str,
    audio_duration: float | None,
    elapsed_seconds: float,
) -> None:
    """Дописывает одну строку в transcribe.log с итогами запуска."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    audio_duration_str = format_timestamp(audio_duration) if audio_duration else "?"
    speed = f"{audio_duration / elapsed_seconds:.2f}x" if audio_duration and elapsed_seconds else "?"
    line = (
        f"{timestamp} | файл={audio_path} | модель={model_size} | устройство={device} | "
        f"длительность_аудио={audio_duration_str} | "
        f"время_транскрибации={format_duration(elapsed_seconds)} | скорость={speed}"
    )
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")


def main() -> int:
    args = parse_args()
    audio_path: Path = args.audio_path

    if not audio_path.exists():
        print(f"Файл не найден: {audio_path}")
        return 1

    if audio_path.suffix.lower() not in SUPPORTED_SUFFIXES:
        print(
            f"Предупреждение: расширение {audio_path.suffix} не проверялось явно, "
            "но PyAV может его понять — пробуем."
        )

    output_path = args.output or audio_path.with_suffix(".md")

    print(f"Модель: {args.model}, устройство: {args.device}")
    print(f"Транскрибирую: {audio_path}")

    # Замер времени: faster-whisper отдаёт сегменты "лениво" (генератором), поэтому
    # реальная работа по распознаванию идёт не в model.transcribe(), а в цикле ниже,
    # где мы этот генератор перебираем. Замеряем всё вместе — от загрузки модели
    # до последнего сегмента, — это и есть "время, потраченное на транскрибацию".
    start_time = time.perf_counter()

    segments, info = transcribe(audio_path, args.model, args.language, args.device)

    print(f"Определён язык: {info.language} (уверенность {info.language_probability:.2f})")

    lines = [f"# Транскрипт: {audio_path.name}", ""]
    full_text_parts = []

    for segment in segments:
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        text = segment.text.strip()
        lines.append(f"**[{start} – {end}]** {text}")
        lines.append("")
        full_text_parts.append(text)
        print(f"[{start} – {end}] {text}")

    elapsed_seconds = time.perf_counter() - start_time

    output_path.write_text("\n".join(lines), encoding="utf-8")

    log_run(audio_path, args.model, args.device, getattr(info, "duration", None), elapsed_seconds)

    print(f"\nГотово. Транскрипт сохранён в: {output_path}")
    print(f"Время транскрибации: {format_duration(elapsed_seconds)} (записано в {LOG_PATH.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
