# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U3", short="바로 예측", title="과거로 바로 예측하기: 평활법", ref="3장 §3.4")

SLIDES = [
    # ------------------------------------------------------------ 1. 단원 첫 화면: 질문 + 표
    slide(
        "과거로 바로 예측하기: 평활법",
        p("주 자료의 과거값들을 가중평균하면 다음 날(2025년 10월 6일)의 거래 횟수는 얼마로 예측되나?"),
        p("평활법은 과거값들의 가중평균으로 변동을 줄여 패턴을 파악하고 미래값을 예측한다. "
          "이동평균법은 최근 m개 값에 같은 가중치를 주고, 지수평활법은 과거로 갈수록 지수적으로 낮은 가중치를 준다. "
          "지수평활법은 추세와 계절성이 없을 때는 단순지수평활법, 있을 때는 Holt-Winters 방법을 쓴다."),
        table(
            ["", "이동평균법", "단순지수평활법", "Holt-Winters 방법"],
            [
                ["과거값의 가중치", "최근 m개에 똑같이 1/m", "과거로 갈수록 지수적으로 감소", "과거로 갈수록 지수적으로 감소"],
                ["쓰는 경우", "추세와 계절성이 없을 때 (가중치가 같아 최근 변화의 반영이 느리다)", "추세와 계절성이 없을 때", "추세와 계절성이 있을 때"],
                ["식",
                 "X̂<sub>t+1</sub> = (X<sub>t</sub> + X<sub>t−1</sub> + ⋯ + X<sub>t−m+1</sub>) / m",
                 "a<sub>t</sub> = αX<sub>t</sub> + (1 − α)a<sub>t−1</sub>",
                 "a<sub>t</sub>, b<sub>t</sub>, s<sub>t</sub>의 갱신식"],
                ["정하는 값", "m", "α", "α, β, γ"],
                ["R", "<code>mean(TRD[(364-m+1):364])</code>",
                 "<code>HoltWinters(TRD, beta=FALSE, gamma=FALSE)</code>",
                 "<code>HoltWinters(TRD, seasonal=\"mult\")</code>"],
            ],
        ),
        ref="3장 p.2–3, p.11–12",
        kind="opener",
    ),

    # ------------------------------------------------------------ 2. 이동평균 예측
    slide(
        "이동평균 예측",
        p("이동평균법은 최근 m개 값의 평균을 다음 값의 예측으로 쓴다: "
          "X̂<sub>t+1</sub> = (X<sub>t</sub> + X<sub>t−1</sub> + ⋯ + X<sub>t−m+1</sub>) / m. "
          "m개의 과거값에 1/m씩 같은 가중치를 준다. "
          "U2의 분해에서 추세 추정에 쓴 것은 앞뒤 값을 함께 쓰는 중심 이동평균이고, 예측에 쓰는 것은 과거값만 쓰는 단측 이동평균이다."),
        p("자료가 364개이므로 t = 364이고, 예측하는 값은 X̂<sub>365</sub>, 곧 2025년 10월 6일(월)의 거래 횟수다. "
          "m = 7은 최근 1주, m = 3은 최근 3일(금·토·일)의 평균이다."),
        cell("u3_ma", "최근 m일 평균으로 다음 날 예측", """
m <- 7                        # 바꿔 보기: m (7 → 3)
TRD[(364-m+1):364]            # X_{t−m+1}, ⋯, X_{t−1}, X_t
mean(TRD[(364-m+1):364])      # X̂_{t+1} = (X_t + X_{t−1} + ⋯ + X_{t−m+1}) / m
"""),
        note("<code>(364-m+1):364</code>는 t − m + 1부터 t까지다 (t = 364). m = 7이면 358:364, 곧 마지막 1주다."),
        more(
            "자료 전체 그림을 다시 보면",
            p("예측에 들어가는 값은 그림 맨 오른쪽 끝의 m개다."),
            cell("u3_plot", "자료 그림", """
plot(TRD, xlab="Time/weeks", ylab="BTC 거래 횟수")
"""),
        ),
        ref="3장 p.2, p.8",
    ),

    # ------------------------------------------------------------ 3. 단순지수평활
    slide(
        "단순지수평활",
        p("단순지수평활법의 모형은 X<sub>t</sub> = 수준<sub>t</sub> + w<sub>t</sub>로, "
          "수준은 시간에 따라 바뀔 수 있지만 한 방향으로 증가하거나 감소하는 체계적인 기울기는 없고 w<sub>t</sub>는 불규칙 성분이다. "
          "t 시점까지의 자료로 구한 수준의 추정치 a<sub>t</sub>는 "
          "a<sub>t</sub> = αX<sub>t</sub> + (1 − α)a<sub>t−1</sub>로 갱신한다 (0 &lt; α &lt; 1, a<sub>1</sub> = X<sub>1</sub>). "
          "α는 예측오차 e<sub>t</sub> = X<sub>t</sub> − a<sub>t−1</sub>의 제곱합 Σ<sub>t=2</sub><sup>n</sup> e<sub>t</sub>²(SSE)가 최소가 되도록 고른다."),
        cell("u3_ses1", "α를 자동으로 고르기", """
trd.hw1 <- HoltWinters(TRD, beta=FALSE, gamma=FALSE)   # 추세·계절성 없이 수준만
trd.hw1
plot(trd.hw1, main="alpha=0.334")
trd.hw1$SSE
"""),
        note("<code>beta=FALSE, gamma=FALSE</code>는 추세(β)와 계절성(γ)을 뺀다는 뜻이다. "
             "출력 첫 줄의 without trend and without seasonal component가 그것이다."),
        note("출력의 alpha가 자동으로 고른 α이고, Coefficients a는 마지막 시점(t = 364)의 수준 추정치 a<sub>364</sub>, 곧 다음 날의 예측값이다. "
             "<code>trd.hw1$SSE</code>는 예측오차 제곱합 Σe<sub>t</sub>²다."),
        note("그림의 검은 선이 자료 X<sub>t</sub>, 빨간 선이 적합선 X̂<sub>t</sub> = a<sub>t−1</sub>이다."),
        ref="3장 p.4, p.6–7, p.9",
    ),
    slide(
        "α를 정해 두기",
        p("갱신식을 풀어 쓰면 a<sub>t</sub> = αX<sub>t</sub> + α(1 − α)X<sub>t−1</sub> + α(1 − α)²X<sub>t−2</sub> + ⋯, "
          "곧 지수가중이동평균(EWMA)이다. 과거 자료일수록 가중치가 지수적으로 줄어든다. "
          "α ≈ 0이면 평활의 효과가 커서 지엽적인 변화에 둔감하고, α ≈ 1이면 평활의 효과가 작아 민감하다. "
          "α를 직접 정해 적합할 수도 있지만, 그 SSE는 제곱합을 최소로 하는 자동 선택의 SSE보다 작을 수 없다."),
        cell("u3_ses2", "α를 정해 두기", """
trd.hw2 <- HoltWinters(TRD, alpha=0.2, beta=FALSE, gamma=FALSE)   # 바꿔 보기: alpha (0.2 → 0.9)
trd.hw2
plot(trd.hw2, main="alpha=0.2")
trd.hw2$SSE
"""),
        note("<code>alpha=0.2</code>는 α를 0.2로 정해 두고 적합한다는 뜻이다. "
             "출력의 alpha: 0.2가 그것이고, Coefficients a는 이 α로 구한 마지막 시점의 수준 추정치다."),
        more(
            "갱신식을 반복문으로 확인하면",
            p("a<sub>t</sub> = αX<sub>t</sub> + (1 − α)a<sub>t−1</sub>, a<sub>1</sub> = X<sub>1</sub>을 "
              "같은 α로 직접 계산해 <code>trd.hw2</code>와 견준다."),
            cell("u3_loop", "갱신식을 반복문으로", """
al <- trd.hw2$alpha                     # α를 trd.hw2와 같게
a <- rep(0, 364)
a[1] <- TRD[1]                          # a_1 = X_1
for (i in 2:364){                       # 자료가 364개
  a[i] <- al*TRD[i] + (1-al)*a[i-1]     # a_t = αX_t + (1 − α)a_{t−1}
}
a[1:5]
trd.hw2$fitted[1:5,]                    # trd.hw2의 xhat(예측값 X̂)·level 앞 5개
a[364]                                  # trd.hw2 출력의 Coefficients a와 비교
"""),
            note("<code>al</code>이 α다. <code>al*TRD[i]</code>가 αX<sub>t</sub>, <code>(1-al)*a[i-1]</code>이 (1 − α)a<sub>t−1</sub>이다."),
            note("<code>a[1:5]</code>는 <code>trd.hw2$fitted</code>의 앞 5행(xhat·level)과 같고, <code>a[364]</code>는 출력의 Coefficients a(2971677)와 같다. "
                 "fitted의 첫 행은 2번째 시점의 예측값 X̂<sub>2</sub> = a<sub>1</sub>이다."),
        ),
        ref="3장 p.5–7, p.10",
    ),

    # ------------------------------------------------------------ 4. Holt-Winters
    slide(
        "Holt-Winters",
        p("추세와 계절성이 있을 때는 수준 a<sub>t</sub>, 추세 b<sub>t</sub>, 계절성 s<sub>t</sub>를 함께 갱신하는 Holt-Winters 방법을 쓴다. "
          "승법모형은 X<sub>t</sub> = (수준<sub>t</sub> + 추세<sub>t</sub>) × 계절성<sub>t</sub> + w<sub>t</sub>이고, 갱신식은 "
          "a<sub>t</sub> = α(X<sub>t</sub> / s<sub>t−p</sub>) + (1 − α)(a<sub>t−1</sub> + b<sub>t−1</sub>), "
          "b<sub>t</sub> = β(a<sub>t</sub> − a<sub>t−1</sub>) + (1 − β)b<sub>t−1</sub>, "
          "s<sub>t</sub> = γ(X<sub>t</sub> / a<sub>t</sub>) + (1 − γ)s<sub>t−p</sub>다 (0 &lt; α, β, γ &lt; 1). "
          "주기 p는 주 자료에서 7이다. "
          "a<sub>t</sub>, b<sub>t</sub>, s<sub>t</sub>는 t 시점까지의 자료로 구한 X<sub>t+1</sub>의 수준(level)·추세(slope)·계절성(seasonal)의 추정치다."),
        cell("u3_hw", "승법 Holt-Winters", """
trd.hw <- HoltWinters(TRD, seasonal="mult")
trd.hw
plot(trd.hw)
"""),
        note("출력의 Coefficients a, b, s1–s7은 마지막 시점(t = 364)의 수준·추세·계절성 추정치다. "
             "s1–s7은 다음 7일(월–일)의 예측에 쓰인다."),
        note("e+06은 × 10<sup>6</sup>, e-01은 × 10<sup>−1</sup>이다: 6.725979e+06은 약 673만, 3.281491e-01은 약 0.328이다."),
        more(
            "가법모형으로 같은 적합을 하면",
            p("가법모형은 X<sub>t</sub> = 수준<sub>t</sub> + 추세<sub>t</sub> + 계절성<sub>t</sub> + w<sub>t</sub>다. "
              "수준과 계절성의 갱신식은 나누는 대신 뺀다: "
              "a<sub>t</sub> = α(X<sub>t</sub> − s<sub>t−p</sub>) + (1 − α)(a<sub>t−1</sub> + b<sub>t−1</sub>), "
              "s<sub>t</sub> = γ(X<sub>t</sub> − a<sub>t</sub>) + (1 − γ)s<sub>t−p</sub>. b<sub>t</sub>는 승법과 같다."),
            cell("u3_hwadd", "가법 Holt-Winters", """
trd.hw.add <- HoltWinters(TRD, seasonal="additive")
trd.hw.add
plot(trd.hw.add)
trd.hw$SSE       # 승법
trd.hw.add$SSE   # 가법
"""),
            note("승법 셀과 다른 곳은 <code>seasonal</code> 인자뿐이다. 가법은 <code>\"additive\"</code>(기본값), 승법은 <code>\"mult\"</code>다."),
        ),
        ref="3장 p.11–13",
    ),
    slide(
        "적합된 성분",
        p("<code>fitted</code>에는 시점마다 xhat(예측값 X̂), level, trend, season이 들어 있다. "
          "네 그림을 나란히 보면 수준·추세·계절성이 각각 어떻게 갱신되어 왔는지 보인다. 마지막 행은 t = 364의 값이다."),
        cell("u3_hwfit", "적합된 성분", """
plot(trd.hw$fitted)      # xhat(예측값 X̂)·level·trend·season
tail(trd.hw$fitted, 1)   # 마지막 행 (t = 364)
""", gh=640),
        note("네 그림은 위에서부터 xhat(예측값 X̂), level(a), trend(b), season(s)이다. 승법이라 season은 1을 중심으로 한 비율이다."),
        note("마지막 행의 xhat은 363일까지의 자료로 구한 X̂<sub>364</sub>이고, level·trend·season은 그 예측에 쓰인 a<sub>363</sub>·b<sub>363</sub>·s<sub>357</sub>이다. "
             "Coefficients a는 364일째 값까지 넣어 갱신한 a<sub>364</sub>라 이 행의 level(a<sub>363</sub>)과 다르다."),
        ref="3장 p.14",
    ),
    slide(
        "2주 앞 예측",
        p("<code>predict()</code>는 마지막 시점의 a, b, s로 <code>n.ahead</code> 시점 앞까지 예측한다. "
          "주 자료는 하루가 한 시점이라 2*7은 다음 2주다."),
        cell("u3_hwpred", "2주 앞 예측", """
trd.predict <- predict(trd.hw, n.ahead=2*7)   # 바꿔 보기: n.ahead (2*7 → 4*7)
trd.predict
ts.plot(TRD, trd.predict, lty=1:2)
"""),
        note("출력의 fit 14개는 월–일 순으로 두 주다 (Start = c(53, 1)은 53주째 월요일). "
             "<code>ts.plot(…, lty=1:2)</code>는 자료를 실선, 예측을 점선으로 한 그림에 그린다."),
        note("예측에는 마지막 시점의 s1–s7이 7일마다 되풀이해 쓰이므로 예측선에도 주말의 하락이 남는다."),
        ref="3장 p.15",
    ),

    # ------------------------------------------------------------ 5. 정리
    slide(
        "바로 예측하기",
        p("평활법의 원리와 주 자료에서 확인한 것."),
        ul(
            "평활법은 새 자료가 들어올 때마다 갱신되므로 순차적 분석과 단기 예측에 강하고, U2의 분해법은 구조 이해가 목적이라 예측에는 제한적이다.",
            "이동평균법은 최근 m개 값에 1/m씩 같은 가중치를 주므로, m에 따라 어떤 값이 들어가느냐로 예측이 바뀐다. "
            "주 자료는 m = 7(마지막 1주)이면 약 314만, m = 3(금·토·일)이면 약 321만으로, 금요일(약 425만)과 평소보다 큰 일요일(약 369만)이 들어간 m = 3 쪽이 조금 더 크다.",
            "단순지수평활은 추세와 계절성이 없을 때 쓰고, α는 예측오차 제곱합 SSE가 최소가 되도록 자동으로 고른다. "
            "주 자료는 α ≈ 0.334, SSE ≈ 1.197 × 10<sup>15</sup>이고 적합선이 요일 주기의 오르내림을 절반쯤 따라가지만, 추세와 요일 주기가 있어 맞는 방법은 Holt-Winters다.",
            "α ≈ 0이면 지엽적인 변화에 둔감하고, α ≈ 1이면 적합선이 자료의 오르내림을 거의 그대로 따라간다. "
            "직접 정한 α의 SSE는 자동 선택보다 작을 수 없다: 주 자료는 α = 0.2에서 약 1.223 × 10<sup>15</sup>, α = 0.9에서 약 1.309 × 10<sup>15</sup>다.",
            "Holt-Winters는 수준 a<sub>t</sub>, 추세 b<sub>t</sub>, 계절성 s<sub>t</sub>를 함께 갱신하고 마지막 시점의 추정치로 예측하므로, 예측선에도 요일 주기가 남는다. "
            "주 자료의 승법 적합은 토(s6 ≈ 0.33)·일(s7 ≈ 0.46)이 평일(약 0.80–0.86)보다 훨씬 작아 주말의 하락이 계절성에 들어 있다.",
            "적합된 성분은 시점마다 갱신된 추정치다. 주 자료는 level이 원자료의 수준을 따라 오르내리고(6주째와 22주째 전후가 높다), "
            "trend는 거래 횟수에 비해 아주 작아 0 근처에 머문다.",
            "예측의 수준은 마지막 시점의 수준 추정치 a가 정한다. "
            "주 자료는 마지막 일요일(약 369만)이 다른 일요일(최근 20주 중앙값 약 145만)보다 훨씬 커서 a가 약 497만에서 약 673만으로 올랐고, "
            "다음 2주 평일 예측(약 544만–596만)도 마지막 주 평일보다 높다.",
            "요일 주기의 폭이 수준에 비례하는 주 자료에는 U2에서 본 대로 승법이 맞다. "
            "SSE도 승법 약 6.85 × 10<sup>14</sup>, 가법 약 7.25 × 10<sup>14</sup>로 승법 쪽이 작다.",
        ),
        p("평활법은 다음 값을 바로 내놓지만 값들 사이의 관계는 말하지 않으므로, 다음 단원은 그 관계를 재는 자기상관이다."),
        ref="3장 p.16",
        kind="wrap",
    ),
]
