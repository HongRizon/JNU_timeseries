# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U7", short="추세·계절 회귀", title="추세·계절 회귀", ref="5장 §5.1–5.3, §5.6–5.7")

SLIDES = [
    # ------------------------------------------------------------ 1. 단원 첫 화면: 질문 + 표
    slide(
        "추세·계절 회귀",
        p("U1에서 본 주 자료의 세 특징, 곧 추세·주기성·변동의 증가를 반영한 회귀모형은 무엇인가?"),
        p("비정상시계열은 ACF가 천천히 감소하고, 추세나 계절성이 있고, 이분산성이 있다. "
          "추세나 계절성이 결정적이면 X<sub>t</sub> = f(t) + ε<sub>t</sub>, f(t) = 추세(t) + 주기성(t)로 적합해 "
          "ε<sub>t</sub> = X<sub>t</sub> − f(t)를 정상시계열로 만든다. "
          "U4에서 결정적 추세로 판정한 주 자료에 이 모형을 쓰고, 이분산성이 있으면 먼저 log 변환한다."),
        table(
            ["", "추세 항", "계절 항 (sin·cos)", "log 변환"],
            [
                ["반영하는 것", "추세", "주기성 또는 계절성", "변동의 증가"],
                ["식",
                 "f(t) = β<sub>0</sub> + β<sub>1</sub>t + β<sub>2</sub>t² + ⋯ + β<sub>p</sub>t<sup>p</sup> (t의 p차 다항함수). 선형추세는 β<sub>0</sub> + β<sub>1</sub>t",
                 "Σ<sub>i</sub>(a<sub>i</sub> sin2πit + b<sub>i</sub> cos2πit). 주기 1, 1/2, 1/3, ⋯의 sin·cos. 월별 자료는 i = 1, ⋯, 6, 주 자료는 i = 1, 2, 3",
                 "log 변환으로 분산을 안정화한 뒤 회귀모형을 적합한다. Box-Cox 변환에서 λ = 0인 경우"],
                ["R",
                 "<code>lm(trd.wd ~ time(trd.wd))</code>, <code>time_st &lt;- (time-mean(time))/sd(time)</code>",
                 "<code>SIN[,i] &lt;- sin(2*pi*i*time)</code>, <code>COS[,i] &lt;- cos(2*pi*i*time)</code>",
                 "<code>lm(log(trd.wd) ~ time_st + ⋯)</code>"],
                ["알아 둘 것",
                 "추세항의 time은 표준화한다 (t² 값이 너무 커지지 않게)",
                 "계절항은 원단위 time을 쓴다 (표준화하면 주기성 자체가 깨진다)",
                 "값이 모두 양수여야 한다"],
            ],
        ),
        ref="5장 p.2–6, p.13, p.19",
        kind="opener",
    ),

    # ------------------------------------------------------------ 2. 추세 항
    slide(
        "추세 항",
        p("추세는 시간 t의 다항함수 f(t) = β<sub>0</sub> + β<sub>1</sub>t + ⋯ + β<sub>p</sub>t<sup>p</sup>로 넣고, 가장 단순한 것이 직선 β<sub>0</sub> + β<sub>1</sub>t다. "
          "추세의 방향이 바뀐 시점이 있으면, 추세가 안정적으로 유지되는 구간의 자료만 쓴다. "
          "주 자료는 6주째 고점 뒤인 7주째(2024년 11월 18일)부터의 <code>trd.wd</code>(322개 = 46주)를 쓰며, 시간 단위는 주다."),
        cell("u7_trend", "직선 추세", """
trd.wd <- window(TRD, st=7)              # 7주째부터: 추세가 한 방향인 구간
plot(trd.wd)
trd.lm <- lm(trd.wd ~ time(trd.wd))      # 직선으로 적합
abline(trd.lm, col="red")
summary(trd.lm)
"""),
        note("<code>window(TRD, st=7)</code>은 7주째 첫날부터 끝까지 자른 구간이다. <code>st</code>는 <code>start</code>의 줄임이다."),
        note("출력의 Coefficients에서 <code>time(trd.wd)</code> 행의 Estimate가 기울기 β̂<sub>1</sub>(1주에 얼마나 변하는지)이고, "
             "Pr(&gt;|t|)가 기울기가 0이라는 가설의 p-value다."),
        ref="5장 p.6–7",
    ),

    # ------------------------------------------------------------ 3. 계절 항 만들기
    slide(
        "계절 항 만들기",
        p("주기성은 sin·cos 항(조화항) Σ<sub>i</sub>(a<sub>i</sub> sin2πit + b<sub>i</sub> cos2πit)로 넣는다. "
          "i = 1, 2, 3, ⋯은 주기 1, 1/2, 1/3, ⋯의 파동이다. "
          "주 자료는 주기 1이 1주(7일)이고 하루 간격(1/7)이라 i = 4, 5, 6이 i = 3, 2, 1과 겹치므로 i = 1, 2, 3만 쓴다."),
        cell("u7_sprep", "time_st와 SIN·COS 만들기", """
time <- time(trd.wd)
time_st <- (time-mean(time))/sd(time)   # 추세항: 표준화 (t² 값이 커지지 않게)
SIN <- matrix(nr=length(time), nc=3)    # 계절항: 원단위 time
COS <- matrix(nr=length(time), nc=3)
for (i in 1:3){                         # 하루 간격 자료라 3까지 (월별은 6)
  SIN[,i] <- sin(2*pi*i*time)
  COS[,i] <- cos(2*pi*i*time)
}
"""),
        note("<code>(time-mean(time))/sd(time)</code>은 추세항의 표준화 t<sub>st</sub>다. "
             "<code>sin(2*pi*i*time)</code>의 i = 1, 2, 3은 주기 1, 1/2, 1/3의 sin이고, 주 자료는 주기 1이 1주라 7일, 3.5일, 약 2.3일 주기다."),
        note("<code>matrix(nr=length(time), nc=3)</code>은 322행 3열의 빈 행렬이고, for 문이 열마다 i = 1, 2, 3의 값을 채운다. "
             "출력 없이 <code>time_st</code>·<code>SIN</code>·<code>COS</code>만 만든다."),
        more(
            "i = 4가 i = 3과 겹치는지 확인하면",
            p("하루 간격 time에서 sin2π4t = −sin2π3t, cos2π4t = cos2π3t다. 같은 열이 둘 들어가면 <code>lm</code>의 계수가 NA로 나온다."),
            cell("u7_sin4", "i = 3과 i = 4의 sin·cos", """
s3 <- sin(2*pi*3*time); s4 <- sin(2*pi*4*time)
c3 <- cos(2*pi*3*time); c4 <- cos(2*pi*4*time)
round(head(cbind(s3, s4, c3, c4)), 3)   # s4 = -s3, c4 = c3
"""),
            note("출력의 s4 열은 s3 열과 부호만 반대이고, c4 열은 c3 열과 같다."),
            note("i + i′ = 7이면 2πit + 2πi′t = 2π·7t이고, t가 1/7의 배수라 이것은 2π의 배수다. "
                 "그래서 i = 5는 i = 2와, i = 6은 i = 1과 겹친다."),
        ),
        ref="5장 p.13–14",
    ),

    # ------------------------------------------------------------ 4. 추세 + 계절 항 적합과 항 고르기
    slide(
        "추세 항과 계절 항을 함께 적합하기",
        p("추세 항과 계절 항을 한 회귀식에 넣는다: "
          "X<sub>t</sub> = β<sub>0</sub> + β<sub>1</sub>t<sub>st</sub> + β<sub>2</sub>t<sub>st</sub>² + Σ<sub>i=1</sub><sup>3</sup>(a<sub>i</sub> sin2πit + b<sub>i</sub> cos2πit) + ε<sub>t</sub>. "
          "추세가 직선에서 조금 휘어 있을 수 있어 2차 항까지 넣고, 필요 없는 항은 <code>summary</code>로 가려낸다. "
          "p-value가 0.05보다 작은 항을 남긴 것이 잠정모형이다."),
        cell("u7_fit", "추세 + 계절 항 전체 적합", """
fit <- lm(trd.wd ~ time_st + I(time_st^2)
          +SIN[,1]+SIN[,2]+SIN[,3]
          +COS[,1]+COS[,2]+COS[,3])     # 추세 2항 + 계절 6항
summary(fit)
"""),
        note("<code>time_st</code>가 표준화한 시간 t<sub>st</sub>이고, <code>SIN</code>·<code>COS</code> 안의 t는 원단위 시간이다. "
             "<code>I(time_st^2)</code>: 회귀식 안에서 제곱을 쓰려면 <code>I()</code>로 감싼다."),
        note("출력의 Pr(&gt;|t|) 열이 각 항의 p-value다. "
             "<code>SIN[, 1]</code> 행은 sin2πt의 계수 a<sub>1</sub>, <code>COS[, 2]</code> 행은 cos2π2t의 계수 b<sub>2</sub>다."),
        ref="5장 p.14–15",
    ),

    # ------------------------------------------------------------ 5. log 변환
    slide(
        "log 변환",
        p("이분산성이 있으면 Box-Cox 변환 (x<sup>λ</sup> − 1)/λ (λ ≠ 0), ln x (λ = 0)으로 분산을 안정화한 뒤 회귀모형을 적합한다. "
          "λ는 변환모수이고, log 변환은 λ = 0인 경우다. 값이 모두 양수여야 한다. "
          "U1에서 주 자료는 수준이 높을 때 변동폭이 큰 이분산성을 보였다."),
        cell("u7_log", "log 변환 전후 그림", """
trd.log <- log(trd.wd)       # λ = 0: ln x
par(mfrow=c(1,2))
plot(trd.wd)
plot(trd.log)
""", gw=840, gh=400),
        note("<code>par(mfrow=c(1,2))</code>는 그림 두 개를 나란히 놓는다. 왼쪽이 변환 전, 오른쪽이 변환 뒤다."),
        more(
            "λ ≠ 0인 Box-Cox 변환을 해 보면",
            p("λ = 0.5면 (x<sup>0.5</sup> − 1)/0.5다. 변환 전, λ = 0.5, λ = 0(ln x)의 세 그림이 나란히 나온다."),
            cell("u7_bc", "Box-Cox 변환", """
lambda <- 0.5                          # 바꿔 보기: λ (0.5 → 0.25)
trd.bc <- (trd.wd^lambda - 1)/lambda   # (x^λ − 1)/λ, λ ≠ 0
par(mfrow=c(1,3))
plot(trd.wd)                           # 변환 전
plot(trd.bc)
plot(trd.log)                          # λ = 0: ln x
""", gw=900, gh=380),
            note("λ = 0을 넣으면 0/0이라 값이 모두 NaN이 되어 둘째 그림에서 오류가 나므로, λ = 0은 셋째 그림 ln x가 맡는다."),
        ),
        ref="5장 p.5, p.19–20",
    ),
    slide(
        "log 모형 적합",
        p("회귀식의 <code>trd.wd</code>를 <code>log(trd.wd)</code>로 바꾼다. 항을 고르는 방법은 같다. "
          "p-value가 0.05보다 작은 항을 남긴 것이 주 자료의 잠정모형이다."),
        cell("u7_logfit", "log 모형 적합", """
fit <- lm(log(trd.wd) ~ time_st + I(time_st^2)
          +SIN[,1]+SIN[,2]+SIN[,3]
          +COS[,1]+COS[,2]+COS[,3])     # 반응변수만 log(trd.wd)로
summary(fit)
"""),
        note("설명변수는 그대로이므로 출력의 Estimate는 log(X<sub>t</sub>) 척도의 계수다."),
        ref="5장 p.21–22",
    ),

    # ------------------------------------------------------------ 6. 대조: QQQ
    slide(
        "QQQ에 log 변환",
        p("대조 자료 QQQ에 같은 변환을 한다. U4에서 QQQ는 ADF가 단위근을 기각하지 못해 확률적 추세로 판정했다. "
          "Box-Cox 변환은 이분산성이 있을 때 분산을 안정화하는 변환이지, 확률적 추세를 없애는 변환이 아니다."),
        cell("u7_qqq", "QQQ에 log 변환", """
library(tseries)
qqq.log <- log(QQQ)
par(mfrow=c(1,2))
plot(QQQ); plot(qqq.log)
adf.test(qqq.log)            # H0: 단위근 존재
""", gw=840, gh=400),
        note("<code>adf.test</code>의 귀무가설은 단위근 존재다. 출력의 p-value가 0.05보다 크면 기각하지 못한 것이고, 확률적 추세가 남아 있다고 본다."),
        ref="5장 p.5, 2장 p.17",
    ),

    # ------------------------------------------------------------ 7. 정리
    slide(
        "추세·계절 회귀",
        p("추세·계절 회귀의 원리와 두 자료에서 확인한 것."),
        ul(
            "추세나 계절성이 결정적이면 X<sub>t</sub> = f(t) + ε<sub>t</sub>를 적합해 ε<sub>t</sub> = X<sub>t</sub> − f(t)를 정상시계열로 만든다.",
            "추세 항은 추세가 한 방향으로 유지되는 구간에만 맞춘다. "
            "주 자료는 7주째부터 자른 <code>trd.wd</code>(322개 = 46주)에 직선을 맞추면 기울기가 약 −88,930(1주당), p-value가 2e-16보다 작아 유의한 감소 추세다.",
            "주기성은 sin·cos 항 Σ<sub>i</sub>(a<sub>i</sub> sin2πit + b<sub>i</sub> cos2πit)로 넣는다. "
            "주 자료는 하루 간격(1/7)이라 i = 4, 5, 6이 i = 3, 2, 1과 겹쳐 i = 1, 2, 3(7일, 3.5일, 약 2.3일 주기)만 쓴다.",
            "추세 항과 계절 항을 한 회귀식에 넣고 <code>summary</code>의 p-value가 0.05보다 작은 항을 남긴 것이 잠정모형이다. "
            "주 자료는 log 변환 전에 <code>time_st</code>, <code>I(time_st^2)</code>, <code>SIN[,1]</code>, <code>SIN[,3]</code>, <code>COS[,2]</code> 다섯 항이 남는다.",
            "이분산성이 있으면 Box-Cox 변환(λ = 0이면 ln x)으로 분산을 안정화한 뒤 적합한다. "
            "주 자료는 log를 취하면 수준이 높았던 앞부분의 큰 변동폭과 요일 주기의 폭이 줄어 전 구간이 고르게 되고, λ = 0.5보다 ln x 쪽이 더 고르다.",
            "변환 뒤에는 항을 다시 고른다. 주 자료는 log 변환 뒤 <code>SIN[,2]</code>가 새로 들어와, 잠정모형은 "
            "log(X<sub>t</sub>) = β<sub>0</sub> + β<sub>1</sub>t<sub>st</sub> + β<sub>2</sub>t<sub>st</sub>² "
            "+ a<sub>1</sub>sin2πt + a<sub>2</sub>sin2π2t + a<sub>3</sub>sin2π3t + b<sub>2</sub>cos2π2t + ε<sub>t</sub>다.",
            "Box-Cox 변환은 분산을 안정화할 뿐 확률적 추세를 없애지 않으므로, 확률적 추세는 회귀가 아니라 ARIMA 모형으로 다룬다. "
            "QQQ는 log 변환으로 변동폭은 고르게 되지만, ADF는 여전히 단위근을 기각하지 못한다 (p ≈ 0.28).",
        ),
        p("잠정모형의 잔차 ε<sub>t</sub>는 정상시계열이지만 서로 독립이 아닐 수 있으므로, "
          "다음 단원은 잔차의 자기상관을 보정하고 예측값을 역변환하는 U8이다."),
        ref="5장 p.2, p.22",
        kind="wrap",
    ),
]
