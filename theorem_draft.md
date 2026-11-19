# Headline 定理草稿（内部，非投稿正文）— v1

> 状态：DRAFT，供投前定理审计。所有量来自 `probe_v2.py` / `probe_v2_results.json`，参数为研究假设（ILLUSTRATIVE）。
> 纪律：定理陈述 = 证明能给出的最弱命题（原则 13）；每个常数显式（硬伤 D）；存在性条件显式（硬伤 C）；Remark 不得抬高结论（硬伤 E）。

## 0. 符号与模型（与 probe_v2 一致）
- $J=\mathrm{diag}(J_1,J_2,J_3)\succ0$；姿态单位四元数 $q=(q_0,q_v)$，$\dot q=\tfrac12 q\otimes[0,\omega]$；姿态角 $\varphi(t)=2\arccos|q_0(t)|$（$SO(3)$ 测地角）。
- 转子推力（平方转速空间）$u\in\mathbb R^4$，可行集
  $\mathcal U=\{u: 0\le u_i\le u_{\max},\ \sum_i u_i=F=mg\}$；力矩 $\tau=M_T u\in\mathbb R^3$，$M_T$ 为混叠器力矩三行（行元素和为 0，故悬停 $u_{\rm hov}=(F/4)\mathbf 1$ 满足 $M_Tu_{\rm hov}=0$）。
- 执行器一阶滞后：$\dot u=(u_c-u)/T_m$，$u(0)=u_{\rm hov}$，$T_m>0$。
- 方向 $n$（$\|n\|=1$）上**可用恢复力矩上界**（可行集支撑函数）：
  $\tau_{\max,n}=\max_{u\in\mathcal U}(-n)^\top M_T u$。
- 持续扰动 $d(t)$，仅假设有界：$|n^\top d(t)|\le \bar d$（对扰动类）。
- 冲击：$\omega(0^+)=\Delta\omega\, n$，角冲量 $L=J_n\Delta\omega$，$J_n=n^\top J n$。
- 恢复（冻结判据）：$\sup_{t\in[0,T]}\varphi(t)\le\Phi_{\max}$。

## 1. Lemma 1（执行器累计恢复力矩上界；控制器无关，严格）
对**任意**取值于 $\mathcal U$ 的控制序列 $u_c(\cdot)$，任意 $t\ge0$：
$$(-n)^\top\tau(t)\ \le\ \tau_{\max,n}\bigl(1-e^{-t/T_m}\bigr),\qquad
\int_0^t(-n)^\top\tau(s)\,ds\ \le\ \tau_{\max,n}\,\psi(t),\quad
\psi(t)=t-T_m\bigl(1-e^{-t/T_m}\bigr).$$

**证明.** 线性时不变方程 $\dot u=(u_c-u)/T_m$ 的卷积解
$u(t)=e^{-t/T_m}u_{\rm hov}+\int_0^t \tfrac{1}{T_m}e^{-(t-s)/T_m}u_c(s)\,ds$。
左乘 $M_T$，并用 $M_Tu_{\rm hov}=0$：
$(-n)^\top\tau(t)=\int_0^t\tfrac{1}{T_m}e^{-(t-s)/T_m}\,(-n)^\top M_Tu_c(s)\,ds$。
因 $u_c(s)\in\mathcal U$，由 $\tau_{\max,n}$ 定义有 $(-n)^\top M_Tu_c(s)\le\tau_{\max,n}$，核非负且
$\int_0^t\tfrac{1}{T_m}e^{-(t-s)/T_m}ds=1-e^{-t/T_m}$，得逐点式；再对 $t$ 积分得 $\psi(t)$。$\blacksquare$

*注*：Lemma 1 只用执行器物理（可行集 + 一阶滞后），**不含任何控制器结构、不含 Lyapunov 函数**，是「控制器无关」的严格来源。

## 2. Assumption A1（主轴解耦；必须显式，不得省略）
冲击方向 $n$ 是 $J$ 的主轴（$n\in\{e_1,e_2,e_3\}$），且恢复窗口内角速度保持平行 $n$：$\omega(t)=\omega_n(t)\,n$。此时 $\omega\times(J\omega)=0$。

## 3. Theorem 1（主轴方向、对抗扰动下的不可恢复必要界）
设 A1 成立，且**存在性条件** $\tau_{\max,n}>\bar d$ 成立，扰动处于**最坏（对抗）实现** $n^\top d(t)=+\bar d$（扰动与冲击同向、阻碍恢复）。定义
$$A(t)=\frac{\tau_{\max,n}\psi(t)-\bar d\, t}{J_n},\qquad
g(t;\Delta\omega)=\Delta\omega\, t-\int_0^t A(s)\,ds .$$
$A$ 最终严格增（$A'(t)\to(\tau_{\max,n}-\bar d)/J_n>0$），令 $t^*(\Delta\omega)$ 为 $A(t^*)=\Delta\omega$ 的唯一正根，$\varphi_{\min}(\Delta\omega)=g(t^*;\Delta\omega)$。
令 $\Delta\omega^*$ 为 $\varphi_{\min}(\Delta\omega^*)=\Phi_{\max}$ 的唯一根，$L^*=J_n\Delta\omega^*$。

