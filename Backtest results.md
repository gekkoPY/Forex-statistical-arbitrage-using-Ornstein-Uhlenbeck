This is what the terminal's output should look like:

📡 INITIALIZING MT5 CONNECTION: EURUSD.pro & GBPUSD.pro
==================================================
✅ Data aligned successfully. Total M15 observations: 12371

==================================================
🧮 PHASE 1: ENGLE-GRANGER COINTEGRATION TEST
==================================================
➤ Calculated Hedge Ratio : 0.6452
➤ ADF P-Value            : 0.0294
✅ COINTEGRATION CONFIRMED. Spread is stationary.

==================================================
⚙️ PHASE 2: EXTRACTING O-U PARAMETERS
==================================================
➤ Theta (Equilibrium) :  -0.001840
➤ Mu (Velocity)       :  0.001218
➤ Sigma (Volatility)  :  0.000234
➤ Trade Half-Life     :  568.89 M15 candles

==================================================
🎯 PHASE 3: HJB OPTIMAL STOPPING BOUNDARIES
==================================================
🔴 SHORT TRIGGER :  0.004394  |  TAKE PROFIT: -0.000653
🟢 LONG TRIGGER  :  -0.008073  |  TAKE PROFIT: -0.003027

==================================================
🚀 PHASE 4: BACKTEST ENGINE RUNNING
==================================================
➤ Total Trades Executed : 5
➤ Win Rate              : 100.00%
➤ Total Net Spread PnL  : 0.03984 (Net of 3.0 pip spread)

==================================================       
📊 PHASE 5: GENERATING HTML DASHBOARD
==================================================       
✅ Dashboard complete! Browser opening...
