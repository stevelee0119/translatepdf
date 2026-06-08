# translatepdf

이 저장소는 영어로 작성된 PDF 논문을 한국어로 번역하면서 페이지 수와 레이아웃을 최대한 유지하는 방법을 제공합니다.

## 🌐 온라인 사용 (GitHub Pages)

GitHub Pages에서 바로 실행 가능합니다:
👉 **[https://stevelee0119.github.io/translatepdf/](https://stevelee0119.github.io/translatepdf/)**

> **주의**: GitHub Pages는 프론트엔드만 호스팅합니다. 번역 기능을 사용하려면 백엔드 API 서버가 필요합니다.
> - **로컬 개발**: 아래의 "로컬 실행" 섹션 참고
> - **클라우드 배포**: Render, Railway, Heroku 등의 서비스에 배포 가능

## 구현 방법

이 프로젝트는 GitHub의 [PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate) 를 참고하여, `pdf2zh` 패키지를 사용해 PDF 내용을 번역하고 원본 형식을 보존합니다.

## 🚀 로컬 실행

### 1. 환경 설정

Python 3.11 또는 3.12 필요:

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Flask API 서버 실행

```bash
python api_server.py
```

그러면 `http://localhost:7860`에서 웹 인터페이스에 접속할 수 있습니다.

### 3. 명령줄 도구로 사용

```bash
python translate_pdf.py input.pdf output_dir
```

예시:
```bash
python translate_pdf.py paper_en.pdf translated
```

결과 파일:
- `translated/paper_en-mono.pdf`

## 🐳 Docker로 실행

```bash
docker build -t translatepdf .
docker run -p 7860:7860 translatepdf
```

## ☁️ 클라우드 배포

### Render에 배포 (권장)

1. [render.com](https://render.com)에 가입
2. 새 Web Service 생성
3. GitHub 저장소 연결
4. 다음 설정으로 배포:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python api_server.py`
   - **Port**: 7860

5. 배포 후 API_BASE를 `docs/index.html`에서 업데이트:
   ```javascript
   const API_BASE = 'https://your-render-app.onrender.com';
   ```

### Railway에 배포

1. [railway.app](https://railway.app)에 가입
2. GitHub 저장소 연결
3. 환경 변수 설정:
   - `PORT=7860`
   - `FLASK_ENV=production`
4. Deploy

## 📋 API 엔드포인트

### POST /api/translate
PDF 파일 번역

**파라미터:**
- `file`: PDF 파일 (선택, gdrive_url 대신 사용 가능)
- `gdrive_url`: Google Drive 공유 링크 (선택, file 대신 사용 가능)
- `service`: 번역 서비스 (기본값: google)
- `lang_in`: 원본 언어 코드 (기본값: en)
- `lang_out`: 목표 언어 코드 (기본값: ko)
- `threads`: 번역 스레드 수 (기본값: 4)

**응답:**
```json
{
  "task_id": "uuid",
  "filename": "paper-mono.pdf",
  "status": "completed"
}
```

### GET /download/<task_id>
번역된 PDF 다운로드

### GET /health
서버 상태 확인

## 📚 사용 예제

### HTML 폼에서 API 호출

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('lang_in', 'en');
formData.append('lang_out', 'ko');

const response = await fetch('http://localhost:7860/api/translate', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
// task_id로 다운로드: /download/{task_id}
```

## 🔧 트러블슈팅

### 1. "모델 로딩 중 오류"
ONNX 모델을 처음 사용할 때 다운로드됩니다. 인터넷 연결 확인 후 재시도하세요.

### 2. "Google Drive 링크 오류"
Google Drive 파일이 "공개" 또는 "링크 있는 사용자"로 공유되어야 합니다.

### 3. "대용량 파일 처리"
클라우드 배포 시 타임아웃이 발생할 수 있습니다.
- 로컬에서 먼저 테스트하세요
- 파일을 분할하여 처리하세요

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

[PDFMathTranslate](https://github.com/PDFMathTranslate/PDFMathTranslate) 프로젝트에 영감을 받았습니다.


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
