#!/usr/bin/env python3
import re
import tempfile
from pathlib import Path
from typing import Optional

import gradio as gr
import requests
from pdf2zh.doclayout import OnnxModel
from pdf2zh.high_level import translate


def download_google_drive(url: str) -> Path:
    if not url:
        raise ValueError("Google Drive 링크가 비어 있습니다.")

    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if not match:
        match = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("유효한 Google Drive 공유 링크를 입력하세요.")

    file_id = match.group(1)
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    session = requests.Session()
    response = session.get(download_url, stream=True)
    token = None
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            token = value
            break

    if token:
        download_url = f"https://drive.google.com/uc?export=download&confirm={token}&id={file_id}"
        response = session.get(download_url, stream=True)

    temp_dir = Path(tempfile.gettempdir()) / "translatepdf"
    temp_dir.mkdir(parents=True, exist_ok=True)
    target_path = temp_dir / f"google_drive_{file_id}.pdf"

    with open(target_path, "wb") as fd:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                fd.write(chunk)

    return target_path


def resolve_input_file(file_input, gdrive_url: str) -> Path:
    if file_input:
        if isinstance(file_input, str):
            return Path(file_input)
        if hasattr(file_input, "name"):
            return Path(file_input.name)
        if isinstance(file_input, dict) and "name" in file_input:
            return Path(file_input["name"])
        raise ValueError("업로드된 파일을 해석할 수 없습니다.")

    if gdrive_url:
        return download_google_drive(gdrive_url)

    raise ValueError("디바이스 업로드 또는 Google Drive 링크 중 하나를 입력하세요.")


def translate_pdf_file(
    file_input,
    gdrive_url: str,
    service: str,
    lang_in: str,
    lang_out: str,
    threads: int,
    progress=gr.Progress(),
):
    input_pdf = resolve_input_file(file_input, gdrive_url)
    output_dir = Path(tempfile.gettempdir()) / "translatepdf_output"
    output_dir.mkdir(parents=True, exist_ok=True)

    progress(0.0, desc="모델 로딩 중...")
    model = OnnxModel.load_onnx()
    progress(0.05, desc="실행 준비 중...")

    def progress_callback(progress_bar):
        try:
            current = getattr(progress_bar, "n", 0)
            total = getattr(progress_bar, "total", 1)
            ratio = float(current) / float(total) if total else 0.0
            progress(min(max(ratio, 0.0), 1.0), desc=f"번역 진행 중: {current}/{total}")
        except Exception:
            pass

    result_files = translate(
        [str(input_pdf)],
        output=str(output_dir),
        lang_in=lang_in,
        lang_out=lang_out,
        service=service,
        thread=threads,
        model=model,
        callback=progress_callback,
    )

    translated_pdf = Path(result_files[0][0])
    output_text = f"번역 완료: {translated_pdf.name}"
    return str(translated_pdf), output_text


def build_interface() -> gr.Blocks:
    with gr.Blocks(css=".title {text-align: center; font-size: 40px; font-weight: 800; margin-bottom: 10px;} .subtitle {text-align: center; color: #555; margin-bottom: 30px;} .section {margin-top: 20px;}") as demo:
        gr.Markdown(
            "<div class='title'>PDF 한영 번역기</div>"
            "<div class='subtitle'>by 법무교육단 — 영어 논문 PDF를 한국어 PDF로 빠르고 깔끔하게 변환합니다.</div>"
        )

        with gr.Row():
            with gr.Column(scale=2):
                file_input = gr.File(
                    label="디바이스에서 PDF 선택",
                    file_count="single",
                    file_types=[".pdf"],
                )
                gdrive_url = gr.Textbox(
                    label="Google Drive PDF 링크",
                    placeholder="https://drive.google.com/file/d/FILE_ID/view?usp=sharing",
                )
                service = gr.Dropdown(
                    label="번역 서비스",
                    choices=["google"],
                    value="google",
                )
                lang_in = gr.Textbox(label="원본 언어 코드", value="en")
                lang_out = gr.Textbox(label="목표 언어 코드", value="ko")
                threads = gr.Slider(label="번역 스레드", minimum=1, maximum=8, step=1, value=4)
                translate_button = gr.Button("번역 시작", variant="primary")

            with gr.Column(scale=1):
                output_file = gr.File(label="번역된 PDF 다운로드")
                output_status = gr.Markdown("### 준비 완료되었습니다. PDF 파일을 업로드하거나 Google Drive 링크를 입력하세요.")

        translate_button.click(
            translate_pdf_file,
            inputs=[file_input, gdrive_url, service, lang_in, lang_out, threads],
            outputs=[output_file, output_status],
            progress=gr.Progress()
        )

    return demo


if __name__ == "__main__":
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
