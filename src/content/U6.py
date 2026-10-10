# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U6", short="AR 모형화", title="AR 모형화: 3단계와 예측", ref="4장 §4.5–4.6")

SLIDES = [
    # ------------------------------------------------------------ 1. 단원 첫 화면: 질문 + 표
    slide(
        "AR 모형화: 3단계와 예측",
        p("주 자료의 주간 평균에 AR 모형을 어떻게 정하고(식별), 맞추고(추정), 검증하고(진단), 예측하나?"),
        p("모형화는 식별·추정·진단의 세 단계를 거친 뒤, 적합된 모형으로 미래 시점의 값을 예측한다. "
          "식별은 그림·ACF·PACF로 모형과 차수를 잠정적으로 정하고, 추정은 자료로부터 모수를 구하며, 진단은 유의성 검정과 잔차분석으로 모형의 타당성을 판정한다. "
          "답을 아는 모의 AR(2) 자료로 세 단계와 예측을 익힌 뒤, 주 자료의 주간 평균과 QQQ에 적용한다."),
        table(
            ["단계", "하는 일", "보는 것", "R"],
            [
                ["1 식별",
                 "그래프와 통계량을 비교하여 가장 적절한 모형을 잠정적(tentative)으로 정한다. "
                 "모수절약의 원칙: 모수가 많을수록 모형이 복잡하고 추정의 효율이 떨어진다",
                 "시계열 그림, ACF, PACF. AR(p)의 PACF는 시차 p 이후로 절단된다",
                 "<code>acf(X)</code>, <code>pacf(X)</code>"],
                ["2 추정",
                 "관측된 자료로부터 잠정모형의 모수를 추정한다",
                 "AIC로 선택된 차수, 추정 계수 φ̂",
                 "<code>ar(X)</code>, <code>ar(X)$order</code>, <code>ar(X)$ar</code>"],
                ["3 진단",
                 "모수의 유의성 검정과 잔차분석으로 적합된 모형의 타당성을 판정한다. 잔차가 백색잡음이 될 때까지 계속 모형화한다",
                 "검정통계량 φ̂ / se(φ̂), 잔차의 그림·ACF·PACF",
                 "<code>sqrt(ar(X)$asy.var[1,1])</code>, <code>tsdisplay(ar(X)$res)</code>"],
                ["예측",
                 "적합된 모형으로 미래 시점의 값을 예측한다: X̂<sub>t+n</sub> = E(X<sub>t+n</sub> ∣ X<sub>1</sub>, ⋯, X<sub>t</sub>)",
                 "예측값 ± 2 × 표준오차. n이 커지면 예측값은 평균 μ로 수렴한다",
                 "<code>predict(ar(X), n.ahead=10)</code>"],
            ],
        ),
        ref="4장 p.2, p.24–25, p.43",
        kind="opener",
    ),

    # ------------------------------------------------------------ 2. 모의 AR(2): 자료와 식별
    slide(
        "모의 AR(2) 자료 만들기",
        p("답을 아는 모의 자료로 세 단계를 연습한다. X<sub>t</sub> = X<sub>t−1</sub> − 0.25X<sub>t−2</sub> + ε<sub>t</sub>는 AR(2)다. "
          "특성방정식 1 − x + 0.25x² = 0의 해는 x = 2로 절대값이 1보다 크므로 정상시계열이다. "
          "U5의 AR 함수처럼 앞의 두 값으로 다음 값을 만드는 함수를 쓴다."),
        cell("u6_sim", "모의 AR(2) 자료 만들기", """
set.seed(1)     # 모두 같은 자료로 실습하기 위해
AR2 <- function(phi1, phi2, n){
  X <- rep(0, n)
  for (i in 1:(n-2)){
    X[i+2] <- phi1*X[i+1] + phi2*X[i] + rnorm(1)
  }
  X
}
X <- AR2(1, -0.25, 500)      # X_t = X_{t−1} − 0.25X_{t−2} + ε_t
X[1:5]                       # 앞 5개
"""),
        note("<code>phi1*X[i+1] + phi2*X[i] + rnorm(1)</code>은 X<sub>t</sub> = φ<sub>1</sub>X<sub>t−1</sub> + φ<sub>2</sub>X<sub>t−2</sub> + ε<sub>t</sub>다: "
             "<code>phi1*X[i+1]</code>이 φ<sub>1</sub>X<sub>t−1</sub>, <code>phi2*X[i]</code>가 φ<sub>2</sub>X<sub>t−2</sub>, <code>rnorm(1)</code>이 ε<sub>t</sub>다."),
        note("처음 두 값 X<sub>1</sub>, X<sub>2</sub>는 0에서 출발한다."),
        note("<code>set.seed(1)</code>이 있어 누가 돌려도 같은 자료가 나온다. "
             "씨앗을 바꾸면 자료가 달라져 <code>ar()</code>이 고르는 차수도 달라질 수 있다."),
        ref="4장 p.33–34",
    ),
    slide(
        "식별",
        p("시차 h의 <b>부분자기상관함수</b>(PACF) φ<sub>hh</sub>는 "
          "X<sub>t</sub>와 X<sub>t+h</sub> 사이에 있는 값 X<sub>t+1</sub>, ⋯, X<sub>t+h−1</sub>의 영향을 제거한 뒤의 두 값의 상관계수다. "
          "<b>AR(p)의 PACF는 시차 p 이후로 절단</b>되고 ACF는 지수적으로 감소한다. "
          "이것이 AR 모형의 차수를 식별하는 기준이다."),
        cell("u6_ident", "그림, ACF, PACF로 식별", """
plot(X, type="l")
acf(X)
pacf(X)
"""),
        note("ACF·PACF의 점선은 상관이 0일 때 막대가 들어가는 약 95% 범위다. 스무 번에 한 번꼴로 우연히 점선을 넘는 막대가 나올 수 있다."),
        note("PACF의 그림은 시차 1부터 시작하고, ACF의 그림은 늘 1인 시차 0부터 시작한다."),
        ref="4장 p.29–32, p.35",
    ),

    # ------------------------------------------------------------ 3. 추정과 유의성 검정
    slide(
        "추정과 유의성 검정",
        p("추정은 잠정모형의 모수를 자료에서 구하는 단계다. 평균이 μ인 AR(p)는 "
          "X<sub>t</sub> − μ = φ<sub>1</sub>(X<sub>t−1</sub> − μ) + ⋯ + φ<sub>p</sub>(X<sub>t−p</sub> − μ) + ε<sub>t</sub>이고, "
          "추정할 모수는 μ, φ<sub>1</sub>, ⋯, φ<sub>p</sub>, σ²다. "
          "<code>ar()</code>는 Yule-Walker 방정식(ACF와 모수의 관계식)에 표본 ACF를 넣어 계수를 추정하고, "
          "AIC(적합도에 모수 개수의 벌점을 더한 값, 작을수록 좋다)가 가장 작은 차수를 고른다."),
        p("진단의 첫 도구는 모수의 유의성 검정이다. H<sub>0</sub>: φ<sub>i</sub> = 0의 검정통계량은 φ̂<sub>i</sub> / se(φ̂<sub>i</sub>)이고, "
          "절대값이 크면(대략 1.96보다 크면) H<sub>0</sub>를 기각하여 H<sub>1</sub>: φ<sub>i</sub> ≠ 0으로 본다."),
        cell("u6_est", "추정과 유의성 검정", """
ar(X)
ar(X)$order                           # AIC로 고른 차수
ar(X)$ar                              # φ̂_1, φ̂_2
phi1 <- ar(X)$ar[1]
phi2 <- ar(X)$ar[2]
se_phi1 <- sqrt(ar(X)$asy.var[1,1])   # se(φ̂_1)
se_phi2 <- sqrt(ar(X)$asy.var[2,2])   # se(φ̂_2)
phi1/se_phi1                          # H0: φ_1 = 0의 검정통계량
phi2/se_phi2                          # H0: φ_2 = 0의 검정통계량
"""),
        note("출력의 Order selected가 AIC로 고른 차수, Coefficients가 φ̂<sub>1</sub>, φ̂<sub>2</sub>, <code>sigma^2</code>가 σ̂²다. "
             "μ̂는 <code>ar(X)$x.mean</code>에 들어 있다."),
        note("<code>ar(X)$asy.var</code>는 추정량의 점근 분산행렬이라, 대각원소의 제곱근이 표준오차 se(φ̂<sub>i</sub>)다. "
             "<code>phi1/se_phi1</code>이 H<sub>0</sub>: φ<sub>1</sub> = 0의 검정통계량이다."),
        ref="4장 p.36–40",
    ),

    # ------------------------------------------------------------ 4. 잔차 진단
    slide(
        "잔차 진단",
        p("잠정모형이 적절하다면 잔차(= 관측값 − 추정값)는 오차항 ε<sub>t</sub>와 유사한 성질을 가져야 한다. "
          "잔차의 그림·ACF·PACF로 모형에 대한 가정이 옳은지 판단하고, 잔차가 백색잡음이 될 때까지 계속 모형화한다. "
          "잔차의 ACF·PACF가 모두 점선 안이면 잔차에 남은 자기상관이 없다는 뜻이다. "
          "<code>tsdisplay()</code>는 시계열 그림, ACF, PACF를 한 번에 그린다."),
        cell("u6_diag", "잔차 진단", """
ar(X)$res[1:5]                  # 잔차 r_t = X_t − X̂_t
library(forecast)
tsdisplay(ar(X)$res)            # 잔차의 그림, ACF, PACF
""", gh=640),
        note("X̂<sub>t</sub>에 X<sub>t−1</sub>과 X<sub>t−2</sub>가 필요하므로 AR(2)의 잔차는 3번째부터 계산된다. 앞의 두 잔차가 NA인 것은 그 때문이다."),
        note("<code>tsdisplay()</code>는 forecast 패키지의 함수라 <code>library(forecast)</code>가 먼저 온다."),
        ref="4장 p.41–42",
    ),

    # ------------------------------------------------------------ 5. 예측
    slide(
        "예측",
        p("예측값은 X̂<sub>t+n</sub> = E(X<sub>t+n</sub> ∣ X<sub>1</sub>, ⋯, X<sub>t</sub>)로, 평균제곱오차(MSE)를 최소로 하는 예측이다. "
          "AR 모형은 주로 n = 10 정도의 단기(short-term)를 예측하고, 장기(long-term) 예측값은 모형에서 주어지는 평균값으로 수렴한다. "
          "<code>predict()</code>는 예측값 <code>pred</code>와 표준오차 <code>se</code>를 주고, 예측값 ± 2 × 표준오차를 예측구간으로 쓴다."),
        cell("u6_pred", "10시점 앞 예측", """
p <- predict(ar(X), n.ahead=10)      # 바꿔 보기: n.ahead (10 → 50)
p.U <- p$pred+2*p$se                 # 예측값 + 2 × 표준오차
p.L <- p$pred-2*p$se                 # 예측값 − 2 × 표준오차
plot(X, type="l", xlim=c(0,550))     # 가로축은 n.ahead = 50까지 미리 잡아 둔다
lines(p$pred, col="red")
lines(p.L, col="red", lty=3)
lines(p.U, col="red", lty=3)
"""),
        note("<code>p$pred+2*p$se</code>는 예측값 + 2 × 표준오차, 곧 예측구간의 위쪽 경계다. <code>p$pred-2*p$se</code>가 아래쪽 경계다."),
        note("<code>xlim=c(0,550)</code>은 가로축을 550까지 미리 잡아, n.ahead를 50으로 바꿔도 예측선이 그림 안에 들어오게 한다."),
        more(
            "AR(1)에서 R이 잔차와 예측값을 구하는 식을 확인하면",
            p("AR(1) X<sub>t</sub> − μ = φ(X<sub>t−1</sub> − μ) + ε<sub>t</sub>에서 잔차는 X̂<sub>1</sub>이 없어 r<sub>1</sub> = NA이고, "
              "X̂<sub>2</sub> = (1 − φ̂)μ̂ + φ̂X<sub>1</sub>, r<sub>2</sub> = X<sub>2</sub> − X̂<sub>2</sub>다. "
              "예측값은 X̂<sub>t+1</sub> = (1 − φ̂)μ̂ + φ̂X<sub>t</sub>, X̂<sub>t+2</sub> = (1 − φ̂²)μ̂ + φ̂²X<sub>t</sub>, ⋯, "
              "X̂<sub>t+n</sub> = (1 − φ̂<sup>n</sup>)μ̂ + φ̂<sup>n</sup>X<sub>t</sub> → μ̂ (n → ∞)다. "
              "U5의 <code>AR</code> 함수로 만든 AR(1) 자료에 이 식을 넣어 <code>ar()</code>·<code>predict()</code>의 결과와 견준다."),
            cell("u6_ar1", "AR(1)의 잔차와 예측값을 식으로 구하기", """
set.seed(10)                          # 모두 같은 자료로 실습하기 위해
X <- AR(0.5, 200)                     # U5의 AR 함수로 만든 AR(1) 자료
ar(X)                                 # Order selected 1인지 확인
phi <- ar(X)$ar                       # φ̂
mu <- mean(X)                         # μ̂ = X̄
ar(X)$res[1:3]                        # r_1 = NA, r_2, r_3
X[2] - ((1-phi)*mu + phi*X[1])        # r_2 = X_2 − X̂_2, X̂_2 = (1 − φ̂)μ̂ + φ̂X_1
n <- 5                                # 바꿔 보기: 예측할 시점 수 n (5 → 10)
predict(ar(X), n.ahead=n)$pred        # R의 예측값
(1-phi^(1:n))*mu + phi^(1:n)*X[200]   # X̂_{t+n} = (1 − φ̂^n)μ̂ + φ̂^nX_t
""", needs=("u5_ar",)),
            note("<code>(1-phi)*mu + phi*X[1]</code>은 X̂<sub>2</sub> = (1 − φ̂)μ̂ + φ̂X<sub>1</sub>이다. "
                 "그래서 <code>X[2] - (…)</code>가 r<sub>2</sub> = X<sub>2</sub> − X̂<sub>2</sub>다."),
            note("<code>(1-phi^(1:n))*mu + phi^(1:n)*X[200]</code>은 n = 1, ⋯, 5의 X̂<sub>t+n</sub>을 한 번에 구한다. "
                 "<code>X[200]</code>이 마지막 값 X<sub>t</sub>다."),
            note("이 셀은 <code>X</code>를 AR(1) 자료로 덮어쓴다."),
        ),
        ref="4장 p.43–44, p.49–50",
    ),

    # ------------------------------------------------------------ 6. 주간 평균에 AR 적합
    slide(
        "주간 평균의 식별",
        p("주 자료에는 요일 주기가 있다. 주간 평균(52개)은 요일 주기가 지워진 시계열이라, 여기에 세 단계와 예측을 적용한다. "
          "주간 평균은 U1에서 본 것처럼 추세가 있어 정상시계열은 아니지만, 근사적으로 AR을 적합해 본다."),
        cell("u6_wk1", "주간 평균의 그림, ACF, PACF", """
plot(TRD)
ag <- aggregate(TRD)/7       # 주간 평균 (한 주 = 7일)
plot(ag); acf(ag); pacf(ag)
"""),
        note("<code>aggregate(TRD)</code>는 주별 합이고, 7로 나누면 주간 평균이다. <code>ag</code>의 가로축은 1칸이 한 주다."),
        note("ACF·PACF의 점선은 ±1.96/√n이라 주간 평균 52개면 ±0.27이고, 모의 자료 500개면 ±0.09다. 자료가 적을수록 점선이 넓다."),
        ref="4장 p.45",
    ),
    slide(
        "주간 평균의 추정과 잔차 진단",
        p("<code>ar()</code>이 AIC로 차수를 고르고 Yule-Walker로 계수를 추정한다. "
          "잔차가 백색잡음과 비슷한지 그림·ACF·PACF로 본다."),
        cell("u6_wk2", "추정과 잔차 진단", """
ar(ag)
mean(ag)
r <- ar(ag)$res
library(forecast)
tsdisplay(r)
""", gh=640),
        note("차수가 p이면 X̂<sub>t</sub>에 앞의 p개 값이 필요하므로 앞의 잔차 p개가 NA다."),
        note("<code>mean(ag)</code>는 μ̂ = X̄로, 장기 예측값이 수렴하는 곳이다."),
        ref="4장 p.46–47",
    ),
    slide(
        "주간 평균의 10주 앞 예측",
        p("<code>ar(ag)</code>로 적합된 모형으로 다음 10주를 예측한다. 예측값 ± 2 × 표준오차가 예측구간이다."),
        cell("u6_wk3", "10주 앞 예측", """
p <- predict(ar(ag), n.ahead=10)
p.U <- p$pred+2*p$se
p.L <- p$pred-2*p$se
plot(ag, ylim=c(-1e6, 9e6), xlim=c(1,62))   # 52주 + 10주, 1e6 = 100만
lines(p$pred, col="red")
lines(p.L, col="red", lty=3)
lines(p.U, col="red", lty=3)
"""),
        note("<code>ylim=c(-1e6, 9e6)</code>은 세로축을 −100만부터 900만까지, <code>xlim=c(1,62)</code>는 가로축을 52주 + 10주까지 미리 잡는다."),
        note("<code>p.L</code>은 예측값 − 2 × 표준오차, 예측구간의 아래쪽 경계다."),
        ref="4장 p.48",
    ),

    # ------------------------------------------------------------ 7. 대조: QQQ
    slide(
        "QQQ에 AR 적합",
        p("대조 자료 QQQ에도 <code>ar()</code>을 적용한다. "
          "AR(1)의 특성방정식 1 − φx = 0의 해는 x = 1/φ라 ∣φ∣ &lt; 1이어야 정상이고, φ = 1이면 확률보행(RW)과 같아 비정상이다. "
          "U4에서 QQQ는 ADF를 기각하지 못한 확률적 추세였다."),
        cell("u6_qqq", "QQQ의 차수와 계수", """
ar(QQQ)$order
ar(QQQ)$ar
"""),
        note("<code>ar()</code>의 추정방법은 Yule-Walker이고 AR(1)의 Yule-Walker 추정량은 φ̂ = ρ̂<sub>1</sub>이라, "
             "차수가 1이면 <code>ar(QQQ)$ar</code>은 시차 1의 표본자기상관이다."),
        ref="4장 p.12, p.15, p.39–40",
    ),

    # ------------------------------------------------------------ 8. 정리
    slide(
        "AR 모형화",
        p("모형화 3단계와 예측의 원리, 모의 AR(2)·주간 평균·QQQ에서 확인한 것."),
        ul(
            "식별: AR(p)의 PACF는 시차 p 이후로 절단되고 ACF는 지수적으로 감소한다. "
            "모의 AR(2)는 PACF의 시차 1·2(0.78, −0.25)가 점선 밖이고 그 뒤는 우연히 살짝 넘는 시차 10 말고는 점선 안이며, "
            "ACF가 지수적으로 줄어 AR(2)가 잠정모형이다.",
            "추정: <code>ar()</code>는 AIC가 가장 작은 차수를 고르고 Yule-Walker로 계수를 추정한다. "
            "모의 AR(2)는 차수 2, φ̂<sub>1</sub> = 0.9769, φ̂<sub>2</sub> = −0.2537로 자료를 만든 1과 −0.25에 가깝고, "
            "주간 평균은 차수 4, φ̂ = 0.833, −0.322, 0.001, 0.295다.",
            "유의성 검정: 검정통계량 φ̂<sub>i</sub> / se(φ̂<sub>i</sub>)의 절대값이 대략 1.96보다 크면 φ<sub>i</sub> ≠ 0이다. "
            "모의 AR(2)는 22.51과 −5.85로 두 계수 모두 필요하다.",
            "잔차 진단: 잔차의 ACF·PACF가 모두 점선 안이면 모형이 적절하다. "
            "모의 AR(2)도 주간 평균의 AR(4)도 잔차의 ACF·PACF가 모두 점선 안이다.",
            "예측: 예측값은 처음 몇 시점은 마지막 값들의 영향으로 움직이다가 평균 μ̂로 수렴하고, 예측구간의 폭은 넓어지다가 일정해진다. "
            "모의 AR(2)는 n.ahead = 50이면 μ̂ = 0.097로 가라앉고 표준오차는 1.01에서 1.67까지 커진다.",
            "자료가 적으면 점선(±1.96/√n)이 넓어 PACF만으로 차수를 정하기 어렵다. "
            "주간 평균(52개, 점선 ±0.27)은 시차 1(0.70)·4(0.30)·10(0.32)·16(−0.31)이 점선 밖이라 분명하지 않다.",
            "주간 평균의 10주 예측값은 평균(약 382만) 쪽으로 움직이고, 아래쪽 경계는 54·55·59·60주째에 0보다 작아진다. "
            "거래 횟수는 0보다 작을 수 없으므로 예측구간의 아래쪽은 뜻이 없다.",
            "φ = 1이면 확률보행이라, φ̂가 1에 가까우면 정상성은 단위근 검정과 함께 판단한다. "
            "QQQ는 차수 1, φ̂ = 0.9798(시차 1의 표본자기상관)로 경계에 있고 U4의 ADF도 기각하지 못해 차분이 필요한 ARIMA 모형으로 간다.",
        ),
        p("주간 평균은 추세가 있어 AR을 근사적으로 적합한 것이다. 다음 단원은 주 자료의 추세와 계절성을 회귀모형으로 설명한다."),
        ref="4장 p.2, p.46",
        kind="wrap",
    ),
]
