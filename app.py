# app.py
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, date
from zoneinfo import ZoneInfo

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# =========================
# KONFIG
# =========================
APP_TZ = ZoneInfo("Europe/Warsaw")

st.set_page_config(
    page_title="SeduceMe — 14 dni namiętności",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# DB (produkcyjnie: najlepiej na persistent volume)
DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "seduceme.db")

# Cookies (USTAW MOCNE HASŁO w prod, najlepiej z env var)
COOKIE_PASSWORD = os.environ.get("SEDUCEME_COOKIE_PASSWORD", "change-me-strong-password")
cookies = EncryptedCookieManager(prefix="seduceme_", password=COOKIE_PASSWORD)

# =========================
# DANE (14 DNI)
# =========================
DAYS = [
    {
        "day": 1,
        "title": "Ogniste Spojrzenia",
        "task": (
            "Spójrzcie sobie głęboko w oczy i powoli zbliżajcie się do pocałunku. "
            "Każdy kolejny pocałunek jest dłuższy, bardziej gorący i pełen napięcia. "
            "Eksplorujcie usta, szyję i ramiona, ciesząc się każdym dotykiem i oddechem partnera."
        ),
        "emoji": "🔥",
        "duration_min": 5,
    },
    {
        "day": 2,
        "title": "Dotyk Zakazany",
        "task": (
            "Masujcie się nawzajem, prowadząc dłonie przez strefy najbardziej podniecające – uda, pośladki, "
            "szyję, klatkę piersiową. Pozwólcie dłoniom „przypadkowo” odkrywać więcej, igrając z przyjemnością "
            "i oczekiwaniem."
        ),
        "emoji": "💋",
        "duration_min": 10,
    },
    {
        "day": 3,
        "title": "Szepty Rozkoszy",
        "task": (
            "Szeptajcie sobie do ucha fantazje, które nigdy nie padły na głos. Niech każde słowo rozpala ciało, "
            "a każdy szept kończy się powolnym, rozkosznym pocałunkiem w szyję, ucho lub wargi."
        ),
        "emoji": "🖤",
        "duration_min": 8,
    },
    {
        "day": 4,
        "title": "Kusiciel i Uległy",
        "task": (
            "Jedna osoba prowadzi grę: decyduje, gdzie i jak dotyka, tempo pocałunków, nacisk dłoni. "
            "Druga poddaje się całkowicie. Po 10–15 minutach zamieńcie role."
        ),
        "emoji": "👑",
        "duration_min": 15,
    },
    {
        "day": 5,
        "title": "Smak Ciebie",
        "task": (
            "Eksplorujcie siebie nawzajem poprzez smak: lody, czekolada, owoce, bita śmietana – "
            "pozwólcie ustom i językowi powoli wędrować po najbardziej erotycznych miejscach."
        ),
        "emoji": "🍓",
        "duration_min": 15,
    },
    {
        "day": 6,
        "title": "Nieprzerwany Pocałunek",
        "task": (
            "Zanurzcie się w powolnym, długim pocałunku, całując i pieszcząc ciało partnera bez przerwy przez "
            "10–15 minut. Nie zmieniajcie tempa – pozwólcie, aby napięcie rosło z każdą sekundą."
        ),
        "emoji": "💋",
        "duration_min": 15,
    },
    {
        "day": 7,
        "title": "Rozgrzany Dotyk",
        "task": (
            "Podarujcie sobie zmysłowy masaż z olejkiem lub balsamem. Powoli przesuwajcie dłonie po całym ciele, "
            "zatrzymując się w miejscach, które wywołują najwięcej przyjemności."
        ),
        "emoji": "🕯️",
        "duration_min": 20,
    },
    {
        "day": 8,
        "title": "Gra Napięcia",
        "task": (
            "Jedna osoba prowokuje drugą do ekstremalnego pożądania, zatrzymując się tuż przed spełnieniem. "
            "Odwracajcie role i powtarzajcie kilka razy, ile wytrzymacie."
        ),
        "emoji": "⚡",
        "duration_min": 15,
    },
    {
        "day": 9,
        "title": "Cisza i Oddychanie",
        "task": (
            "Leżcie naprzeciw siebie, ciało przy ciele. Jedna osoba przesuwa dłonie powoli po ciele partnera, "
            "blisko najbardziej podniecających miejsc, bez bezpośredniego dotyku. Po kilku minutach zamieńcie role."
        ),
        "emoji": "🌙",
        "duration_min": 10,
    },
    {
        "day": 10,
        "title": "Dotyk w Cieniu",
        "task": (
            "Jedna osoba ma zasłonięte oczy i całkowicie oddaje się prowadzeniu. Druga eksploruje ciało ustami i dłonią, "
            "odkrywając miejsca, które najbardziej rozpędzają krew i przyspieszają oddech."
        ),
        "emoji": "🎭",
        "duration_min": 15,
    },
    {
        "day": 11,
        "title": "Zmysłowy Tekst",
        "task": (
            "Przez cały dzień wysyłajcie sobie krótkie, pikantne instrukcje (max. 3 wiadomości na osobę). "
            "Wieczorem zrealizujcie jedną z tych fantazji."
        ),
        "emoji": "📩",
        "duration_min": 5,
    },
    {
        "day": 12,
        "title": "Tajemniczy Kusiciel",
        "task": (
            "Każde z Was wybiera jedną cechę, którą dziś przejmuje (np. pewność siebie, kontrolę, powolność). "
            "Nie mówcie tego na głos. Pozwólcie, by cecha kierowała każdym dotykiem i spojrzeniem."
        ),
        "emoji": "🦂",
        "duration_min": 12,
    },
    {
        "day": 13,
        "title": "Pełne Odkrycie",
        "task": (
            "Powiedzcie sobie po jednym, skrywanym sekrecie lub fantazji — jedno zdanie, bez kompromisów. "
            "Następnie druga osoba realizuje dokładnie to, co usłyszała — powoli, świadomie, z maksymalnym napięciem."
        ),
        "emoji": "🔓",
        "duration_min": 20,
    },
    {
        "day": 14,
        "title": "Rytuał Rozkoszy",
        "task": (
            "Dziś możecie wszystko. Każdy pocałunek, dotyk, fantazja, oddech jest dozwolony. "
            "Połączcie wszystkie zmysły: dotyk, smak, zapach, słowo, spojrzenie. "
            "Dajcie się ponieść namiętności i zanurzcie się w siebie nawzajem."
        ),
        "emoji": "✨",
        "duration_min": 30,
    },
]

