#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""timeseries_webr.html 생성기.

    python3 src/build.py              # 검사 후 timeseries_webr.html 생성
    python3 src/build.py --check      # 검사만 (전체)
    python3 src/build.py --check U3   # 한 단원만 검사
    python3 src/build.py --cells      # 셀 의존 관계 표 출력

내용은 src/content/U0.py … U8.py (src/dsl.py 참고), 자료는 src/data/, 실행 코드는 src/runtime.js,
모양은 src/style.css, 도움말은 src/help.html 에 있다.
"""
import argparse
import html
import importlib.util
import json
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
OUT = os.path.join(ROOT, "timeseries_webr.html")
UNIT_IDS = ["U0", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8"]
VERSION = "2026-10-10"
TITLE = "시계열분석 webR 실습"

# R 준비 때 만들어 두는 자료 객체 (셀이 만들지 않아도 쓸 수 있다)
BUILTIN_DATA = {"TRD", "QQQ"}
DATA_FILES = ["trd.txt", "qqq.txt"]
EXTRA_FILES = ["trd_dates.txt", "qqq_months.txt"]

# ---------------------------------------------------------------- 금지 표현
# (학생 화면에 보이면 안 되는 것: 강의 자료 이름, 옛 변수 이름, 운영 메모 문구)
FORBIDDEN = [
    (r"AirPassengers", "강의 자료 이름"), (r"\bAP\b", "강의 자료 이름 AP"), (r"\bElec\b|Elec\.ts", "강의 자료 이름"),
    (r"\bcbe\b|\bCBE\b", "강의 자료 이름"), (r"\bMaine\b", "강의 자료 이름"), (r"\bglobal\b", "강의 자료 이름 global"),
    (r"waveht", "강의 자료 이름"), (r"comp\.(ts|hw)", "강의 자료 이름"), (r"\bmotor\b|\bcomplaints\b", "강의 자료 이름"),
    (r"\bZ\.ts\b", "강의 자료 이름"), (r"\bap\.(lm|gls)\b|\bAP\.hw\b", "강의 객체 이름"),
    (r"TRD_RAW|QQQ_RAW|TRD_WD|TRD_LOG|TRD_BC|QQQ_LOG|TRD_TUE", "옛 변수 이름 (TRD, QQQ, trd.wd, trd.log … 로)"),
    (r"\bwww\b", "www 변수 (자료는 미리 읽혀 있다)"),
    (r"#\s*강의", "# 강의: 주석"), (r"강의\s*:", "'강의:' 표기"), (r"강의 코드", "'강의 코드' 라벨"),
    (r"넘어온 이유|다음 화면|이 단원 끝|시험 범위|운영용|운영 메모|R의 동작|교재 발췌|강의 기준 답|강의 예\b", "운영 메모 문구"),
    (r"\(선택|선택\)|이론 카드|도입 카드|정리 카드|연결 카드|비교표\s*:|대조 셀|준비 셀|손잡이|강의 식 구현|강의 자료|강의 코드 아님|강의 식 p", "옛 라벨 문구"),
    (r"\bp\.\s?\d", "쪽 번호 (ref= 로만 적는다)"),
]

# ---------------------------------------------------------------- R 정적 분석
R_KEYWORDS = {"function", "for", "in", "if", "else", "while", "repeat", "break", "next", "return", "TRUE", "FALSE",
              "NULL", "NA", "Inf", "NaN", "T", "F", "NA_integer_", "NA_real_", "NA_character_"}
R_VALUES = {"pi", "letters", "LETTERS", "month.name", "month.abb"}
# 이름만으로 넘겨도 되는 흔한 함수 (sapply(x, mean) 같은 꼴)
R_FUNS = {"mean", "sum", "sd", "var", "median", "max", "min", "abs", "exp", "log", "sqrt", "length", "sin", "cos",
          "diff", "cumsum", "round", "print", "plot", "lines", "points", "paste", "c", "rnorm", "identity", "rev"}
_TOK = re.compile(r"""
    (?P<ws>[ \t]+) | (?P<nl>\n) | (?P<com>\#[^\n]*) |
    (?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`[^`]*`) |
    (?P<num>(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?L?) |
    (?P<id>[A-Za-z.][A-Za-z0-9._]*) |
    (?P<op><<-|->>|<-|->|<=|>=|==|!=|&&|\|\||%[^%\n]*%|::|[-+*/^<>=!&|~$@(){}\[\],;?:])
""", re.X)


def r_tokens(code):
    toks = []
    i = 0
    while i < len(code):
        m = _TOK.match(code, i)
        if not m:
            toks.append(("junk", code[i], i))
            i += 1
            continue
        kind = m.lastgroup
        if kind not in ("ws", "com"):
            toks.append((kind, m.group(), i))
        i = m.end()
    return toks


def r_check_syntax(code):
    """괄호·따옴표 균형만 본다 (R이 없으므로)."""
    errs = []
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for kind, val, pos in r_tokens(code):
        if kind == "junk":
            errs.append(f"알 수 없는 문자 {val!r}")
        if kind != "op":
            continue
        if val in "([{":
            stack.append(val)
        elif val in ")]}":
            if not stack or stack[-1] != pairs[val]:
                errs.append(f"괄호가 맞지 않음: {val} (위치 {pos})")
                return errs
            stack.pop()
    if stack:
        errs.append(f"닫히지 않은 괄호: {''.join(stack)}")
    return errs


def r_analyze(code):
    """셀 코드에서 (전역 정의 이름, 사용 이름, 패키지) 를 찾는다.

    정의: 함수 밖에서 `이름 <-`, `이름 =`(문장 머리), `for (이름 in`
    사용: 함수 호출이 아닌 이름 중 R 예약어·상수·지역 변수가 아니고, 같은 셀에서 먼저 정의되지 않은 것
    """
    toks = [t for t in r_tokens(code) if t[0] != "nl"] if False else r_tokens(code)
    defs, uses, pkgs = [], [], []
    n = len(toks)
    local_scopes = []          # [set(names), end_mode]  end_mode: ('brace', depth) | ('line',)
    brace_depth = 0
    paren_depth = 0
    pending_fn_params = None

    def is_local(name):
        return any(name in s for s, _ in local_scopes)

    def nxt(k):
        j = k + 1
        while j < n and toks[j][0] == "nl":
            j += 1
        return toks[j] if j < n else (None, None, None)

    def nxt_raw(k):
        return toks[k + 1] if k + 1 < n else (None, None, None)

    def prev_raw(k):
        return toks[k - 1] if k > 0 else (None, None, None)

    def stmt_start(k):
        kind, val, _ = prev_raw(k)
        return kind is None or kind == "nl" or (kind == "op" and val in ("{", ";", "}"))

    k = 0
    while k < n:
        kind, val, pos = toks[k]
        if kind == "nl":
            local_scopes = [s for s in local_scopes if s[1][0] != "line"]
        elif kind == "op":
            if val in ("(", "["):
                paren_depth += 1
            elif val in (")", "]"):
                paren_depth -= 1
            if val == "{":
                brace_depth += 1
                if pending_fn_params is not None:
                    local_scopes.append((pending_fn_params, ("brace", brace_depth)))
                    pending_fn_params = None
            elif val == "}":
                local_scopes = [s for s in local_scopes if not (s[1][0] == "brace" and s[1][1] == brace_depth)]
                brace_depth -= 1
            elif val == ")" and pending_fn_params is not None:
                # function(...) 바로 뒤에 { 가 없으면 한 줄짜리 함수
                k2, v2, _ = nxt_raw(k)
                if not (k2 == "op" and v2 == "{"):
                    pass
        elif kind == "id":
            nk, nv, _ = nxt_raw(k)
            pk, pv, _ = prev_raw(k)
            if val == "function":
                # 매개변수 수집
                params = set()
                j = k + 1
                depth = 0
                while j < n:
                    kj, vj, _ = toks[j]
                    if kj == "op" and vj == "(":
                        depth += 1
                    elif kj == "op" and vj == ")":
                        depth -= 1
                        if depth == 0:
                            break
                    elif kj == "id" and depth == 1:
                        pj = toks[j - 1]
                        if pj[0] == "op" and pj[1] in ("(", ","):
                            params.add(vj)
                    j += 1
                after = toks[j + 1] if j + 1 < n else (None, None, None)
                if after[0] == "op" and after[1] == "{":
                    pending_fn_params = params
                else:
                    local_scopes.append((params, ("line",)))
                k = j + 1
                continue
            if val in R_KEYWORDS:
                k += 1
                continue
            if pk == "op" and pv in ("$", "@"):
                k += 1
                continue
            if pk == "op" and pv == "::":
                k += 1
                continue
            if nk == "op" and nv == "::":
                k += 1
                continue
            if pk == "id" and pv in ("library", "require") and False:
                pass
            # library(pkg) / require(pkg)
            if pk == "op" and pv == "(" and k >= 2 and toks[k - 2][0] == "id" and toks[k - 2][1] in ("library", "require"):
                pkgs.append(val)
                k += 1
                continue
            if nk == "op" and nv == "(":           # 함수 호출
                k += 1
                continue
            if nk == "op" and nv == "=":           # 이름 있는 인자 또는 = 대입
                if paren_depth == 0 and stmt_start(k) and not is_local(val):
                    if pending_fn_params is None and not any(s[1][0] == "brace" for s in local_scopes):
                        defs.append((val, pos))
                    else:
                        for s, _ in local_scopes[-1:]:
                            s.add(val)
                k += 1
                continue
            if nk == "op" and nv in ("<-", "<<-"):  # 대입
                in_fn = any(s[1][0] == "brace" for s in local_scopes) or any(s[1][0] == "line" for s in local_scopes)
                if in_fn:
                    local_scopes[-1][0].add(val)
                else:
                    defs.append((val, pos))
                k += 1
                continue
            if pk == "op" and pv == "(" and k >= 2 and toks[k - 2][0] == "id" and toks[k - 2][1] == "for" \
                    and nk == "id" and nv == "in":
                in_fn = any(s[1][0] == "brace" for s in local_scopes)
                if in_fn:
                    local_scopes[-1][0].add(val)
                else:
                    defs.append((val, pos))
                k += 1
                continue
            if is_local(val) or val in R_VALUES:
                k += 1
                continue
            uses.append((val, pos))
        k += 1
    # 같은 셀에서 먼저 정의된 이름은 사용 목록에서 뺀다
    first_def = {}
    for name, pos in defs:
        first_def.setdefault(name, pos)
    ext_uses = []
    for name, pos in uses:
        if name in first_def and first_def[name] < pos:
            continue
        if name not in ext_uses:
            ext_uses.append(name)
    def_names = []
    for name, _ in defs:
        if name not in def_names:
            def_names.append(name)
    return def_names, ext_uses, pkgs


# ---------------------------------------------------------------- 내용 불러오기


def load_unit(uid):
    path = os.path.join(SRC, "content", uid + ".py")
    spec = importlib.util.spec_from_file_location("content_" + uid, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, SRC)
    spec.loader.exec_module(mod)
    return mod.UNIT, mod.SLIDES


def walk(elements):
    """본문 요소를 (접힌 블록 포함) 순서대로 낸다."""
    for el in elements:
        yield el
        if el["type"] == "more":
            yield from walk(el["body"])


def texts_of(el):
    """요소 안의 사람 글(검사용)."""
    t = el["type"]
    if t == "p" or t == "note" or t == "raw":
        return [el["html"]]
    if t == "h3":
        return [el["text"]]
    if t == "ul":
        return list(el["items"])
    if t == "table":
        return [c for c in el["head"]] + [c for r in el["rows"] for c in r if isinstance(c, str)]
    if t == "ask":
        return [el["q"]] + ([el["a"]] if el["a"] else [])
    if t == "cell":
        return [el["title"], el["code"]]
    if t == "more":
        return [el["summary"]]
    if t == "write":
        return [el["label"], el["prompt"]]
    if t == "flow":
        return [el["left"]] + list(el["rights"])
    return []


# ---------------------------------------------------------------- 검사


class Deck:
    def __init__(self, unit_ids=UNIT_IDS):
        self.units = []        # [{id, short, title, ref, slides:[...]}]
        self.slides = []       # 전체 순서
        self.cells = []        # 전체 순서의 셀 (dict), 'unit','slide' 키 추가
        self.errors = []
        self.warnings = []
        for uid in unit_ids:
            try:
                u, slides = load_unit(uid)
            except Exception as e:  # noqa
                self.errors.append(f"{uid}: 내용 파일을 읽지 못함: {type(e).__name__}: {e}")
                continue
            u = dict(u)
            u["slides"] = slides
            if u["id"] != uid:
                self.errors.append(f"{uid}: UNIT id가 파일 이름과 다름 ({u['id']})")
            self.units.append(u)
            for i, s in enumerate(slides):
                s["unit"] = uid
                s["key"] = f"{uid}-{i + 1}"
                self.slides.append(s)
                for el in walk(s["body"]):
                    if el["type"] == "cell":
                        el["unit"] = uid
                        el["slide"] = s["key"]
                        self.cells.append(el)
        self.analyze()
        self.validate()

    # ---- 셀 의존
    def analyze(self):
        seen = {}
        for c in self.cells:
            if c["id"] in seen:
                self.errors.append(f"{c['slide']}: 셀 id 중복 {c['id']}")
            seen[c["id"]] = c
            c["syntax"] = r_check_syntax(c["code"])
            c["defs"], c["uses"], c["pkgs"] = r_analyze(c["code"])
        index = {c["id"]: i for i, c in enumerate(self.cells)}
        for i, c in enumerate(self.cells):
            prov = {}
            missing = []
            for v in c["uses"]:
                if v in BUILTIN_DATA or v in R_FUNS:
                    continue
                P = None
                for j in range(i - 1, -1, -1):
                    d = self.cells[j]
                    if d["noprov"]:
                        continue
                    if v in d["defs"]:
                        P = d["id"]
                        break
                if P:
                    prov[v] = P
                else:
                    missing.append(v)
            c["prov"] = prov
            c["imports"] = [v for v in c["uses"] if v in prov]
            c["missing"] = missing
            needs = []
            for P in list(prov.values()) + list(c["needs"]):
                if P not in index:
                    self.errors.append(f"{c['id']}: needs에 적은 셀 {P}가 없음")
                    continue
                if index[P] >= i:
                    self.errors.append(f"{c['id']}: needs에 적은 셀 {P}가 뒤에 있음")
                    continue
                if P not in needs:
                    needs.append(P)
            c["needs_all"] = sorted(needs, key=lambda x: index[x])
        # closure
        for c in self.cells:
            clos = []

            def add(x):
                for d in self.cells[index[x]]["needs_all"]:
                    if d not in clos:
                        add(d)
                        clos.append(d)
            add(c["id"])
            c["closure"] = sorted(clos, key=lambda x: index[x])

    # ---- 규칙
    def validate(self):
        E, W = self.errors, self.warnings
        write_keys = set()
        for u in self.units:
            uid = u["id"]
            if uid != "U0":
                if not u["slides"]:
                    E.append(f"{uid}: 화면이 없음")
                    continue
                if u["slides"][0].get("kind") != "opener":
                    E.append(f"{uid}: 첫 화면은 kind='opener'여야 함")
                if u["slides"][-1].get("kind") != "wrap":
                    E.append(f"{uid}: 마지막 화면은 kind='wrap'이어야 함")
                if len(u["slides"]) > 9:
                    W.append(f"{uid}: 화면이 {len(u['slides'])}장 (9장 이하를 권함)")
                if not u.get("ref"):
                    W.append(f"{uid}: UNIT ref(강의 장)가 비어 있음")
            for s in u["slides"]:
                key = s["key"]
                if s.get("ref") is not None and not re.match(r"^\d장", s["ref"]):
                    E.append(f"{key}: ref는 '1장 p.8–9' 꼴이어야 함: {s['ref']!r}")
                ncell = sum(1 for el in s["body"] if el["type"] == "cell")
                if ncell > 3:
                    W.append(f"{key}: 접히지 않은 셀이 {ncell}개 (3개 이하를 권함)")
                for el in walk(s["body"]):
                    where = f"{key}" + (f" 셀 {el['id']}" if el["type"] == "cell" else "")
                    for t in [s["title"]] + texts_of(el):
                        for pat, why in FORBIDDEN:
                            m = re.search(pat, t)
                            if m:
                                E.append(f"{where}: {why}: …{t[max(0, m.start() - 25):m.end() + 25]!r}…")
                    if el["type"] == "p" and len(re.sub(r"<[^>]+>", "", el["html"])) > 700:
                        W.append(f"{key}: 문단이 깁니다 ({len(el['html'])}자). 나누거나 줄이세요")
                    if el["type"] == "ask" and "?" not in el["q"]:
                        E.append(f"{key}: ask 질문에 물음표가 없음: {el['q'][:40]!r}")
                    if el["type"] == "write":
                        if el["key"] in write_keys:
                            E.append(f"{key}: write key 중복 {el['key']}")
                        write_keys.add(el["key"])
                    if el["type"] == "cell":
                        c = el
                        if not re.match(r"^u\d_[a-z0-9_]+$", c["id"]) or not c["id"].startswith(uid.lower() + "_"):
                            E.append(f"{key}: 셀 id는 '{uid.lower()}_이름' 꼴이어야 함: {c['id']}")
                        for e in c["syntax"]:
                            E.append(f"{key} 셀 {c['id']}: R 코드: {e}")
                        for v in c["missing"]:
                            E.append(f"{key} 셀 {c['id']}: 앞 셀에서 만들지 않은 이름을 씀: {v}")
                        for ln in c["code"].split("\n"):
                            if len(ln) > 96:
                                W.append(f"{key} 셀 {c['id']}: 코드 줄이 깁니다 ({len(ln)}자): {ln[:40]!r}…")
                        if not c["code"].strip():
                            E.append(f"{key} 셀 {c['id']}: 코드가 비어 있음")

    def report(self):
        for e in self.errors:
            print("오류:", e)
        for w in self.warnings:
            print("주의:", w)
        n_slides = len(self.slides)
        print(f"화면 {n_slides}장, 셀 {len(self.cells)}개, 오류 {len(self.errors)}, 주의 {len(self.warnings)}")
        return not self.errors

    def cell_table(self):
        for c in self.cells:
            print(f"{c['id']:14s} {c['slide']:6s} defs={c['defs']} imports={c['imports']} needs={c['needs_all']} pkgs={c['pkgs']}")


# ---------------------------------------------------------------- HTML


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """본문 문자열: HTML을 그대로 쓴다 (저자가 적은 것)."""
    return s


class Renderer:
    def __init__(self, deck):
        self.deck = deck
        self.cell_by_id = {c["id"]: c for c in deck.cells}
        self.unit_by_id = {u["id"]: u for u in deck.units}

    def unit_label(self, uid):
        u = self.unit_by_id[uid]
        return "시작" if uid == "U0" else f"{uid} {u['short']}"

    def slide(self, s):
        uid = s["unit"]
        u = self.unit_by_id[uid]
        kind = s.get("kind") or ""
        cls = "slide" + (f" {kind}" if kind else "")
        plain_title = re.sub("<[^>]+>", "", s["title"])
        list_title = ("정리 · " + plain_title) if kind == "wrap" else plain_title
        h2 = (f'<h2><span class="pre">정리 · </span>{inline(s["title"])}</h2>' if kind == "wrap" else f'<h2>{inline(s["title"])}</h2>')
        parts = [f'<section class="{cls}" id="s-{s["key"]}" data-unit="{uid}" data-key="{s["key"]}" data-title="{esc(list_title)}" hidden>']
        if uid == "U0":
            parts.append(f'<header class="shead">{h2}</header>')
        elif kind == "opener":
            parts.append(f'<header class="shead"><div class="sunit">{uid} · {esc(u.get("ref", ""))}</div>{h2}</header>')
        else:
            parts.append(f'<header class="shead"><div class="sunit">{esc(self.unit_label(uid))}</div>{h2}</header>')
        parts.append('<div class="sbody">')
        parts.extend(self.element(el, s) for el in s["body"])
        parts.append("</div>")
        if s.get("ref"):
            parts.append(f'<footer class="sfoot">강의 {esc(s["ref"])}</footer>')
        parts.append("</section>")
        return "\n".join(parts)

    def element(self, el, s, tcount=None):
        t = el["type"]
        if t == "p":
            return f"<p>{inline(el['html'])}</p>"
        if t == "note":
            return f'<p class="note">{inline(el["html"])}</p>'
        if t == "raw":
            return el["html"]
        if t == "h3":
            return f"<h3>{inline(el['text'])}</h3>"
        if t == "ul":
            return "<ul>" + "".join(f"<li>{inline(x)}</li>" for x in el["items"]) + "</ul>"
        if t == "table":
            return self.table(el, s)
        if t == "ask":
            a = f'<details><summary>답</summary><div class="ans">{inline(el["a"])}</div></details>' if el["a"] else ""
            return f'<div class="ask"><p class="q">{inline(el["q"])}</p>{a}</div>'
        if t == "more":
            body = "".join(self.element(x, s) for x in el["body"])
            return f'<details class="more"><summary>{inline(el["summary"])}</summary><div class="morebody">{body}</div></details>'
        if t == "write":
            return (f'<div class="write"><div class="wlabel">{inline(el["label"])}</div><div class="wprompt">{inline(el["prompt"])}</div>'
                    f'<textarea class="note-input" rows="4" data-key="w:{esc(el["key"])}" data-label="{esc(re.sub("<[^>]+>", "", el["label"]))}" '
                    f'aria-label="{esc(re.sub("<[^>]+>", "", el["label"]))}"></textarea></div>')
        if t == "flow":
            rights = "".join(f'<div class="fbox">{inline(r)}</div>' for r in el["rights"])
            return f'<div class="flow"><div class="fbox">{inline(el["left"])}</div><div class="farrow">→</div><div class="fcol">{rights}</div></div>'
        if t == "cell":
            return self.cell(el)
        raise ValueError(f"알 수 없는 요소 {t}")

    def table(self, el, s):
        s.setdefault("_tcount", 0)
        ti = s["_tcount"]
        s["_tcount"] += 1
        head = "".join(f"<th>{inline(h)}</th>" for h in el["head"])
        rows = []
        for ri, r in enumerate(el["rows"]):
            cells = []
            for ci, c in enumerate(r):
                if isinstance(c, str):
                    cells.append(f"<td>{inline(c)}</td>")
                else:
                    rh = re.sub("<[^>]+>", "", str(r[0])) if isinstance(r[0], str) else ""
                    ch = re.sub("<[^>]+>", "", el["head"][ci]) if ci < len(el["head"]) else ""
                    label = f"{rh} · {ch}".strip(" ·")
                    key = f"{s['key']}-t{ti}-{ri}-{ci}"
                    cells.append(f'<td><textarea class="blankcell note-input" rows="2" data-key="{esc(key)}" data-label="{esc(label)}" aria-label="{esc(label)}"></textarea></td>')
            rows.append("<tr>" + "".join(cells) + "</tr>")
        cls = "t" + ("" if el.get("first_bold", True) else " plain")
        return f'<div class="tblwrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'

    def cell(self, c):
        needs = ""
        if c["needs_all"]:
            links = []
            for d in c["needs_all"]:
                dc = self.cell_by_id[d]
                other = f' <span class="nu">[{dc["unit"]}]</span>' if dc["unit"] != c["unit"] else ""
                links.append(f'<a data-goto-cell="{d}">{inline(dc["title"])}</a>{other}')
            needs = f'<div class="cneeds">앞 셀: {" · ".join(links)}</div>'
        rows = c["code"].count("\n") + 1
        return (
            f'<div class="cell" id="cell-{c["id"]}" data-cell="{c["id"]}">'
            f'<div class="chead"><span class="ctitle">{inline(c["title"])}</span>'
            f'<span class="cbtns"><button type="button" class="btn run" title="실행 (Ctrl+Enter / ⌘+Enter)">▶ 실행</button>'
            f'<button type="button" class="btn reset" title="코드를 처음 상태로 되돌리기" aria-label="코드 되돌리기">↺</button></span></div>'
            f'{needs}'
            f'<div class="editor"><pre class="hl" aria-hidden="true"></pre>'
            f'<textarea class="code" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off" rows="{rows}" '
            f'aria-label="R 코드: {esc(re.sub("<[^>]+>", "", c["title"]))}">{esc(c["code"])}</textarea></div>'
            f'<div class="cstatus" aria-live="polite"></div><div class="out"></div></div>'
        )

    def topbar(self):
        tabs = []
        for u in self.deck.units:
            uid = u["id"]
            if uid == "U0":
                tabs.append(f'<button type="button" data-unit-tab="U0" title="시작">시작</button>')
            else:
                tabs.append(f'<button type="button" data-unit-tab="{uid}" title="{esc(uid + " " + u["title"])}">{uid}<span class="tabname"> {esc(u["short"])}</span></button>')
        return (
            '<header class="topbar">'
            f'<div class="brand">{TITLE}</div>'
            f'<nav class="units" aria-label="단원">{"".join(tabs)}</nav>'
            '<div class="rstatus" id="rstatus" data-state="loading" role="status" aria-live="polite"><span class="dot"></span><span class="txt">R 준비 중…</span></div>'
            '<button type="button" class="tbtn" id="btn-help" aria-haspopup="dialog" title="사용법">도움말</button>'
            '<button type="button" class="tbtn" id="btn-toc" aria-haspopup="dialog">목록</button>'
            '<button type="button" class="tbtn" id="btn-reset" title="R 세션의 변수를 모두 지우고 자료만 다시 읽습니다">R 초기화</button>'
            '</header>'
        )

    def cells_json(self):
        out = {}
        for c in self.deck.cells:
            out[c["id"]] = {
                "id": c["id"], "unit": c["unit"], "title": re.sub("<[^>]+>", "", c["title"]),
                "needs": c["needs_all"], "defs": [] if c["noprov"] else c["defs"], "imports": c["imports"],
                "prov": c["prov"], "closure": c["closure"], "gw": c["gw"], "gh": c["gh"], "pkgs": c["pkgs"],
            }
        return out

    def build(self):
        css = open(os.path.join(SRC, "style.css"), encoding="utf-8").read()
        js = open(os.path.join(SRC, "runtime.js"), encoding="utf-8").read()
        run_r = open(os.path.join(SRC, "run.R"), encoding="utf-8").read()
        setup_r = open(os.path.join(SRC, "setup.R"), encoding="utf-8").read()
        help_html = open(os.path.join(SRC, "help.html"), encoding="utf-8").read()
        season_cell = next((c["id"] for c in self.deck.cells if "SIN" in c["defs"] and "time_st" in c["defs"]), None)
        cfg = {
            "version": VERSION,
            "webr": [
                {"mod": "https://webr.r-wasm.org/v0.6.0/webr.mjs", "base": "https://webr.r-wasm.org/v0.6.0/"},
                {"mod": "https://webr.r-wasm.org/v0.6.0/webr.js", "base": "https://webr.r-wasm.org/v0.6.0/"},
                {"mod": "https://cdn.jsdelivr.net/npm/webr@0.6.0/dist/webr.js", "base": "https://cdn.jsdelivr.net/npm/webr@0.6.0/dist/"},
            ],
            "repoAttempts": [["https://repo.r-wasm.org/", "https://cran.r-universe.dev"], ["https://cran.r-universe.dev"], ["https://repo.r-wasm.org/"]],
            "dataFiles": DATA_FILES,
            "basePkgs": ["base", "stats", "graphics", "grDevices", "utils", "datasets", "methods", "grid", "splines", "stats4", "tools", "compiler", "parallel"],
            "seasonCell": season_cell,
        }
        units = [{"id": u["id"], "short": u["short"], "title": u["title"]} for u in self.deck.units]
        data_scripts = []
        for name in DATA_FILES + EXTRA_FILES:
            txt = open(os.path.join(SRC, "data", name), encoding="utf-8").read()
            data_scripts.append(f'<script type="text/plain" id="data-{name}">{txt}</script>')
        slides = "\n".join(self.slide(s) for s in self.deck.slides)
        doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="강의 1–5장 webR 실습: 주 자료 BTCUSDT 일별 거래 횟수, 대조 자료 QQQ 월말 종가">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Gothic+Coding:wght@400;700&display=swap" media="print" onload="this.media='all'">
<style>
{css}
</style>
</head>
<body>
{self.topbar()}
<main id="deck">
{slides}
</main>
<footer class="navbar">
  <button type="button" class="nbtn" id="btn-prev">◀ 이전</button>
  <div class="pos" id="pos"></div>
  <div class="progress" aria-hidden="true"><div class="bar" id="bar"></div></div>
  <button type="button" class="nbtn" id="btn-next">다음 ▶</button>
</footer>
<div id="toc" hidden role="dialog" aria-label="화면 목록"><div class="panel"><button type="button" class="tbtn close" id="btn-toc-close">닫기</button><div id="toc-body"></div></div></div>
<div id="help" hidden role="dialog" aria-label="사용법"><div class="panel"><button type="button" class="tbtn close" id="btn-help-close">닫기</button>
{help_html}
</div></div>
{"".join(data_scripts)}
<script>
window.DECK_CONFIG = {json.dumps(cfg, ensure_ascii=False)};
window.DECK_CELLS = {json.dumps(self.cells_json(), ensure_ascii=False)};
window.DECK_UNITS = {json.dumps(units, ensure_ascii=False)};
window.DECK_RUN_R = {json.dumps(run_r, ensure_ascii=False)};
window.DECK_SETUP_R = {json.dumps(setup_r, ensure_ascii=False)};
</script>
<script type="module">
{js}
</script>
</body>
</html>
"""
        return doc


# ---------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", nargs="?", const="ALL", default=None, help="검사만. 단원 id를 주면 그 단원만")
    ap.add_argument("--cells", action="store_true", help="셀 의존 관계 표 출력")
    ap.add_argument("-o", "--out", default=OUT)
    ap.add_argument("--units", default=None, help="이 단원만으로 생성 (시험용), 예 U0,U2")
    a = ap.parse_args()
    if a.check and a.check != "ALL":
        ids = [x.strip().upper() for x in a.check.split(",")]
        # 한 단원만 검사할 때도 앞 단원이 만든 변수를 알아야 하므로 앞 단원은 함께 읽는다 (파일이 있을 때)
        ids_all = [u for u in UNIT_IDS if u in ids or (u < max(ids) and os.path.exists(os.path.join(SRC, "content", u + ".py")))]
        deck = Deck(ids_all)
        deck.errors = [e for e in deck.errors if any(e.startswith(i) or f" {i.lower()}_" in e or e.startswith(i.lower() + "_") for i in ids)]
        deck.warnings = [w for w in deck.warnings if any(w.startswith(i) or w.startswith(i.lower() + "_") for i in ids)]
        ok = deck.report()
        if a.cells:
            deck.cell_table()
        sys.exit(0 if ok else 1)
    deck = Deck([u.strip().upper() for u in a.units.split(",")]) if a.units else Deck()
    ok = deck.report()
    if a.cells:
        deck.cell_table()
    if a.check:
        sys.exit(0 if ok else 1)
    if not ok:
        print("오류가 있어 생성하지 않음")
        sys.exit(1)
    doc = Renderer(deck).build()
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"생성: {a.out} ({len(doc.encode('utf-8')) // 1024} KB)")


if __name__ == "__main__":
    main()
