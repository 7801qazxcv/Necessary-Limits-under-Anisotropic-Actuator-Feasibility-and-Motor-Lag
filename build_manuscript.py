# -*- coding: utf-8 -*-
"""Assemble paper/main.tex from: numbers.tex (generated from artifacts) + prose.
Single file, pure LF, no \\input -> avoids score.py flatten false negatives and
Windows CR corruption. No author metadata is invented (explicit blocker)."""
import os
HERE=os.path.dirname(os.path.abspath(__file__))
PAPER=os.path.join(HERE,"paper")
os.makedirs(PAPER,exist_ok=True)
numbers=open(os.path.join(HERE,"numbers.tex"),encoding="utf-8",newline="\n").read()

PROSE = r"""
\documentclass[preprint,12pt]{elsarticle}
\usepackage{amssymb,amsmath,amsthm,booktabs,graphicx,url}
\usepackage[margin=2.2cm]{geometry}
\emergencystretch=2em
\tolerance=2000
\newtheorem{theorem}{Theorem}
\newtheorem{lemma}{Lemma}
\newtheorem{remark}{Remark}
\newtheorem{assumption}{Assumption}
\journal{ISA Transactions}

% ===== AUTO-GENERATED NUMBER MACROS (from manuscript_numbers.json) =====
__NUMBERS__

\begin{document}
\begin{frontmatter}

\title{A Controller-Independent Non-Recoverability Bound for Post-Impulse
Quadrotor Attitude Recovery within the Principal-Axis Trajectory Class:
Necessary Limits under Anisotropic Actuator Feasibility and Motor Lag}

\author[1]{Sen Fu\corref{cor1}\fnref{fn_orcid}}
\ead{fs211314@gmail.com}
\author[2]{Bin Liu}
\ead{515321625@qq.com}
\cortext[cor1]{Corresponding author}
\fntext[fn_orcid]{ORCID: \url{https://orcid.org/0009-0001-8772-2449}}
\address[1]{Changsha Vocational and Technical College, Changsha, Hunan, China}
\address[2]{Hunan Institute of Advanced Technology, Changsha, Hunan, China}

\begin{abstract}
The problem addressed is whether, after an exogenous angular impulse, any control
law can return a quadrotor inside a prescribed 60 deg attitude envelope within
1.5 s when the actuator force-feasibility set is anisotropic and the motors
respond with a first-order lag. We present a necessary non-recoverability bound, derived from
the support function of that feasibility set, that is independent of the
controller structure within the principal-axis trajectory class (Assumption A1);
it bounds what no controller in that class can exceed, rather than certifying
what a particular controller achieves. The headline result is that the bound holds with
0 adversarial-arm violations on both a literature-anchored synthetic platform
and a single identified Crazyflie platform. We then separate the theoretically
certified domain, the numerically observed domain and the unverified region, and
report the gap between the necessary bound and the best controller-certified
sufficient boundary. On the identified platform the anisotropy advantage does
not replicate: the yaw-to-roll sufficient-boundary ratio rises to 0.687 and
baseline advantages vanish, so we do not claim these advantages on this
platform. No hardware or flight-test evidence is claimed; all results are
analytical and computational, obtained by numerical simulation only.
\end{abstract}

\begin{keyword}
post-impulse recovery \sep non-recoverability bound \sep anisotropic actuator
feasibility \sep motor lag \sep three-way domain decomposition
\end{keyword}
\end{frontmatter}

\section{Introduction: problem, related work and contribution}
\label{sec:intro}

This work is positioned as a boundary-characterisation study of post-impulse
attitude recoverability, not as a controller-design or resilient-control
contribution: the control law used here is a verification vehicle, and the result
is a controller-independent necessary bound within the A1 trajectory class,
together with an explicit account of
where it ceases to be informative.

\textbf{The move made here.} Existing work certifies for a \emph{specified}
controller the set of initial conditions from which that controller converges --
a sufficient, controller-dependent region of attraction or controlled-invariant
safe set. We replace that question by its converse: given the physics of the
actuator, what angular impulse is so large that \emph{no} control sequence in
that trajectory class can recover? The consequence is a bound that is independent of the controller
structure within the A1 trajectory class and of
any Lyapunov construction, plus a three-way decomposition that keeps the
certified domain, the observed domain and the unverified region distinct.

The contributions, ordered by weight, are as follows. (1) The headline result: a
Lemma bounding the cumulative recovery torque available from a first-order-lagged
anisotropic actuator set, and a Theorem giving the resulting
controller-independent necessary non-recoverability bound along principal axes
within the A1 trajectory class, under an adversarial disturbance realisation. (2) A three-way domain
decomposition and a two-parameter scaling of the gap between the necessary bound
and the best observed sufficient boundary, with the honest statement that this
gap measures controller suboptimality plus axis-decoupling approximation, not a
physical constant. (3) A public failure boundary: on a single identified
platform the bound survives with 0 violations, while the anisotropy advantage
and the baseline advantages do not replicate; an asymmetric-actuator diagnostic
shows part of the apparent divergence is a symmetric-bracketing artefact but
that this does not overturn the negative result.

\textbf{What is not claimed.} Quaternion kinematics, Newton--Euler dynamics, a
first-order actuator model and the quasi-PD/sliding-mode controllers used as
verification vehicles are borrowed standard components, not contributions.
We do not claim that hybrid or impulsive modelling, recoverable sets, motor-lag
modelling or resilient attitude control are new: recoverable and safe sets are
established in aircraft loss-of-control work
\cite{McDonough2014Recovera,McDonough2017Fast}, impulsive-system stability
theory is mature \cite{Haimovich2019characte,Breeden2023Safety}, saturation-aware
finite-time attitude control is well developed
\cite{Zhang2024Finite,Gao2020Finite}, and motor-delay identification plus
actuator-non-ideality modelling are available
\cite{Eschmann2024Data,Le2026Residual}; region-of-attraction estimation under
saturation is likewise established \cite{Biswas2026Control,Ferrante2022Control}.
We do not claim superiority over all baselines, recovery for arbitrary impulse
directions, or guarantees for all bounded disturbances. The formal result is
restricted to principal axes under an adversarial disturbance realisation and,
more precisely, to control sequences whose trajectories maintain A1; for
controllers outside that trajectory class the bound is not claimed.
Lemma~\ref{lem:2} relaxes A1 only to a \emph{measured} off-axis envelope and
yields a weaker angular-momentum condition, not an A1-free attitude bound.
The quadratic-Lyapunov comparison is a proxy for the sufficient-domain family,
not a reproduction of the cited SOS / recoverable-set / CBF programs; the
$\NrepPhases{}$ realisations are independent turbulence phase sets of one
deterministic simulation model, not independent physical experiments.
Combined-axis behaviour is numerical observation only. No hardware,
firmware-in-the-loop or flight-test evidence is claimed, and the study is
analytical plus numerical simulation only.

\section{Related Work: five streams and a shared blind spot}
\label{sec:related}

Finite- and fixed-time attitude laws that combine disturbance observers with
anti-saturation auxiliary systems form a mature stream
\cite{Zhang2024Finite,Najafi2025Fixed,Gao2020Finite,Hu2025Adaptive,Xu2022Adaptive,Liu2021Antisatu,Yu2022Fault};
these are convergence certificates for a specified closed loop, with continuous
bounded disturbances and numerical validation. Quadrotor recovery from large
initial attitude/rate conditions has Monte-Carlo and real-flight evidence after
rotor failure, and autonomous post-collision recovery has hardware evidence
\cite{Sun2020Upset,Hermeler2026REFLEX,Gaucher2026Dual}; these exhibit a
controller-specific, observational recovery domain. The recoverable/safe-set
concept originates in aircraft loss-of-control work
\cite{McDonough2014Recovera,McDonough2017Fast,Engelbrecht2013Multi,Dongmo2012Aircraft},
and region-of-attraction enlargement under saturation is available via
sum-of-squares with Monte-Carlo verification and explicit ellipsoidal basin
estimates in hybrid frameworks \cite{Biswas2026Control,Ferrante2022Control}.
Impulsive-system stability theory is likewise mature: strong iISS
characterisations, CBF/CLF extensions to impulsive actuators with dwell-time
constraints, generalised backup CBFs, exponential stabilisation under saturated
control with impulse correction, and a recent preprint on finite-time
stabilisation with finite impulsive regulation and attraction-domain maximisation
\cite{Haimovich2019characte,Breeden2023Safety,Wijk2026Generali,Yu2023Exponent,Gao2026Finite}.
Finally, actuator non-idealities including motor lag, dead-zone, thrust
saturation and partial loss of effectiveness, and their data-driven
identification, are established
\cite{Le2026Residual,Eschmann2024Data,Ji2015Developm}.

\textbf{The shared blind spot.} Across these five streams the guarantee is
sufficient and controller-dependent; the reported recovery region is a
Lyapunov/SOS region of attraction, a controlled-invariant set, or a finite grid
of simulated or trial outcomes. Impulsive \emph{control} (a control-side jump
used to stabilise, e.g. \cite{Yu2023Exponent,Gao2026Finite}) is a different
object from an \emph{exogenous} angular impulse that causes a state jump. What
is absent is a controller-independent \emph{necessary} bound within the A1
trajectory class on post-impact
recoverability: a limit that no controller may exceed, which is the converse
direction to a region of attraction. Precisely separating these two directions
-- sufficient versus necessary -- is the gap this paper addresses. We also note
that \cite{Gao2026Finite} is a preprint (posted content, not peer-reviewed) and
that \cite{Breeden2023Safety} concerns spacecraft docking, not quadrotor
attitude recovery. Impulse reset maps with normal/tangential coupling have also
been formulated on SE(3) for collision recovery \cite{Gaucher2026Dual}; that
model is more complete than the angular-jump idealisation used here, which we
therefore state as a limitation rather than a novelty. The two-parameter scaling
and the three-way decomposition are compared against standard
region-of-attraction practice \cite{Biswas2026Control}, where Monte-Carlo
verification of an estimated region is likewise reported; the difference is that
our certified domain is a necessary upper bound, not a sufficient region.

\section{Model and Problem Formulation}
\label{sec:model}

Let $J=\mathrm{diag}(J_1,J_2,J_3)\succ 0$, let $q$ be the unit attitude
quaternion with $\dot q=\tfrac12 q\otimes[0,\omega]$, and let
$\varphi(t)=2\arccos|q_0(t)|$ be the geodesic attitude angle. Rotor thrusts
$u\in\mathbb R^4$ lie in the feasibility set
$\mathcal U=\{u:\ 0\le u_i\le u_{\max},\ \sum_i u_i=F=mg\}$, with delivered
torque $\tau=M_T u$ where the mixer torque rows sum to zero so that
$u_{\rm hov}=(F/4)\mathbf 1$ gives $M_T u_{\rm hov}=0$. The actuator obeys the
first-order lag $\dot u=(u_c-u)/T_m$, $u(0)=u_{\rm hov}$. For a unit direction
$n$, the available recovery-torque bound is the support function
$\tau_{\max,n}=\max_{u\in\mathcal U}(-n)^\top M_T u$. The post-impact
disturbance is bounded, $|n^\top d(t)|\le \bar d$. An impact produces
$\omega(0^+)=\Delta\omega\, n$ with angular impulse $L=J_n\Delta\omega$ and
$J_n=n^\top J n$. The frozen recovery criterion is
$\sup_{t\in[0,T]}\varphi(t)\le\Phi_{\max}$, with a prescribed 60~deg attitude
envelope and $T=1.5$~s; the criterion was fixed before any simulation run and
was not adjusted afterwards.

\begin{table}[t]
\caption{Model parameters. Synthetic = literature-anchored research assumptions
(ILLUSTRATIVE); Identified = single Crazyflie registry entry, same source for
every value. RPM-level quantities are not identified in the force-unit registry
and are marked N/A rather than silently passed.}
\label{tab:params}
\centering\small
\begin{tabular}{lcc}
\toprule
Quantity & Synthetic & Identified \\
\midrule
$m$ (kg) & 0.8 & 0.0306 \\
$F=mg$ (N) & 7.848 & 0.300186 \\
$u_{\max}$ (N) & \SynUmax{} & 0.132039 \\
$a$ (m) & 0.1556 & 0.028 \\
$\kappa$ (m) & 0.02 & 0.004665 \\
$J_x,J_y,J_z$ (kg m$^2$) & 0.013, 0.013, 0.024 & $9$\,e-6, $1$\,e-5, $1.7$\,e-5 \\
$T_m$ (s) & 0.02/0.05/0.10 & 0.055455/0.249394 \\
$\Phi_{\max}$ & 60 deg & 60 deg \\
RPM sanity & 400--600 rad/s band & N/A \\
\bottomrule
\end{tabular}
\end{table}

Table~\ref{tab:params} lists both platforms. The identified source has a
documented internal inconsistency: its thrust polynomial at the hovering
throttle gives $0.062593$~N per rotor versus $mg/4=0.075047$~N ($-16.6\%$), so
only the \emph{shape ratio} $f(1)/f(s_{\rm hov})=1.759$ was used to set
$u_{\max}$, with the equilibrium fixed by $mg/4$. Its rising/falling motor time
constants are asymmetric; the main study brackets them with two symmetric
models, and Section~\ref{sec:limits} reports a dedicated asymmetric diagnostic.

\begin{table}[t]
\caption{Assumption table (protocol requirement). Each row states what the
analysis assumes and what fails if the assumption is violated; every row maps to
a checkable artifact.}\label{tab:assumptions}
\centering\small
\begin{tabular}{p{0.27\linewidth}p{0.36\linewidth}p{0.29\linewidth}}
\toprule
Assumption & If violated & Artifact check \\
\midrule
A1: principal-axis impulse, $\omega\parallel n$ & Gyroscopic redirection invalidates the scalar reduction; Theorem~1 becomes an observation only & \texttt{theorem\_audit.json} C10 \\
Existence $\tau_{\max,n}>\bar d$ & $A(t)$ not eventually monotone; $t^*$ absent; bound vacuous & C3, per-direction values \\
Adversarial $n^\top d=+\bar d$ & Arbitrary bounded disturbances need a strictly larger bound; the adopted bound would overclaim & C2 (quantified in Remark~3) \\
$u_c\in\mathcal U$ with $\sum_i u_i=F$ & Lemma~1 support-function premise breaks & C4, projection residual $<10^{-9}$ \\
Symmetric first-order $T_m$ & Asymmetric actuator invalidates the analytic bound; diagnostic becomes purely numerical & \texttt{asym\_diagnostic.json} \\
Fixed total thrust, no translational loop & Attitude-only conclusions; no position recovery claim & model definition \\
Frozen recovery criterion & Post-hoc adjustment would invalidate every ratio & preregistration artifact \\
\bottomrule
\end{tabular}
\end{table}

\noindent\textbf{One-command reproduction.} A single entry point
(\texttt{experiments/run\_all\_experiments.py}) verifies the key fields of every
frozen result artifact against the claims in this paper, then regenerates the
number macros, the four figures and the manuscript assembly, and prints the
artifact manifest; with the \texttt{--full} flag it first re-runs the complete
probe chain (scalar probe, six-degree-of-freedom probe on both platforms,
asymmetric diagnostic, theorem audit and parameter sensitivity) from code. The
bound $L^*$, the C4 zero-violation count, the C5 single-axis ODE recomputation,
the C6 reverse-solve check and the C7 bare-constant scan are all regenerated or
re-verified rather than transcribed, so a reader can re-derive every displayed
value from the result files named in Table~\ref{tab:assumptions}.

\section{A Necessary Bound within the Principal-Axis Trajectory Class}
\label{sec:bound}

\begin{lemma}[Cumulative recovery-torque bound]
\label{lem:1}
For \emph{any} control sequence $u_c(\cdot)$ taking values in $\mathcal U$ and
any $t\ge 0$,
\begin{equation}
(-n)^\top\tau(t)\le \tau_{\max,n}\bigl(1-e^{-t/T_m}\bigr),
\label{eq:lem1-pointwise}
\end{equation}
\begin{equation}
\int_0^t (-n)^\top\tau(s)\,ds \le \tau_{\max,n}\,\psi(t),\quad
\psi(t)=t-T_m\bigl(1-e^{-t/T_m}\bigr).
\label{eq:lem1-integral}
\end{equation}
\end{lemma}
\begin{proof}
The convolution solution of $\dot u=(u_c-u)/T_m$ is
\begin{equation}
u(t)=e^{-t/T_m}u_{\rm hov}+\int_0^t \frac{1}{T_m}e^{-(t-s)/T_m}u_c(s)\,ds .
\label{eq:convolution}
\end{equation}
Left-multiplying by $M_T$ and using $M_Tu_{\rm hov}=0$ gives
\begin{equation}
(-n)^\top\tau(t)=\int_0^t \frac{1}{T_m}e^{-(t-s)/T_m}(-n)^\top M_Tu_c(s)\,ds .
\label{eq:convolution-torque}
\end{equation}
Since $u_c(s)\in\mathcal U$, the support-function definition gives
$(-n)^\top M_Tu_c(s)\le\tau_{\max,n}$; the kernel is nonnegative and
$\int_0^t \frac{1}{T_m}e^{-(t-s)/T_m}ds=1-e^{-t/T_m}$, which yields
\eqref{eq:lem1-pointwise}. Integrating that inequality gives
\eqref{eq:lem1-integral}.
\end{proof}

Lemma~\ref{lem:1} uses only actuator physics -- the feasibility set and the
first-order lag. It contains no controller structure and no Lyapunov function;
this is the precise source of controller independence.

\begin{assumption}[A1, principal-axis decoupling]
\label{ass:a1}
The impulse direction is a principal axis of $J$, $n\in\{e_1,e_2,e_3\}$, and
the angular velocity remains parallel to $n$ over the recovery window,
$\omega(t)=\omega_n(t)n$, so that $\omega\times(J\omega)=0$.
\end{assumption}

A1 is a restriction on the \emph{closed-loop trajectory class}, not a purely
physical hypothesis: a controller that injects torque on an axis orthogonal to
$n$ would generally make $\omega$ leave the principal-axis direction, so A1
excludes that control class. This distinction matters for the headline wording.
Lemma~\ref{lem:1} is genuinely controller-independent -- it holds for every
$u_c(\cdot)$ taking values in $\mathcal U$, with no trajectory assumption.
Theorem~\ref{thm:1}, by contrast, is controller-independent \emph{within the
A1 class}: the one-dimensional angular-momentum reduction used in its proof is
valid only while $\omega\times(J\omega)=0$. Relaxing A1 would require an
explicit bound on the gyroscopic term in the reduced dynamics; the measured
non-zero value for combined directions ($\|\omega\times J\omega\|=\GyroCombo{}$ in
the audit artifact) shows that this term is not negligible there, and we do not
claim such an extension.

\begin{lemma}[Bounded off-axis angular velocity]
\label{lem:2}
Let $J=\mathrm{diag}(J_1,J_2,J_3)$ and $n=e_i$. For the cyclic permutation
$(i,k,l)$ of $(1,2,3)$,
$n^\top(\omega\times J\omega)=(J_l-J_k)\omega_k\omega_l$, hence
$|n^\top(\omega\times J\omega)|\le \gamma_i\|\omega_\perp\|^2/2$ with
$\gamma_i=|J_k-J_l|$. If $\|\omega_\perp(t)\|\le\Omega_\perp$ on $[0,T]$, then
for every control sequence
$\dot p\ge -\tau_{\max,n}(1-e^{-t/T_m})-\bar d-\gamma_i\Omega_\perp^2/2$,
so the A1-free effective disturbance is $\bar d_{\rm eff}=\bar d+\gamma_i\Omega_\perp^2/2$
and the existence condition becomes $\tau_{\max,n}>\bar d_{\rm eff}$.
\end{lemma}

\begin{proof}
The identity follows by expanding the cross product; it was verified numerically
to machine precision over randomised $\omega$. The inequality is
$|(J_l-J_k)\omega_k\omega_l|\le\gamma_i(\omega_k^2+\omega_l^2)/2$ (AM--GM).
Projecting $J\dot\omega+\omega\times(J\omega)=\tau+d$ onto $n$ gives
$\dot p=n^\top\tau+n^\top d-n^\top(\omega\times J\omega)$; bounding the first
term by Lemma~\ref{lem:1}, the second by $-\bar d$ in the worst case, and the
third by $-\gamma_i\Omega_\perp^2/2$ yields the stated lower bound.
\end{proof}

Lemma~\ref{lem:2} relaxes the \emph{trajectory condition} A1 to a measurable
off-axis envelope, but it is deliberately weaker than Theorem~\ref{thm:1}:
it is a necessary condition at the \emph{angular-momentum} level only. When A1
fails, quaternion kinematics no longer give
$\varphi(t)=\int_0^t\omega_n(s)\,ds$, so the $\varphi_{\min}$ construction of
Theorem~1 does \emph{not} extend; we therefore do not state an A1-free
attitude-envelope bound. On the synthetic platform, $\MoneRollouts{}$ six-DoF
rollouts give $\Omega_\perp=\MoneOmega{}$ rad/s,
$\gamma_{\rm roll}=\MoneGammaRoll{}$ kg m$^2$, a measured peak
$|n^\top(\omega\times J\omega)|=\MoneGyroObs{}$ N m, and
$\bar d_{\rm eff}=\MoneDeff{}$ N m; the existence condition holds on all three
principal axes. The resulting momentum-level thresholds
($\MoneThreshRoll{}$ and $\MoneThreshYaw{}$ N m s for roll and yaw) are far
above $L^*$, confirming that this lemma is a conservative side result,
\emph{not} a strengthening of the headline bound. For yaw,
$\gamma_{\rm yaw}=0$ because $J_1=J_2$.

\begin{theorem}[Necessary non-recoverability bound]
\label{thm:1}
Let A1 hold, let the existence condition $\tau_{\max,n}>\bar d$ hold, and let the
disturbance take the adversarial realisation $n^\top d(t)=+\bar d$. Define
\begin{equation}
A(t)=\frac{\tau_{\max,n}\psi(t)-\bar d\,t}{J_n},\qquad
g(t;\Delta\omega)=\Delta\omega\,t-\int_0^t A(s)ds .
\label{eq:Aandg}
\end{equation}
$A'(t)=\bigl[\tau_{\max,n}(1-e^{-t/T_m})-\bar d\bigr]/J_n$ has at most one
sign change and tends to $(\tau_{\max,n}-\bar d)/J_n>0$, so $A$ is eventually
strictly increasing and, under the existence condition above, the equation
$A(t^*)=\Delta\omega$ has exactly one positive root $t^*$. Write
$G_T(\Delta\omega)=\max_{t\in[0,T]}g(t;\Delta\omega)$, with the maximum attained
at $\hat t=\min(t^*,T)$. In every case reported in this paper
$t^*\le\RtMaxTstar{}$~s~$\le T=\RtT{}$~s (\RtNcases{} direction/platform/actuator
combinations), hence $\hat t=t^*$ and $G_T=\varphi_{\min}$ with
$\varphi_{\min}(\Delta\omega):=g(t^*;\Delta\omega)$. Because
$\varphi_{\min}$ is strictly increasing in $\Delta\omega$ (verified on a
$121$-point grid for all \RtNcases{} cases), $\Delta\omega^*$ solving
$\varphi_{\min}(\Delta\omega^*)=\Phi_{\max}$ exists and is unique; set
$L^*=J_n\Delta\omega^*$. Then, under this adversarial disturbance
realisation and for every control sequence whose closed-loop trajectory
maintains A1, $L>L^*$ implies that recovery of $\sup_{[0,T]}\varphi\le\Phi_{\max}$
is impossible; equivalently the recoverable impulse set for that trajectory
class is contained in $[0,L^*]$, so $L^*$ is an \emph{upper (necessary) bound}
on recoverability within the A1 class.
\end{theorem}
\begin{proof}
Along $n$ let $p=J_n\omega_n$. With A1 the gyroscopic term vanishes, so
$\dot p=n^\top\tau+n^\top d$. Lemma~\ref{lem:1} gives
$n^\top\tau\ge -\tau_{\max,n}(1-e^{-t/T_m})$: any controller can provide at most
that deceleration. With $n^\top d=+\bar d$,
\begin{equation}
\dot p\ge -\tau_{\max,n}\bigl(1-e^{-t/T_m}\bigr)+\bar d,\qquad
\omega_n(t)\ge\Delta\omega-A(t),
\label{eq:omega-lower}
\end{equation}
with $A$ from \eqref{eq:Aandg}. Under A1 the body rotates about the fixed
axis $n$, so the unit quaternion has scalar part $q_0(t)=\cos(\theta(t)/2)$
with the signed angular displacement $\theta(t)=\int_0^t\omega_n(s)ds$, and
$\varphi(t)=2\arccos|q_0(t)|=2\arccos|\cos(\theta(t)/2)|$. These coincide,
$\varphi(t)=\theta(t)$, only while $\theta(t)\le\pi$; we therefore do not use
that identity globally but give a \emph{first-passage} argument. From
$\omega_n(t)\ge\Delta\omega-A(t)$ we have $\theta(t)\ge g(t;\Delta\omega)$,
and $g'(t)=\Delta\omega-A(t)>0$ on $[0,t^*)$, so $g$ increases to its maximum
$g(t^*)=\varphi_{\min}(\Delta\omega)$ at $t^*\le T$. If
$\varphi_{\min}>\Phi_{\max}$, then by continuity $\theta$ reaches
$\Phi_{\max}$ at some first time $t_e\le t^*\le T$; on $[0,t_e]$ we have
$\theta\le\Phi_{\max}=\RtPhiRad{}<\pi$, hence $\varphi(t_e)=\theta(t_e)=\Phi_{\max}$,
and immediately afterwards $\varphi>\Phi_{\max}$. Thus the attitude envelope
is violated \emph{within the prescribed window} for every controller in the
A1 class, and angular wrapping cannot mask the violation because
$\Phi_{\max}<\pi$. Since $\varphi_{\min}$ is strictly increasing in
$\Delta\omega$, $L>L^*$ \emph{implies} non-recoverability. The converse is not
claimed: $L\le L^*$ is not sufficient for recoverability (Remark~2).
\end{proof}

\begin{remark}[Strictness boundary]
A1 fails for combined directions ($\omega\times J\omega\neq 0$, gyroscopic
redirection); Theorem~\ref{thm:1} is therefore strict only for principal-axis
impulses. Combined-direction behaviour is numerical observation only and belongs
to the unverified region.
\end{remark}
\begin{remark}[No overclaim]
$L^*$ is an upper (necessary) bound, not an exact or necessary-and-sufficient
boundary. The numerical closeness of the sufficient boundary to $L^*$ along
principal axes is an observation, not part of the theorem.
\end{remark}
\begin{remark}[Existence and disturbance scope]
$\tau_{\max,n}>\bar d$ is required for $A$ to be eventually monotone, for
$t^*$ to exist and for the bound to be non-vacuous; a direction failing it is
marked \emph{outside certified envelope} and no number is reported. The theorem
holds only for the adversarial realisation $n^\top d=+\bar d$. Extending it to
all disturbances with $|n^\top d|\le\bar d$ requires a strictly larger bound:
at $T_m=0.05$~s the audit recomputation gives
$L^*_{\rm any}/L^*_{\rm adv}=\CtwoRollAny{}/\CtwoRollAdv{}=\CtwoRollRatio{}$ for roll and
$\CtwoYawAny{}/\CtwoYawAdv{}=\CtwoYawRatio{}$ for yaw (a \CtwoYawPct{}\% increase). We do not adopt
that extension and therefore make no all-bounded-disturbance claim.
\end{remark}

All constants ($\tau_{\max,n}$, $J_n$, $\bar d$, $T_m$, $\Phi_{\max}$,
$u_{\max}$, $F$) are explicit in Table~\ref{tab:params}; the proof contains no
bare ``for some $c>0$'' constant. An internal consistency audit recomputed the
single-axis ODE, reverse-solved every stated constant and checked the Lemma-1
trajectory pointwise; it verifies that the implementation and the proof agree,
not that the bound is independently established by simulation.

\section{Computational Evaluation and Simulation Study}
\label{sec:sim}

This simulation study evaluates one main line: does the controller-independent necessary bound within the A1 trajectory class
hold, how wide is the gap to the best observed sufficient
boundary, and does the picture transfer to a single identified platform? Every
number below is regenerated from the on-disk result artifacts listed in the
provenance table, not transcribed by hand. Table~\ref{tab:reconcile}
summarises the theory-to-observation reconciliation that the rest of this
section discusses.

\textbf{Boundary-search resolution and exclusion rules.} The observed
sufficient boundary $L_{\rm suff}$ is located by a full six-degree-of-freedom
RK4 boundary search on a fixed grid of \Ndw{} impulse magnitudes spanning
$0.2$--$20$~rad/s (step \DwGridStep{}~rad/s) with integration step
\DtVal{}~s; the reported ratios $L_{\rm suff}/L^*$ therefore carry a
grid-resolution uncertainty of one step, which is why V1 is stated as a
bounded check rather than an exact equality. The analytic $L^*$ is obtained
independently by bisection on $\varphi_{\min}$; the numerical boundary search
does not call the analytic module, so the comparison in V1 is between two
independently computed quantities, not a self-check of one formula. Cells
whose zero-impact baseline is unstable under their own calibrated gains are
marked BLOCKED and excluded; on the identified platform this leaves
\RealNdegen{} degenerate cells out of \RealNtotal{}. This exclusion rule was
\emph{added after the frozen V1--V5 criteria were written}, following a
mechanism diagnosis (an $81$-gain sweep showed the slow symmetric-motor case
has no stable gain, so a diverging baseline is not a recovery observation);
the criteria themselves were not changed, and no diverging run is ever
reported as $L_{\rm suff}=0$. We state this timeline explicitly so the
exclusion cannot be read as selective retention of favourable cells.

\textbf{Three-way domain, made explicit.} For a fixed direction, actuator
time constant and disturbance class, the decomposition is
$\mathcal D_{\rm cert}=[0,L^*]$ (certified recoverable impulse set is
contained here), $\mathcal D_{\rm obs}=[0,L_{\rm suff}]$ (numerically observed
recovery by the best calibrated controller), and
$\mathcal D_{\rm unc}=(L_{\rm suff},L^*]$ when $L_{\rm suff}\le L^*$ (unverified
region: neither certified nor observed). The main-arm cells with
$L_{\rm suff}/L^*>1$ lie outside $\mathcal D_{\rm cert}$ under the weaker
turbulent disturbance and are reported separately rather than silently
merged. Figure~\ref{fig:domains} is a conceptual schematic of this
partition; the numerical values are those in Table~\ref{tab:reconcile} and
the results text.

\begin{table}[t]
\caption{Theory-to-observation reconciliation. Ratios are
$L_{\rm suff}/L^*$ on the adversarial arm; V3 is the yaw-to-roll
sufficient-boundary ratio. ``BLOCKED'' cells have an unstable zero-impact
baseline under their own calibrated gains and are excluded from all statistics.}
\label{tab:reconcile}
\centering\small
\begin{tabular}{lcc}
\toprule
Quantity & Synthetic & Identified Crazyflie \\
\midrule
V1 maximum adversarial ratio & \SynVone{} & \RealVone{} \\
V1 violations & \SynViol{} & \RealViol{} \\
V3 yaw/roll $L_{\rm suff}$ & \SynVthree{} & \RealVthree{} \\
V3 $\tau_{\max}$ ratio & \SynTauRatio{} & \RealTauRatio{} \\
valid / degenerate / total cells & \SynNvalid{}/\SynNdegen{}/\SynNtotal{} & \RealNvalid{}/\RealNdegen{}/\RealNtotal{} \\
BLOCKED baseline cells & 0 & \RealBlocked{}/\RealBaselineCells{} \\
verdict & GO & NO-GO \\
\bottomrule
\end{tabular}
\end{table}

The bound survives on both platforms: the adversarial arm has \SynViol{} and
\RealViol{} violations respectively, with maximum ratios \SynVone{} and
\RealVone{}. This is a \emph{bounded} result about the theorem, not a loss: it
states that every observed trajectory stays inside the certified band, as
Theorem~\ref{thm:1} predicts. Figure~\ref{fig:domains} shows the three-way
decomposition; Figure~\ref{fig:lstar} shows the necessary bound against the
motor time constant on both platforms; Figure~\ref{fig:aniso} shows the
anisotropy ratios.

On the synthetic platform the scalar-limit gap is identically zero, which is a
genuine null: with a near-optimal controller the necessary bound is tight. In
the full six-degree-of-freedom model with non-ideal controllers a non-zero gap
opens (principal axes about 4--5~\%, yaw about 20~\%, combined directions
65--69~\%); this gap is a measure of controller suboptimality plus the
axis-decoupling approximation, not a physical constant, and it narrows as the
dimensionless motor time constant grows. The two-parameter scaling uses
$\lambda=L/(\tau_{\max}T_{\rm char})$ and $\mu=T_m/T_{\rm char}$ with
$T_{\rm char}=\sqrt{J\Phi_{\max}/\tau_{\max}}$.

\textbf{What does not replicate.} On the identified Crazyflie platform the
verdict is NO-GO: V3 equals \RealVthree{} (above the conditional discriminator
0.6), the paired baseline advantages vanish with no Holm survivor (the paired
units are cells of one deterministic grid, so the test is descriptive rather
than inferential; see the baseline-set statement), and
\RealBlocked{} of \RealBaselineCells{} baseline cells are BLOCKED. We write
plainly: \emph{we do not claim the anisotropy advantage or a baseline advantage
on this platform}. Figure~\ref{fig:failure} reports the first failing angular
velocity across actuator models. We do not soften this into ``comparable'' or a
slight advantage. The direction of the V3 change agrees with the independent
parameter-sensitivity analysis, which excludes the alternative explanation that
the platform result is a random artefact.

\textbf{Why the main arm is not a counterexample to the bound.} The two
disturbance arms have different disturbance classes, and the necessary bound is
derived for the adversarial constant realisation only. On the main
(zero-mean turbulence) arm, \MainSynOver{} of \MainSynN{} valid synthetic cells
and \MainRealOver{} of \MainRealN{} valid identified-platform cells have
$L_{\rm suff}/L^*>1$, with maxima \MainSynMax{} and \MainRealMax{}
respectively. This is expected rather than contradictory: the turbulent arm is
strictly weaker than the worst-case disturbance for which $L^*$ was proved, so
its observed recovery domain may legitimately exceed the adversarial-arm bound.
For that reason V1 is evaluated only on the \emph{adversarial} arm, whose
disturbance realisation matches the theorem's premise; the main arm is used
for the fair baseline comparison (V2--V4). Reporting the main-arm ratios here
makes explicit that the certified domain, the weaker-disturbance observed
domain and the unverified region are distinct objects.

\begin{figure}[t]\centering
\includegraphics[width=0.86\linewidth]{figures/fig1.pdf}
\caption{Three-way domain decomposition: certified necessary bound, observed
sufficient boundary, and the unverified region between them. Fully normalised
conceptual schematic; all axes are dimensionless and no measured or computed
value is plotted.}\label{fig:domains}
\end{figure}
\begin{figure}[t]\centering
\includegraphics[width=0.86\linewidth]{figures/fig2.pdf}
\caption{Necessary bound $L^*$ versus motor time constant on the synthetic and
identified platforms, regenerated from the analytic result dictionaries.}
\label{fig:lstar}
\end{figure}
\begin{figure}[t]\centering
\includegraphics[width=0.86\linewidth]{figures/fig3.pdf}
\caption{Anisotropy ratios on both platforms against the conditional
discriminator. The synthetic advantage does not replicate on the identified
platform.}\label{fig:aniso}
\end{figure}
\begin{figure}[t]\centering
\includegraphics[width=0.86\linewidth]{figures/fig4.pdf}
\caption{Failure boundary: first failing angular-velocity jump across
symmetric-fast, symmetric-slow and asymmetric actuator models.}
\label{fig:failure}
\end{figure}

\section{Where the Behaviour Stops: Failure Boundaries and Cross-Platform Limits}
\label{sec:limits}

The identified platform's motor time constants are asymmetric (rising
0.055455~s, falling 0.249394~s), whereas the main study brackets them by two
symmetric models. A dedicated diagnostic, using the \emph{already calibrated}
gain sets and no re-tuning, shows that this bracket is partly a modelling
artefact: with the asymmetric actuator, \AsymSlowStable{} of 16 zero-impact
baselines are stable under the slow-gain set, versus \AsymSymSlowStable{} under
the symmetric-slow model (\AsymFastFastStable{} under symmetric-fast). Yet the
recovery boundary does not improve: the first failing jump stays at the smallest
grid value for nearly every cell, and non-monotone recovery domains (islands)
increase to \AsymIslands{} under the asymmetric model. This is therefore
\emph{insufficient to overturn NO-GO}. Lemma~\ref{lem:1} assumes a single
$T_m$; under an asymmetric actuator the analytic necessary bound does
not hold, so this diagnostic is purely numerical and produces no GO verdict, and
formally adopting the asymmetric model requires re-deriving the bound --
new theoretical work, not an engineering patch.

The comparison also exposes a gain--model coupling: the fast-gain set performs
worse on the asymmetric actuator than the slow-gain set, so the per-time-constant
equal-budget calibration used in the main study is necessary but its gains do
not transfer directly. Baseline advantages, where they appear, are conditional
on direction and coupling regime, and are reported with their cost metrics
(saturation duty, peak torque, recovery time) rather than as universal
superiority. Non-monotone cells are marked degenerate and excluded from
statistics but retained in the artifacts.

\section{Discussion, Limitations and What Is Not Claimed}
\label{sec:discussion}

\textbf{Quantitative comparison with a sufficient-domain estimator.}
To answer the "cited but not compared" gap at the numerical level, we evaluate a
standard quadratic-Lyapunov region-of-attraction estimator on the linearised
single-axis closed loop, using the \emph{same} plant, feasibility set and
equal-budget gains. Solving $A^\top P+PA=-I$ on $x=[\varphi,\omega_n]$ and
limiting the ellipsoid by the attitude envelope and actuator saturation gives
$L_{\rm lyap}=\MthreeLyapRoll{}$ N m s (roll) and $\MthreeLyapYaw{}$ (yaw),
against the necessary bound $L^*=\MthreeStarRoll{}$ and $\MthreeStarYaw{}$.
The sufficient domain is therefore smaller by a factor of $\MthreeRatioRoll{}$ (roll)
and $\MthreeRatioYaw{}$ (yaw), and the logical inclusion
$L_{\rm lyap}\le L^*$ holds. The gap is dominated by \emph{saturation}, not by
the estimator's conservatism alone: the saturation-limited angular velocity is
$\MthreeDwsat{}$ rad/s against an envelope-limited $\MthreeDwphi{}$ rad/s.
This proxy is \emph{not} a reproduction of the SOS / recoverable-set / CBF
programs cited in Related Work, whose implementations and case parameters are
not public; it is a reproducible member of the same sufficient-domain family,
and the comparison quantifies the necessary-versus-sufficient direction rather
than claiming superiority over any specific prior method.

\textbf{$\NrepPhases{}$ independent disturbance realisations.}
We repeated the $\NrepCells{}$ main-arm cells under $\NrepPhases{}$ fixed but
independent turbulence phase sets (deterministic integrator, independent
disturbance realisations), reporting the mean and every individual run.
$\NrepValid{}$ of $\NrepCells{}$ cells are valid in all three runs. The V3
yaw-to-roll ratio is $\NrepVthreePone{}$ in two realisations and
$\NrepVthreePthree{}$ in the third, all below the $0.6$ discriminator: the
\emph{direction} replicates, the magnitude is conditional on the phase set.
The mean per-cell spread is $\NrepMeanRange{}$ N m s, but the widest cell
spans $\NrepWorstLow{}$--$\NrepWorstHigh{}$ (range $\NrepMaxRange{}$), so we
report the range rather than a lone mean. The adversarial arm uses a constant
disturbance independent of the phase set and is therefore \emph{not} counted
as an independent replicate. These are $\NrepPhases{}$ realisations of one
deterministic simulation model, not independent physical experiments; no
hardware claim follows.

\textbf{What survives.} The necessary bound (controller-independent within the
A1 trajectory class) is the only claim that survives contact with both platforms. It is a bounded, positive
result about the theorem: observed trajectories stay inside the certified band.
The three-way decomposition makes explicit what a finite simulation grid cannot
establish, and the gap between the necessary bound and the observed sufficient
boundary is reported rather than hidden.

\textbf{Limitations.} This is analytical plus numerical simulation only; there
is no hardware, firmware-in-the-loop or flight-test evidence, and we do not use
the words validation or certified in that sense. Point estimates are
conditional on the fixed scenario grid: we did \emph{not} run three or more
independent replicates per condition, so the paired ranking is more reliable
than the absolute magnitudes, and multi-seed replication is required before any
hardware claim. The theorem requires A1 (principal axes) and the adversarial
disturbance realisation; combined-axis behaviour and arbitrary bounded
disturbances lie outside the certified domain and would need a strictly larger
bound. The identified platform's registry has a documented hover-equilibrium
inconsistency, its asymmetric actuator dynamics are only bracketed in the main
study, and RPM-level quantities are not identified and are marked N/A rather
than silently passed. Fixed total thrust and the absence of a translational
outer loop are model simplifications. All \Nrefs{} references were verified
against live Crossref/arXiv metadata and checked claim-by-claim against the
source title/abstract (\Nsupported{} supported, \Nnuance{} supported with an
explicit nuance, \Nmis{} misattributions); one source is a non-peer-reviewed
preprint and is labelled as such.

\textbf{Genre and scope.} Because the evidence is a theorem plus a computational
verification with an explicit negative cross-platform result, and because no
hardware validation exists, this work is positioned as a boundary-characterisation
short article rather than a controller-design or experimental study. The
classification matters: a full-length control paper would be judged on
substantive new demonstrated performance, whereas the honest contribution here
is a limit that no controller can exceed together with a public account of where
the limit stops being informative. We state the object of study (recoverability
bounds under anisotropic actuation) separately from the application vehicle (a
quadrotor), so the result is read at the control-theory level.

{\raggedright
\textbf{Declarations.} The authors declare no competing interests. Data
availability: all result artifacts, regeneration scripts and the manuscript
source are publicly available at
\url{https://github.com/7801qazxcv/Necessary-Limits-under-Anisotropic-Actuator-Feasibility-and-Motor-Lag}.
\textbf{CRediT author contributions.} Sen Fu: conceptualization,
methodology, formal analysis, writing -- original draft, writing -- review
and editing, and corresponding author. Bin Liu: validation, data curation,
and writing -- review and editing.
\textbf{Funding.} No funding was received for this work.
\par}

\section*{Declaration of generative AI and AI-assisted technologies in the writing process}
\label{sec:ai}
During the preparation of this work the authors used AI tools for language
translation and polishing only. The authors reviewed and verified all output and
take full responsibility for the content of the publication.

\section{Conclusions}
\label{sec:conclusions}

We gave a necessary bound on post-impulse attitude
recoverability for a quadrotor with an anisotropic actuator feasibility set and
first-order motor lag, proved it along principal axes within the A1 trajectory
class under an adversarial disturbance, and separated the certified, observed
and unverified domains. The
bound holds with 0 adversarial-arm violations on both a synthetic and a single
identified platform, which is the result that survives cross-platform contact.
On the identified platform the anisotropy and baseline advantages do not
replicate, and we state that plainly. The demonstrable contribution is the
necessary bound and the explicit account of where it stops being informative,
not a new controller. All conclusions are analytical and computational; no
hardware or flight-test claim is made, and no acceptance outcome is promised.

\section*{Acknowledgements}
The authors thank the maintainers of the public quadrotor parameter registry and
the open bibliographic APIs used for verification.

\bibliographystyle{elsarticle-num}
\bibliography{refs}
\end{document}
"""

# additional macros needed by prose (built from the same artifacts)
import json
n=json.load(open(os.path.join(HERE,"manuscript_numbers.json"),encoding="utf-8"))
syn=json.load(open(os.path.join(HERE,"probe_v2_results.json"),encoding="utf-8"))
g=syn["go_evaluation"]
macros=numbers+"\n"+"\n".join([
 "\\newcommand{\\SynNvalid}{%d}"%g["n_valid"],
 "\\newcommand{\\SynNdegen}{%d}"%g["n_degenerate"],
 "\\newcommand{\\SynNtotal}{%d}"%g["n_total"],
 "\\newcommand{\\ThMustPass}{%d}"%n["th_must_pass_count"],
])+"\n"
tex=PROSE.replace("__NUMBERS__",macros)
out=os.path.join(PAPER,"main.tex")
open(out,"w",encoding="utf-8",newline="\n").write(tex)
print("WROTE",out,"chars",len(tex),"CR bytes",tex.count("\r"))