# =========================
# CSS + mikro-animacje
# =========================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,600;1,700&family=Montserrat:wght@300;400;600;700&display=swap');

:root{
  --bg: #1A1A1A;
  --accent: #C1272D;
  --heading: #7B1E24;
  --gold: #D4AF37;
  --muted: rgba(255,255,255,.68);
  --muted2: rgba(255,255,255,.52);
}

html, body, [data-testid="stAppViewContainer"]{
  background:
    radial-gradient(900px 480px at 18% 8%, rgba(193,39,45,.18), transparent 60%),
    radial-gradient(780px 440px at 85% 22%, rgba(212,175,55,.10), transparent 58%),
    var(--bg);
  color: white;
  font-family: "Montserrat", system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  overflow-x: hidden;
}

[data-testid="stHeader"]{ background: transparent; }

/* delikatne "światło" */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset:-20%;
  pointer-events:none;
  background:
    radial-gradient(540px 240px at 20% 20%, rgba(212,175,55,.10), transparent 60%),
    radial-gradient(520px 260px at 70% 35%, rgba(193,39,45,.14), transparent 62%),
    radial-gradient(480px 220px at 55% 80%, rgba(212,175,55,.08), transparent 60%);
  animation: sdmLight 10s ease-in-out infinite alternate;
  opacity: .9;
}
@keyframes sdmLight{
  from{ transform: translate3d(0px, 0px, 0) scale(1); }
  to  { transform: translate3d(-18px, 12px, 0) scale(1.02); }
}

/* iskry */
[data-testid="stAppViewContainer"]::after{
  content:"";
  position: fixed;
  inset:0;
  pointer-events:none;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(212,175,55,.14) 0 1px, transparent 2px),
    radial-gradient(circle at 30% 70%, rgba(255,255,255,.08) 0 1px, transparent 2px),
    radial-gradient(circle at 60% 30%, rgba(193,39,45,.12) 0 1px, transparent 2px),
    radial-gradient(circle at 80% 60%, rgba(212,175,55,.10) 0 1px, transparent 2px),
    radial-gradient(circle at 50% 90%, rgba(255,255,255,.06) 0 1px, transparent 2px);
  background-size: 320px 320px;
  opacity: .55;
  animation: sdmSparks 12s linear infinite;
}
@keyframes sdmSparks{
  from{ background-position: 0 0; }
  to  { background-position: 320px 640px; }
}

