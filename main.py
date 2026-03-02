# main.py

"""
=========================================================
MAIN - CREIERUL APLICAȚIEI
=========================================================

Acest fișier orchestrează întreaga aplicație.

Fluxul este următorul:

0️⃣ Verifică biletele din ziua precedentă
1️⃣ Încarcă meciurile din API
2️⃣ Filtrează doar meciurile din următoarele X ore
3️⃣ Construiește DAILY PICKS (high probability, separat)
4️⃣ Construiește OPTIMIZER POOL (independent)
5️⃣ Rulează optimizerul profesional pentru bilete
6️⃣ Trimite mesajele pe Telegram
7️⃣ Salvează biletele generate

IMPORTANT:
Daily Picks și Optimizer sunt COMPLET separate.
Daily Picks NU influențează biletele automate.
"""

import random
from datetime import datetime, timezone, timedelta

import scraper
import model
import config
import telegram_bot
import ticket_builder
import ticket_checker
import storage


# =====================================================
# 0️⃣ VERIFICARE ZI PRECEDENTĂ
# =====================================================

"""
La fiecare rulare verificăm dacă există bilete din ziua precedentă
care nu au fost încă evaluate.

Dacă există, le evaluăm și actualizăm bankroll-ul.
"""

report = ticket_checker.check_old_tickets()

if report:
    telegram_bot.send_message(report)


# =====================================================
# 1️⃣ ÎNCĂRCARE MECIURI DIN API
# =====================================================

matches = scraper.get_matches()

print("====================================================")
print("Total meciuri primite din API:", len(matches))


# =====================================================
# 2️⃣ FILTRARE MECIURI ÎN URMĂTOARELE X ORE
# =====================================================

"""
În loc să filtrăm strict după zi calendaristică,
analizăm meciurile care încep în următoarele
config.MATCH_WINDOW_HOURS ore.

Astfel:
- dacă rulăm seara → prindem meciuri de noapte
- dacă rulăm dimineața → prindem meciuri până seara
"""

now = datetime.now(timezone.utc)
limit_time = now + timedelta(hours=config.MATCH_WINDOW_HOURS)

filtered_matches = []

eliminated_started = 0
eliminated_future = 0

for match in matches:

    try:
        kickoff = datetime.fromisoformat(
            match["commence_time"].replace("Z", "+00:00")
        )
    except:
        continue

    # Eliminăm meciurile deja începute
    if kickoff <= now:
        eliminated_started += 1
        continue

    # Eliminăm meciurile prea departe în viitor
    if kickoff > limit_time:
        eliminated_future += 1
        continue

    filtered_matches.append(match)

matches = filtered_matches

print("Meciuri în următoarele", config.MATCH_WINDOW_HOURS, "ore:", len(matches))
print("Eliminate (deja începute):", eliminated_started)
print("Eliminate (prea departe):", eliminated_future)
print("====================================================")


# =====================================================
# 3️⃣ DAILY PICKS – HIGH PROBABILITY (SEPARAT)
# =====================================================

"""
Scop:
- Maxim 10 meciuri
- Fără repetare meci
- Probabilitate individuală ≥ 75%
- Cotă ≥ 1.15
- Validare prin mini-simulare Monte Carlo

Aceste pickuri sunt doar orientative pentru tine.
NU sunt folosite de optimizer.
"""

def simulate_single_pick(prob, simulations=20000):
    """
    Simulează un singur pariu pentru validare empirică.
    Returnează rata de succes observată.
    """
    wins = 0
    for _ in range(simulations):
        if random.random() < prob:
            wins += 1
    return wins / simulations


daily_candidates = []

for match in matches:

    odds_values = list(match["odds"].values())

    if len(odds_values) != 3:
        continue

    # Calcul probabilități normalizate
    probs = model.normalize_probabilities(odds_values)

    # Construim piețele double chance
    dc = model.double_chance(*probs)

    for name, prob in dc.items():

        odd = 1 / prob

        # Filtru strict pentru daily picks
        if prob < 0.75:
            continue

        if odd < 1.15:
            continue

        # Validare prin simulare
        simulated_rate = simulate_single_pick(prob)

        # Scor final = medie între teoretic și simulat
        final_score = (prob + simulated_rate) / 2

        daily_candidates.append({
            "match": f"{match['home']} vs {match['away']}",
            "bet": name,
            "odds": odd,
            "prob": prob,
            "sim_prob": simulated_rate,
            "final_score": final_score
        })


