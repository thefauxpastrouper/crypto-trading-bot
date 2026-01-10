# BINANCEBOT - Binance Futures Trading Bot

A Terminal User Interface (TUI) for trading Binance futures.

## Setup Virtual Environment

### Ubuntu
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Run directly:
```bash
python tui_bot.py
```

## Configuration

Set your Binance API credentials in `.env` file:
```
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

## Features

### 1. LIMIT Order
Places a limit order that executes only at your specified price.

**Required Inputs:**
- Symbol (e.g., BTCUSDT) - The trading pair you want to trade
- Side (BUY/SELL) - Direction of your trade; BUY for long positions, SELL for short positions
- Quantity - Number of contracts or amount to trade
- Price - The specific price at which your limit order will execute

### 2. MARKET Order
Places a market order that executes immediately at the best available price.

**Required Inputs:**
- Symbol (e.g., BTCUSDT) - The trading pair you want to trade
- Side (BUY/SELL) - Direction of your trade; BUY for long positions, SELL for short positions
- Quantity - Number of contracts or amount to trade

### 3. STOP_LIMIT Order
Places a stop-limit order that triggers when the stop price is reached, then executes as a limit order.

**Required Inputs:**
- Symbol (e.g., BTCUSDT) - The trading pair you want to trade
- Side (BUY/SELL) - Direction of your trade; BUY for long positions, SELL for short positions
- Quantity - Number of contracts or amount to trade
- Price (limit price) - The execution price for your order once triggered
- Stop Price (trigger price) - The price level that triggers your order to become active
- Trigger Source (LAST_PRICE or MARK_PRICE) - Which price to watch for triggering; LAST_PRICE uses the last traded price, MARK_PRICE uses the mark price