.sdm-wrap{ max-width: 1120px; margin: 0 auto; padding: 0.5rem 0 2.5rem; }

.sdm-logo{
  font-family: "Playfair Display", serif;
  font-style: italic;
  letter-spacing: .5px;
  font-size: 64px;
  line-height: 1.0;
  text-align: center;
  background: linear-gradient(90deg, var(--accent), var(--heading));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  text-shadow: 0 0 18px rgba(212,175,55,.20);
  margin: 0.6rem 0 0.3rem;
}

.sdm-subtitle{
  text-align:center;
  color: var(--muted);
  margin: 0 0 1.2rem;
  font-weight: 300;
}

.sdm-hero{
  position: relative;
  border-radius: 26px;
  padding: 28px 26px;
  background:
     radial-gradient(700px 280px at 25% 20%, rgba(193,39,45,.22), transparent 62%),
     radial-gradient(700px 280px at 80% 40%, rgba(212,175,55,.10), transparent 60%),
     linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 18px 55px rgba(0,0,0,.50);
  overflow: hidden;
}

/* shimmer */
.sdm-hero::after{
  content:"";
  position:absolute;
  inset:-40%;
  background: linear-gradient(120deg, transparent 40%, rgba(255,255,255,.05) 50%, transparent 60%);
  transform: translateX(-35%);
  animation: sdmShimmer 6s ease-in-out infinite;
  pointer-events:none;
  opacity:.75;
}
@keyframes sdmShimmer{
  0%   { transform: translateX(-35%) rotate(8deg); }
  50%  { transform: translateX(35%) rotate(8deg); }
  100% { transform: translateX(-35%) rotate(8deg); }
}

.sdm-card{
  background: linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,.01));
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 22px;
  padding: 20px 20px;
  box-shadow: 0 14px 40px rgba(0,0,0,.45);
}

.sdm-h2{
  font-family: "Playfair Display", serif;
  font-style: italic;
  color: var(--heading);
  margin: 0 0 8px;
  font-size: 34px;
}

.sdm-task{
  color: rgba(255,255,255,.82);
  font-size: 17px;
  line-height: 1.65;
  margin: 0 0 14px;
}

.sdm-meta{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
  color: var(--muted2);
  font-size: 14px;
  margin-top: 6px;
}

.sdm-pill{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08);
}

.sdm-progress{
  margin: 10px 0 18px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(0,0,0,.18);
  border: 1px solid rgba(255,255,255,.06);
}

.sdm-bar{
  height: 8px;
  border-radius: 999px;
  background: rgba(255,255,255,.08);
  overflow:hidden;
}

.sdm-bar > div{
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--heading));
  border-radius: 999px;
  box-shadow: 0 0 18px rgba(193,39,45,.35);
  transition: width .35s ease;
}

div.stButton > button{
  border-radius: 14px !important;
  border: 1px solid rgba(212,175,55,.42) !important;
  background: radial-gradient(120px 40px at 20% 20%, rgba(255,255,255,.18), transparent 60%),
              linear-gradient(90deg, var(--accent), var(--heading)) !important;
  color: #F6E7B5 !important;
  font-weight: 700 !important;
  padding: 0.65rem 1.05rem !important;
  box-shadow: 0 10px 28px rgba(0,0,0,.45) !important;
  transition: transform .12s ease, filter .12s ease;
}
div.stButton > button:hover{ transform: translateY(-1px); filter: brightness(1.08); }
div.stButton > button:active{ transform: translateY(0px) scale(.99); }

.sdm-flip{
  animation: sdmFlip .55s ease;
  transform-origin: center;
}
@keyframes sdmFlip{
  from{ transform: rotateY(-10deg) scale(.985); opacity: .6; }
  to{ transform: rotateY(0deg) scale(1); opacity: 1; }
}