# Eliminăm duplicate de meci (păstrăm cea mai bună variantă per meci)
unique_daily = {}

for pick in sorted(daily_candidates, key=lambda x: x["final_score"], reverse=True):
    if pick["match"] not in unique_daily:
        unique_daily[pick["match"]] = pick

# Luăm maxim 10, dar dacă sunt mai puține, luăm câte sunt
daily_picks = list(unique_daily.values())[:10]

print("Daily high-probability picks găsite:", len(daily_picks))


# =====================================================
# 4️⃣ AFIȘARE DAILY PICKS
# =====================================================

daily_msg = "🔥 DAILY PICKS – HIGH PROBABILITY\n"
daily_msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

daily_msg += f"📊 Meciuri analizate: {len(matches)}\n"
daily_msg += f"✅ Selecții 75%+ găsite: {len(daily_picks)}\n\n"

if not daily_picks:

    daily_msg += "⚠️ Nu există selecții 75%+ în interval.\n"

else:

    for i, p in enumerate(daily_picks, 1):

        daily_msg += f"{i}. ⚽ {p['match']}\n"
        daily_msg += f"   ➡️ {p['bet']} @ {round(p['odds'],2)}\n"
        daily_msg += f"   📊 Prob teoretică: {round(p['prob']*100,1)}%\n"
        daily_msg += f"   🧪 Prob simulată: {round(p['sim_prob']*100,1)}%\n"
        daily_msg += f"   ⭐ Scor final: {round(p['final_score']*100,1)}%\n\n"

telegram_bot.send_message(daily_msg)


# =====================================================
# 5️⃣ CONSTRUIRE OPTIMIZER POOL (RELAXED, INDEPENDENT)
# =====================================================

"""
Acest pool este separat de daily picks.

Filtrare mai relaxată:
- probabilitate mai mică acceptată
- strength minim mai mic
"""

optimizer_pool = []

for match in matches:

    odds_values = list(match["odds"].values())

    if len(odds_values) != 3:
        continue

    probs = model.normalize_probabilities(odds_values)
    strength = model.market_strength(odds_values)
    dc = model.double_chance(*probs)

    if strength < config.MIN_STRENGTH_RELAXED:
        continue

    for name, prob in dc.items():

        if prob < config.MIN_PROBABILITY_RELAXED:
            continue

        odd = 1 / prob
        score = model.pick_score(prob, strength, match["consensus"])

        optimizer_pool.append({
            "league": match["league"],
            "match": f"{match['home']} vs {match['away']}",
            "bet": name,
            "odds": odd,
            "prob": prob,
            "score": score
        })

optimizer_pool = sorted(optimizer_pool, key=lambda x: x["score"], reverse=True)

print("Optimizer pool size:", len(optimizer_pool))


# =====================================================
# 6️⃣ OPTIMIZER PROFESIONAL (ACCA TICKETS)
# =====================================================

tickets, summary = ticket_builder.build_tickets(optimizer_pool)

telegram_bot.send_message(summary)


# =====================================================
# 7️⃣ AFIȘARE BILETE AUTOMATE
# =====================================================

ticket_msg = "🎟 DAILY ACCA TICKETS\n"
ticket_msg += "━━━━━━━━━━━━━━━\n\n"

if not tickets:

    ticket_msg += "Nu au fost generate bilete automate."

else:

    for i, t in enumerate(tickets, 1):

        ticket_msg += f"🎫 Ticket {i}\n"
        ticket_msg += f"💰 Stake: {config.STAKE} lei\n"
        ticket_msg += f"🎯 Total odds: {t['odds']}\n\n"

        avg_prob = sum(b["prob"] for b in t["bets"]) / len(t["bets"])
        avg_score = sum(b["score"] for b in t["bets"]) / len(t["bets"])

        ticket_msg += f"📊 Prob medie selecții: {round(avg_prob*100,1)}%\n"
        ticket_msg += f"⭐ Scor mediu selecții: {round(avg_score,2)}\n\n"

        for bet in t["bets"]:
            ticket_msg += f"⚽ {bet['match']}\n"
            ticket_msg += f"➡️ {bet['bet']} @ {round(bet['odds'],2)}\n\n"

        ticket_msg += "──────────────\n\n"

telegram_bot.send_message(ticket_msg)


# =====================================================
# 8️⃣ SALVARE BILETE
# =====================================================

if tickets:
    storage.save_daily_tickets(tickets)

print("Bot finalizat cu succes.")
print("====================================================")