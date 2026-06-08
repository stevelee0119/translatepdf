# translatepdf

이 저장소는 영어로 작성된 PDF 논문을 한국어로 번역하면서 페이지 수와 레이아웃을 최대한 유지하는 방법을 제공합니다.

## 구현 방법

이 프로젝트는 GitHub의 [PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate) 를 참고하여, `pdf2zh` 패키지를 사용해 PDF 내용을 번역하고 원본 형식을 보존합니다.

## 사용법

1. Python 3.11 또는 3.12를 설치합니다.
2. 가상환경 생성 후 의존성을 설치합니다:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. 영어 PDF를 한국어 PDF로 변환합니다:

```bash
python translate_pdf.py input.pdf output_dir
```

4. 변환 결과는 `output_dir` 에 저장됩니다. 기본적으로 `input-mono.pdf` 형식으로 생성됩니다.

## 예시

```bash
python translate_pdf.py paper_en.pdf translated
```

결과 파일:
- `translated/paper_en-mono.pdf`

## 옵션

- `--service`: 번역 서비스 지정 (기본값: `google`)
- `--lang-in`: 원본 언어 코드 (기본값: `en`)
- `--lang-out`: 목표 언어 코드 (기본값: `ko`)
- `--threads`: 번역 스레드 수 (기본값: `4`)

## 참고

이 구현은 PDFMathTranslate의 `pdf2zh` 라이브러리를 활용하므로, 가능한 한 원본 PDF의 페이지, 레이아웃, 수식, 표 등을 동일하게 유지하면서 번역을 수행합니다.