.sdm-culm{
  border-radius: 28px;
  padding: 34px 26px;
  background: radial-gradient(900px 420px at 20% 20%, rgba(212,175,55,.15), transparent 62%),
              radial-gradient(900px 420px at 70% 30%, rgba(193,39,45,.28), transparent 62%),
              linear-gradient(180deg, rgba(123,30,36,.28), rgba(17,17,17,.25));
  border: 1px solid rgba(212,175,55,.18);
  box-shadow: 0 22px 70px rgba(0,0,0,.55);
  position: relative;
  overflow:hidden;
}

.sdm-glow{
  position:absolute;
  inset:-120px -120px auto auto;
  width: 520px;
  height: 520px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(212,175,55,.20), transparent 60%);
  animation: sdmGlow 3.6s ease-in-out infinite alternate;
  pointer-events:none;
}
@keyframes sdmGlow{
  from{ transform: translate(0px, 0px) scale(1); opacity: .55; }
  to{ transform: translate(-22px, 18px) scale(1.06); opacity: .85; }
}
</style>
"""

# =========================
# DB
# =========================
def db_connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con

def db_init():
    con = db_connect()
    con.execute("""
    CREATE TABLE IF NOT EXISTS users (
      user_id TEXT PRIMARY KEY,
      created_at TEXT NOT NULL,
      start_date TEXT
    );
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS progress (
      user_id TEXT NOT NULL,
      day INTEGER NOT NULL,
      completed_at TEXT,
      favorite INTEGER NOT NULL DEFAULT 0,
      reaction TEXT,
      PRIMARY KEY (user_id, day),
      FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)
    con.commit()
    con.close()

@dataclass
class UserState:
    user_id: str
    started: bool
    start_date: date | None
    completed: set[int]
    favorites: set[int]
    reactions: dict[int, str]

def now_local() -> datetime:
    return datetime.now(APP_TZ)

def today_local() -> date:
    return now_local().date()

def load_user(con: sqlite3.Connection, user_id: str) -> UserState:
    cur = con.execute("SELECT start_date FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        con.execute(
            "INSERT INTO users(user_id, created_at, start_date) VALUES(?, ?, NULL)",
            (user_id, now_local().isoformat()),
        )
        con.commit()
        start_date = None
    else:
        start_date = date.fromisoformat(row[0]) if row[0] else None

    completed = set()
    favorites = set()
    reactions: dict[int, str] = {}

    cur = con.execute(
        "SELECT day, completed_at, favorite, reaction FROM progress WHERE user_id = ?",
        (user_id,),
    )
    for d, completed_at, favorite, reaction in cur.fetchall():
        d = int(d)
        if completed_at:
            completed.add(d)
        if int(favorite) == 1:
            favorites.add(d)
        if reaction:
            reactions[d] = reaction

    return UserState(
        user_id=user_id,
        started=start_date is not None,
        start_date=start_date,
        completed=completed,
        favorites=favorites,
        reactions=reactions,
    )

def save_start(con: sqlite3.Connection, user_id: str, start_date: date):
    con.execute(
        "UPDATE users SET start_date = ? WHERE user_id = ?",
        (start_date.isoformat(), user_id),
    )
    con.commit()

def upsert_progress(con: sqlite3.Connection, user_id: str, day: int,
                    completed_at: str | None = None,
                    favorite: int | None = None,
                    reaction: str | None = None):
    con.execute("""
    INSERT INTO progress(user_id, day, completed_at, favorite, reaction)
    VALUES (?, ?, ?, COALESCE(?, 0), ?)
    ON CONFLICT(user_id, day) DO UPDATE SET
      completed_at = COALESCE(excluded.completed_at, progress.completed_at),
      favorite     = COALESCE(excluded.favorite, progress.favorite),
      reaction     = COALESCE(excluded.reaction, progress.reaction);
    """, (user_id, day, completed_at, favorite, reaction))
    con.commit()

def reset_user(con: sqlite3.Connection, user_id: str):
    con.execute("UPDATE users SET start_date = NULL WHERE user_id = ?", (user_id,))
    con.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
    con.commit()

# =========================
# UID w cookie (per przeglądarka/urządzenie)
# =========================
def ensure_user_id() -> str:
    # cookie manager potrzebuje 1 renderu na inicjalizację
    if not cookies.ready():
        st.markdown('<div class="sdm-wrap"><div class="sdm-card">Ładowanie…</div></div>', unsafe_allow_html=True)
        return ""

    uid = cookies.get("uid")
    if not uid:
        uid = str(uuid.uuid4())
        cookies["uid"] = uid
        cookies.save()

    st.session_state.user_id = uid
    return uid