**结论**：在该对抗扰动实现下，若 $L>L^*$，则**任意**控制序列都无法使 $\sup_{[0,T]}\varphi\le\Phi_{\max}$。等价地，可恢复角冲量集合 $\subseteq[0,L^*]$，即 $L^*$ 是可恢复域的一个**上界（必要界）**。

**证明.** 沿 $n$ 的角动量标量 $p=J_n\omega_n$。由刚体方程与 A1（陀螺项为零）：
$\dot p=n^\top\tau+n^\top d$。
由 Lemma 1 逐点式 $(-n)^\top\tau\le\tau_{\max,n}(1-e^{-t/T_m})$，即 $n^\top\tau\ge-\tau_{\max,n}(1-e^{-t/T_m})$：任意控制器**最多**只能提供该幅值的减速。代入对抗扰动 $n^\top d=+\bar d$，得
$$\dot p\ \ge\ -\tau_{\max,n}\bigl(1-e^{-t/T_m}\bigr)+\bar d .$$
积分：$\omega_n(t)\ge\Delta\omega-\dfrac{\tau_{\max,n}\psi(t)-\bar d\,t}{J_n}=\Delta\omega-A(t)$。

A1 下 $\varphi(t)=\int_0^t\omega_n(s)ds$（绕固定主轴的旋转角），故 $\varphi(t)\ge g(t;\Delta\omega)$。
$g'(t)=\Delta\omega-A(t)$，$A$ 单调段上 $g$ 在 $t^*$ 取极大，故 $\varphi(t^*)\ge\varphi_{\min}(\Delta\omega)$。
若 $\varphi_{\min}>\Phi_{\max}$，则任意控制器在 $t^*$ 时刻姿态已超限。由 $\varphi_{\min}$ 对 $\Delta\omega$ 严格增，$\Delta\omega>\Delta\omega^*\iff L>L^*$ 即不可恢复。$\blacksquare$

*证明链已由 `theorem_audit.py` 的 C5/P10 独立单轴 ODE 积分复算验证（analytic vs ODE rel = 1e-4 量级），且 C6/13b 从 $L^*$ 反解 $\Delta\omega^*$ 代回 $\varphi_{\min}=\Phi_{\max}$ 自洽。*

## 4. Remark 1（严格性边界，必写，防硬伤 E）
A1 在**组合方向**不成立（$\omega\times J\omega\neq0$，陀螺重定向），故 Theorem 1 **仅对主轴冲击严格成立**。组合方向的 $L^*$ 目前只有数值观测支持（`probe_v2_results.json`：对抗臂 $L_{\rm suff}/L_{\rm nec}\approx0.26$–$0.43$），**未获理论保证**，归入「未验证区域」。不得写成 "for arbitrary impulse directions"。

## 5. Remark 2（不抬高结论）
$L^*$ 是可恢复域的**上界（必要界）**，不是精确边界、不是充要条件。主轴方向数值上 $L_{\rm suff}/L^*\approx0.997$（紧）属**数值观测**，不作为定理结论，也不写 "tight / exact / if and only if" 于定理陈述。

## 6. Remark 3（存在性条件 + 扰动口径，硬伤 C / 防超证）
$\tau_{\max,n}>\bar d$ 是 $A$ 最终单调、$t^*$ 存在、界非 vacuous 的前提；若 $\tau_{\max,n}\le\bar d$ 则该方向标记为 `outside certified envelope`，**不得填数**。审计项 C3 逐方向给出数值。

**扰动口径（C2 量化裁定，必须写进 Limitations）**：Theorem 1 只对**对抗扰动实现** $n^\top d=+\bar d$ 成立。若要把结论推广到「对任意 $|n^\top d|\le\bar d$ 的扰动」，须改用更保守的 $A(t)=[\tau_{\max,n}\psi(t)+\bar d\,t]/J_n$，其必要界**更大**：`theorem_audit.json` C2 实测 roll 0.14257（vs 对抗 0.13736）、**yaw 0.09037（vs 0.07202，差 25%）**。本稿**未**采用该推广，故不得在摘要/结论里写「对任意有界扰动均保证不可恢复」。

## 7. 常数显式化（硬伤 D）
$\tau_{\max,n}$（支撑函数 LP）、$J_n$、$\bar d$、$T_m$、$\Phi_{\max}$、$u_{\max}$、$F$ 均由参数表给出显式数值；证明中**无** "for some $c>0$" 裸常数。$t^*$、$\Delta\omega^*$ 由一维根求解给出并落盘，可独立复算（审计项 P10）。

## 8. 待审计项映射（claim → evidence）
| 陈述中的 claim | 证明/证据来源 | 审计 |
|---|---|---|
| Lemma 1 逐点式 | 卷积解 + 支撑函数定义 | 真实轨迹逐点实测（C4） |
| $\omega_n\ge\Delta\omega-A(t)$ | Lemma 1 + A1 + 对抗扰动 | 独立单轴 ODE 积分（P10） |
| $\varphi\ge g$ | A1 固定轴旋转角 | Remark 1 限定 |
| $\varphi_{\min}$ 单调、根唯一 | $A$ 最终单调 + 存在性条件 | reverse-solve（C3/13b） |
| $L^*$ 为上界而非精确边界 | Remark 2 | 措辞扫描（E） |
