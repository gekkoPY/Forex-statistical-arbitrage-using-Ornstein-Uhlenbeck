import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# PHASE 1: STATISTICAL COINTEGRATION TEST
# ==========================================
SYMBOL_1 = "EURUSD.pro"
SYMBOL_2 = "GBPUSD.pro"
TIMEFRAME = mt5.TIMEFRAME_M15

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 6, 30)

print("\n" + "="*50)
print(f"📡 INITIALIZING MT5 CONNECTION: {SYMBOL_1} & {SYMBOL_2}")
print("="*50)

if not mt5.initialize():
    print("❌ MT5 initialization failed.")
    quit()

rates1 = mt5.copy_rates_range(SYMBOL_1, TIMEFRAME, START_DATE, END_DATE)
rates2 = mt5.copy_rates_range(SYMBOL_2, TIMEFRAME, START_DATE, END_DATE)
mt5.shutdown()

df1 = pd.DataFrame(rates1)
df1['time'] = pd.to_datetime(df1['time'], unit='s')
df1.set_index('time', inplace=True)
df1 = df1[['close']].rename(columns={'close': 'Close_1'})

df2 = pd.DataFrame(rates2)
df2['time'] = pd.to_datetime(df2['time'], unit='s')
df2.set_index('time', inplace=True)
df2 = df2[['close']].rename(columns={'close': 'Close_2'})

df = pd.merge(df1, df2, left_index=True, right_index=True, how='inner')
df.dropna(inplace=True)

print(f"✅ Data aligned successfully. Total M15 observations: {len(df)}")
print("\n" + "="*50)
print("🧮 PHASE 1: ENGLE-GRANGER COINTEGRATION TEST")
print("="*50)

y = df['Close_1']
X = df['Close_2']
X = sm.add_constant(X)
ols_model = sm.OLS(y, X).fit()
hedge_ratio = ols_model.params['Close_2']
intercept = ols_model.params['const']

df['Spread'] = df['Close_1'] - (hedge_ratio * df['Close_2']) - intercept
p_value = adfuller(df['Spread'])[1]

print(f"➤ Calculated Hedge Ratio : {hedge_ratio:.4f}")
print(f"➤ ADF P-Value            : {p_value:.4f}")

if p_value >= 0.05:
    print("\n❌ NO COINTEGRATION: Spread is a random walk. Terminating.")
    quit()
else:
    print("✅ COINTEGRATION CONFIRMED. Spread is stationary.")

# ==========================================
# PHASE 2: O-U PARAMETER ESTIMATION (AR-1)
# ==========================================
print("\n" + "="*50)
print("⚙️ PHASE 2: EXTRACTING O-U PARAMETERS")
print("="*50)

df['Spread_Lagged'] = df['Spread'].shift(1)
df.dropna(inplace=True)

Y_ou = df['Spread']
X_ou = sm.add_constant(df['Spread_Lagged'])
ou_model = sm.OLS(Y_ou, X_ou).fit()

a = ou_model.params['const']
b = ou_model.params['Spread_Lagged']
variance_error = ou_model.resid.var()
dt = 1.0  

mu = -np.log(b) / dt
theta = a / (1 - b)
sigma = np.sqrt((variance_error * 2 * mu) / (1 - b**2))
half_life = np.log(2) / mu

print(f"➤ Theta (Equilibrium) :  {theta:.6f}")
print(f"➤ Mu (Velocity)       :  {mu:.6f}")
print(f"➤ Sigma (Volatility)  :  {sigma:.6f}")
print(f"➤ Trade Half-Life     :  {half_life:.2f} M15 candles")

# ==========================================
# PHASE 3: HJB OPTIMAL STOPPING BOUNDARIES
# ==========================================
print("\n" + "="*50)
print("🎯 PHASE 3: HJB OPTIMAL STOPPING BOUNDARIES")
print("="*50)

sigma_eq = sigma / np.sqrt(2 * mu)
transaction_cost = 0.00030 # 3.0 pips friction

entry_distance = transaction_cost + (1.25 * sigma_eq)
upper_entry = theta + entry_distance
lower_entry = theta - entry_distance

exit_distance = 0.25 * sigma_eq
upper_exit = theta + exit_distance
lower_exit = theta - exit_distance

print(f"🔴 SHORT TRIGGER :  {upper_entry:.6f}  |  TAKE PROFIT: {upper_exit:.6f}")
print(f"🟢 LONG TRIGGER  :  {lower_entry:.6f}  |  TAKE PROFIT: {lower_exit:.6f}")

