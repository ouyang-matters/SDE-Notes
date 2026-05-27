"""Generate 3 figures for SDE IV (BSDE article) as PNG files.

Output:
    figures/fig1_fwd_bwd.png       — forward-backward time picture
    figures/fig2_fisher_kpp.png    — simulated Y-paths for Fisher-KPP BSDE
    figures/fig3_deep_bsde.png     — Deep BSDE architecture schematic
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)
DPI = 200


# ---------- Figure 1: Forward-backward time picture ----------
def fig_fwd_bwd():
    rng = np.random.default_rng(11)
    T = 1.0
    t_start = 0.3
    n = 240
    ts = np.linspace(t_start, T, n)
    dt = ts[1] - ts[0]

    # Forward X path: drift 1.2, sigma 0.45, starting at x = 1.6
    dW = rng.normal(scale=np.sqrt(dt), size=n - 1)
    X = np.concatenate([[1.6], 1.6 + np.cumsum(1.2 * dt + 0.45 * dW)])

    fig, ax = plt.subplots(figsize=(10, 5.2))

    # X axis (time)
    ax.axhline(0, color="black", lw=0.8)
    ax.annotate("", xy=(1.06, 0), xytext=(-0.02, 0),
                arrowprops=dict(arrowstyle="->", lw=1.0, color="black"),
                xycoords=("axes fraction", "data"))
    ax.text(1.07, 0, "time", transform=ax.get_yaxis_transform(),
            ha="left", va="center", fontsize=11)

    # Time tick marks
    for tx, lbl in [(0.0, "$0$"), (t_start, "$t$"), (T, "$T$")]:
        ax.plot([tx, tx], [-0.05, 0.05], color="black", lw=1.0)
        ax.text(tx, -0.18, lbl, ha="center", va="top", fontsize=12)

    # Forward X path
    ax.plot(ts, X, color="C0", lw=2.0, label=r"forward SDE $X^{t,x}$")
    ax.plot(t_start, X[0], "o", color="C0", ms=7)
    ax.plot(T, X[-1], "o", color="C0", ms=7)
    ax.text(t_start - 0.012, X[0], r"$X^{t,x}_t = x$",
            ha="right", va="center", color="C0", fontsize=11)
    ax.text(T + 0.012, X[-1], r"$X^{t,x}_T$",
            ha="left", va="center", color="C0", fontsize=11)
    ax.annotate("", xy=(t_start + 0.30, 0.9), xytext=(t_start + 0.04, 0.9),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="C0", alpha=0.7))
    ax.text(t_start + 0.17, 0.78, "time $\\longrightarrow$",
            color="C0", alpha=0.8, fontsize=10, ha="center")

    # Backward Y path: synthetic descending random walk
    dWy = rng.normal(scale=np.sqrt(dt), size=n - 1)
    Y_top = -1.40
    Y_end = -2.05
    drift = (Y_end - Y_top) / (n - 1)
    Y = np.concatenate([[Y_top], Y_top + np.cumsum(drift + 0.10 * dWy)])
    # Force endpoints
    Y[-1] = Y_end
    ax.plot(ts, Y, color="C3", lw=2.0, label=r"backward SDE $(Y, Z)$")
    ax.plot(t_start, Y[0], "o", color="C3", ms=7)
    ax.plot(T, Y[-1], "o", color="C3", ms=7)
    ax.text(t_start - 0.012, Y[0], r"$Y_t = u(t, x)$",
            ha="right", va="center", color="C3", fontsize=11)
    ax.text(T + 0.012, Y[-1], r"$\xi = g(X_T)$",
            ha="left", va="center", color="C3", fontsize=11)
    ax.annotate("", xy=(t_start + 0.10, -0.55), xytext=(t_start + 0.36, -0.55),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="C3", alpha=0.7))
    ax.text(t_start + 0.23, -0.68, "$\\longleftarrow$ time",
            color="C3", alpha=0.8, fontsize=10, ha="center")

    # Dashed vertical connectors
    ax.plot([t_start, t_start], [Y[0], X[0]], "--", color="gray", lw=0.8, alpha=0.6)
    ax.plot([T, T], [Y[-1], X[-1]], "--", color="gray", lw=0.8, alpha=0.6)

    # Shared dB annotation
    ax.annotate("same $dB_s$", xy=(0.83, 0.6),
                xytext=(0.93, 1.4),
                arrowprops=dict(arrowstyle="->", lw=1.0,
                                color="gray", alpha=0.7),
                fontsize=10, color="dimgray", ha="center")
    ax.annotate("", xy=(0.83, -0.4),
                xytext=(0.93, 1.25),
                arrowprops=dict(arrowstyle="->", lw=1.0,
                                color="gray", alpha=0.7))

    ax.set_xlim(-0.03, 1.12)
    ax.set_ylim(-2.7, 3.6)
    ax.axis("off")
    ax.legend(loc="upper left", fontsize=11, frameon=True,
              bbox_to_anchor=(0.02, 0.98))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig1_fwd_bwd.png"),
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------- Figure 2: Fisher-KPP BSDE paths ----------
def fig_fisher_kpp():
    """Solve the semilinear PDE
        partial_t u + 1/2 partial_xx u + u(1-u) = 0,  u(T,x) = 1_{x>0}
    by backward finite differences (forward time tau = T - t), then sample
    Brownian paths and plot Y_s = u(s, B_s + x0) for several starting x0.
    """
    rng = np.random.default_rng(2026)
    T = 1.0
    # Spatial grid
    L = 6.0
    Nx = 481
    xs = np.linspace(-L, L, Nx)
    dx = xs[1] - xs[0]
    # Time grid (fine, explicit FTCS for the heat reaction equation)
    Nt = 4000
    dt = T / Nt
    assert dt / dx ** 2 < 0.5

    # Smooth the indicator slightly to avoid Gibbs near 0
    u = 0.5 * (1.0 + np.tanh(xs / 0.08))  # ≈ 1_{x>0}, smoothed
    U = np.zeros((Nt + 1, Nx))
    U[Nt] = u  # u at tau=0 corresponds to t=T

    # Time-reverse: integrate forward in tau = T - t
    # PDE for tilde u(tau, x) = u(T - tau, x):
    #   partial_tau tilde u = 1/2 partial_xx tilde u + tilde u (1 - tilde u)
    for k in range(Nt, 0, -1):
        lap = np.zeros_like(u)
        lap[1:-1] = (u[2:] - 2 * u[1:-1] + u[:-2]) / dx ** 2
        u = u + dt * (0.5 * lap + u * (1.0 - u))
        u = np.clip(u, 0.0, 1.0)  # numerical safety
        U[k - 1] = u

    def u_eval(t_idx, x_val):
        return np.interp(x_val, xs, U[t_idx])

    # Sample Brownian paths
    n_steps = Nt
    times = np.linspace(0.0, T, n_steps + 1)
    starting_x = [-0.5, -0.2, 0.2, 0.5]
    colors = ["C0", "C1", "C2", "C3"]
    labels = [f"$x_0 = {x0:+.1f}$" for x0 in starting_x]

    fig, ax = plt.subplots(figsize=(9, 5))
    # Bounds y=0, y=1
    ax.axhline(1, color="gray", lw=1.2, linestyle="--")
    ax.axhline(0, color="gray", lw=1.2, linestyle="--")
    ax.text(1.012, 1, r"$y\equiv 1$", color="gray", fontsize=10, va="center")
    ax.text(1.012, 0, r"$y\equiv 0$", color="gray", fontsize=10, va="center")

    for x0, c, lbl in zip(starting_x, colors, labels):
        dW = rng.normal(scale=np.sqrt(dt), size=n_steps)
        B = np.concatenate([[0.0], np.cumsum(dW)])
        path = x0 + B
        Y = np.array([u_eval(k, path[k]) for k in range(n_steps + 1)])
        ax.plot(times, Y, color=c, lw=1.8, label=lbl)
        ax.plot(times[0], Y[0], "o", color=c, ms=6)
        ax.plot(times[-1], Y[-1], "o", color=c, ms=6)

    ax.set_xlabel("$s$", fontsize=12)
    ax.set_ylabel("$Y_s = u(s, B_s + x_0)$", fontsize=12)
    ax.set_xlim(-0.02, 1.05)
    ax.set_ylim(-0.08, 1.12)
    ax.legend(loc="center right", fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig2_fisher_kpp.png"),
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)


# ---------- Figure 3: Deep BSDE architecture ----------
def fig_deep_bsde():
    fig, ax = plt.subplots(figsize=(11, 5.0))

    # Layout: Y row at y=1.4, X row at y=-0.6, loss box at y=-2.2
    y_y, y_x, y_loss = 1.4, -0.6, -2.4

    # Column x-positions for time steps 0, 1, 2, ..., M (5 nodes)
    cols_Y = [0.6, 2.6, 4.6, 6.6, 9.6]
    cols_z = [1.6, 3.6, 5.6, 8.6]  # between Y_k and Y_{k+1}
    cols_X = cols_Y

    # ----- draw Y circles (red) -----
    rY = 0.32
    Y_labels = ["$Y_0$", "$Y_1$", "$Y_2$", r"$\cdots$", "$Y_M$"]
    for cx, lbl in zip(cols_Y, Y_labels):
        if "cdots" in lbl:
            ax.text(cx, y_y, lbl, ha="center", va="center", fontsize=18)
        else:
            ax.add_patch(plt.Circle((cx, y_y), rY,
                                    facecolor="#fce0e0", edgecolor="#b04848",
                                    lw=1.4))
            ax.text(cx, y_y, lbl, ha="center", va="center", fontsize=11)
    ax.text(cols_Y[0], y_y - rY - 0.22, r"$= \theta_0$",
            ha="center", fontsize=10, color="#b04848")

    # ----- draw z-network boxes (blue) -----
    zw, zh = 0.85, 0.55
    z_labels = [r"$z^{\theta}_{0}$", r"$z^{\theta}_{1}$",
                r"$z^{\theta}_{2}$", r"$z^{\theta}_{M-1}$"]
    for cx, lbl in zip(cols_z, z_labels):
        ax.add_patch(FancyBboxPatch((cx - zw / 2, y_y - zh / 2), zw, zh,
                                    boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor="#dfe7fb", edgecolor="#3a5da6",
                                    lw=1.4))
        ax.text(cx, y_y, lbl, ha="center", va="center", fontsize=11)

    # ----- draw X boxes (gray) -----
    xw, xh = 1.05, 0.55
    X_labels = ["$X_0 = x_0$", "$X_1$", "$X_2$", r"$\cdots$", "$X_M$"]
    for cx, lbl in zip(cols_X, X_labels):
        if "cdots" in lbl:
            ax.text(cx, y_x, lbl, ha="center", va="center", fontsize=18)
        else:
            ax.add_patch(FancyBboxPatch((cx - xw / 2, y_x - xh / 2), xw, xh,
                                        boxstyle="round,pad=0.02,rounding_size=0.08",
                                        facecolor="#ececec", edgecolor="black",
                                        lw=1.2))
            ax.text(cx, y_x, lbl, ha="center", va="center", fontsize=11)

    # ----- arrows along Y row, edge-to-edge -----
    def harrow(x1, x2, y, **kw):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="-|>", lw=1.2,
                                    color="black", **kw))

    # Y_k -> z_k  and  z_k -> Y_{k+1}
    for k, zx in enumerate(cols_z):
        # left edge of z-box / right edge of Y_k circle (or text "...")
        ycenter_left = cols_Y[k]
        right_of_Y = ycenter_left + rY if Y_labels[k] != r"$\cdots$" else ycenter_left + 0.25
        left_of_z = zx - zw / 2
        right_of_z = zx + zw / 2
        ycenter_right = cols_Y[k + 1]
        left_of_Yn = ycenter_right - rY if Y_labels[k + 1] != r"$\cdots$" else ycenter_right - 0.25
        harrow(right_of_Y, left_of_z, y_y)
        harrow(right_of_z, left_of_Yn, y_y)

    # ----- arrows along X row -----
    for k in range(len(cols_X) - 1):
        left = cols_X[k] + (xw / 2 if X_labels[k] != r"$\cdots$" else 0.25)
        right = cols_X[k + 1] - (xw / 2 if X_labels[k + 1] != r"$\cdots$" else 0.25)
        harrow(left, right, y_x)
        if k < 2:
            mx = (left + right) / 2
            ax.text(mx, y_x + 0.45, f"$\\Delta B_{k}$",
                    ha="center", fontsize=10, color="dimgray")

    # ----- dashed feed-in from X_k to z_k -----
    for k, zx in enumerate(cols_z):
        xk_top = (cols_X[k], y_x + xh / 2)
        zk_bot = (zx, y_y - zh / 2)
        ax.annotate("", xy=zk_bot, xytext=xk_top,
                    arrowprops=dict(arrowstyle="-|>", lw=0.9,
                                    color="gray", linestyle="dashed",
                                    alpha=0.75))

    # ----- loss box -----
    lw, lh = 5.2, 0.75
    lx = 6.6
    ax.add_patch(FancyBboxPatch((lx - lw / 2, y_loss - lh / 2), lw, lh,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor="white", edgecolor="black",
                                lw=1.4))
    ax.text(lx, y_loss,
            r"$\mathcal{J}(\theta) = \mathbb{E}\,|g(X_M) - Y_M|^2$",
            ha="center", va="center", fontsize=12)

    # arrows from X_M and Y_M to loss box
    XM_x, XM_yb = cols_X[-1], y_x - xh / 2
    YM_x = cols_Y[-1]
    YM_yb = y_y - rY
    loss_top_left = (lx - lw / 4, y_loss + lh / 2)
    loss_top_right = (lx + lw / 4, y_loss + lh / 2)
    ax.annotate("", xy=loss_top_right, xytext=(XM_x, XM_yb),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color="black",
                                connectionstyle="arc3,rad=-0.15"))
    ax.annotate("", xy=loss_top_left, xytext=(YM_x, YM_yb),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color="black",
                                connectionstyle="arc3,rad=0.25"))

    # ----- row labels -----
    ax.text(-0.4, y_y, "$Y$:", ha="right", va="center", fontsize=13)
    ax.text(-0.4, y_x, "$X$:", ha="right", va="center", fontsize=13)
    ax.text(-0.4, y_loss, "loss:", ha="right", va="center", fontsize=13)

    # ----- caption-style legend at top -----
    ax.text(-0.4, 2.95,
            r"trainable: $\theta_0\in\mathbb{R}$ (initial value), "
            r"$\theta_{\mathrm{net}}$ (per-step neural nets);   "
            r"sampled: $\Delta B_k\sim\mathcal{N}(0,\Delta t)$",
            ha="left", va="center", fontsize=10, color="black",
            bbox=dict(boxstyle="round,pad=0.3", fc="#fafafa",
                      ec="lightgray"))

    ax.set_xlim(-0.9, 10.8)
    ax.set_ylim(-3.2, 3.4)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig3_deep_bsde.png"),
                dpi=DPI, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    fig_fwd_bwd()
    fig_fisher_kpp()
    fig_deep_bsde()
    print("All figures written to:", OUT)
