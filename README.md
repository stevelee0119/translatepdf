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

## 웹 인터페이스 실행

로컬 웹 브라우저에서 사용할 수 있는 간단한 프론트엔드를 제공합니다.

```bash
python app.py
```

브라우저에서 열리는 페이지에서:
- 디바이스에서 PDF 파일 업로드
- Google Drive 공유 링크 입력
- 변환 진행 상황을 확인
- 변환 완료된 PDF를 다운로드

## 옵션

- `--service`: 번역 서비스 지정 (기본값: `google`)
- `--lang-in`: 원본 언어 코드 (기본값: `en`)
- `--lang-out`: 목표 언어 코드 (기본값: `ko`)
- `--threads`: 번역 스레드 수 (기본값: `4`)

## 참고

이 구현은 PDFMathTranslate의 `pdf2zh` 라이브러리를 활용하므로, 가능한 한 원본 PDF의 페이지, 레이아웃, 수식, 표 등을 동일하게 유지하면서 번역을 수행합니다.

## GitHub 온라인 사용

이 저장소는 GitHub Codespaces 및 Docker 기반 온라인 실행을 지원하도록 구성되어 있습니다.

### GitHub Codespaces

1. GitHub 저장소에서 `Code > Codespaces`로 이동합니다.
2. `main` 브랜치를 선택해 Codespace를 엽니다.
3. Codespace가 열리면 자동으로 `7860` 포트를 전달하도록 설정됩니다.
4. `app.py`를 실행하려면 Codespace 터미널에서:

```bash
python app.py
```

5. 브라우저에서 표시된 `http://0.0.0.0:7860` 또는 Codespaces 포트 프록시 URL로 접속합니다.

### Docker로 실행

로컬 또는 클라우드 환경에서 Docker로 앱을 실행할 수 있습니다.

```bash
docker build -t translatepdf:latest .
docker run -p 7860:7860 translatepdf:latest
```

### GitHub Actions

GitHub Actions 워크플로가 추가되어, `main` 브랜치에 푸시할 때마다:

- `python-app.yml`: Python 의존성을 설치하고 `app.py` 및 `translate_pdf.py` 문법 검사를 실행합니다.
- `publish-ghcr.yml`: GitHub Container Registry에 Docker 이미지를 빌드하고 푸시합니다.

이미지를 사용할 때는 `ghcr.io/<your-username>/translatepdf:latest`를 참조하세요.