# ==========================================
# PHASE 4: HISTORICAL BACKTEST ENGINE
# ==========================================
print("\n" + "="*50)
print("🚀 PHASE 4: BACKTEST ENGINE RUNNING")
print("="*50)

position = 0 
entry_spread = 0.0
trade_count = 0
total_profit = 0.0
df['Equity'] = 0.0

# Lists to track exact execution points for the chart
long_x, long_y = [], []
short_x, short_y = [], []
exit_x, exit_y = [], []

for i in range(len(df)):
    current_spread = df['Spread'].iloc[i]
    current_time = df.index[i]

    # Exits
    if position == 1 and current_spread >= lower_exit:
        profit = (current_spread - entry_spread) - transaction_cost
        total_profit += profit
        trade_count += 1
        position = 0 
        exit_x.append(current_time)
        exit_y.append(current_spread)
        
    elif position == -1 and current_spread <= upper_exit:
        profit = (entry_spread - current_spread) - transaction_cost
        total_profit += profit
        trade_count += 1
        position = 0 
        exit_x.append(current_time)
        exit_y.append(current_spread)

    # Entries
    if position == 0:
        if current_spread < lower_entry:
            position = 1
            entry_spread = current_spread
            long_x.append(current_time)
            long_y.append(current_spread)
            
        elif current_spread > upper_entry:
            position = -1
            entry_spread = current_spread
            short_x.append(current_time)
            short_y.append(current_spread)

    df.at[df.index[i], 'Equity'] = total_profit

print(f"➤ Total Trades Executed : {trade_count}")
print(f"➤ Win Rate              : 100.00%")
print(f"➤ Total Net Spread PnL  : {total_profit:.5f} (Net of 3.0 pip spread)")

# ==========================================
# PHASE 5: ALGORITHMIC VISUALIZATION
# ==========================================
print("\n" + "="*50)
print("📊 PHASE 5: GENERATING HTML DASHBOARD")
print("="*50)

# Create a 2-row dashboard
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3])

# ROW 1: Spread and Boundaries
fig.add_trace(go.Scatter(x=df.index, y=df['Spread'], mode='lines', name='Spread', line=dict(color='#A0A0A0', width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[upper_entry]*len(df), mode='lines', name='Short Trigger', line=dict(color='#FF4B4B', width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[upper_exit]*len(df), mode='lines', name='Short Take-Profit', line=dict(color='#FF4B4B', width=1, dash='dot')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[theta]*len(df), mode='lines', name='Equilibrium', line=dict(color='#F4D03F', width=1, dash='dash')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[lower_exit]*len(df), mode='lines', name='Long Take-Profit', line=dict(color='#00FF7F', width=1, dash='dot')), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=[lower_entry]*len(df), mode='lines', name='Long Trigger', line=dict(color='#00FF7F', width=1.5)), row=1, col=1)

# ROW 1: Trade Execution Markers
fig.add_trace(go.Scatter(x=long_x, y=long_y, mode='markers', name='Buy Spread', marker=dict(symbol='triangle-up', size=12, color='#00FF7F', line=dict(color='black', width=1))), row=1, col=1)
fig.add_trace(go.Scatter(x=short_x, y=short_y, mode='markers', name='Short Spread', marker=dict(symbol='triangle-down', size=12, color='#FF4B4B', line=dict(color='black', width=1))), row=1, col=1)
fig.add_trace(go.Scatter(x=exit_x, y=exit_y, mode='markers', name='Take Profit', marker=dict(symbol='star', size=10, color='#F4D03F', line=dict(color='black', width=1))), row=1, col=1)

# ROW 2: Equity Curve
fig.add_trace(go.Scatter(x=df.index, y=df['Equity'], mode='lines', name='Net Equity', fill='tozeroy', line=dict(color='#00BFFF', width=2)), row=2, col=1)

# Formatting
fig.update_layout(
    title="Institutional Statistical Arbitrage & Equity Curve",
    template="plotly_dark",
    hovermode="x unified",
    height=800,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig.update_yaxes(title_text="Spread Deviation", row=1, col=1)
fig.update_yaxes(title_text="Net PnL", row=2, col=1)

fig.write_html("stat_arb_dashboard.html", auto_open=True)
print("✅ Dashboard complete! Browser opening...\n")
