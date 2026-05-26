# Stochastic Differential Equations — Lecture Notes

A series of self-contained notes on Stochastic Differential Equations (SDEs), from the construction of Brownian motion to the SDE–PDE bridge, including a chapter on numerical methods.

**Author:** Anqiao Ouyang (with Xuecheng Liu on Lectures II & III)

---

## Lectures

| # | Topic | Language | Date | Folder |
|---|---|---|---|---|
| I | 布朗运动与随机过程的构造 / Brownian Motion and the Construction of Stochastic Processes | 中文 + English | 2025-07-29 | [`01-brownian-motion/`](01-brownian-motion/) |
| II | 伊藤积分与数值方法入门 / Itô Integral and Introduction to Numerical Methods | 中文 + English | 2025-08-29 | [`02-ito-integral/`](02-ito-integral/) |
| III | Existence, Uniqueness, and the SDE–PDE Bridge | English | 2026-05-26 | [`03-existence-uniqueness/`](03-existence-uniqueness/) |
| EM | Numerical SDE: The Euler–Maruyama Method | 中文 | 2025-07-29 | [`04-euler-maruyama/`](04-euler-maruyama/) |

---

## Lecture I — Brownian Motion

Formal definitions of stochastic processes, filtrations and adapted processes, and Brownian motion as the driving noise in SDEs. Includes a construction of Brownian motion.

- [`I.tex`](01-brownian-motion/I.tex) — 中文版
- [`I_en_us.tex`](01-brownian-motion/I_en_us.tex) — English version
- [`figures/`](01-brownian-motion/figures/)

## Lecture II — Itô Integral

From deterministic ODEs to SDEs, the Itô integral, Itô's formula, and a first look at numerical methods.

- [`II.tex`](02-ito-integral/II.tex) — 中文版
- [`II_en_us.tex`](02-ito-integral/II_en_us.tex) — English version

## Lecture III — Existence, Uniqueness, and the SDE–PDE Bridge

Existence and uniqueness theorems for SDEs, infinitesimal generators, the Fokker–Planck equation, the Ornstein–Uhlenbeck stationary distribution, Girsanov's theorem, and Brownian bridge.

- [`III_en_us.tex`](03-existence-uniqueness/III_en_us.tex) — main note (English)
- [`generate_figures.py`](03-existence-uniqueness/generate_figures.py) — reproduces all figures
- [`figures/`](03-existence-uniqueness/figures/) — generator, Fokker–Planck, OU, Girsanov, bridge

## Lecture EM — Euler–Maruyama

The Euler–Maruyama scheme for numerically solving SDEs: derivation, strong/weak convergence, and worked examples.

- [`EM.tex`](04-euler-maruyama/EM.tex) — 中文版
- [`ref.bib`](04-euler-maruyama/ref.bib)

---

## Building the PDFs

Each lecture folder is self-contained — it ships its own copy of `math_blog.sty` so you can compile in place:

```bash
cd 01-brownian-motion
xelatex I.tex          # 中文版 (needs XeLaTeX for CJK)
pdflatex I_en_us.tex   # English version
```

Lecture EM uses `biblatex`; build with:

```bash
cd 04-euler-maruyama
xelatex EM.tex && biber EM && xelatex EM.tex && xelatex EM.tex
```

Lecture III's figures can be regenerated with:

```bash
cd 03-existence-uniqueness
python generate_figures.py
```

## Layout

```
SDE/
├── README.md
├── 01-brownian-motion/        # Lecture I
│   ├── I.tex, I_en_us.tex
│   ├── math_blog.sty
│   └── figures/
├── 02-ito-integral/           # Lecture II
│   ├── II.tex, II_en_us.tex
│   └── math_blog.sty
├── 03-existence-uniqueness/   # Lecture III
│   ├── III_en_us.tex
│   ├── generate_figures.py
│   ├── math_blog.sty
│   └── figures/
└── 04-euler-maruyama/         # Lecture EM
    ├── EM.tex
    ├── math_blog.sty
    └── ref.bib
```
