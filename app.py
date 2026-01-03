import base64
import json
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================
# KONFIG
# =========================
APP_TZ = ZoneInfo("Europe/Warsaw")
GLOBAL_START = date(2026, 1, 1)
TOTAL_DAYS = 14

st.set_page_config(
    page_title="SeduceMe — 14 dni",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

UID_STORAGE_KEY = "seduceme_uid"

# =========================
# CSS (skrót, ale z Twoimi mikro-animacjami)
# =========================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,600;1,700&family=Montserrat:wght@300;400;600;700&display=swap');

:root{ --bg:#1A1A1A; --accent:#C1272D; --heading:#7B1E24; --gold:#D4AF37; --muted:rgba(255,255,255,.68); --muted2:rgba(255,255,255,.52); }

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(900px 480px at 18% 8%, rgba(193,39,45,.18), transparent 60%),
    radial-gradient(780px 440px at 85% 22%, rgba(212,175,55,.10), transparent 58%),
    var(--bg);
  color:white; font-family:Montserrat,system-ui; overflow-x:hidden;
}
[data-testid="stHeader"]{ background:transparent; }

/* delikatne światło */
[data-testid="stAppViewContainer"]::before{
  content:""; position:fixed; inset:-20%; pointer-events:none;
  background:
    radial-gradient(540px 240px at 20% 20%, rgba(212,175,55,.10), transparent 60%),
    radial-gradient(520px 260px at 70% 35%, rgba(193,39,45,.14), transparent 62%),
    radial-gradient(480px 220px at 55% 80%, rgba(212,175,55,.08), transparent 60%);
  animation: sdmLight 10s ease-in-out infinite alternate; opacity:.9;
}
@keyframes sdmLight{ from{transform:translate3d(0,0,0) scale(1);} to{transform:translate3d(-18px,12px,0) scale(1.02);} }

/* iskry */
[data-testid="stAppViewContainer"]::after{
  content:""; position:fixed; inset:0; pointer-events:none; opacity:.55;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(212,175,55,.14) 0 1px, transparent 2px),
    radial-gradient(circle at 30% 70%, rgba(255,255,255,.08) 0 1px, transparent 2px),
    radial-gradient(circle at 60% 30%, rgba(193,39,45,.12) 0 1px, transparent 2px),
    radial-gradient(circle at 80% 60%, rgba(212,175,55,.10) 0 1px, transparent 2px),
    radial-gradient(circle at 50% 90%, rgba(255,255,255,.06) 0 1px, transparent 2px);
  background-size:320px 320px; animation: sdmSparks 12s linear infinite;
}
@keyframes sdmSparks{ from{background-position:0 0;} to{background-position:320px 640px;} }

