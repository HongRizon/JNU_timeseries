# JNU_timeseries

시계열분석 강의 1–5장을 브라우저 안의 R(webR)로 따라 하는 실습 교재. `timeseries_webr.html` 파일 하나를 열면 된다 (인터넷 필요).

- 주 자료 `TRD`: BTCUSDT 일별 거래 횟수 (2024-10-07 ~ 2025-10-05, 52주)
- 대조 자료 `QQQ`: 나스닥100 ETF QQQ 월말 종가 (1999-04 ~ 2025-12)

## 고치기

`timeseries_webr.html`은 생성 파일이다. 직접 고치지 말고 `src/`를 고친 뒤 다시 만든다.

```
python3 src/build.py --check      # 규칙 검사
python3 src/build.py              # timeseries_webr.html 생성
```

| 위치 | 내용 |
|---|---|
| `src/content/U0.py … U8.py` | 화면 내용 (글·표·질문·R 셀). 쓰는 법은 `src/CONTENT_GUIDE.md` |
| `src/dsl.py` | 내용 파일에서 쓰는 함수 |
| `src/build.py` | 생성기. 셀의 변수 의존을 분석해 '앞 셀'을 자동 연결하고 규칙을 검사한다 |
| `src/style.css`, `src/runtime.js` | 모양과 동작 |
| `src/run.R`, `src/setup.R` | 셀 실행 함수, R 준비 때 자료를 읽는 코드 |
| `src/help.html` | 도움말 창 |
| `src/data/` | 자료 파일 (페이지 안에 내장된다) |
| `src/tools/runcells.mjs` | 생성된 페이지의 모든 셀을 Node의 webR에서 실행해 오류를 찾는다 (`npm install webr@0.6.0` 필요) |
