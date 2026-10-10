# -*- coding: utf-8 -*-
from dsl import *

UNIT = unit("U8", short="보정과 예측", title="보정과 예측", ref="5장 §5.3–5.4, §5.6–5.7, §5.9–5.10")

SLIDES = [
    # ------------------------------------------------------------ 1. 단원 첫 화면: 질문 + 표
    slide(
        "보정과 예측",
        p("회귀 잔차에 남은 자기상관을 반영하고 미래 시점을 원래 단위로 예측하면, 주 자료의 다음 2주는 어떻게 보이나?"),
        p("회귀모형 X<sub>t</sub> = f(t) + ε<sub>t</sub>를 최소제곱법(OLS)으로 적합한 잠정모형의 잔차는 정상시계열이지만 서로 독립이 아닐 수 있다. "
          "오차항이 독립이 아니면 OLS 대신 일반화최소제곱법(GLS)이 더 효율적이라, 잔차의 AR 구조를 넣어 다시 적합한 것이 최종모형이다. "
          "예측은 설명변수의 새 시점 값으로 하고, log 변환한 모형의 예측값은 보정해 역변환한다."),
        table(
            ["단계", "하는 일", "R"],
            [
                ["적합",
                 "잠정모형을 <code>lm</code>으로 적합한다 (U7)",
                 "<code>trd.lm &lt;- lm(log(trd.wd) ~ time_st + ⋯)</code>"],
                ["잔차 진단",
                 "잔차의 ACF·PACF로 AR 차수를 정해 <code>arima</code>로 적합하고, 그 잔차가 WN인지 본다",
                 "<code>r &lt;- trd.lm$res</code>, <code>acf(r)</code>, <code>pacf(r)</code>, <code>r.ar &lt;- arima(r, order=c(1,0,0))</code>"],
                ["GLS 재적합",
                 "잔차의 AR 구조를 넣어 다시 적합한 최종모형. 오차항에 대한 정보(AR 차수와 φ̂)가 필요하다",
                 "<code>library(nlme)</code>, <code>trd.gls &lt;- gls(…, cor=corARMA(0.65, p=1))</code>"],
                ["예측과 역변환",
                 "새 시점의 설명변수 <code>new.X</code>로 예측하고, log 예측값은 보정해 역변환한다",
                 "<code>pred &lt;- predict(trd.gls, new.X)</code>, <code>cr &lt;- mean(exp(trd.gls$res))</code>, <code>exp(pred)*cr</code>"],
            ],
        ),
        ref="5장 p.7–12, p.23–29",
        kind="opener",
    ),

    # ------------------------------------------------------------ 2. 직선 추세의 잔차
    slide(
        "직선 추세의 잔차",
        p("잠정모형의 잔차 ε<sub>t</sub>는 서로 독립이 아닐 수 있어, ACF·PACF로 AR 차수를 정해 적합한다. "
          "직선 추세의 잠정모형은 X<sub>t</sub> = β<sub>0</sub> + β<sub>1</sub>t + ε<sub>t</sub>이고, 잔차가 AR(p)이면 "
          "ε<sub>t</sub> = φ<sub>1</sub>ε<sub>t−1</sub> + ⋯ + φ<sub>p</sub>ε<sub>t−p</sub> + η<sub>t</sub>, η<sub>t</sub> ~ WN이다. "
          "계절 항이 없는 모형의 잔차에 요일 주기가 남으면 ACF의 시차 7, 14, 21에 봉우리가 선다."),
        cell("u8_resid", "잔차 그림·ACF·PACF", """
trd.lm <- lm(trd.wd ~ time(trd.wd))   # U7의 직선 모형
r <- trd.lm$res                       # 잔차
layout(1:3)
plot(r, type="l")
acf(r, main="")
pacf(r, main="")
""", gh=720),
        note("<code>trd.lm$res</code>가 잔차 ε̂<sub>t</sub> = X<sub>t</sub> − f̂(t)다. "
             "<code>lm</code>의 잔차는 ts가 아니라서 이 그림들의 가로축 한 칸은 1일이고, 시차 7이 한 주다."),
        ref="5장 p.8",
    ),
    slide(
        "잔차에 AR(2) 적합",
        p("차수는 잔차의 PACF가 절단되는 시차로 정한다. 한 차수 높은 AR(2)를 적합해 ar2가 유의하지 않으면 AR(1)로 충분하다. "
          "AR을 적합한 뒤의 잔차 r1이 WN이면 잔차의 자기상관이 그 AR로 설명된 것이고, WN이 아니면 차수나 잠정모형을 다시 본다."),
        cell("u8_resar", "잔차에 AR(2) 적합", """
r.ar <- arima(r, order=c(2,0,0))     # 바꿔 보기: AR 차수 (2 → 1)
r.ar
r1 <- r.ar$res                       # AR(2)를 적합한 뒤의 잔차
layout(1:3)
plot(r1)
acf(r1, main="")
pacf(r1, main="")
""", gh=720),
        note("출력의 ar1, ar2가 φ̂<sub>1</sub>, φ̂<sub>2</sub>이고 s.e.가 그 표준오차다. "
             "∣φ̂<sub>i</sub> / s.e.∣가 대략 1.96보다 작으면 그 계수는 유의하지 않다."),
        note("<code>r.ar$res</code>는 AR(2)를 적합한 뒤의 잔차 η̂<sub>t</sub>다. r1의 ACF에서는 시차 7, 14, 21이 점선 안인지 본다."),
        ref="5장 p.9–10",
    ),

    # ------------------------------------------------------------ 3. 잠정모형의 잔차 진단
    slide(
        "잠정모형의 잔차",
        p("U7에서 고른 잠정모형은 log(X<sub>t</sub>) = β<sub>0</sub> + β<sub>1</sub>t<sub>st</sub> + β<sub>2</sub>t<sub>st</sub>² "
          "+ a<sub>1</sub>sin2πt + a<sub>2</sub>sin2π2t + a<sub>3</sub>sin2π3t + b<sub>2</sub>cos2π2t + ε<sub>t</sub>다. "
          "잔차를 그림·ACF·PACF로 진단한다. PACF가 시차 p 이후 절단되면 AR(p)로 적합한다."),
        cell("u8_logres", "잠정모형과 잔차", """
trd.lm <- lm(log(trd.wd) ~ time_st + I(time_st^2)
             + SIN[,1] + SIN[,2] + SIN[,3] + COS[,2])   # U7에서 고른 항
r <- trd.lm$res
layout(1:3)
plot(r, type="l")
acf(r, main="")
pacf(r, main="")
""", gh=720),
        note("<code>time_st</code>·<code>SIN</code>·<code>COS</code>는 U7에서 만든 학습 구간(322일)의 값이다. "
             "반응변수가 <code>log(trd.wd)</code>라 잔차 r도 log 척도다."),
        ref="5장 p.23",
    ),
    slide(
        "잔차에 AR(1) 적합",
        p("잔차에 AR(1)을 적합하고 그 잔차 r1의 ACF·PACF가 점선 안이면 WN으로 본다. "
          "점선 ±1.96/√n은 ρ̂<sub>h</sub>가 약 95%의 확률로 들어오는 범위라서, WN이라도 20개에 하나쯤은 점선을 넘을 수 있다."),
        cell("u8_logar", "잔차에 AR(1) 적합", """
r.ar <- arima(r, order=c(1,0,0))     # 바꿔 보기: AR 차수 (1 → 2)
r.ar
r1 <- r.ar$res
layout(1:3)
plot(r1)
acf(r1, main="")
pacf(r1, main="")
""", gh=720),
        note("출력의 ar1이 잔차 AR(1)의 φ̂이다. 이 값이 GLS의 <code>corARMA(φ̂, p=1)</code>에 들어간다."),
        ref="5장 p.24",
    ),

    # ------------------------------------------------------------ 4. GLS 최종모형
    slide(
        "GLS 최종모형",
        p("ε<sub>t</sub> ~ i.i.d.(0, σ²)이면 잔차제곱합을 최소로 하는 OLS가 BLUE(최량선형불편추정량)지만, "
          "오차항이 독립이 아니거나 분산이 같지 않으면 GLS가 더 효율적이다. "
          "GLS는 오차항의 가정이 만족되도록 자료를 선형변환한 뒤 OLS를 쓰므로 오차항에 대한 정보가 필요하다. "
          "최종모형은 log(X<sub>t</sub>) = f(t) + ε<sub>t</sub>, ε<sub>t</sub> = φε<sub>t−1</sub> + η<sub>t</sub>, η<sub>t</sub> ~ WN이다."),
        cell("u8_gls", "GLS 최종모형", """
library(nlme)
trd.gls <- gls(log(trd.wd) ~ time_st + I(time_st^2)
               + SIN[,1] + SIN[,2] + SIN[,3] + COS[,2],
               cor=corARMA(0.65, p=1))   # 0.65 = r.ar의 ar1 추정값
summary(trd.gls)
"""),
        note("<code>corARMA(0.65, p=1)</code>는 오차항이 AR(1)이고 φ̂ ≈ 0.65라는 정보다. "
             "0.65는 잔차 진단에서 본 <code>r.ar</code>의 ar1 추정값(약 0.648)이다."),
        note("출력의 Correlation Structure 아래 Phi가 GLS가 다시 추정한 φ̂이고, "
             "Coefficients 표의 p-value 열이 각 항의 계수가 0이라는 가설의 p-value다."),
        ref="5장 p.11–12, p.25",
    ),

    # ------------------------------------------------------------ 5. 예측
    slide(
        "예측",
        p("예측은 두 가지다. 시계열모형 기반의 예측은 <code>predict(fit, n.ahead=14)</code>처럼 몇 시점 앞인지만 준다. "
          "회귀모형 기반의 예측은 <code>predict(fit, new.X)</code>로, 예측하려는 시점의 설명변수 값을 "
          "회귀식과 같은 이름으로 <code>new.X</code>에 data.frame으로 준다."),
        cell("u8_pred", "회귀모형 기반 예측", """
library(nlme)
new.t <- seq(53, 54+6/7, 1/7)            # 다음 2주 = 14일
time_st <- (new.t-mean(time))/sd(time)   # 학습 자료 time의 평균·표준편차로 표준화
SIN <- matrix(nr=length(new.t), nc=3)
COS <- matrix(nr=length(new.t), nc=3)
for (i in 1:3){
  SIN[,i] <- sin(2*pi*i*new.t)
  COS[,i] <- cos(2*pi*i*new.t)
}
new.X <- data.frame(time_st=time_st, SIN=SIN, COS=COS)
pred <- predict(trd.gls, new.X)
pred <- ts(pred, st=c(53,1), fr=7)
ts.plot(log(trd.wd), pred, col=c("black","red"), lty=1:2)
"""),
        note("<code>seq(53, 54+6/7, 1/7)</code>은 53주째 첫날부터 54주째 마지막 날까지 하루(1/7) 간격의 시점 14개다. "
             "주 자료는 52주째 일요일(52 + 6/7)에 끝난다."),
        note("회귀식이 <code>SIN[,1]</code>처럼 행렬의 열을 직접 쓰므로 <code>predict</code>는 <code>SIN</code>·<code>COS</code>를 "
             "<code>new.X</code>가 아니라 전역 환경에서 읽는다. 그래서 <code>time_st</code>·<code>SIN</code>·<code>COS</code> 세 객체를 새 시점의 값으로 덮어쓴다."),
        note("예측선의 요일 주기는 계절 항에서 온다. 새 시점 <code>new.t</code>에서도 sin(2πit)·cos(2πit)가 같은 7일 주기를 만든다."),
        ref="5장 p.26–27",
    ),

    # ------------------------------------------------------------ 6. 역변환과 보정
    slide(
        "역변환과 보정",
        p("log(X<sub>t</sub>) = f(t) + ε<sub>t</sub>에서 E(ε<sub>t</sub>) = 0이므로 log(X<sub>t</sub>)의 예측은 f̂(t)다. "
          "그러나 X<sub>t</sub> = e<sup>f(t)+ε<sub>t</sub></sup> = e<sup>f(t)</sup>e<sup>ε<sub>t</sub></sup>이고, "
          "ε<sub>t</sub> ~ N(0, σ²)일 때 E(e<sup>ε<sub>t</sub></sup>) = e<sup>σ²/2</sup> ≠ 1이라 "
          "X̂<sub>t</sub> = e<sup>f̂(t)</sup>로는 모자란다. "
          "그래서 X̂<sub>t</sub> = e<sup>f̂(t)</sup>e<sup>ε̂<sub>t</sub></sup>로 보정한다."),
        cell("u8_back", "원래 단위로 되돌리기", """
library(nlme)
X_pred <- exp(pred)                   # 보정 없이 역변환
X_pred <- ts(X_pred, st=c(53,1), fr=7)
cr <- mean(exp(trd.gls$res))          # 보정계수 (1/n)Σ e^{r_t}
cr
X_pred_cr <- exp(pred)*cr             # 보정한 예측값
X_pred_cr <- ts(X_pred_cr, st=c(53,1), fr=7)
ts.plot(trd.wd, X_pred, col=c("black","red"), lty=1:2)
lines(X_pred_cr, col="blue")
"""),
        note("<code>cr &lt;- mean(exp(trd.gls$res))</code>가 보정계수(correction term) e<sup>ε̂<sub>t</sub></sup> = (1/n)Σ<sub>t=1</sub><sup>n</sup> e<sup>r<sub>t</sub></sup>(r<sub>t</sub>는 잔차)이고, "
             "<code>exp(pred)*cr</code>가 X̂<sub>t</sub> = e<sup>f̂(t)</sup>e<sup>ε̂<sub>t</sub></sup>다."),
        note("그림의 빨간 점선이 보정 없이 역변환한 <code>X_pred</code>, 파란 실선이 보정한 <code>X_pred_cr</code>다. "
             "cr가 1보다 크면 파란 선이 빨간 선 위에 있다."),
        more(
            "e<sup>σ²/2</sup>와 견주면",
            p("ε<sub>t</sub> ~ N(0, σ²)이면 E(e<sup>ε<sub>t</sub></sup>) = e<sup>σ²/2</sup>다. σ² 자리에 잔차의 분산을 넣어 cr와 견준다."),
            cell("u8_corr", "보정계수 cr와 e<sup>σ²/2</sup>", """
library(nlme)
exp(sd(trd.gls$res)^2/2)        # σ² 자리에 잔차의 분산
cr                              # mean(exp(trd.gls$res))
"""),
            note("cr는 잔차로 직접 구한 (1/n)Σe<sup>r<sub>t</sub></sup>이고, e<sup>σ²/2</sup>는 ε<sub>t</sub>가 정규분포라고 가정한 식이라 똑같지는 않다."),
        ),
        ref="5장 p.28–29",
    ),

    # ------------------------------------------------------------ 7. 정리
    slide(
        "보정과 예측",
        p("보정과 예측의 원리와 주 자료에서 확인한 것."),
        ul(
            "잠정모형의 잔차는 정상시계열이어도 서로 독립이 아닐 수 있어, ACF·PACF로 AR 차수를 정해 잔차가 WN이 될 때까지 모형화한다. "
            "주 자료의 직선 모형 잔차는 ACF가 시차 7·14·21(일)마다 봉우리이고 PACF는 시차 1(약 0.48)이 커서, 계절 항이 없으면 요일 주기가 잔차에 남는다.",
            "AR을 적합한 뒤의 잔차 r1이 WN이 아니면 차수를 바꾸거나 잠정모형을 다시 본다. "
            "추가한 계수가 유의하지 않고 ACF의 봉우리가 주기(시차 7·14·21)에 남으면 차수가 아니라 잠정모형의 문제다. "
            "주 자료는 직선 모형 잔차에 AR(2)를 적합해도 r1의 ACF가 시차 7·14·21에서 점선 밖(약 0.48, 0.32, 0.24)이고 ar2(약 −0.09)는 유의하지 않아, 계절 항이 있는 잠정모형으로 간다.",
            "차수는 PACF가 절단되는 시차로 정하고, 적합 뒤 r1의 ACF·PACF가 점선 안이면 WN으로 본다. "
            "주 자료의 log·계절 항 잠정모형은 잔차의 ACF가 지수적으로 줄고 PACF가 시차 1(약 0.64)만 크며 7일 봉우리가 없어 AR(1)(ar1 ≈ 0.65)이다. "
            "적합 뒤의 r1은 시차 4·20만 살짝 넘어 WN으로 보고 GLS에 넘긴다.",
            "오차항이 독립이 아니면 잔차의 AR 구조를 넣은 GLS가 OLS보다 효율적이고 이것이 최종모형이다. "
            "주 자료는 Phi ≈ 0.66이고 <code>I(time_st^2)</code>의 p-value가 0.1567로 OLS(약 0.0093)와 달리 0.05보다 커서, 2차 항은 최종모형에서 다시 볼 항이다.",
            "회귀모형 기반 예측은 새 시점의 설명변수 <code>new.X</code>로 한다. "
            "주 자료의 다음 2주는 보정한 예측값이 월요일 약 312만 건에서 토요일 약 126만 건까지 내려가는 7일 모양을 두 번 반복하고, 두 주의 수준은 거의 같다.",
            "log 모형의 예측값 e<sup>f̂(t)</sup>는 E(e<sup>ε<sub>t</sub></sup>) ≠ 1이라 보정계수 cr = (1/n)Σe<sup>r<sub>t</sub></sup>를 곱해 역변환한다. "
            "주 자료는 cr ≈ 1.0718로 1보다 커서 보정한 예측값이 약 7% 위에 있고, 정규분포를 가정한 e<sup>σ²/2</sup> ≈ 1.0752와 비슷하지만 같지는 않다.",
        ),
        p("주 자료의 모형화는 여기서 끝난다."),
        ref="5장 p.23–29",
        kind="wrap",
    ),

    # ------------------------------------------------------------ 10. 전체 흐름
    slide(
        "전체 흐름",
        p("U1–U8이 주 자료에 한 일과 QQQ가 회귀로 가지 않은 이유."),
        ul(
            "그려 읽기 → 분해 → 평활 (U1–U3): 주 자료는 6주째 고점 뒤 감소하는 추세, 토·일이 낮은 요일 주기, 수준이 높을 때 커지는 변동폭을 보였다. "
            "승법 분해가 맞았고, 평활법 중에서는 추세와 요일 주기를 함께 갱신하는 Holt-Winters가 맞았다.",
            "정상성 판정 (U4): KPSS(trend)를 기각하지 못하고 ADF가 단위근을 기각해 결정적 추세로 판정했다. 이 갈림길에서 주 자료는 회귀모형으로 갔다.",
            "모형의 재료 → AR 모형화 (U5–U6): 백색잡음·확률보행·AR을 알고, 주간 평균에 AR을 식별·추정·진단·예측했다. 추세가 있어 근사적 적합이었다.",
            "회귀 → 보정과 예측 (U7–U8): log 변환한 추세·계절 회귀의 잠정모형, 잔차의 AR(1)을 넣은 GLS 최종모형, 보정계수 cr로 역변환한 다음 2주 예측이다.",
            "QQQ는 ADF가 단위근을 기각하지 못하는 확률적 추세라(U4) AR(1)의 φ̂ = 0.9798로 경계에 있고(U6), log 변환도 추세를 없애지 못한다(U7). "
            "회귀가 아니라 ARIMA 모형의 경로이고, 이 교재에서는 다루지 않는다.",
        ),
        p("모형화는 자료를 가장 잘 설명하는 모형을 고르는 작업이고 정답인 모형은 하나가 아니다."),
        ref="2장 p.19, 4장 p.41",
        kind="wrap",
    ),
]
