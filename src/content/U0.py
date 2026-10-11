# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U0", short="시작", title="시작")

SLIDES = [
    slide(
        "시계열분석 webR 실습",
        raw('<p class="cover-sub">강의 1–5장 · 주 자료 BTCUSDT 일별 거래 횟수 · 대조 자료 QQQ 월말 종가</p>'),
        table(
            ["자료", "내용", "R에서"],
            [
                ["주 자료 TRD",
                 "바이낸스 현물 BTCUSDT 일봉의 거래 횟수(number of trades). 2024년 10월 7일(월) ~ 2025년 10월 5일(일), 364일 = 52주. "
                 "날짜는 UTC 기준(일봉은 한국시간 오전 9시 시작).",
                 "<code>TRD</code> · 일별, 요일 주기 ⇒ <code>freq=7</code>"],
                ["대조 자료 QQQ",
                 "나스닥100 ETF QQQ의 월말 종가. 1999년 4월 ~ 2025년 12월, 321개. 2000년 3월 주식분할 전 값은 2로 나눈 것.",
                 "<code>QQQ</code> · 월별 ⇒ <code>freq=12</code>"],
            ],
        ),
        p("주 자료는 추세, 요일 주기, 변동의 증가가 함께 보이는 자료. 대조 자료는 금융 시계열에 흔한 '확률적 추세'를 같은 도구로 판정해 보는 자료. "
          "U1부터 U8까지 주 자료로 한 바퀴, 대조 자료는 U1·U4·U5·U6·U7에서 같은 도구로 비교."),
        h3("하는 법"),
        ul(
            "<b>R 준비</b>: 페이지를 열면 브라우저 안에서 자동 (10–30초, 인터넷 필요). 오른쪽 위가 <b>R 준비됨</b>이 되면 실행 가능.",
            "<b>셀 전체 실행</b>: <b>▶ 실행</b> 단추 또는 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>Enter</kbd>. 결과와 그림은 오른쪽 결과 칸에.",
            "<b>부분 실행</b>: 코드 상자에서 드래그한 부분 또는 커서가 있는 줄만 <kbd>Ctrl</kbd>+<kbd>Enter</kbd> (RStudio와 같음).",
            "<b>바꿔 보기</b>: <code># 바꿔 보기</code> 줄의 값만 바꿔 다시 실행. ↺ 단추는 처음 코드로 되돌리기.",
            "<b>자료</b>: <code>TRD</code>와 <code>QQQ</code>는 미리 읽혀 있음. 앞 셀이 만든 변수를 쓰는 셀은 앞 셀 자동 실행.",
            "<b>넘기기</b>: 아래의 ◀ ▶, 키보드 ← →, 위의 단원 단추. 자세한 사용법과 자료 파일은 위의 <b>도움말</b>.",
        ),
        raw('<div class="actions"><button type="button" class="btn" data-action="preload">R 패키지 미리 받기 (tseries · forecast · nlme)</button>'
            '<span class="actions-note" data-preload-status>U4·U6·U8에서 사용. 지금 받아 두면 그때 기다림 없음.</span></div>'),
        kind="cover",
    ),
]
