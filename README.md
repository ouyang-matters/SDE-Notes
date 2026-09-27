# Stochastic Differential Equations — Lecture Notes

A series of self-contained notes on Stochastic Differential Equations (SDEs), from the construction of Brownian motion to backward SDEs, the nonlinear Feynman–Kac formula, and forward–backward SDEs with the stochastic maximum principle.

**Author:** Anqiao Ouyang (with Xuecheng Liu on Lectures II, III, IV)

---

## Lectures

| # | Topic | Language | Date | Folder |
|---|---|---|---|---|
| I | 布朗运动与随机过程的构造 / Brownian Motion and the Construction of Stochastic Processes | 中文 + English | 2025-07-29 | [`01-brownian-motion/`](01-brownian-motion/) |
| II | 伊藤积分与数值方法入门 / Itô Integral and Introduction to Numerical Methods | 中文 + English | 2025-08-29 | [`02-ito-integral/`](02-ito-integral/) |
| III | 存在唯一性与 SDE–PDE 之间的桥梁 / Existence, Uniqueness, and the SDE–PDE Bridge | 中文 + English | 2026-05-26 | [`03-existence-uniqueness/`](03-existence-uniqueness/) |
| IV | 倒向随机微分方程与非线性 Feynman–Kac 公式 / Backward SDEs and the Nonlinear Feynman–Kac Formula | 中文 + English *(draft)* | _in progress_ | [`04-bsde/`](04-bsde/) |
| V | 前向–倒向随机微分方程与随机极大值原理 / Forward–Backward SDEs and the Stochastic Maximum Principle | 中文 | 2026-06-06 | [`05-fbsde/`](05-fbsde/) |

---

## Lecture I — Brownian Motion

Formal definitions of stochastic processes, filtrations and adapted processes, and Brownian motion as the driving noise in SDEs. Includes a construction of Brownian motion.

- [`I.tex`](01-brownian-motion/I.tex) — 中文版
- [`I_en_us.tex`](01-brownian-motion/I_en_us.tex) — English version
- [`figures/`](01-brownian-motion/figures/)

## Lecture II — Itô Integral and Numerical Methods

From deterministic ODEs to SDEs, the Itô integral, Itô's formula, and the Euler–Maruyama scheme for numerical solution.

- [`II.tex`](02-ito-integral/II.tex) — 中文版
- [`II_en_us.tex`](02-ito-integral/II_en_us.tex) — English version
- [`EM.tex`](02-ito-integral/EM.tex) — supplementary note on the Euler–Maruyama method (中文; uses `ref.bib` via `biblatex`)

## Lecture III — Existence, Uniqueness, and the SDE–PDE Bridge

Existence and uniqueness theorems for SDEs, infinitesimal generators, the Fokker–Planck equation, the Ornstein–Uhlenbeck stationary distribution, Girsanov's theorem, and Brownian bridge.

- [`III.tex`](03-existence-uniqueness/III.tex) — 中文版
- [`III_en_us.tex`](03-existence-uniqueness/III_en_us.tex) — English version
- [`generate_figures.py`](03-existence-uniqueness/generate_figures.py) — reproduces all figures
- [`figures/`](03-existence-uniqueness/figures/) — generator, Fokker–Planck, OU, Girsanov, bridge

## Lecture IV — Backward SDEs and Nonlinear Feynman–Kac

The Pardoux–Peng theorem for BSDEs, the comparison theorem, and the nonlinear Feynman–Kac formula that represents semilinear parabolic PDEs probabilistically. Applications to stochastic optimal control (HJB) and the Deep BSDE numerical method.

- [`IV.tex`](04-bsde/IV.tex) — 中文版
- [`IV_en_us.tex`](04-bsde/IV_en_us.tex) — English draft
- [`figures/`](04-bsde/figures/)

## Lecture V — Forward–Backward SDEs and the Stochastic Maximum Principle

Coupled FBSDEs and why naive Picard iteration fails (Antonelli's example), the Hu–Peng monotonicity method, the Ma–Protter–Yong four-step scheme and decoupling fields, the stochastic maximum principle and its duality with HJB, the LQ problem via Riccati, constrained utility maximization, and Deep FBSDE.

- [`V.tex`](05-fbsde/V.tex) — 中文版 (an English version exists only as the published PDF; no `V_en_us.tex` source yet)
- [`figures/`](05-fbsde/figures/)

---

## Building the PDFs

Each lecture folder is self-contained — it ships its own copy of `math_blog.sty` so you can compile in place:

```bash
cd 01-brownian-motion
xelatex I.tex          # 中文版 (Lectures III–V 中文版 also build with pdflatex via CJKutf8)
pdflatex I_en_us.tex   # English version
```

The `EM.tex` supplement in Lecture II uses `biblatex`; build with:

```bash
cd 02-ito-integral
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
├── 02-ito-integral/           # Lecture II (Itô integral + EM numerics)
│   ├── II.tex, II_en_us.tex
│   ├── EM.tex                 # supplementary
│   ├── ref.bib
│   └── math_blog.sty
├── 03-existence-uniqueness/   # Lecture III
│   ├── III.tex, III_en_us.tex
│   ├── generate_figures.py
│   ├── math_blog.sty
│   └── figures/
├── 04-bsde/                   # Lecture IV
│   ├── IV.tex, IV_en_us.tex (draft)
│   ├── generate_figures.py
│   ├── math_blog.sty
│   └── figures/
└── 05-fbsde/                  # Lecture V
    ├── V.tex
    ├── math_blog.sty
    └── figures/
```