.sdm-wrap{ max-width:1120px; margin:0 auto; padding:.5rem 0 2.5rem; }
.sdm-logo{
  font-family:"Playfair Display",serif; font-style:italic; letter-spacing:.5px;
  font-size:64px; text-align:center;
  background:linear-gradient(90deg,var(--accent),var(--heading));
  -webkit-background-clip:text; color:transparent;
  text-shadow:0 0 18px rgba(212,175,55,.20);
  margin:.6rem 0 .3rem;
}
.sdm-subtitle{ text-align:center; color:var(--muted); margin:0 0 1.2rem; font-weight:300; }
.sdm-card{
  background:linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01));
  border:1px solid rgba(255,255,255,.08); border-radius:22px; padding:20px;
  box-shadow:0 14px 40px rgba(0,0,0,.45);
}
.sdm-h2{ font-family:"Playfair Display",serif; font-style:italic; color:var(--heading); margin:0 0 8px; font-size:34px; }
.sdm-task{ color:rgba(255,255,255,.82); font-size:17px; line-height:1.65; margin:0 0 14px; }
.sdm-meta{ display:flex; gap:10px; flex-wrap:wrap; color:var(--muted2); font-size:14px; margin-top:6px; }
.sdm-pill{ display:inline-flex; align-items:center; gap:8px; padding:7px 10px; border-radius:999px; background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); }
.sdm-progress{ margin:10px 0 18px; padding:10px 12px; border-radius:14px; background:rgba(0,0,0,.18); border:1px solid rgba(255,255,255,.06); }
.sdm-bar{ height:8px; border-radius:999px; background:rgba(255,255,255,.08); overflow:hidden; }
.sdm-bar > div{ height:100%; background:linear-gradient(90deg,var(--accent),var(--heading)); border-radius:999px; box-shadow:0 0 18px rgba(193,39,45,.35); transition: width .35s ease; }
div.stButton > button{
  border-radius:14px!important; border:1px solid rgba(212,175,55,.42)!important;
  background: radial-gradient(120px 40px at 20% 20%, rgba(255,255,255,.18), transparent 60%),
              linear-gradient(90deg,var(--accent),var(--heading))!important;
  color:#F6E7B5!important; font-weight:700!important; padding:.65rem 1.05rem!important;
  box-shadow:0 10px 28px rgba(0,0,0,.45)!important;
}
</style>
"""

# =========================
# 14 dni (treści)
# =========================
DAYS = [
    {"day": 1, "title": "Ogniste Spojrzenia", "task": "Spójrzcie sobie głęboko w oczy i powoli zbliżajcie się do pocałunku. Każdy kolejny pocałunek jest dłuższy, bardziej gorący i pełen napięcia. Eksplorujcie usta, szyję i ramiona, ciesząc się każdym dotykiem i oddechem partnera.", "emoji": "🔥", "duration_min": 5},
    {"day": 2, "title": "Dotyk Zakazany", "task": "Masujcie się nawzajem, prowadząc dłonie przez strefy najbardziej podniecające – uda, pośladki, szyję, klatkę piersiową. Pozwólcie dłoniom „przypadkowo” odkrywać więcej, igrając z przyjemnością i oczekiwaniem.", "emoji": "💋", "duration_min": 10},
    {"day": 3, "title": "Szepty Rozkoszy", "task": "Szeptajcie sobie do ucha fantazje, które nigdy nie padły na głos. Niech każde słowo rozpala ciało, a każdy szept kończy się powolnym, rozkosznym pocałunkiem w szyję, ucho lub wargi.", "emoji": "🖤", "duration_min": 8},
    {"day": 4, "title": "Kusiciel i Uległy", "task": "Jedna osoba prowadzi grę: decyduje, gdzie i jak dotyka, tempo pocałunków, nacisk dłoni. Druga poddaje się całkowicie. Po 10–15 minutach zamieńcie role.", "emoji": "👑", "duration_min": 15},
    {"day": 5, "title": "Smak Ciebie", "task": "Eksplorujcie siebie nawzajem poprzez smak: lody, czekolada, owoce, bita śmietana – pozwólcie ustom i językowi powoli wędrować po najbardziej erotycznych miejscach.", "emoji": "🍓", "duration_min": 15},
    {"day": 6, "title": "Nieprzerwany Pocałunek", "task": "Zanurzcie się w powolnym, długim pocałunku, całując i pieszcząc ciało partnera bez przerwy przez 10–15 minut. Nie zmieniajcie tempa – pozwólcie, aby napięcie rosło z każdą sekundą.", "emoji": "💋", "duration_min": 15},
    {"day": 7, "title": "Rozgrzany Dotyk", "task": "Podarujcie sobie zmysłowy masaż z olejkiem lub balsamem. Powoli przesuwajcie dłonie po całym ciele, zatrzymując się w miejscach, które wywołują najwięcej przyjemności.", "emoji": "🕯️", "duration_min": 20},
    {"day": 8, "title": "Gra Napięcia", "task": "Jedna osoba prowokuje drugą do ekstremalnego pożądania, zatrzymując się tuż przed spełnieniem. Odwracajcie role i powtarzajcie kilka razy, ile wytrzymacie.", "emoji": "⚡", "duration_min": 15},
    {"day": 9, "title": "Cisza i Oddychanie", "task": "Leżcie naprzeciw siebie, ciało przy ciele. Jedna osoba przesuwa dłonie powoli po ciele partnera, blisko najbardziej podniecających miejsc, bez bezpośredniego dotyku. Po kilku minutach zamieńcie role.", "emoji": "🌙", "duration_min": 10},
    {"day": 10, "title": "Dotyk w Cieniu", "task": "Jedna osoba ma zasłonięte oczy i całkowicie oddaje się prowadzeniu. Druga eksploruje ciało ustami i dłonią, odkrywając miejsca, które najbardziej rozpędzają krew i przyspieszają oddech.", "emoji": "🎭", "duration_min": 15},
    {"day": 11, "title": "Zmysłowy Tekst", "task": "Przez cały dzień wysyłajcie sobie krótkie, pikantne instrukcje (max. 3 wiadomości na osobę). Wieczorem zrealizujcie jedną z tych fantazji.", "emoji": "📩", "duration_min": 5},
    {"day": 12, "title": "Tajemniczy Kusiciel", "task": "Każde z Was wybiera jedną cechę, którą dziś przejmuje (np. pewność siebie, kontrolę, powolność). Nie mówcie tego na głos. Pozwólcie, by cecha kierowała każdym dotykiem i spojrzeniem.", "emoji": "🦂", "duration_min": 12},
    {"day": 13, "title": "Pełne Odkrycie", "task": "Powiedzcie sobie po jednym, skrywanym sekrecie lub fantazji — jedno zdanie, bez kompromisów. Następnie druga osoba realizuje dokładnie to, co usłyszała — powoli, świadomie, z maksymalnym napięciem.", "emoji": "🔓", "duration_min": 20},
    {"day": 14, "title": "Rytuał Rozkoszy", "task": "Dziś możecie wszystko. Każdy pocałunek, dotyk, fantazja, oddech jest dozwolony. Połączcie wszystkie zmysły: dotyk, smak, zapach, słowo, spojrzenie. Dajcie się ponieść namiętności i zanurzcie się w siebie nawzajem.", "emoji": "✨", "duration_min": 30},
]

# =========================
# Czas / odblokowanie
# =========================
def now_local() -> datetime:
    return datetime.now(APP_TZ)

def today_local() -> date:
    return now_local().date()

def active_day_global() -> int:
    if today_local() < GLOBAL_START:
        return 0
    delta = (today_local() - GLOBAL_START).days
    return max(1, min(TOTAL_DAYS, delta + 1))

def is_unlocked(day: int) -> bool:
    return day <= active_day_global()

def progress_percent() -> int:
    d = active_day_global()
    if d <= 0:
        return 0
    return int(round((d / TOTAL_DAYS) * 100))

# =========================
# UID: JS ustawia URL jeśli brak uid, Python tylko czyta URL
# =========================
def bootstrap_uid_from_localstorage():
    """
    Jeśli URL nie ma uid, JS:
    - czyta localStorage
    - jeśli brak -> generuje UUID i zapisuje
    - dopisuje ?uid=... do URL i robi reload
    """
    # Robimy to zawsze, ale JS sam sprawdzi czy uid jest w URL.
    components.html(
        f"""
        <script>
        (function() {{
          const KEY = "{UID_STORAGE_KEY}";
          const url = new URL(window.location.href);
          const hasUid = url.searchParams.get("uid");
          if (hasUid) {{
            try {{ localStorage.setItem(KEY, hasUid); }} catch(e) {{}}
            return;
          }}
          let uid = null;
          try {{
            uid = localStorage.getItem(KEY);
            if (!uid) {{
              uid = (crypto.randomUUID ? crypto.randomUUID()
                : (Date.now().toString(36) + Math.random().toString(36).slice(2)));
              localStorage.setItem(KEY, uid);
            }}
          }} catch(e) {{
            uid = (Date.now().toString(36) + Math.random().toString(36).slice(2));
          }}
          url.searchParams.set("uid", uid);
          window.location.replace(url.toString());
        }})();
        </script>
        """,
        height=0,
    )

def ensure_uid() -> str:
    bootstrap_uid_from_localstorage()

    uid = st.query_params.get("uid")
    # Bezpieczeństwo: nigdy nie akceptuj dziwnych wartości (DeltaGenerator itp.)
    if isinstance(uid, str) and 8 <= len(uid) <= 80 and "DeltaGenerator" not in uid:
        st.session_state["user_id"] = uid
        return uid

    # Jeżeli jeszcze nie zdążyło przeładować (pierwszy render), zatrzymaj render
    st.stop()

# =========================
# GitHub storage
# =========================
def _secrets_ok() -> bool:
    return ("GITHUB_TOKEN" in st.secrets) and ("GITHUB_REPO" in st.secrets)

def _gh_repo() -> str:
    return st.secrets["GITHUB_REPO"]

def _gh_branch() -> str:
    return st.secrets.get("GITHUB_BRANCH", "main")

def _gh_headers() -> dict:
    return {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "seduceme-streamlit",
    }

def _gh_url(path: str) -> str:
    return f"https://api.github.com/repos/{_gh_repo()}/contents/{path}"

def gh_get_json(path: str) -> tuple[dict | None, str | None]:
    r = requests.get(_gh_url(path), headers=_gh_headers(), params={"ref": _gh_branch()}, timeout=20)
    if r.status_code == 404:
        return None, None
    r.raise_for_status()
    data = r.json()
    content_b64 = data.get("content", "")
    raw = base64.b64decode(content_b64).decode("utf-8") if content_b64 else "{}"
    return json.loads(raw), data.get("sha")

def gh_put_json(path: str, obj: dict, sha: str | None) -> None:
    raw = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
    payload = {
        "message": f"Update {path}",
        "content": base64.b64encode(raw).decode("utf-8"),
        "branch": _gh_branch(),
    }
    if sha:
        payload["sha"] = sha

    r = requests.put(_gh_url(path), headers=_gh_headers(), json=payload, timeout=20)
    if r.status_code in (409, 422):
        _, latest_sha = gh_get_json(path)
        payload.pop("sha", None)
        if latest_sha:
            payload["sha"] = latest_sha
        r2 = requests.put(_gh_url(path), headers=_gh_headers(), json=payload, timeout=20)
        r2.raise_for_status()
        return
    r.raise_for_status()

def gh_delete_file(path: str, sha: str) -> None:
    payload = {"message": f"Delete {path}", "sha": sha, "branch": _gh_branch()}
    r = requests.delete(_gh_url(path), headers=_gh_headers(), json=payload, timeout=20)
    if r.status_code == 404:
        return
    r.raise_for_status()

# =========================
# Progres
# =========================
@dataclass
class ProgressState:
    completed: set[int]
    favorites: set[int]
    reactions: dict[int, str]
    sha: str | None

def progress_path(uid: str) -> str:
    return f"progress/{uid}.json"

def load_progress(uid: str) -> ProgressState:
    if not _secrets_ok():
        return ProgressState(set(), set(), {}, None)

    obj, sha = gh_get_json(progress_path(uid))
    if not obj:
        return ProgressState(set(), set(), {}, None)

    completed = set(int(x) for x in obj.get("completed", []) if str(x).isdigit())
    favorites = set(int(x) for x in obj.get("favorites", []) if str(x).isdigit())
    reactions_raw = obj.get("reactions", {})
    reactions: dict[int, str] = {}
    if isinstance(reactions_raw, dict):
        for k, v in reactions_raw.items():
            try:
                dk = int(k)
            except Exception:
                continue
            if isinstance(v, str) and v.strip():
                reactions[dk] = v

    return ProgressState(completed, favorites, reactions, sha)

def save_progress(uid: str, prog: ProgressState) -> ProgressState:
    obj = {
        "uid": uid,
        "updated_at": now_local().isoformat(),
        "completed": sorted(list(prog.completed)),
        "favorites": sorted(list(prog.favorites)),
        "reactions": {str(k): v for k, v in prog.reactions.items()},
        "schema_version": 1,
    }
    path = progress_path(uid)
    gh_put_json(path, obj, prog.sha)
    _, sha2 = gh_get_json(path)
    prog.sha = sha2 or prog.sha
    return prog

# =========================
# UI
# =========================
def render_progress_bar():
    d = active_day_global()
    pct = progress_percent()
    if d == 0:
        st.markdown(
            f"""
            <div class="sdm-progress">
              <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
                <div style="color:rgba(255,255,255,.78); font-size:14px;"><b>Start już wkrótce</b></div>
                <div style="color:rgba(255,255,255,.55); font-size:12px;">
                  Start globalny: {GLOBAL_START.isoformat()} (Europe/Warsaw)
                </div>
              </div>
              <div class="sdm-bar" style="margin-top:8px;"><div style="width:0%;"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        f"""
        <div class="sdm-progress">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div style="color:rgba(255,255,255,.78); font-size:14px;">
              Odblokowane: <b>Dzień {d}/{TOTAL_DAYS}</b>
            </div>
            <div style="color:rgba(255,255,255,.55); font-size:12px;">
              {pct}%
            </div>
          </div>
          <div class="sdm-bar" style="margin-top:8px;"><div style="width:{pct}%;"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar(uid: str, prog: ProgressState):
    with st.sidebar:
        st.markdown("### Informacje")
        st.caption(f"uid: {uid[:8]}…")
        st.caption(f"Start globalny: {GLOBAL_START.isoformat()}")
        st.caption(f"Dziś odblokowane: {active_day_global()}/{TOTAL_DAYS}")

        st.markdown("---")
        st.markdown("### Twój link (do przeniesienia na inne urządzenie)")
        st.code(st.get_url(), language="text")

        st.markdown("---")
        if _secrets_ok():
            st.caption(f"Repo storage: {_gh_repo()} ({_gh_branch()})")
            st.caption(f"Plik: {progress_path(uid)}")
        else:
            st.error("Brak secrets: GITHUB_TOKEN i/lub GITHUB_REPO — zapis nie działa.")

        st.markdown("---")
        if st.button("Reset (wyczyść mój progres)", type="secondary"):
            if not _secrets_ok():
                st.warning("Brak konfiguracji GitHub — nie mogę zresetować.")
            else:
                path = progress_path(uid)
                _, sha = gh_get_json(path)
                if sha:
                    gh_delete_file(path, sha)
                st.toast("Progres zresetowany", icon="🗑️")
                st.rerun()

def render_history(prog: ProgressState):
    st.markdown(
        """
        <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin-top:10px;">
          <div class="sdm-h2" style="margin:0;">Historia / Postępy</div>
          <div style="color:rgba(255,255,255,.55); font-size:13px;">Kliknij dzień (zablokowane nieaktywne)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    cols = st.columns(7)
    for i in range(TOTAL_DAYS):
        day = i + 1
        reacted = prog.reactions.get(day, DAYS[i]["emoji"])
        unlocked = is_unlocked(day)
        with cols[i % 7]:
            if st.button(f"{reacted}  Dzień {day}", key=f"grid_{day}", use_container_width=True, disabled=not unlocked):
                st.session_state.selected_day = day
                st.session_state.show_history = False
                st.rerun()
        if (i % 7) == 6 and i != TOTAL_DAYS - 1:
            cols = st.columns(7)

