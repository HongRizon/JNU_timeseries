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
        ask("m = 7(최근 1주)과 m = 3(금·토·일)의 예측값 중 어느 쪽이 클까?"),
        cell("u3_ma", "최근 m일 평균으로 다음 날 예측", """
m <- 7                        # 바꿔 보기: m (7 → 3)
TRD[(364-m+1):364]            # X_{t−m+1}, ⋯, X_{t−1}, X_t
mean(TRD[(364-m+1):364])      # X̂_{t+1} = (X_t + X_{t−1} + ⋯ + X_{t−m+1}) / m
"""),
        ask("<code>(364-m+1):364</code>는 식의 어느 부분인가?",
            "t − m + 1부터 t까지다 (t = 364). m = 7이면 358:364, 곧 마지막 1주다."),
        ask("m을 7에서 3으로 바꾸면 예측값이 달라지는가?",
            "달라진다. 가중치는 m개 모두 1/m로 같아서, 어떤 값이 평균에 들어가느냐에 따라 예측이 바뀐다. "
            "m = 7이면 약 314만, m = 3이면 약 321만이다. "
            "마지막 3일에는 주말이 들어 있지만, 금요일(약 425만)과 평소보다 큰 일요일(약 369만)이 들어가 m = 3 쪽이 조금 더 크다."),
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
        p("단순지수평활법의 모형은 X<sub>t</sub> = 수준<sub>t</sub> + w<sub>t</sub>다. "
          "수준<sub>t</sub>는 U2 분해법의 추세 m<sub>t</sub>에 해당하고, w<sub>t</sub>는 불규칙 성분이다. "
          "수준은 시간에 따라 바뀔 수 있지만 한 방향으로 증가하거나 감소하는 체계적인 기울기는 없다. "
          "t 시점까지의 자료로 구한 X<sub>t+1</sub> 수준의 추정치 a<sub>t</sub>는 "
          "a<sub>t</sub> = αX<sub>t</sub> + (1 − α)a<sub>t−1</sub>로 갱신한다 (0 &lt; α &lt; 1, a<sub>1</sub> = X<sub>1</sub>). "
          "α는 예측오차 e<sub>t</sub> = X<sub>t</sub> − a<sub>t−1</sub>의 제곱합 Σ<sub>t=2</sub><sup>n</sup> e<sub>t</sub>²가 최소가 되도록 고른다. "
          "<code>HoltWinters()</code>는 이 제곱합을 SSE로 출력한다."),
        ask("요일 주기가 뚜렷한 주 자료에서 자동으로 고른 α는 0과 1 중 어디에 가까울까?"),
        cell("u3_ses1", "α를 자동으로 고르기", """
trd.hw1 <- HoltWinters(TRD, beta=FALSE, gamma=FALSE)   # 추세·계절성 없이 수준만
trd.hw1
plot(trd.hw1, main="alpha=0.334")
trd.hw1$SSE
"""),
        note("<code>beta=FALSE, gamma=FALSE</code>는 추세(β)와 계절성(γ)을 뺀다는 뜻이다. "
             "출력 첫 줄의 without trend and without seasonal component가 그것이다."),
        ask("자동으로 고른 α는 얼마이고, 적합선(빨간 선)은 자료를 얼마나 따라가나?",
            "약 0.334다. 적합선은 요일 주기의 오르내림을 절반쯤 따라간다. SSE는 약 1.197 × 10<sup>15</sup>다."),
        ask("주 자료에 단순지수평활이 맞는 방법인가?",
            "아니다. 단순지수평활은 추세와 계절성이 없을 때 쓴다. 주 자료에는 추세와 요일 주기가 있으므로 맞는 방법은 Holt-Winters다."),
        ref="3장 p.4, p.6–7, p.9",
    ),
    slide(
        "α를 정해 두기",
        p("갱신식을 풀어 쓰면 a<sub>t</sub> = αX<sub>t</sub> + α(1 − α)X<sub>t−1</sub> + α(1 − α)²X<sub>t−2</sub> + ⋯, "
          "곧 지수가중이동평균(EWMA)이다. 과거 자료일수록 가중치가 지수적으로 줄어든다. "
          "α ≈ 0이면 평활의 효과가 커서 지엽적인 변화에 둔감하고, α ≈ 1이면 평활의 효과가 작아 민감하다. "
          "α를 직접 정해 적합하고 SSE를 자동 선택과 견준다."),
        ask("α = 0.2의 SSE는 자동으로 고른 α의 SSE보다 작을까?"),
        cell("u3_ses2", "α를 정해 두기", """
trd.hw2 <- HoltWinters(TRD, alpha=0.2, beta=FALSE, gamma=FALSE)   # 바꿔 보기: alpha (0.2 → 0.9)
trd.hw2
plot(trd.hw2, main="alpha=0.2")
trd.hw2$SSE
"""),
        ask("α = 0.2의 SSE는 자동으로 고른 α의 SSE보다 작은가?",
            "크다. α = 0.2의 SSE는 약 1.223 × 10<sup>15</sup>, 자동으로 고른 α ≈ 0.334의 SSE는 약 1.197 × 10<sup>15</sup>다. "
            "α는 이 제곱합이 최소가 되도록 고르기 때문에 자동 선택보다 작을 수 없다."),
        ask("<code>alpha</code>를 0.9로 바꾸면 적합선은 어떻게 달라지나?",
            "지엽적인 변화에 더 민감해져 적합선이 자료의 오르내림을 거의 그대로 따라간다. α ≈ 1이면 평활의 효과가 작다. "
            "SSE는 약 1.309 × 10<sup>15</sup>로 더 커진다."),
        more(
            "갱신식을 반복문으로 확인하면",
            p("a<sub>t</sub> = αX<sub>t</sub> + (1 − α)a<sub>t−1</sub>, a<sub>1</sub> = X<sub>1</sub>을 "
              "<code>trd.hw2</code>와 같은 α로 직접 계산해 <code>trd.hw2</code>와 견준다."),
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
            ask("반복문으로 구한 a<sub>t</sub>가 <code>HoltWinters()</code>의 결과와 같은가?",
                "같다. <code>a[1:5]</code>와 <code>trd.hw2$fitted</code>의 앞 5개(xhat·level)가 같고, "
                "<code>a[364]</code>는 출력의 Coefficients a(2971677)와 같다. "
                "fitted의 첫 행은 2번째 시점의 예측값이고 그 값이 a<sub>1</sub>이다. "
                "a<sub>t</sub>는 t 시점까지의 자료로 구한 X<sub>t+1</sub> 수준의 추정치이기 때문이다."),
            ask("<code>al*TRD[i] + (1-al)*a[i-1]</code>은 식의 어느 부분인가?",
                "<code>al</code>이 α다. <code>al*TRD[i]</code>가 αX<sub>t</sub>, <code>(1-al)*a[i-1]</code>이 (1 − α)a<sub>t−1</sub>이다."),
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
        ask("단순지수평활과 달리 적합선이 요일 주기를 따라갈까?"),
        cell("u3_hw", "승법 Holt-Winters", """
trd.hw <- HoltWinters(TRD, seasonal="mult")
trd.hw
plot(trd.hw)
"""),
        ask("출력의 Coefficients a, b, s1–s7은 무엇인가?",
            "마지막 시점(t = 364)의 수준·추세·계절성 추정치다. 6.725979e+06은 약 673만, 3.281491e-01은 약 0.328이다. "
            "s1–s7은 다음 7일(월–일)의 예측에 쓰이는 계절성 추정치 s다. "
            "토(s6 ≈ 0.33)·일(s7 ≈ 0.46)이 평일(약 0.80–0.86)보다 훨씬 작아, 주말의 하락이 여기에 들어 있다."),
        ref="3장 p.11–13",
    ),
    slide(
        "적합된 성분",
        p("<code>fitted</code>에는 시점마다 xhat(예측값 X̂), level, trend, season이 들어 있다. "
          "네 그림을 겹쳐 보면 수준·추세·계절성이 각각 어떻게 갱신되어 왔는지 보인다. 마지막 행은 t = 364의 값이다."),
        cell("u3_hwfit", "적합된 성분", """
plot(trd.hw$fitted)      # xhat(예측값 X̂)·level·trend·season
tail(trd.hw$fitted, 1)   # 마지막 행 (t = 364)
""", gh=640),
        ask("level, trend, season 그림은 각각 어떻게 움직이나?",
            "level은 원자료의 수준을 따라 오르내리고(6주째 전후가 높다), trend는 거래 횟수에 비해 아주 작은 값이라 거의 0 근처에 머문다. "
            "season은 7일마다 같은 모양이 반복되는 비율이고 토·일이 1보다 훨씬 작다."),
        ref="3장 p.14",
    ),
    slide(
        "2주 앞 예측",
        p("<code>predict()</code>는 마지막 시점의 a, b, s로 <code>n.ahead</code> 시점 앞까지 예측한다. "
          "주 자료는 하루가 한 시점이라 2*7은 다음 2주다."),
        ask("다음 2주의 예측값은 마지막 주의 값과 비슷할까?"),
        cell("u3_hwpred", "2주 앞 예측", """
trd.predict <- predict(trd.hw, n.ahead=2*7)   # 바꿔 보기: n.ahead (2*7 → 4*7)
trd.predict
ts.plot(TRD, trd.predict, lty=1:2)
"""),
        ask("다음 2주의 예측값은 마지막 주의 값과 비슷한가?",
            "평일 예측(약 544만–596만)이 마지막 주 평일(약 244만–425만)보다 높다. "
            "마지막 날(2025년 10월 5일 일요일, 약 369만)이 다른 일요일(최근 20주 중앙값 약 145만)보다 훨씬 커서, "
            "수준의 추정치 a가 약 497만(<code>trd.hw$fitted</code> 마지막 행의 level)에서 약 673만(Coefficients a)으로 올라갔기 때문이다. "
            "승법모형의 수준 갱신식 a<sub>t</sub> = α(X<sub>t</sub> / s<sub>t−p</sub>) + (1 − α)(a<sub>t−1</sub> + b<sub>t−1</sub>)에서 "
            "갱신에 쓰인 일요일의 계절성 추정치 s<sub>t−7</sub>이 약 0.42(같은 행의 season)로 작아, 369만이 수준으로는 약 878만으로 들어갔다 (α ≈ 0.46). "
            "일요일 값들은 U1의 같은 요일만 뽑기 셀에서 요일을 7로 바꾸면 볼 수 있다."),
        ask("예측선에 요일 주기가 남아 있나?",
            "남아 있다. 계절성 s<sub>t</sub>의 추정치가 7일마다 반복되어 예측에도 주말의 하락이 나온다."),
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
            ask("승법 셀(<code>trd.hw</code>)과 다른 곳은 어디인가?",
                "<code>seasonal</code> 인자다. 가법은 <code>\"additive\"</code>(기본값), 승법은 <code>\"mult\"</code>다. "
                "요일 주기의 폭이 수준에 비례하는 주 자료에는 U2에서 본 대로 승법이 맞다. "
                "SSE도 승법이 약 6.85 × 10<sup>14</sup>, 가법이 약 7.25 × 10<sup>14</sup>로 승법 쪽이 작다."),
        ),
        ref="3장 p.11, p.15",
    ),

    # ------------------------------------------------------------ 5. 정리
    slide(
        "바로 예측하기",
        p("평활법은 예측이 목적이고, U2의 분해법은 구조 이해가 목적이다. 주 자료에서 본 것을 마지막 행에 적는다."),
        table(
            ["", "평활법", "분해법"],
            [
                ["하는 일", "변동성을 줄여 패턴을 파악하고 미래값을 예측한다", "추세·계절성·불규칙성을 분리해 각 성분을 분석하고 이해한다"],
                ["쓰임", "새 자료가 들어올 때마다 갱신하므로 실시간·순차적 분석에 유리하고, 단기 예측에 강하다", "주로 자료의 구조를 설명하거나 장기 패턴을 분석한다"],
                ["예측", "강점", "평활법보다 제한적"],
                ["주 자료에서", BLANK, BLANK],
            ],
        ),
        p("평활법은 다음 값을 바로 내놓지만, 값들 사이의 관계가 어떤지는 말하지 않는다. 다음 단원은 그 관계를 재는 자기상관이다."),
        ref="3장 p.16",
        kind="wrap",
    ),
]
