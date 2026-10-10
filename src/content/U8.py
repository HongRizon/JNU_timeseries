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
        p("잠정모형의 잔차 ε<sub>t</sub>는 서로 독립이 아닐 수 있다. "
          "잔차의 ACF·PACF로 AR 차수를 정해 AR 모형을 적합하고, 그 잔차가 WN가 될 때까지 계속 모형화한다. "
          "직선 추세의 잠정모형은 X<sub>t</sub> = β<sub>0</sub> + β<sub>1</sub>t + ε<sub>t</sub>이고, 잔차가 AR(p)이면 "
          "ε<sub>t</sub> = φ<sub>1</sub>ε<sub>t−1</sub> + ⋯ + φ<sub>p</sub>ε<sub>t−p</sub> + η<sub>t</sub>, η<sub>t</sub> ~ WN이다. "
          "U7의 직선 모형 <code>trd.lm</code>에는 계절 항이 없으므로, 잔차에 요일 주기가 남는지도 본다."),
        ask("계절 항이 없는 직선 모형의 잔차 ACF에는 어떤 모양이 남을까?"),
        cell("u8_resid", "잔차 그림·ACF·PACF", """
trd.lm <- lm(trd.wd ~ time(trd.wd))   # U7의 직선 모형
r <- trd.lm$res                       # 잔차
layout(1:3)
plot(r, type="l")
acf(r, main="")
pacf(r, main="")
""", gh=720),
        ask("잔차의 ACF와 PACF에서 무엇이 보이나?",
            "ACF는 7일마다(시차 7, 14, 21) 봉우리가 있다. 요일 주기가 잔차에 남은 것이다. "
            "PACF는 시차 1(약 0.48)이 크고 시차 2는 점선 안이다. "
            "<code>lm</code>의 잔차는 ts가 아니라서 이 그림들의 가로축 한 칸은 1일이다."),
        ref="5장 p.8",
    ),
    slide(
        "잔차에 AR(2) 적합",
        p("차수는 잔차의 PACF가 절단되는 시차로 정한다. 먼저 AR(2)로 적합해 보고 차수를 바꿔 볼 수 있다. "
          "AR을 적합한 뒤의 잔차 r1이 WN이면 잔차의 자기상관이 그 AR로 설명된 것이다."),
        cell("u8_resar", "잔차에 AR(2) 적합", """
r.ar <- arima(r, order=c(2,0,0))     # 바꿔 보기: AR 차수 (2 → 1)
r.ar
r1 <- r.ar$res                       # AR(2)를 적합한 뒤의 잔차
layout(1:3)
plot(r1)
acf(r1, main="")
pacf(r1, main="")
""", gh=720),
        ask("주 자료의 r1은 WN인가?",
            "아니다. AR(2)를 적합한 뒤에도 r1의 ACF가 시차 7, 14, 21(일)에서 점선 밖으로 크게 나온다 (약 0.48, 0.32, 0.24). "
            "ar2(약 −0.09)는 유의하지 않아 차수보다 시차 7·14·21의 봉우리가 문제다. "
            "직선 추세만으로는 모자라므로 계절 항이 있는 잠정모형으로 간다."),
        ref="5장 p.9–10",
    ),

    # ------------------------------------------------------------ 3. 잠정모형의 잔차 진단
    slide(
        "잠정모형의 잔차",
        p("U7에서 고른 잠정모형은 log(X<sub>t</sub>) = β<sub>0</sub> + β<sub>1</sub>t<sub>st</sub> + β<sub>2</sub>t<sub>st</sub>² "
          "+ a<sub>1</sub>sin2πt + a<sub>2</sub>sin2π2t + a<sub>3</sub>sin2π3t + b<sub>2</sub>cos2π2t + ε<sub>t</sub>다. "
          "같은 순서로 잔차를 진단한다. PACF가 시차 p 이후 절단되면 AR(p)로 적합한다."),
        ask("계절 항을 넣었으니 잔차 ACF의 시차 7 봉우리는 사라질까?"),
        cell("u8_logres", "잠정모형과 잔차", """
trd.lm <- lm(log(trd.wd) ~ time_st + I(time_st^2)
             + SIN[,1] + SIN[,2] + SIN[,3] + COS[,2])   # U7에서 고른 항
r <- trd.lm$res
layout(1:3)
plot(r, type="l")
acf(r, main="")
pacf(r, main="")
""", gh=720),
        ask("PACF는 몇 시차 이후 절단되나?",
            "시차 1(약 0.64)에서 크고 그 뒤로는 거의 점선 안이라 AR(1)로 잡는다. "
            "ACF는 지수적으로 줄어들고, 직선 모형 때처럼 7일마다 크게 솟는 봉우리는 없다."),
        ref="5장 p.23",
    ),
    slide(
        "잔차에 AR(1) 적합",
        p("잔차에 AR(1)을 적합하고 그 잔차 r1의 ACF·PACF가 점선 안이면 WN로 본다."),
        cell("u8_logar", "잔차에 AR(1) 적합", """
r.ar <- arima(r, order=c(1,0,0))     # 바꿔 보기: AR 차수 (1 → 2)
r.ar
r1 <- r.ar$res
layout(1:3)
plot(r1)
acf(r1, main="")
pacf(r1, main="")
""", gh=720),
        ask("r1은 WN인가?",
            "<code>r.ar</code>의 ar1 ≈ 0.65다. AR(1)을 적합한 뒤 r1의 ACF·PACF는 거의 모두 점선 안이고, 시차 4·20 등 두세 개만 점선을 살짝 넘는다. "
            "점선 ±1.96/√n은 ρ̂<sub>h</sub>가 약 95%의 확률로 들어오는 범위라서, WN라도 20개에 하나쯤은 점선을 넘을 수 있다. "
            "그래서 r1은 WN로 보고, 잔차가 AR(1)이라는 정보를 GLS에 넘긴다."),
        ref="5장 p.24",
    ),

    # ------------------------------------------------------------ 4. GLS 최종모형
    slide(
        "GLS 최종모형",
        p("ε<sub>i</sub> ~ i.i.d.(0, σ²)이면 잔차제곱합을 최소로 하는 OLS가 BLUE(최량선형불편추정량)지만, "
          "오차항이 독립이 아니거나 분산이 같지 않으면 GLS가 더 효율적이다. "
          "GLS는 오차항의 가정이 만족되도록 자료를 선형변환한 뒤 OLS를 쓰므로 오차항에 대한 정보가 필요하다. "
          "주 자료는 ε<sub>t</sub> ~ AR(1), φ̂ ≈ 0.65를 <code>corARMA(0.65, p=1)</code>로 넣는다. "
          "최종모형은 log(X<sub>t</sub>) = f(t) + ε<sub>t</sub>, ε<sub>t</sub> = φε<sub>t−1</sub> + η<sub>t</sub>, η<sub>t</sub> ~ WN이다."),
        note("<code>gls()</code>는 nlme 패키지의 함수다."),
        cell("u8_gls", "GLS 최종모형", """
library(nlme)
trd.gls <- gls(log(trd.wd) ~ time_st + I(time_st^2)
               + SIN[,1] + SIN[,2] + SIN[,3] + COS[,2],
               cor=corARMA(0.65, p=1))   # 0.65 = r.ar의 ar1 추정값
summary(trd.gls)
"""),
        ask("<code>corARMA(0.65, p=1)</code>의 0.65는 어디서 왔나?",
            "잔차 진단에서 본 <code>r.ar</code>의 ar1 추정값(약 0.648)이다. 잔차가 AR(1)이라는 정보를 GLS에 넣는 자리다."),
        ask("출력의 Phi는? p-value가 0.05보다 큰 항이 있나?",
            "Phi는 약 0.66이다 (0.661859). <code>I(time_st^2)</code>의 p-value가 0.1567로 0.05보다 크다. "
            "U7의 OLS 적합에서는 0.00952였다. 항은 OLS 출력에서 골랐는데 GLS에서는 유의하지 않게 된 것이다. "
            "모형의 진단에는 모수의 유의성 검정이 들어간다."),
        ref="5장 p.11–12, p.25",
    ),

    # ------------------------------------------------------------ 5. 예측
    slide(
        "예측",
        p("예측은 두 가지다. 시계열모형 기반의 예측은 <code>predict(fit, n.ahead=14)</code>처럼 몇 시점 앞인지만 준다. "
          "회귀모형 기반의 예측은 <code>predict(fit, new.X)</code>로, 예측하려는 시점의 설명변수 값을 <code>new.X</code>에 "
          "data.frame으로 준다. <code>new.X</code>에는 회귀식에 쓴 설명변수를 같은 이름으로 준다."),
        ask("예측선에 요일 주기가 있을까?"),
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
        note("회귀식이 <code>SIN[,1]</code>처럼 행렬의 열을 직접 쓰므로 <code>predict</code>는 전역 환경의 "
             "<code>time_st</code>·<code>SIN</code>·<code>COS</code>를 읽는다. 그래서 이 셀은 세 객체를 새 시점의 값으로 덮어쓴다. "
             "학습 구간의 값이 다시 필요하면 U7의 <code>time_st</code>와 SIN·COS 만들기 셀을 다시 돌린다."),
        ask("<code>seq(53, 54+6/7, 1/7)</code>은 무엇인가?",
            "53주째 첫날부터 54주째 마지막 날까지 1/7(하루) 간격의 시점 14개다. 주 자료는 52주째 일요일(52 + 6/7)에 끝난다."),
        ask("예측선의 요일 주기는 모형의 어느 항에서 오나?",
            "계절 항 sin·cos에서 온다. 새 시점에서도 sin(2πit)·cos(2πit)가 같은 7일 주기를 만든다."),
        ref="5장 p.26–27",
    ),

    # ------------------------------------------------------------ 6. 역변환과 보정
    slide(
        "역변환과 보정",
        p("log(X<sub>t</sub>) = f(t) + ε<sub>t</sub>에서 E(ε<sub>t</sub>) = 0이므로 log(X<sub>t</sub>)의 예측은 f̂(t)다. "
          "그러면 X̂<sub>t</sub> = e<sup>f̂(t)</sup>일까? "
          "X<sub>t</sub> = e<sup>f(t)+ε<sub>t</sub></sup> = e<sup>f(t)</sup>e<sup>ε<sub>t</sub></sup>이므로 "
          "E(e<sup>ε<sub>t</sub></sup>) = 1이면 그렇지만, ε<sub>t</sub> ~ N(0, σ²)일 때 E(e<sup>ε<sub>t</sub></sup>) = e<sup>σ²/2</sup> ≠ 1이다. "
          "그래서 X̂<sub>t</sub> = e<sup>f̂(t)</sup>e<sup>ε̂<sub>t</sub></sup>로 보정한다. "
          "보정계수는 e<sup>ε̂<sub>t</sub></sup> = (1/n)Σ<sub>t=1</sub><sup>n</sup> e<sup>r<sub>t</sub></sup>(correction term)이고, r<sub>t</sub>는 잔차다."),
        ask("보정한 예측선은 보정 전보다 위에 있을까, 아래에 있을까?"),
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
        ask("<code>cr &lt;- mean(exp(trd.gls$res))</code>는 어느 식인가? <code>exp(pred)*cr</code>는?",
            "correction term e<sup>ε̂<sub>t</sub></sup> = (1/n)Σe<sup>r<sub>t</sub></sup>이고, "
            "<code>exp(pred)*cr</code>는 X̂<sub>t</sub> = e<sup>f̂(t)</sup>e<sup>ε̂<sub>t</sub></sup>다."),
        ask("주 자료의 cr는?",
            "약 1.0718이다. 1보다 커서 보정한 파란 선이 빨간 선보다 약 7% 위에 있다 (그림에서는 간격이 작다)."),
        more(
            "e<sup>σ²/2</sup>와 견주면",
            p("ε<sub>t</sub> ~ N(0, σ²)이면 E(e<sup>ε<sub>t</sub></sup>) = e<sup>σ²/2</sup>다. σ² 자리에 잔차의 분산을 넣어 cr와 견준다."),
            cell("u8_corr", "보정계수 cr와 e<sup>σ²/2</sup>", """
library(nlme)
exp(sd(trd.gls$res)^2/2)        # σ² 자리에 잔차의 분산
cr                              # mean(exp(trd.gls$res))
"""),
            ask("두 값은 1에서 얼마나 떨어져 있나? 왜 똑같지 않은가?",
                "cr ≈ 1.0718, e<sup>σ²/2</sup> ≈ 1.0752로 둘 다 1보다 크다. E(e<sup>ε<sub>t</sub></sup>) ≠ 1이라 보정이 필요하다. "
                "cr는 잔차로 직접 구한 (1/n)Σe<sup>r<sub>t</sub></sup>이고, e<sup>σ²/2</sup>는 ε<sub>t</sub>가 정규분포라고 가정한 식이라 똑같지는 않다."),
        ),
        ref="5장 p.28–29",
    ),

    # ------------------------------------------------------------ 7. 최종 분석 기록
    slide(
        "최종 분석 기록",
        p("한 바퀴를 마치며 네 칸을 채운다. 모형화는 주어진 자료를 가장 잘 설명해 주는 모형을 선택하는 작업이고, 정답인 모형은 하나가 아니다. "
          "맞히기가 아니라 근거를 적는 활동이다."),
        write("final-1", "1. 자료의 특징",
              "주 자료의 추세·요일 주기·변동의 증가 (U1), 정상인가와 흐름도의 경로 (U4). "
              "대조 자료 QQQ는 왜 다른 경로인가 (U1·U4·U5·U6·U7에서 QQQ에 같은 도구를 돌린 결과). 주어진 자료의 특징을 파악하는 단계다."),
        write("final-2", "2. 선택한 모형과 이유",
              "잠정모형의 항, 잔차의 AR 차수, GLS 최종모형 (U7·U8). GLS에서 유의하지 않게 된 항이 있으면 함께 적는다. "
              "자료와 비슷한 형태를 만들어내는 모형을 선택하는 단계다."),
        write("final-3", "3. 잔차에서 확인한 것",
              "마지막 잔차 r1의 ACF·PACF가 점선 안인가. 잔차가 WN가 될 때까지 계속 모형화한다."),
        write("final-4", "4. 예측과 남은 질문",
              "원래 단위의 예측값과 보정계수 cr. 직선 추세 모형과 log·계절 항 모형 중 어느 쪽이 나은가? "
              "마지막 잔차 r1의 ACF가 시차 7(일)에서 점선을 넘는가? 넘으면 요일 주기가 sin·cos만으로는 다 설명되지 않은 것이다."),
        raw('<div class="actions"><button type="button" class="btn" data-action="export-notes">내 기록을 텍스트 파일로 저장</button>'
            '<span class="actions-note">빈칸 표와 기록 칸의 내용을 모두 담는다.</span></div>'),
        ref="2장 p.19, 4장 p.41",
        kind="wrap",
    ),
]
