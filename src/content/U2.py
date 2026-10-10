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

    # ------------------------------------------------------------ 2. 가법 분해
    slide(
        "가법 분해",
        p("분해는 세 단계다. ① 이동평균 등으로 추세 m̂<sub>t</sub>를 추정한다. 월별 자료면 12개월 중심 이동평균 "
          "m̂<sub>t</sub> = (½x<sub>t−6</sub> + x<sub>t−5</sub> + ⋯ + x<sub>t+5</sub> + ½x<sub>t+6</sub>) / 12이고, "
          "주 자료는 <code>freq=7</code>이라 <code>decompose()</code>가 7일 중심 이동평균을 쓴다. "
          "② 추세를 뺀 X<sub>t</sub> − m̂<sub>t</sub>의 요일별 평균으로 ŝ<sub>t</sub>를 구한다. "
          "③ 남은 것이 불규칙 ẑ<sub>t</sub>다."),
        cell("u2_add", "가법 분해", """
plot(decompose(TRD))
""", gh=640),
        note("네 그림 observed · trend · seasonal · random은 원자료 X<sub>t</sub>, 추세 m̂<sub>t</sub>, 계절 ŝ<sub>t</sub>, 불규칙 ẑ<sub>t</sub>다."),
        note("trend의 양 끝이 비어 있는 것은 중심 이동평균이 앞뒤 3일을 쓰기 때문이다."),
        ref="1장 p.23, p.25",
    ),

    # ------------------------------------------------------------ 3. 승법 분해
    slide(
        "승법 분해",
        p("승법모형은 추세를 빼는 대신 나눈다. X<sub>t</sub> / m̂<sub>t</sub>의 요일별 평균이 ŝ<sub>t</sub>이고, "
          "불규칙은 X<sub>t</sub> / (m̂<sub>t</sub> ŝ<sub>t</sub>)다."),
        cell("u2_mult", "승법 분해", """
plot(decompose(TRD, type="mult"))
""", gh=640),
        note("승법의 seasonal은 1을 중심으로 곱하는 비율이고, 가법의 seasonal은 0을 중심으로 더하는 양(거래 횟수)이다. 모양은 같다."),
        ref="1장 p.22, p.25",
    ),

    # ------------------------------------------------------------ 4. 계절조정·추세 제거
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
        note("<code>d$seasonal</code>이 ŝ<sub>t</sub>, <code>d$trend</code>가 m̂<sub>t</sub>다. "
             "<code>TRD/d$seasonal</code>은 승법 계절조정 X<sub>t</sub> / ŝ<sub>t</sub>, <code>TRD/d$trend</code>는 승법 추세 제거 X<sub>t</sub> / m̂<sub>t</sub>다."),
        more(
            "가법모형으로 같은 계산을 하면",
            p("가법은 나누는 대신 뺀다: 계절조정 X<sub>t</sub> − ŝ<sub>t</sub>, 추세 제거 X<sub>t</sub> − m̂<sub>t</sub>."),
            cell("u2_addadj", "가법 계절조정과 추세 제거", """
d <- decompose(TRD)
plot(TRD - d$seasonal, main="계절변동을 제거한 시계열 (가법)")
plot(TRD - d$trend, main="추세변동을 제거한 시계열 (가법)")
"""),
            note("승법 셀의 <code>/</code>가 여기서는 <code>-</code>다. 가법은 X<sub>t</sub> = m<sub>t</sub> + s<sub>t</sub> + z<sub>t</sub>라서 빼고, 승법은 곱이라서 나눈다."),
        ),
        ref="1장 p.24, p.26",
    ),

    # ------------------------------------------------------------ 5. 정리
    slide(
        "성분 나누기",
        p("분해법의 원리."),
        ul(
            "분해법은 X<sub>t</sub>를 추세 m<sub>t</sub>, 계절 s<sub>t</sub>, 불규칙 z<sub>t</sub>로 나눈다. 추세는 중심 이동평균으로, 계절은 추세를 제거한 값의 주기별 평균으로, 불규칙은 나머지로 구한다.",
            "계절변동의 폭이 수준과 무관하면 가법 X<sub>t</sub> = m<sub>t</sub> + s<sub>t</sub> + z<sub>t</sub>, 수준에 비례하면 승법 X<sub>t</sub> = m<sub>t</sub> × s<sub>t</sub> × z<sub>t</sub>다.",
            "가법은 빼고 승법은 나눈다. 가법의 seasonal은 0을 중심으로 더하는 양, 승법의 seasonal은 1을 중심으로 곱하는 비율이다.",
            "<code>decompose</code> 그림의 trend는 평활된 수준의 움직임, seasonal은 주기마다 똑같이 반복되는 모양, random은 두 성분으로 설명되지 않은 나머지다.",
            "계절조정 시계열(가법 X<sub>t</sub> − ŝ<sub>t</sub>, 승법 X<sub>t</sub> / ŝ<sub>t</sub>)은 계절 변동을 걷어낸 것이라, 계절성이 관심이 아닐 때 수준과 추세를 보는 데 쓴다.",
            "분해법은 계절성분이 매 주기 같다고 가정하므로 구조를 이해하는 데 좋고, 예측에는 제한적이다.",
        ),
        p("다음 단원은 과거값으로 바로 예측하는 평활법이다."),
        ref="1장 p.21–26",
        kind="wrap",
    ),
]
