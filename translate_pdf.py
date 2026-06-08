#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


def translate_pdf(input_pdf: str, output_dir: str, lang_in: str, lang_out: str, service: str, threads: int) -> str:
    try:
        from pdf2zh.high_level import translate
        from pdf2zh.doclayout import OnnxModel
    except ImportError as exc:
        raise RuntimeError(
            "The pdf2zh package is required. Install it with:\n"
            "  pip install pdf2zh==1.9.11\n"
            "or use the provided requirements.txt file."
        ) from exc

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model = OnnxModel.load_onnx()
    result_files = translate(
        [str(input_pdf)],
        output=str(output_path),
        lang_in=lang_in,
        lang_out=lang_out,
        service=service,
        thread=threads,
        model=model,
    )

    if not result_files:
        raise RuntimeError("Translation finished but no output file was generated.")

    translated_pdf = result_files[0][0]
    return translated_pdf


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Translate an English PDF to Korean while preserving layout and page structure."
    )
    parser.add_argument("input_pdf", help="Path to the English source PDF.")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=".",
        help="Directory where the translated PDF will be written.",
    )
    parser.add_argument(
        "--service",
        default="google",
        help="Translation service used by pdf2zh (default: google).",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of translation threads (default: 4).",
    )
    parser.add_argument(
        "--lang-in",
        default="en",
        help="Source language code (default: en).",
    )
    parser.add_argument(
        "--lang-out",
        default="ko",
        help="Target language code (default: ko).",
    )

    args = parser.parse_args()

    input_path = Path(args.input_pdf)
    if not input_path.exists():
        print(f"Input file does not exist: {input_path}", file=sys.stderr)
        return 1

    try:
        output_pdf = translate_pdf(
            input_pdf=str(input_path),
            output_dir=args.output_dir,
            lang_in=args.lang_in,
            lang_out=args.lang_out,
            service=args.service,
            threads=args.threads,
        )
        print(f"Translated PDF created:\n  {output_pdf}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
