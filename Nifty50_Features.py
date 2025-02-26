import pandas as pd
import numpy as np

# Assume daily is already created with proper date as datetime and columns: open, high, low, close, volume
# For example, after resampling and dropping missing days
daily = pd.read_csv('Nifty50_Daily.csv')

# 1. Candlestick pattern description and 2. Candle color:
# Define a simple logic:
#   - Bullish if close > open, Bearish if close < open, and Doji if they are nearly equal (difference less than 0.1% of open)
import pandas as pd
import numpy as np

# Example daily DataFrame with required columns: date, open, high, low, close, volume
# Assume 'daily' is already created and sorted by date

def classify_candle(row):
    o = row['open']
    h = row['high']
    l = row['low']
    c = row['close']
    
    body = abs(c - o)
    upper_shadow = h - max(o, c)
    lower_shadow = min(o, c) - l

    # Default simple classification (Bullish, Bearish, Doji)
    if body == 0 or (body/o < 0.001):
        base = "Doji"
        color = "Gray"
    elif c > o:
        base = "Bullish"
        color = "Green"
    else:
        base = "Bearish"
        color = "Red"
        
    # Check for marubozu: little or no shadows (threshold 5% of body)
    if body > 0:
        if upper_shadow/body < 0.05 and lower_shadow/body < 0.05:
            if c > o:
                return "Bullish Marubozu", "Green"
            else:
                return "Bearish Marubozu", "Red"
    
    # Hammer & Hanging Man: small body with long lower shadow
    # Common criteria: lower shadow at least 2 times body, and small upper shadow.
    if body > 0:
        if lower_shadow >= 2 * body and upper_shadow < 0.5 * body:
            # Hammer usually occurs in uptrend and Hanging Man in downtrend.
            # Here we simply label them; you might incorporate trend context if available.
            if base == "Bullish":
                return "Hammer", "Green"
            else:
                return "Hanging Man", "Red"
    
    # Inverted Hammer & Shooting Star: small body with long upper shadow
    # Criteria: upper shadow at least 2 times body and lower shadow is small.
    if body > 0:
        if upper_shadow >= 2 * body and lower_shadow < 0.5 * body:
            # Inverted Hammer in an uptrend vs. Shooting Star in a downtrend.
            if base == "Bullish":
                return "Inverted Hammer", "Green"
            else:
                return "Shooting Star", "Red"
    
    # If none of the special patterns are detected, return base classification
    return base, color

# Apply the function to each row in daily DataFrame
daily[['pattern', 'candle_color']] = daily.apply(lambda r: pd.Series(classify_candle(r)), axis=1)

# For demonstration, print the resulting DataFrame
print(daily[['date', 'open', 'high', 'low', 'close', 'pattern', 'candle_color']].head(10))

# 3. Absolute move in a day (high - low)
daily['abs_move'] = daily['high'] - daily['low']

# 4. Percentage move in a day (abs_move / open * 100)
daily['pct_move_day'] = daily['abs_move'] / daily['open'] * 100

# 5. Percentage move in 3 days: percent change from the close 3 days ago to today
daily['pct_move_3d'] = daily['close'].pct_change(periods=3) * 100

# 6. Percentage move in 5 days: percent change from the close 5 days ago to today
daily['pct_move_5d'] = daily['close'].pct_change(periods=5) * 100

# 7. Flag - closing in a range for previous 2 days: 
# For the previous 2 days, if both daily high and low differences (as percentage of previous day's close) are within 0.2%, flag = 1, else 0.
def close_in_range(idx, df, threshold=0.2):
    # idx: current row index
    # Check previous 2 days exist:
    if idx < 2:
        return 0
    prev_days = df.iloc[idx-2:idx]
    # For each day, compute (high - low) / close * 100 and check if it is <= threshold
    if all(((day['high'] - day['low']) / day['close'] * 100) <= threshold for _, day in prev_days.iterrows()):
        return 1
    else:
        return 0

daily = daily.sort_values('date').reset_index(drop=True)
daily['flag_close_range'] = [close_in_range(i, daily) for i in range(len(daily))]

# 8. Flag - above 200 EMA, 9. above 50 EMA, 10. above 100 EMA
daily['EMA_200'] = daily['close'].ewm(span=200, adjust=False).mean()
daily['EMA_50']  = daily['close'].ewm(span=50, adjust=False).mean()
daily['EMA_100'] = daily['close'].ewm(span=100, adjust=False).mean()

daily['flag_above_200EMA'] = (daily['close'] > daily['EMA_200']).astype(int)
daily['flag_above_50EMA']  = (daily['close'] > daily['EMA_50']).astype(int)
daily['flag_above_100EMA'] = (daily['close'] > daily['EMA_100']).astype(int)

# 11. Category - Type of opening:
# Compare today's open with previous day's close; if open is > previous close by > 0.44% => Gap Up; if < previous close by > 0.44% => Gap Down; else Flat.
daily['prev_close'] = daily['close'].shift(1)
def opening_category(row):
    if pd.isna(row['prev_close']):
        return "N/A"
    gap_pct = (row['open'] - row['prev_close']) / row['prev_close'] * 100
    if gap_pct > 0.44:
        return "Gap Up"
    elif gap_pct > 0.65:
        return "LGap up"
    elif gap_pct < -0.65:
        return "LGap Down"
    elif gap_pct < -0.44:
        return "Gap Down"
    else:
        return "Flat"

daily['opening_category'] = daily.apply(opening_category, axis=1)

# 12. Points away from 3 month high/low and 13. Percentage away from 3 month high/low
# Assuming 3 months ~ 63 trading days. Compute rolling high and low.
window = 63
daily['3m_high'] = daily['high'].rolling(window=window, min_periods=1).max()
daily['3m_low']  = daily['low'].rolling(window=window, min_periods=1).min()

# Points away:
daily['pts_from_3m_high'] = daily['3m_high'] - daily['close']
daily['pts_from_3m_low']  = daily['close'] - daily['3m_low']

# Percentage away:
daily['pct_from_3m_high'] = daily['pts_from_3m_high'] / daily['3m_high'] * 100
daily['pct_from_3m_low']  = daily['pts_from_3m_low'] / daily['3m_low'] * 100

# Optionally, if you want one column summarizing "points away" and "pct away", you can merge these results.

# Clean up: Drop the helper column for previous close if not needed
# daily.drop(columns=['prev_close'], inplace=True)

# Create a new column for the cumulative maximum of the close price
daily['cummax_close'] = daily['close'].cummax()

# Flag as 1 if today's close is equal to the cumulative maximum, else 0
daily['flag_all_time_high'] = (daily['close'] == daily['cummax_close']).astype(int)
# Shift the cumulative maximum and close columns by one day
daily['prev_cummax_close'] = daily['cummax_close'].shift(1)

# Create the flag: 1 if previous day's close equals the previous cumulative max, else 0
daily['flag_prev_at_all_time_high'] = (daily['prev_close'] == daily['prev_cummax_close']).astype(int)
daily.drop(columns=['cummax_close', 'prev_cummax_close'], inplace=True)

# Print final DataFrame with new columns
print(daily.head(10))

daily.to_csv('Nifty_Features.csv')

