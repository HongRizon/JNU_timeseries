# -*- coding: utf-8 -*-
"""슬라이드 내용을 적는 작은 DSL.

단원 파일(src/content/U1.py 등)은 아래 두 이름을 정의한다.

    UNIT   = unit("U1", short="그려 읽기", title="그려 읽기", ref="1장")
    SLIDES = [slide(...), slide(...), ...]

본문 문자열에는 인라인 HTML을 쓸 수 있다: <sub>, <sup>, <code>, <b>, <i>, <br>.
"""

# ---------------------------------------------------------------- 단원·화면


def unit(uid, short, title, ref=""):
    """단원 정보. uid='U1', short=탭에 보이는 짧은 이름, title=단원 제목, ref='1장'."""
    return {"id": uid, "short": short, "title": title, "ref": ref}


def slide(title, *elements, ref=None, kind=None):
    """화면 하나.

    title : 화면 제목 (쪽 번호 없이)
    elements : p(), ul(), table(), ask(), cell(), more(), note(), write() 등
    ref : 이 화면이 따르는 강의 쪽, 예 "1장 p.8–9" (화면 맨 아래 작은 글씨로만 표시)
    kind : "opener" (단원 첫 화면) | "wrap" (단원 마지막 정리 화면) | None
    """
    return {"type": "slide", "title": title, "ref": ref, "kind": kind, "body": list(elements)}


# ---------------------------------------------------------------- 본문 요소


def p(html):
    """문단."""
    return {"type": "p", "html": html}


def ul(*items):
    """글머리 목록."""
    return {"type": "ul", "items": list(items)}


def h3(text):
    """화면 안의 작은 제목."""
    return {"type": "h3", "text": text}


class _Blank:
    """빈칸 표의 빈칸 (학생이 적는 칸, 브라우저에 저장)."""

    def __repr__(self):
        return "BLANK"


BLANK = _Blank()


def table(head, rows, first_bold=True):
    """표. head=열 이름 목록, rows=행 목록(각 행은 문자열 또는 BLANK의 목록)."""
    return {"type": "table", "head": list(head), "rows": [list(r) for r in rows], "first_bold": first_bold}


def ask(question, answer=None):
    """질문. 셀 앞에 두면 '실행 전에 예상해 보는 질문', 셀 뒤에 두면 '실행 후 확인 질문'.
    answer를 주면 '답'을 눌러 열어 볼 수 있다. (셀 앞 질문에는 보통 답을 달지 않는다.)"""
    return {"type": "ask", "q": question, "a": answer}


def cell(cid, title, code, needs=(), gw=720, gh=450, noprov=False):
    """실행 셀.

    cid : 셀 id. 단원 소문자 접두 + 밑줄 + 짧은 영문, 예 "u1_trend". 전체에서 유일.
    title : 셀 제목 (쪽 번호 없이)
    code : R 코드 문자열. 앞뒤 빈 줄은 지워진다.
    needs : 변수로 추적되지 않는 앞 셀 의존이 있을 때만 셀 id를 적는다 (보통 비워 둔다).
    gw, gh : 그림 크기(px). 그림이 세로로 긴 셀(layout(1:3) 등)은 gh=720.
    noprov : True이면 이 셀이 만드는 변수를 다른 셀의 의존으로 삼지 않는다 (자료 읽기 셀처럼
             R 준비 때 이미 만들어지는 것을 다시 보여 주는 셀).
    """
    return {
        "type": "cell",
        "id": cid,
        "title": title,
        "code": code.strip("\n").rstrip(),
        "needs": list(needs),
        "gw": gw,
        "gh": gh,
        "noprov": noprov,
    }


def more(summary, *elements):
    """접힌 블록. 꼭 필요하지 않은 확인 셀이나 긴 설명을 넣는다. summary=접힌 상태의 한 줄."""
    return {"type": "more", "summary": summary, "body": list(elements)}


def note(html):
    """작은 회색 글씨의 보충 설명 한 줄 (R 동작 설명 등)."""
    return {"type": "note", "html": html}


def write(key, label, prompt):
    """기록 칸. key=저장 키(전체에서 유일, 예 "final-1"), label=제목, prompt=무엇을 적을지."""
    return {"type": "write", "key": key, "label": label, "prompt": prompt}


def flow(left, rights):
    """왼쪽 상자 하나에서 오른쪽 상자 여러 개로 가는 간단한 흐름도. rights=문자열 목록."""
    return {"type": "flow", "left": left, "rights": list(rights)}


def raw(html):
    """그대로 넣는 HTML (U0 전용: 내려받기 단추 등)."""
    return {"type": "raw", "html": html}
