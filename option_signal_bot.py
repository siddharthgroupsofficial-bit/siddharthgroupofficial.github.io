# option_signal_bot.py
import requests
import datetime
import time
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice

# -------------------------------
# === PERSONAL DATA CONFIGURATION ===
# -------------------------------
TELEGRAM_BOT_TOKEN = '8359676634:AAGsdQQ-HklB6tUnKJKFgMUWwzD21Lf6elM'
TELEGRAM_CHAT_ID = '1369709866'

LOT_SIZE = {'BANKNIFTY': 25, 'NIFTY': 50, 'FINNIFTY': 40}
USER_CAPITAL = {'BANKNIFTY': 15000, 'NIFTY': 20000, 'FINNIFTY': 12000}

MARKET_OPEN = datetime.time(9, 15)
MARKET_CLOSE = datetime.time(15, 30)
TIMEFRAME = 3  # minutes

# -------------------------------
# Telegram Alert Function
# -------------------------------
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=data)

# -------------------------------
# Market Timing Check
# -------------------------------
def is_market_open():
    now = datetime.datetime.now().time()
    return MARKET_OPEN <= now <= MARKET_CLOSE

# -------------------------------
# Indicators Calculation
# -------------------------------
def calculate_indicators(df):
    df['EMA20'] = EMAIndicator(df['Close'], 20).ema_indicator()
    df['EMA50'] = EMAIndicator(df['Close'], 50).ema_indicator()
    df['EMA200'] = EMAIndicator(df['Close'], 200).ema_indicator()
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_SIGNAL'] = macd.macd_signal()
    df['RSI'] = RSIIndicator(df['Close'], 14).rsi()
    df['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close'], 14).adx()
    df['VWAP'] = VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume'], 14).vwap()
    return df

# -------------------------------
# Fetch Live Option Chain (Pseudo-API)
# -------------------------------
def get_best_buy_option(symbol):
    # Replace this with actual broker API integration (SmartAPI, Kite, Upstox)
    strikes = np.arange(59000, 60000, 100)
    premiums = np.random.randint(400, 450, len(strikes))
    # Pick strike with highest pseudo OI / delta
    buy_strike = strikes[-1]
    buy_premium = premiums[-1]
    return buy_strike, buy_premium

# -------------------------------
# Generate Buy Signal & Telegram Alert
# -------------------------------
def generate_signal(symbol, df, buy_strike, buy_premium):
    last_row = df.iloc[-1]
    if (last_row['EMA20'] > last_row['EMA50'] > last_row['EMA200'] and
        last_row['MACD'] > last_row['MACD_SIGNAL'] and
        40 < last_row['RSI'] < 70 and
        last_row['ADX'] > 25):
        
        # Momentum-based suggested exit
        sell_strike = buy_strike + 200 if symbol.upper() == 'BANKNIFTY' else buy_strike + 100
        stoploss = int(buy_premium * 0.85)
        sell_premium_min = int(buy_premium * 1.08)
        sell_premium_max = int(buy_premium * 1.15)
        expected_profit_min = (sell_premium_min - buy_premium) * LOT_SIZE.get(symbol.upper(),1)
        expected_profit_max = (sell_premium_max - buy_premium) * LOT_SIZE.get(symbol.upper(),1)

        message = f"""
🔥 STRONG BUY SIGNAL (Auto-Calculated + Manual Buy Only)

Index: {symbol}  
Timeframe: {TIMEFRAME} Minutes  

🟢 BUY DETAILS
Buy Strike: {buy_strike} CE
Buy Premium: ₹{buy_premium}
Lot Size: {LOT_SIZE.get(symbol.upper(),1)}

📌 MOMENTUM-BASED EXIT
Suggested Exit Strike: {sell_strike} CE
Target Premium Range: ₹{sell_premium_min} – ₹{sell_premium_max}
Stop Loss: ₹{stoploss}

💰 EXPECTED PROFIT
Min: ₹{expected_profit_min} | Max: ₹{expected_profit_max}

📌 BOT NOTES
- Only BUY options
- Quick-entry recommended
"""
        send_telegram_message(message)

# -------------------------------
# Main Loop
# -------------------------------
def main():
    send_telegram_message("🔵 Bot Started – Market Opened")
    symbols = ['BANKNIFTY', 'NIFTY', 'FINNIFTY']  # Add more listed companies as needed
    while is_market_open():
        for symbol in symbols:
            # Replace below with real API data
            df = pd.DataFrame({
                'Close': np.random.randint(59000,60000,100),
                'High': np.random.randint(59050,60050,100),
                'Low': np.random.randint(58950,59950,100),
                'Volume': np.random.randint(100,1000,100)
            })
            df = calculate_indicators(df)
            buy_strike, buy_premium = get_best_buy_option(symbol)
            generate_signal(symbol, df, buy_strike, buy_premium)
        time.sleep(TIMEFRAME*60)
    send_telegram_message("🔴 Market Closed – Bot Paused")

if __name__ == "__main__":
    main()