def render_day_card(uid: str, prog: ProgressState, day: int) -> ProgressState:
    data = DAYS[day - 1]
    unlocked = is_unlocked(day)

    if not unlocked:
        st.markdown(
            f"""
            <div class="sdm-card">
              <div class="sdm-h2">Dzień {day}: {data["title"]}</div>
              <div class="sdm-task">Ta karta jest jeszcze zablokowana — odblokowuje się jedna dziennie od {GLOBAL_START.isoformat()}.</div>
              <div class="sdm-meta">
                <span class="sdm-pill">🔒 Zablokowana</span>
                <span class="sdm-pill">Odblokowany dzień dziś: {active_day_global()}/{TOTAL_DAYS}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return prog

    reacted = prog.reactions.get(day, data["emoji"])
    is_done = day in prog.completed
    is_fav = day in prog.favorites

    st.markdown(
        f"""
        <div class="sdm-card">
          <div class="sdm-h2">Dzień {day}: {data["title"]}</div>
          <div class="sdm-task">{data["task"]}</div>
          <div class="sdm-meta">
            <span class="sdm-pill">⏱️ {data["duration_min"]}–{data["duration_min"]+5} min</span>
            <span class="sdm-pill">Reakcja: <b>{reacted}</b></span>
            <span class="sdm-pill">{'✅ Ukończone' if is_done else '⬜ Do wykonania'}</span>
            <span class="sdm-pill">{'❤️ Ulubione' if is_fav else '🤍 Ulubione'}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def persist(p: ProgressState) -> ProgressState:
        if not _secrets_ok():
            st.warning("Brak secrets GitHub — nie zapiszę zmian.")
            return p
        try:
            return save_progress(uid, p)
        except Exception as e:
            st.error(f"Błąd zapisu do GitHub: {e}")
            return p

    st.write("")
    a1, a2, a3, a4 = st.columns([1.1, 1, 1, 1.3])

    with a1:
        if st.button("Zapisz jako ukończone", use_container_width=True):
            prog.completed.add(day)
            prog = persist(prog)
            st.toast("Zapisano ✅", icon="✅")
            st.rerun()

    with a2:
        if st.button("❤️ / 🤍 Ulubione", use_container_width=True):
            if is_fav:
                prog.favorites.discard(day)
            else:
                prog.favorites.add(day)
            prog = persist(prog)
            st.rerun()

    with a3:
        emoji_options = ["🔥", "💋", "✨", "🖤", "⚡", "🕯️", "🌙", "🎭", "🍓", "🔓"]
        idx = emoji_options.index(reacted) if reacted in emoji_options else 0
        emoji = st.selectbox("Emoji reakcji", options=emoji_options, index=idx, key=f"react_{day}")
        if st.button("Zapisz reakcję", use_container_width=True):
            prog.reactions[day] = emoji
            prog = persist(prog)
            st.rerun()

    with a4:
        if st.button("Pokaż kolejny dzień", use_container_width=True):
            st.session_state.selected_day = min(TOTAL_DAYS, day + 1)
            st.rerun()

    return prog

# =========================
# MAIN
# =========================
def main():
    st.markdown(CSS, unsafe_allow_html=True)

    uid = ensure_uid()

    prog = ProgressState(set(), set(), {}, None)
    if _secrets_ok():
        try:
            prog = load_progress(uid)
        except Exception as e:
            st.error(f"Nie mogę pobrać progresu z GitHuba: {e}")

    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = 1

    render_sidebar(uid, prog)

    st.markdown('<div class="sdm-wrap">', unsafe_allow_html=True)
    st.markdown("<div class='sdm-logo' style='font-size:44px;'>SeduceMe</div>", unsafe_allow_html=True)
    st.markdown("<div class='sdm-subtitle'>Globalne odblokowanie od 1 stycznia 2026 — po dniu 14 wszystko odblokowane na stałe</div>", unsafe_allow_html=True)

    render_progress_bar()

    top1, top2, top4 = st.columns([1, 1, 1.4])
    with top1:
        if st.button("Dzisiaj", use_container_width=True):
            d = active_day_global()
            st.session_state.selected_day = 1 if d == 0 else d
            st.session_state.show_history = False
            st.rerun()
    with top2:
        if st.button("Historia", use_container_width=True):
            st.session_state.show_history = True
            st.rerun()
    with top4:
        st.markdown(
            f"<div style='text-align:right; padding-top:10px; color:rgba(255,255,255,.65); font-size:14px;'>Ukończone: <b>{len(prog.completed)}</b> / {TOTAL_DAYS}</div>",
            unsafe_allow_html=True,
        )

    st.write("")

    if st.session_state.show_history:
        render_history(prog)
    else:
        day = int(st.session_state.selected_day)
        day = max(1, min(TOTAL_DAYS, day))
        prog = render_day_card(uid, prog, day)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
