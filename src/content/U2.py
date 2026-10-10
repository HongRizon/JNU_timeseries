# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U2", short="성분 나누기", title="성분 나누기: 분해법", ref="1장 §1.5")

SLIDES = [
    # ------------------------------------------------------------ 1. 단원 첫 화면: 질문 + 표
    slide(
        "성분 나누기: 분해법",
        p("주 자료를 추세 + 계절 + 불규칙으로 나누면 U1에서 본 특징이 성분별로 어떻게 보이나?"),
        p("분해법은 시계열 X<sub>t</sub>를 체계적 성분과 불규칙 성분으로, 곧 추세 m<sub>t</sub>, 계절 s<sub>t</sub>, 불규칙 z<sub>t</sub>로 나눈다. "
          "계절조정된 시계열을 얻을 수 있고 직관적이지만, 계절성분이 매 주기 똑같이 반복된다고 가정하므로 긴 시계열에는 맞지 않을 수 있다. "
          "계절변동의 폭이 수준과 무관하면 가법, 수준에 비례하면 승법을 쓴다."),
        table(
            ["", "가법모형", "승법모형"],
            [
                ["식", "X<sub>t</sub> = m<sub>t</sub> + s<sub>t</sub> + z<sub>t</sub>", "X<sub>t</sub> = m<sub>t</sub> × s<sub>t</sub> × z<sub>t</sub>"],
                ["언제", "계절변동이 수준에 관계없이 일정할 때", "계절변동이 수준에 비례하게 변할 때"],
                ["추세 제거", "X<sub>t</sub> − m̂<sub>t</sub>", "X<sub>t</sub> / m̂<sub>t</sub>"],
                ["불규칙", "X<sub>t</sub> − m̂<sub>t</sub> − ŝ<sub>t</sub>", "X<sub>t</sub> / (m̂<sub>t</sub> ŝ<sub>t</sub>)"],
                ["계절조정", "X<sub>t</sub> − ŝ<sub>t</sub>", "X<sub>t</sub> / ŝ<sub>t</sub>"],
                ["R", "<code>decompose(TRD)</code>", "<code>decompose(TRD, type=\"mult\")</code>"],
            ],
        ),
        ref="1장 p.21–25",
        kind="opener",
    ),

    # ------------------------------------------------------------ 2. 분해 그림
    slide(
        "가법 분해",
        p("분해는 세 단계다. ① 이동평균 등으로 추세 m̂<sub>t</sub>를 추정한다. 월별 자료면 12개월 중심 이동평균 "
          "m̂<sub>t</sub> = (½x<sub>t−6</sub> + x<sub>t−5</sub> + ⋯ + x<sub>t+5</sub> + ½x<sub>t+6</sub>) / 12이고, "
          "주 자료는 <code>freq=7</code>이라 <code>decompose()</code>가 7일 중심 이동평균을 쓴다. "
          "② 추세를 뺀 X<sub>t</sub> − m̂<sub>t</sub>의 요일별 평균으로 ŝ<sub>t</sub>를 구한다. "
          "③ 남은 것이 불규칙 ẑ<sub>t</sub>다."),
        ask("주 자료의 요일 주기의 폭(평일과 주말의 차이)은 수준에 관계없이 일정한가, 수준에 비례하는가? U1의 그림을 떠올려 본다."),
        cell("u2_add", "가법 분해", """
plot(decompose(TRD))
""", gh=640),
        ask("네 그림 observed · trend · seasonal · random은 식의 어느 기호인가?",
            "원자료 X<sub>t</sub>, 추세 m̂<sub>t</sub>, 계절 ŝ<sub>t</sub>, 불규칙 ẑ<sub>t</sub>다. "
            "seasonal은 7일마다 같은 모양이 반복되고(토·일에 낮음), trend는 U1의 주간 평균처럼 증가하다가 감소한다."),
        ref="1장 p.23, p.25",
    ),
    slide(
        "승법 분해",
        p("승법모형은 추세를 빼는 대신 나눈다. X<sub>t</sub> / m̂<sub>t</sub>의 요일별 평균이 ŝ<sub>t</sub>이고, "
          "seasonal 그림의 값은 1을 중심으로 한 비율이다. 불규칙은 X<sub>t</sub> / (m̂<sub>t</sub> ŝ<sub>t</sub>)다."),
        cell("u2_mult", "승법 분해", """
plot(decompose(TRD, type="mult"))
""", gh=640),
        ask("가법의 seasonal과 승법의 seasonal은 무엇이 다른가?",
            "모양은 같지만 단위가 다르다. 가법은 0을 중심으로 더하는 양(거래 횟수)이고, 승법은 1을 중심으로 곱하는 비율이다. 토·일은 1보다 작다."),
        ask("주 자료에는 가법과 승법 중 어느 쪽이 맞나?",
            "승법 쪽이다. 수준이 높았던 2024년 11월 ~ 2025년 3월에는 평일과 주말의 차이가 크고, 수준이 낮아진 뒤에는 작다. "
            "계절변동이 수준에 비례하게 변하면 승법모형이다."),
        ref="1장 p.22, p.25",
    ),

    # ------------------------------------------------------------ 3. 계절조정·추세 제거
    slide(
        "계절조정과 추세 제거",
        p("계절성에 의한 변동이 주된 관심이 아닐 때는 계절변동을 제거한 <b>계절조정</b> 시계열을 본다. "
          "월별 실업률처럼 경제 상황에 따른 비계절 변동이 더 중요한 금융·경제 시계열에 주로 쓴다. "
          "승법모형이면 계절조정은 X<sub>t</sub> / ŝ<sub>t</sub>, 추세 제거는 X<sub>t</sub> / m̂<sub>t</sub>다."),
        cell("u2_adj", "승법 계절조정과 추세 제거", """
d <- decompose(TRD, type="mult")
plot(TRD/d$seasonal, main="계절변동을 제거한 시계열")
plot(TRD/d$trend, main="추세변동을 제거한 시계열")
"""),
        ask("<code>TRD/d$seasonal</code>과 <code>TRD/d$trend</code>는 각각 어느 식인가?",
            "승법 계절조정 X<sub>t</sub> / ŝ<sub>t</sub>와 승법 추세 제거 X<sub>t</sub> / m̂<sub>t</sub>다."),
        ask("계절변동을 제거한 그림에서 무엇이 사라졌나?",
            "7일마다 반복되던 주말의 하락(요일 주기)이 사라지고, 추세와 불규칙 변동이 남는다."),
        more(
            "가법모형으로 같은 계산을 하면",
            p("가법은 나누는 대신 뺀다: 계절조정 X<sub>t</sub> − ŝ<sub>t</sub>, 추세 제거 X<sub>t</sub> − m̂<sub>t</sub>."),
            cell("u2_addadj", "가법 계절조정과 추세 제거", """
d <- decompose(TRD)
plot(TRD - d$seasonal, main="계절변동을 제거한 시계열 (가법)")
plot(TRD - d$trend, main="추세변동을 제거한 시계열 (가법)")
"""),
            ask("승법 셀의 <code>/</code>가 이 셀에서 <code>-</code>로 바뀐 이유는?",
                "가법은 X<sub>t</sub> = m<sub>t</sub> + s<sub>t</sub> + z<sub>t</sub>, 승법은 X<sub>t</sub> = m<sub>t</sub> × s<sub>t</sub> × z<sub>t</sub>라서, "
                "가법에서는 빼고 승법에서는 나눈다."),
        ),
        ref="1장 p.24, p.26",
    ),

    # ------------------------------------------------------------ 4. 정리
    slide(
        "성분 나누기",
        p("분해 그림에서 본 것을 성분별로 적는다."),
        table(
            ["성분", "식의 기호", "주 자료에서 본 것"],
            [
                ["추세", "m̂<sub>t</sub> (trend)", BLANK],
                ["계절", "ŝ<sub>t</sub> (seasonal)", BLANK],
                ["불규칙", "ẑ<sub>t</sub> (random)", BLANK],
                ["가법·승법 중 맞는 쪽과 이유", "", BLANK],
            ],
        ),
        p("분해법은 자료의 구조를 이해하는 데 좋고, 예측에는 제한적이다. 다음 단원은 과거값으로 바로 예측하는 평활법이다."),
        ref="1장 p.21–26",
        kind="wrap",
    ),
]