# =========================
# LOGIKA "1 karta dziennie"
# =========================
def active_day(start_date: date | None) -> int:
    if not start_date:
        return 1
    delta = (today_local() - start_date).days
    return max(1, min(14, delta + 1))

def is_unlocked(day: int, start_date: date | None) -> bool:
    return day <= active_day(start_date)

def progress_percent(start_date: date | None) -> int:
    d = active_day(start_date)
    return int(round((d / 14) * 100))

# =========================
# UI
# =========================
def render_progress(start_date: date | None):
    d = active_day(start_date)
    pct = progress_percent(start_date)
    st.markdown(
        f"""
        <div class="sdm-progress">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:12px;">
            <div style="color:rgba(255,255,255,.78); font-size:14px;">
              Postęp: <b>Dzień {d}/14</b>
            </div>
            <div style="color:rgba(255,255,255,.55); font-size:12px;">
              {pct}%
            </div>
          </div>
          <div class="sdm-bar" style="margin-top:8px;">
            <div style="width:{pct}%;"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_start_screen(con: sqlite3.Connection, user: UserState):
    st.markdown('<div class="sdm-wrap">', unsafe_allow_html=True)
    st.markdown(f"<div class='sdm-logo'>SeduceMe</div>", unsafe_allow_html=True)
    st.markdown("<div class='sdm-subtitle'>14 dni namiętności dla par</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sdm-hero">
          <div style="max-width:780px;">
            <div style="font-family:'Playfair Display',serif;font-style:italic;color:rgba(255,255,255,.86);
                        font-size:28px;margin-bottom:10px;">
              ZACZNIJCIE SWOJĄ PODRÓŻ JUŻ DZIŚ!
            </div>
            <div style="color:rgba(255,255,255,.72); font-size:16px; line-height:1.7;">
              Dyskretny, zmysłowy kalendarz z codzienną kartą. Jedno zadanie dziennie, historia postępów
              i kulminacja w dniu 14 — wszystko w eleganckiej oprawie.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3 = st.columns([1.2, 1, 1.2])
    with c2:
        if st.button("Rozpocznij swoją 14-dniową podróż", use_container_width=True):
            save_start(con, user.user_id, today_local())
            st.rerun()

    st.write("")
    st.caption("Progres zapisuje się w SQLite, a identyfikacja jest per urządzenie (cookie).")
    st.markdown("</div>", unsafe_allow_html=True)

def render_day_card(con: sqlite3.Connection, user: UserState, day: int):
    data = DAYS[day - 1]
    unlocked = is_unlocked(day, user.start_date)

    if day == 14 and unlocked:
        st.markdown(
            f"""
            <div class="sdm-culm sdm-flip">
              <div class="sdm-glow"></div>
              <div class="sdm-h2">Dzień 14: {data["title"]}</div>
              <div class="sdm-task" style="font-size:18px;">
                {data["task"]}
              </div>
              <div class="sdm-meta">
                <span class="sdm-pill">⏱️ {data["duration_min"]}–{data["duration_min"]+10} min</span>
                <span class="sdm-pill">✨ Kulminacja</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.button("Zanurz się teraz", use_container_width=True)
        return

    if not unlocked:
        st.markdown(
            f"""
            <div class="sdm-card">
              <div class="sdm-h2">Dzień {day}: {data["title"]}</div>
              <div class="sdm-task">
                Ta karta jest jeszcze zablokowana — odblokowuje się jedna dziennie.
              </div>
              <div class="sdm-meta">
                <span class="sdm-pill">🔒 Zablokowana</span>
                <span class="sdm-pill">⏳ Odblokuje się w kolejnych dniach</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    reacted = user.reactions.get(day, data["emoji"])
    is_done = day in user.completed
    is_fav = day in user.favorites

    st.markdown(
        f"""
        <div class="sdm-card sdm-flip">
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

    st.write("")
    a1, a2, a3, a4 = st.columns([1.1, 1, 1, 1.3])

    with a1:
        if st.button("Zapisz jako ukończone", use_container_width=True):
            upsert_progress(con, user.user_id, day, completed_at=now_local().isoformat())
            st.toast("Zapisano ✅", icon="✅")
            st.rerun()

    with a2:
        if st.button("❤️ / 🤍 Ulubione", use_container_width=True):
            fav_value = 0 if is_fav else 1
            upsert_progress(con, user.user_id, day, favorite=fav_value)
            st.rerun()

    with a3:
        emoji_options = ["🔥", "💋", "✨", "🖤", "⚡", "🕯️", "🌙", "🎭", "🍓", "🔓"]
        idx = emoji_options.index(reacted) if reacted in emoji_options else 0
        emoji = st.selectbox("Emoji reakcji", options=emoji_options, index=idx, key=f"react_{day}")
        if st.button("Zapisz reakcję", use_container_width=True):
            upsert_progress(con, user.user_id, day, reaction=emoji)
            st.toast("Reakcja zapisana", icon="✨")
            st.rerun()

    with a4:
        if st.button("Odkryj kolejną kartę", use_container_width=True):
            st.session_state.selected_day = min(14, day + 1)
            st.rerun()

def render_history(user: UserState):
    st.markdown(
        """
        <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; margin-top:10px;">
          <div class="sdm-h2" style="margin:0;">Historia / Postępy</div>
          <div style="color:rgba(255,255,255,.55); font-size:13px;">
            Kliknij dzień, aby podejrzeć
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    cols = st.columns(7)
    for i in range(14):
        day = i + 1
        data = DAYS[i]
        unlocked = is_unlocked(day, user.start_date)
        reacted = user.reactions.get(day, data["emoji"])
        label = f"{reacted}  Dzień {day}"

        col = cols[i % 7]
        with col:
            if st.button(label, key=f"grid_{day}", use_container_width=True, disabled=not unlocked):
                st.session_state.selected_day = day
                st.session_state.show_history = False
                st.rerun()

        if (i % 7) == 6 and i != 13:
            cols = st.columns(7)

def render_sidebar(con: sqlite3.Connection, user: UserState):
    with st.sidebar:
        st.markdown("### Informacje")
        st.caption(f"UID: {user.user_id[:8]}…")
        if user.start_date:
            st.caption(f"Start: {user.start_date.isoformat()} (Europe/Warsaw)")
            st.caption(f"Odblokowany dzień: {active_day(user.start_date)}/14")
        else:
            st.caption("Nie rozpoczęto jeszcze podróży.")

        st.markdown("---")
        if st.button("Reset (wyczyść postęp)", type="secondary"):
            reset_user(con, user.user_id)
            st.rerun()

# =========================
# MAIN
# =========================
def main():
    st.markdown(CSS, unsafe_allow_html=True)

    db_init()

    user_id = ensure_user_id()
    if not user_id:
        st.stop()

    con = db_connect()
    user = load_user(con, user_id)

    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    if "selected_day" not in st.session_state:
        st.session_state.selected_day = 1

    render_sidebar(con, user)

    if not user.started:
        render_start_screen(con, user)
        con.close()
        return

    st.markdown('<div class="sdm-wrap">', unsafe_allow_html=True)
    st.markdown(f"<div class='sdm-logo' style='font-size:44px;'>SeduceMe</div>", unsafe_allow_html=True)
    st.markdown("<div class='sdm-subtitle'>Twoja 14-dniowa podróż — jedna karta dziennie, zapis postępu, dyskretnie</div>", unsafe_allow_html=True)

    render_progress(user.start_date)

    top1, top2, top3, top4 = st.columns([1, 1, 1, 1.4])
    with top1:
        if st.button("Dzisiaj", use_container_width=True):
            st.session_state.selected_day = active_day(user.start_date)
            st.session_state.show_history = False
            st.rerun()
    with top2:
        if st.button("Historia", use_container_width=True):
            st.session_state.show_history = True
            st.rerun()
    with top3:
        if st.button("Karta dnia", use_container_width=True):
            st.session_state.show_history = False
            st.rerun()
    with top4:
        st.markdown(
            f"""
            <div style="text-align:right; padding-top:10px; color:rgba(255,255,255,.65); font-size:14px;">
              Ukończone: <b>{len(user.completed)}</b> / 14
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    if st.session_state.show_history:
        render_history(user)
    else:
        if st.session_state.selected_day is None:
            st.session_state.selected_day = active_day(user.start_date)

        day = int(st.session_state.selected_day)
        day = max(1, min(14, day))
        render_day_card(con, user, day)

    st.markdown("</div>", unsafe_allow_html=True)
    con.close()

if __name__ == "__main__":
    main()

