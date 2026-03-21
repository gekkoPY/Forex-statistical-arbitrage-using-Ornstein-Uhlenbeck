# 📚 Academic Foundations & Theoretical Lineage

The vast majority of retail algorithmic trading fails because it attempts to force static, lagging technical indicators onto dynamic, non-stationary markets. To build a robust, institutional-grade engine, the underlying logic must be anchored in peer-reviewed quantitative research and rigorous statistical mechanics. 

This repository discards traditional charting concepts in favor of advanced stochastic calculus. The core execution mechanics—specifically the spread modeling, the spread-friction immunization, and the optimal exit boundaries—were directly adapted from two foundational academic papers on capacity-constrained alpha.

---

### 1. Modeling the Spread & Immunizing Transaction Costs

**Primary Source:** [*Optimal Mean Reversion Trading with Transaction Costs and Stop-Loss Exit* (Leung & Li, 2015)](https://arxiv.org/abs/1411.5062)


**The Engineering Problem:**
Standard pairs trading models rely on simple distance-based metrics, such as Z-scores or Bollinger Bands. However, these models frequently collapse in retail environments because crossing the bid-ask spread on two separate assets completely erodes the profit margin. Theoretical models often ignore this friction.

**The Academic Application:**

**Primary Source:** [*On the Efficacy of Optimized Exit Rule for Mean Reversion Trading* (Lee & Leung, 2020)](https://ideas.repec.org/a/wsi/ijfexx/v07y2020i03ns2424786320500243.html)

To solve this, the engine completely abandons arbitrary indicators. Instead, it formalizes the cointegrated relationship between the two assets using the Ornstein-Uhlenbeck (OU) stochastic process. The spread is modeled via the stochastic differential equation: 
[cite_start]$dX_{t}=\mu(\theta-X_{t})dt+\sigma dW_{t}$[cite: 26].

By treating the trade lifecycle as an optimal double stopping problem, the algorithm dynamically extracts the equilibrium mean ($\theta$), the reversion velocity ($\mu$), and the instantaneous volatility ($\sigma$)  Crucially, the Leung and Li (2015) framework ensures viability by explicitly incorporating fixed transaction costs directly into the Hamilton-Jacobi-Bellman (HJB) variational inequalities[cite: 40]. [cite_start]The algorithm mathematically guarantees that a trade is only executed when the expected reversion strictly exceeds the broker's spread.

---

### 2. Solving Capital Lock-Up via Optimal Stopping
[cite_start]**Primary Source:** *On the Efficacy of Optimized Exit Rule for Mean Reversion Trading* (Lee & Leung, 2020)[cite: 17, 281].

**The Engineering Problem:**
Even if a spread is perfectly cointegrated, its mathematical "half-life" (the time it takes to revert to the mean) can span several days or weeks. [cite_start]Retail traders passively wait for the spread to hit the exact equilibrium ($\theta$), which locks up margin, incurs massive overnight swap fees, and exposes the portfolio to sudden macroeconomic shocks[cite: 63, 256].

**The Academic Application:**
This codebase utilizes the findings of Lee and Leung (2020) to entirely bypass the half-life trap. Their research demonstrates that dynamically optimizing the exit rule—rather than passively waiting for a complete reversion to the mean—drastically improves the annualized return profile.

The algorithm's Python execution engine is programmed to calculate a dynamically bounded take-profit interval. By doing so, it mathematically targets the highest-velocity phase of the snap-back, exiting the position early to maximize yield and immediately free up margin for the next execution. 

---

### 🔬 Conclusion
By bridging the gap between theoretical stochastic calculus and actual MetaTrader 5 execution, this engine demonstrates that market-neutral statistical arbitrage is viable in a retail infrastructure. The reliance on mathematically defined "no-trade regions" and optimal stopping boundaries ensures the algorithm only assumes risk when the statistical probability of a net-positive reversion is absolute.
