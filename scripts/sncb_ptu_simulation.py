"""SNCB chatbot — Azure OpenAI PAYG vs PTU business-case simulation.

Pricing sourced from researcher brief (May 2026, Azure OpenAI EU Data Zone):
- GPT-4o mini Data Zone PAYG: $0.165 / 1M input, $0.66 / 1M output
- GPT-4o      Data Zone PAYG: $2.75  / 1M input, $11.00 / 1M output
- PTU EU Data Zone: $1.10/PTU/hr hourly, $2,916/PTU/yr (1-yr reservation, ~70% off)
- PTU EU Data Zone: $286/PTU/month (1-month reservation)
- Minimum deployment: 15 PTU (EU Data Zone, all chat models)
- No 3-year reservation exists for Foundry PTU; multi-year TCO rolls 1-yr renewals.

All outputs in EUR. USD->EUR = 0.92.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Assumptions (all editable here)
# ---------------------------------------------------------------------------
USD_EUR = 0.92

ANNUAL_JOURNEYS = 225_000_000
ADOPTION_RATE = 0.04
TURNS_PER_SESSION = 6
INPUT_TOKENS_PER_TURN = 2200    # RAG: system + timetable/disruption snippets + history
OUTPUT_TOKENS_PER_TURN = 350
PEAK_TO_AVG = 4.0

MINI_TRAFFIC_SHARE = 0.70
LARGE_TRAFFIC_SHARE = 1.0 - MINI_TRAFFIC_SHARE

PAYG = {
    "mini":  {"in": 0.165, "out": 0.66},
    "large": {"in": 2.75,  "out": 11.00},
}

PTU_HOURLY_USD = 1.10
PTU_1MO_USD = 286.0
PTU_1YR_USD = 2916.0

TPM_PER_PTU = {"mini": 37_000, "large": 2_500}
MIN_PTU_BY_MODEL = {"mini": 15, "large": 15}

OUT_DIR = Path(__file__).resolve().parent.parent / "knowledge" / "assets" / "sncb-ptu"
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (16, 9),
    "figure.dpi": 100,
    "savefig.dpi": 100,
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.size": 14,
    "axes.titlesize": 22,
    "axes.titleweight": "bold",
    "axes.labelsize": 16,
    "legend.fontsize": 14,
})

C_PAYG, C_HR, C_1MO, C_1YR, C_OK = "#D64545", "#F2A65A", "#5B8DEF", "#1F6F8B", "#2E933C"


def annual_tokens(adoption: float, mini_share: float = MINI_TRAFFIC_SHARE) -> dict:
    sessions = ANNUAL_JOURNEYS * adoption
    turns = sessions * TURNS_PER_SESSION
    in_tok = turns * INPUT_TOKENS_PER_TURN
    out_tok = turns * OUTPUT_TOKENS_PER_TURN
    large_share = 1.0 - mini_share
    return {
        "sessions": sessions,
        "in_mini": in_tok * mini_share, "out_mini": out_tok * mini_share,
        "in_large": in_tok * large_share, "out_large": out_tok * large_share,
    }


def payg_cost_usd(t: dict) -> float:
    return (t["in_mini"]/1e6 * PAYG["mini"]["in"] + t["out_mini"]/1e6 * PAYG["mini"]["out"]
            + t["in_large"]/1e6 * PAYG["large"]["in"] + t["out_large"]/1e6 * PAYG["large"]["out"])


def required_ptu(t: dict) -> dict:
    mins = 365 * 24 * 60
    ow = 4.0
    avg_mini = (t["in_mini"] + t["out_mini"] * ow) / mins
    avg_large = (t["in_large"] + t["out_large"] * ow) / mins
    peak_mini, peak_large = avg_mini * PEAK_TO_AVG, avg_large * PEAK_TO_AVG
    n_mini = max(MIN_PTU_BY_MODEL["mini"], int(np.ceil(peak_mini / TPM_PER_PTU["mini"])))
    n_large = max(MIN_PTU_BY_MODEL["large"], int(np.ceil(peak_large / TPM_PER_PTU["large"])))
    n_mini = int(np.ceil(n_mini / 5) * 5) if t["in_mini"] > 0 else 0
    n_large = int(np.ceil(n_large / 5) * 5) if t["in_large"] > 0 else 0
    return {"mini": n_mini, "large": n_large,
            "avg_tpm_mini": avg_mini, "avg_tpm_large": avg_large,
            "peak_tpm_mini": peak_mini, "peak_tpm_large": peak_large}


def ptu_cost_usd(n: int, mode: str) -> float:
    return {"hourly": n * PTU_HOURLY_USD * 24 * 365,
            "1mo": n * PTU_1MO_USD * 12,
            "1yr": n * PTU_1YR_USD}[mode]


def eur(x): return x * USD_EUR


# Base case
t_base = annual_tokens(ADOPTION_RATE)
sizing = required_ptu(t_base)
n_total = sizing["mini"] + sizing["large"]
payg_eur = eur(payg_cost_usd(t_base))
ptu_hr_eur = eur(ptu_cost_usd(n_total, "hourly"))
ptu_1mo_eur = eur(ptu_cost_usd(n_total, "1mo"))
ptu_1yr_eur = eur(ptu_cost_usd(n_total, "1yr"))

print("===== SNCB CHATBOT — PTU BUSINESS CASE =====")
print(f"Adoption: {ADOPTION_RATE*100:.1f}% -> {t_base['sessions']:,.0f} sessions/yr")
print(f"Mix: {MINI_TRAFFIC_SHARE*100:.0f}% mini / {LARGE_TRAFFIC_SHARE*100:.0f}% GPT-4o")
print(f"PTU sizing (peak): {sizing['mini']} mini + {sizing['large']} large = {n_total}")
print(f"PAYG annual:        €{payg_eur:>10,.0f}")
print(f"PTU hourly annual:  €{ptu_hr_eur:>10,.0f}")
print(f"PTU 1-mo  annual:   €{ptu_1mo_eur:>10,.0f}")
print(f"PTU 1-yr  annual:   €{ptu_1yr_eur:>10,.0f}")


# Chart 1: daily traffic + disruption
hours = np.arange(24)
profile = (0.3 + 1.6*np.exp(-0.5*((hours-8)/1.2)**2)
           + 1.8*np.exp(-0.5*((hours-18)/1.3)**2)
           + 0.4*np.exp(-0.5*((hours-12)/2.5)**2))
profile = profile / profile.mean()
daily = (t_base["in_mini"]+t_base["out_mini"]+t_base["in_large"]+t_base["out_large"])/365
hourly = profile * daily / 24
disrupt = hourly.copy()
disrupt[16:20] *= np.array([3, 10, 8, 5])

fig, ax = plt.subplots()
ax.fill_between(hours, hourly/1e6, color=C_1YR, alpha=0.8, label="Normal day")
ax.plot(hours, disrupt/1e6, color=C_PAYG, linewidth=3, label="Disruption day (strike / snow)")
ax.axhline(daily/24/1e6, color="grey", linestyle="--", linewidth=1.5, label="Daily average")
ax.annotate("10× spike when\npassengers need it most",
            xy=(17, disrupt[17]/1e6), xytext=(10, disrupt[17]/1e6*0.85),
            fontsize=14, fontweight="bold", color=C_PAYG,
            arrowprops=dict(arrowstyle="->", color=C_PAYG, lw=2))
ax.set_title("SNCB chatbot — daily token traffic (base case 4% adoption)")
ax.set_xlabel("Hour of day (CET)"); ax.set_ylabel("Tokens per hour (millions)")
ax.set_xticks(range(0, 24, 2)); ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(OUT_DIR / "01-traffic-profile.png"); plt.close(fig)


# Chart 2: annual cost comparison
labels = ["PAYG\n(pay-as-you-go)", "PTU hourly\n(no commitment)",
          "PTU 1-month\nreservation", "PTU 1-year\nreservation"]
values = [payg_eur, ptu_hr_eur, ptu_1mo_eur, ptu_1yr_eur]
colors = [C_PAYG, C_HR, C_1MO, C_1YR]
fig, ax = plt.subplots()
bars = ax.bar(labels, [v/1e3 for v in values], color=colors, width=0.6)
for b, v in zip(bars, values):
    ax.text(b.get_x()+b.get_width()/2, b.get_height(), f"€{v/1e3:.0f}K",
            ha="center", va="bottom", fontsize=15, fontweight="bold")
ax.set_title(f"Annual compute cost — base case (4% adoption, 70/30 mini/4o, {n_total} PTU)")
ax.set_ylabel("Annual cost (€ thousands)")
ax.set_ylim(0, max(values)/1e3 * 1.18)
ax.text(0.02, 0.97,
        "At this scale & model mix, PAYG is cheapest on €.\n"
        "PTU's value here is SLO, no throttling, EU residency.",
        transform=ax.transAxes, fontsize=13, va="top",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#FFF4E0", edgecolor="#D4A017"))
fig.tight_layout(); fig.savefig(OUT_DIR / "02-annual-cost-comparison.png"); plt.close(fig)


# Chart 3: model-mix sensitivity
mini_shares = np.linspace(0.0, 1.0, 21)
payg_by_mix, ptu_by_mix = [], []
for ms in mini_shares:
    ta = annual_tokens(ADOPTION_RATE, mini_share=ms)
    sa = required_ptu(ta)
    n = sa["mini"] + sa["large"]
    payg_by_mix.append(eur(payg_cost_usd(ta)))
    ptu_by_mix.append(eur(ptu_cost_usd(n, "1yr")))
payg_by_mix, ptu_by_mix = np.array(payg_by_mix), np.array(ptu_by_mix)
large_shares = (1 - mini_shares) * 100

fig, ax = plt.subplots()
ax.plot(large_shares, payg_by_mix/1e3, color=C_PAYG, linewidth=3, label="PAYG", marker="o")
ax.plot(large_shares, ptu_by_mix/1e3, color=C_1YR, linewidth=3, label="PTU 1-year reserved", marker="s")
diff = payg_by_mix - ptu_by_mix
if (diff > 0).any():
    idx = int(np.argmax(diff > 0))
    be = large_shares[idx]
    ax.axvline(be, color=C_OK, linestyle=":", linewidth=2)
    ax.annotate(f"Break-even at\n{be:.0f}% GPT-4o traffic",
                xy=(be, ptu_by_mix[idx]/1e3),
                xytext=(be + 8, ptu_by_mix[idx]/1e3 * 1.4),
                fontsize=14, fontweight="bold", color=C_OK,
                arrowprops=dict(arrowstyle="->", color=C_OK, lw=2))
ax.fill_between(large_shares, payg_by_mix/1e3, ptu_by_mix/1e3,
                where=(payg_by_mix > ptu_by_mix), color=C_OK, alpha=0.15,
                label="PTU cheaper zone")
ax.set_title("When does PTU win on €? Sensitivity to GPT-4o share of traffic")
ax.set_xlabel("Share of traffic routed to GPT-4o (vs GPT-4o mini), %")
ax.set_ylabel("Annual cost (€ thousands)")
ax.axvline(LARGE_TRAFFIC_SHARE*100, color="black", linestyle="--", alpha=0.4)
ax.text(LARGE_TRAFFIC_SHARE*100 + 1, 5, f"Base case ({LARGE_TRAFFIC_SHARE*100:.0f}%)",
        fontsize=11, rotation=90, va="bottom", alpha=0.6)
ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(OUT_DIR / "03-model-mix-sensitivity.png"); plt.close(fig)


# Chart 4: utilization
capacity_tph = (sizing["mini"]*TPM_PER_PTU["mini"] + sizing["large"]*TPM_PER_PTU["large"]) * 60
util = hourly / capacity_tph * 100
util_d = disrupt / capacity_tph * 100

fig, ax = plt.subplots()
ax.fill_between(hours, util, color=C_1YR, alpha=0.5, label="Normal day")
ax.plot(hours, util_d, color=C_PAYG, linewidth=3, label="Disruption day")
ax.axhline(100, color="grey", linestyle=":", linewidth=2, label="PTU capacity ceiling")
ax.axhline(util.mean(), color=C_1YR, linestyle="--", linewidth=1.5,
           label=f"Normal avg = {util.mean():.0f}%")
over = util_d > 100
if over.any():
    ax.fill_between(hours, 100, util_d, where=over, color=C_PAYG, alpha=0.3,
                    label="Spillover → PAYG (or throttling on PAYG-only)")
ax.set_title("PTU utilization — capacity sized to commute peak")
ax.set_xlabel("Hour of day (CET)"); ax.set_ylabel("Utilization (%)")
ax.set_xticks(range(0, 24, 2))
ax.set_ylim(0, max(150, util_d.max()*1.05))
ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(OUT_DIR / "04-utilization.png"); plt.close(fig)


# Chart 5: 3-year TCO with adoption ramp
years = ["Year 1", "Year 2", "Year 3"]
ramp = [0.02, 0.04, 0.06]
py, hy, my, yy = [], [], [], []
for a in ramp:
    ta = annual_tokens(a)
    sa = required_ptu(ta)
    n = sa["mini"] + sa["large"]
    py.append(eur(payg_cost_usd(ta)))
    hy.append(eur(ptu_cost_usd(n, "hourly")))
    my.append(eur(ptu_cost_usd(n, "1mo")))
    yy.append(eur(ptu_cost_usd(n, "1yr")))
cp, ch, cm, cy = np.cumsum(py), np.cumsum(hy), np.cumsum(my), np.cumsum(yy)
x, w = np.arange(3), 0.2

fig, ax = plt.subplots()
ax.bar(x - 1.5*w, cp/1e3, w, label="PAYG", color=C_PAYG)
ax.bar(x - 0.5*w, ch/1e3, w, label="PTU hourly", color=C_HR)
ax.bar(x + 0.5*w, cm/1e3, w, label="PTU 1-month", color=C_1MO)
ax.bar(x + 1.5*w, cy/1e3, w, label="PTU 1-year (renewed)", color=C_1YR)
ax.set_xticks(x, [f"{y}\n({r*100:.0f}% adoption)" for y, r in zip(years, ramp)])
ax.set_ylabel("Cumulative cost (€ thousands)")
ax.set_title("3-year cumulative TCO under realistic adoption ramp\n"
             "(no 3-yr Foundry reservation; 1-yr reservations renewed)")
ax.legend(loc="upper left")
fig.tight_layout(); fig.savefig(OUT_DIR / "05-tco-3year.png"); plt.close(fig)


# Chart 6: hybrid recommendation
h_mini = max(MIN_PTU_BY_MODEL["mini"],
             int(np.ceil(sizing["avg_tpm_mini"] / TPM_PER_PTU["mini"] / 5) * 5))
h_large = max(MIN_PTU_BY_MODEL["large"],
              int(np.ceil(sizing["avg_tpm_large"] / TPM_PER_PTU["large"] / 5) * 5))
h_n = h_mini + h_large
avg_cap_tph = (h_mini*TPM_PER_PTU["mini"] + h_large*TPM_PER_PTU["large"]) * 60
spill_tph = np.maximum(hourly - avg_cap_tph, 0)
blended_payg = ((PAYG["mini"]["in"]*INPUT_TOKENS_PER_TURN + PAYG["mini"]["out"]*OUTPUT_TOKENS_PER_TURN) * MINI_TRAFFIC_SHARE
                + (PAYG["large"]["in"]*INPUT_TOKENS_PER_TURN + PAYG["large"]["out"]*OUTPUT_TOKENS_PER_TURN) * LARGE_TRAFFIC_SHARE) \
                / (INPUT_TOKENS_PER_TURN + OUTPUT_TOKENS_PER_TURN) / 1e6
spill_annual_tok = spill_tph.sum() * 365
hybrid_eur = (eur(ptu_cost_usd(h_n, "1yr")) + eur(spill_annual_tok * blended_payg))

scs = ["PAYG only", "PTU 1-yr\n(peak-sized)", "Hybrid\n(PTU avg + PAYG burst)"]
svals = [payg_eur, ptu_1yr_eur, hybrid_eur]
scols = [C_PAYG, C_1YR, C_OK]

fig, ax = plt.subplots()
bars = ax.bar(scs, [v/1e3 for v in svals], color=scols, width=0.55)
for b, v in zip(bars, svals):
    ax.text(b.get_x()+b.get_width()/2, b.get_height(), f"€{v/1e3:.0f}K",
            ha="center", va="bottom", fontsize=16, fontweight="bold")
ax.set_title(f"Recommended approach: hybrid deployment\n"
             f"({h_n} PTU sized to average + PAYG spillover for peaks)")
ax.set_ylabel("Annual cost (€ thousands)")
ax.set_ylim(0, max(svals)/1e3 * 1.2)
ax.text(0.02, 0.97,
        "Hybrid keeps PAYG-like cost AND gets:\n"
        "  • Latency SLO on the steady 80% of traffic\n"
        "  • No throttling during disruption spikes\n"
        "  • EU Data Zone residency for GDPR",
        transform=ax.transAxes, fontsize=13, va="top",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#E8F5E9", edgecolor=C_OK))
fig.tight_layout(); fig.savefig(OUT_DIR / "06-hybrid-recommendation.png"); plt.close(fig)


print(f"\nHybrid sizing: {h_mini} mini + {h_large} large = {h_n} PTU")
print(f"Hybrid annual cost:  €{hybrid_eur:>10,.0f}")
print(f"\nAll charts -> {OUT_DIR}")
