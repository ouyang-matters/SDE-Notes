"""Generate 5 figures for SDE III as PNG files."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
import os

OUT = os.path.dirname(os.path.abspath(__file__))
DPI = 200

# ---------- Figure 1: Generator (drift + diffusion cloud) ----------
def fig_generator():
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.axhline(0, color='black', lw=0.8)
    ax.annotate('', xy=(7, 0), xytext=(-0.3, 0),
                arrowprops=dict(arrowstyle='->', lw=1.0, color='black'))
    ax.text(7.05, 0, '$x$', fontsize=13, va='center')

    # point x
    ax.plot(1.5, 0, 'ko', ms=6)
    ax.text(1.5, -0.15, '$x$', fontsize=12, ha='center', va='top')
    ax.plot([1.5, 1.5], [-0.1, 2.4], '--', color='gray', lw=0.6, alpha=0.6)

    # drift arrow
    ax.annotate('', xy=(4, 1.6), xytext=(1.5, 1.6),
                arrowprops=dict(arrowstyle='->', lw=2.5, color='C0'))
    ax.text(2.75, 1.75, r'$a(x)\,\Delta t$', color='C0', fontsize=12, ha='center')
    ax.plot(4, 1.6, 'o', color='C0', ms=6)
    ax.plot([4, 4], [-0.1, 1.6], '--', color='C0', alpha=0.45, lw=0.7)
    ax.text(4, -0.15, r'$\mathbb{E}_x[X_{\Delta t}]$', color='C0', fontsize=11,
            ha='center', va='top')

    # Gaussian cloud
    xs = np.linspace(1.4, 6.6, 200)
    base = 0.55
    gauss = base + 1.5 * np.exp(-(xs - 4) ** 2 / (2 * 0.55 ** 2))
    ax.fill_between(xs, base, gauss, color='C3', alpha=0.30, edgecolor='C3', lw=1.5)
    ax.annotate('', xy=(4.85, 0.45), xytext=(3.15, 0.45),
                arrowprops=dict(arrowstyle='<->', lw=1.5, color='C3'))
    ax.text(4, 0.35, r'$\sim b(x)\,\sqrt{\Delta t}$', color='C3', fontsize=11,
            ha='center', va='top')

    ax.set_xlim(-0.5, 7.5)
    ax.set_ylim(-0.6, 2.7)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig1_generator.png'), dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ---------- Figure 2: Fokker–Planck (OU density evolution) ----------
def fig_fpe():
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = np.linspace(-3.5, 4, 400)

    def gauss(x, m, v):
        return np.exp(-(x - m) ** 2 / (2 * v)) / np.sqrt(2 * np.pi * v)

    # OU: theta=0.5, mu=0, sigma=1, X0=2
    # m(t)=2*exp(-0.5t), v(t)=1-exp(-t)
    cases = [
        (0.1, 1.903, 0.0952, 'C0', '$t=0.1$'),
        (0.5, 1.558, 0.393, 'C3', '$t=0.5$'),
        (2.0, 0.736, 0.865, 'C2', '$t=2.0$'),
    ]
    for t, m, v, c, lbl in cases:
        ax.plot(xs, gauss(xs, m, v), color=c, lw=2.0, label=lbl)
    ax.plot(xs, gauss(xs, 0, 1), 'k--', lw=2.0, label=r'$t\to\infty$ (stationary)')

    ax.set_xlabel('$x$', fontsize=12)
    ax.set_ylabel(r'$\rho(t,x)$', fontsize=12)
    ax.set_xlim(-3.5, 4)
    ax.set_ylim(0, 1.45)
    ax.legend(loc='upper right', fontsize=11, frameon=True)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig2_fokker_planck.png'), dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ---------- Figure 3: OU stationary histogram ----------
def fig_ou_stationary():
    rng = np.random.default_rng(42)
    theta, mu, sigma = 0.5, 0.0, 1.0
    dt, N = 0.01, 200_000
    x = np.zeros(N)
    sqrt_dt = np.sqrt(dt)
    for i in range(1, N):
        x[i] = x[i - 1] + theta * (mu - x[i - 1]) * dt + sigma * sqrt_dt * rng.normal()
    burn = 5000
    samples = x[burn:]

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.hist(samples, bins=50, density=True, color='gray', alpha=0.55,
            edgecolor='dimgray', lw=0.5, label='empirical histogram (simulated path)')
    xs = np.linspace(-4, 4, 400)
    ax.plot(xs, np.exp(-xs ** 2 / 2) / np.sqrt(2 * np.pi),
            color='C0', lw=2.5, label=r'$\mathcal{N}(\mu,\sigma^2/2\theta)$')

    ax.set_xlabel('$x$', fontsize=12)
    ax.set_ylabel('density', fontsize=12)
    ax.set_xlim(-4, 4)
    ax.set_ylim(0, 0.48)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig3_ou_stationary.png'), dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ---------- Figure 4: Girsanov (same paths under P vs Q) ----------
def fig_girsanov():
    rng = np.random.default_rng(7)
    T, N = 5.0, 500
    t = np.linspace(0, T, N)
    dt = T / (N - 1)
    sigma = 0.5
    mu_P, r_Q = 0.5, 0.05

    # generate 3 paths under P (drift mu_P)
    paths = []
    for _ in range(3):
        dW = rng.normal(scale=np.sqrt(dt), size=N - 1)
        x = np.concatenate([[0], np.cumsum(mu_P * dt + sigma * dW)])
        paths.append(x)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), sharey=True)
    colors = ['gray', 'dimgray', 'darkgray']

    # Left: under P
    ax = axes[0]
    for p, c in zip(paths, colors):
        ax.plot(t, p, color=c, lw=1.3)
    ax.plot(t, mu_P * t, '--', color='C0', lw=2.2, label=r'$\mu t$')
    ax.set_title(r'Under $\mathbb{P}$ (drift $\mu$)', fontsize=13)
    ax.set_xlabel('$t$', fontsize=12)
    ax.set_ylabel('$X_t$', fontsize=12)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.25)

    # Right: same paths under Q
    ax = axes[1]
    for p, c in zip(paths, colors):
        ax.plot(t, p, color=c, lw=1.3)
    ax.plot(t, r_Q * t, '--', color='C3', lw=2.2, label=r'$rt$')
    ax.set_title(r'Under $\mathbb{Q}$ (drift $r$)', fontsize=13)
    ax.set_xlabel('$t$', fontsize=12)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.25)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig4_girsanov.png'), dpi=DPI, bbox_inches='tight')
    plt.close(fig)


# ---------- Figure 5: Coda triangle (SDE-PDE bridge) ----------
def fig_bridge():
    fig, ax = plt.subplots(figsize=(11, 7))

    def box(xy, w, h, text, fc):
        x, y = xy
        rect = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                              boxstyle="round,pad=0.02,rounding_size=0.1",
                              linewidth=1.6, edgecolor='black', facecolor=fc)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=11)
        return (x, y, w, h)

    def arrow(p1, p2, label='', dy_lbl=0, dx_lbl=0, style='->'):
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle=style, lw=1.6, color='black',
                                    shrinkA=2, shrinkB=2))
        if label:
            mx, my = (p1[0] + p2[0]) / 2 + dx_lbl, (p1[1] + p2[1]) / 2 + dy_lbl
            ax.text(mx, my, label, ha='center', va='center', fontsize=10,
                    style='italic',
                    bbox=dict(boxstyle='round,pad=0.2', fc='white',
                              ec='none', alpha=0.9))

    # Boxes
    box_w, box_h = 4.4, 1.1
    sde_pos  = (5.0, 6.0)
    gen_pos  = (5.0, 3.8)
    back_pos = (2.3, 1.3)
    fwd_pos  = (7.7, 1.3)

    box(sde_pos, box_w, box_h,
        r"$\mathbf{SDE}$" + "\n" + r"$dX_t = a(X_t)\,dt + b(X_t)\,dB_t$", '#cfe2ff')
    box(gen_pos, box_w, box_h,
        r"$\mathbf{Generator}$" + "\n" + r"$\mathcal{L} = a\,\partial_x + \frac{1}{2}b^2\,\partial_{xx}^2$", '#ffe5b4')
    box(back_pos, box_w, 1.4,
        r"$\mathbf{Backward}$" + "\n" + r"$\partial_t u + \mathcal{L}u = 0$" + "\n" +
        r"$u(t,x)=\mathbb{E}_{t,x}[f(X_T)]$", '#d4edda')
    box(fwd_pos, box_w, 1.4,
        r"$\mathbf{Forward\ (FPE)}$" + "\n" + r"$\partial_t \rho = \mathcal{L}^* \rho$" + "\n" +
        r"$\rho(t,x):$ density of $X_t$", '#d4edda')

    # Arrows
    arrow((sde_pos[0], sde_pos[1] - box_h / 2),
          (gen_pos[0], gen_pos[1] + box_h / 2),
          label="Itô's formula", dx_lbl=1.0)

    arrow((gen_pos[0] - box_w / 4, gen_pos[1] - box_h / 2),
          (back_pos[0] + box_w / 4, back_pos[1] + 0.7),
          label='observables', dx_lbl=-0.5, dy_lbl=0.25)

    arrow((gen_pos[0] + box_w / 4, gen_pos[1] - box_h / 2),
          (fwd_pos[0] - box_w / 4, fwd_pos[1] + 0.7),
          label='densities ($\\mathcal{L}^*$)', dx_lbl=0.5, dy_lbl=0.25)

    # Feynman-Kac: dashed curved arrow between bottom boxes
    ax.annotate('', xy=(fwd_pos[0] - box_w / 2 - 0.05, fwd_pos[1] - 0.3),
                xytext=(back_pos[0] + box_w / 2 + 0.05, back_pos[1] - 0.3),
                arrowprops=dict(arrowstyle='->', lw=1.4, color='black',
                                linestyle='dashed',
                                connectionstyle='arc3,rad=-0.35'))
    ax.text(5.0, -0.1, 'Feynman–Kac (discount $r$, source $g$)',
            ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='gray', alpha=0.95))

    # Girsanov self-loop on SDE box (right side)
    sde_r = (sde_pos[0] + box_w / 2, sde_pos[1])
    ax.annotate('', xy=(sde_r[0], sde_r[1] - 0.35),
                xytext=(sde_r[0], sde_r[1] + 0.35),
                arrowprops=dict(arrowstyle='->', lw=1.4, color='black',
                                linestyle='dashed',
                                connectionstyle='arc3,rad=-1.5'))
    ax.text(sde_r[0] + 1.1, sde_r[1], 'Girsanov', fontsize=10, style='italic',
            ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.9))

    ax.set_xlim(-0.5, 11)
    ax.set_ylim(-0.8, 7.3)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig5_bridge.png'), dpi=DPI, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    fig_generator()
    fig_fpe()
    fig_ou_stationary()
    fig_girsanov()
    fig_bridge()
    print('All figures generated in', OUT)
