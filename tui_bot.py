import os
import sys
import uuid
from typing import Optional, Any
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Static, Label, Select, Log
from textual.binding import Binding
from textual.reactive import reactive
from textual import work

# Assuming these are in your local directory
from bot import BasicBot, api_key, api_secret 

load_dotenv()

# UI Design with Neobrutalist accents
CSS = """
$bg-primary: #050505;
$bg-secondary: #171717;
$border-subtle: #333333;
$text-main: #d1d5db;
$accent-green: #10a37f;

Screen {
    background: $bg-primary;
    color: $text-main;
}

#header-area {
    height: 3;
    content-align: center middle;
    text-style: bold;
    color: $accent-green;
    border-bottom: solid $border-subtle;
    background: $bg-primary;
}

#sidebar {
    width: 40;
    background: $bg-primary;
    border-right: solid $border-subtle;
    padding: 1 2;
}

#main-viewport {
    background: $bg-secondary;
    padding: 1;
}

Label {
    margin-top: 1;
    color: #8e8e93;
    text-style: bold;
}

Input, Select {
    background: #212121;
    color: white;
    border: solid $border-subtle;
    margin-bottom: 1;
}

Input:focus {
    border: solid $accent-green;
}

Button {
    width: 100%;
    margin-top: 1;
    border: none;
    background: $bg-secondary;
    color: white;
    height: 3;
}

#execute-btn {
    background: $accent-green;
    color: white;
    text-style: bold;
    margin-top: 2;
}

#order-preview {
    height: auto;
    min-height: 10;
    background: #000000;
    border: solid $accent-green;
    padding: 1 2;
    margin-bottom: 1;
    color: $text-main;
}

Log {
    background: #000000;
    color: #e0e0e0;
    border: solid $border-subtle;
    height: 1fr;
}

.status-bar {
    height: 1;
    color: #666;
    padding-left: 1;
}

.ticker-box {
    background: #0a0a0a;
    color: $accent-green;
    border: tall $border-subtle;
    padding: 0 1;
    margin-bottom: 1;
    text-align: center;
    height: 3;
    content-align: center middle;
    text-style: bold;
}
"""

class CodexBinanceTUI(App):
    CSS = CSS
    
    # Reactive variable to track the symbol across the whole app
    active_symbol = reactive("BTCUSDT")

    BINDINGS = [
        Binding("q", "quit", "Exit System", show=True),
        Binding("c", "clear", "Clear Log", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static("CODEX // BINANCE FUTURES INTERFACE", id="header-area")
        
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("LIVE_MARKET_DATA")
                yield Static("LOADING...", id="live-ticker", classes="ticker-box")

                yield Label("SYMBOL")
                yield Input(value="BTCUSDT", id="symbol")

                yield Label("ORDER_TYPE")
                yield Select(
                    options=[("LIMIT", "LIMIT"), ("MARKET", "MARKET"), ("STOP_LIMIT", "STOP_LIMIT")],
                    value="LIMIT", id="order_type"
                )
                
                yield Label("TRANSACTION_TYPE")
                yield Select(
                    options=[("LONG / BUY", "BUY"), ("SHORT / SELL", "SELL")],
                    value="BUY", id="side"
                )

                yield Label("TRIGGER_SOURCE", id="label_trigger_source")
                yield Select(
                    options=[("LAST_PRICE", "LAST_PRICE"), ("MARK_PRICE", "MARK_PRICE")],
                    value="LAST_PRICE", id="trigger_source"
                )
                
                yield Label("QUANTITY")
                yield Input(placeholder="0.00", id="qty")
                
                yield Label("PRICE (EXECUTION)", id="label_price")
                yield Input(placeholder="0.00", id="price")
                
                yield Label("STOP_PRICE (TRIGGER)", id="label_stop_price")
                yield Input(placeholder="0.00", id="stop_price")
                
                yield Button("EXECUTE_TRANSACTION", id="execute-btn")
                yield Button("CANCEL_ALL_ORDERS", id="cancel-btn")

            with Vertical(id="main-viewport"):
                yield Label("LIVE ORDER PREVIEW")
                yield Static("Initializing...", id="order-preview")
                yield Label("SYSTEM_OUTPUT")
                yield Log(id="log")
                yield Static("System: Ready | Mode: Testnet", classes="status-bar")
        
        yield Footer()

    def on_mount(self) -> None:
        try:
            self.bot = BasicBot(api_key, api_secret)
            self.log_msg("Engine Initialized. API Connected.")
            # Set price refresh interval
            self.set_interval(2.5, self.refresh_ticker)
        except Exception as e:
            self.log_msg(f"Init Error: {str(e)}")

        # Hide stop-specific fields by default
        self.update_ui_visibility("LIMIT")
        self.update_preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "symbol":
            # Updating this reactive variable triggers watch_active_symbol
            self.active_symbol = event.value.upper()
        self.update_preview()

    def watch_active_symbol(self, symbol: str) -> None:
        """Called automatically whenever active_symbol is modified."""
        self.query_one("#live-ticker", Static).update(f"{symbol}: ...")
        self.refresh_ticker()

    @work(exclusive=True) # Runs in background thread to prevent UI freezing
    async def refresh_ticker(self) -> None:
        """Fetches the latest price for the currently active symbol."""
        if not self.active_symbol:
            return
        
        try:
            price_data = self.bot.get_mark_price(self.active_symbol)
            if price_data:
                price = float(price_data.get('markPrice', 0))
                self.query_one("#live-ticker", Static).update(f"{self.active_symbol}: {price:,.2f}")
        except Exception:
            self.query_one("#live-ticker", Static).update(f"{self.active_symbol}: ERROR")

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "order_type":
            self.update_ui_visibility(str(event.value))
        self.update_preview()

    def update_ui_visibility(self, otype: str) -> None:
        """Handles showing/hiding conditional input fields."""
        is_stop = otype == "STOP_LIMIT"
        is_market = otype == "MARKET"

        self.query_one("#stop_price").display = is_stop
        self.query_one("#label_stop_price").display = is_stop
        self.query_one("#trigger_source").display = is_stop
        self.query_one("#label_trigger_source").display = is_stop

        self.query_one("#price").display = not is_market
        self.query_one("#label_price").display = not is_market

    def update_preview(self) -> None:
        otype = self.query_one("#order_type", Select).value
        side = self.query_one("#side", Select).value
        qty = self.query_one("#qty", Input).value
        price = self.query_one("#price", Input).value
        stop = self.query_one("#stop_price", Input).value
        trigger = self.query_one("#trigger_source", Select).value

        side_fmt = f"[b green]{side}[/]" if side == "BUY" else f"[b red]{side}[/]"
        preview_text = f"[b]Type:[/] {otype} | [b]Side:[/] {side_fmt} | [b]Asset:[/] {self.active_symbol}\n"
        preview_text += "----------------------------------------\n"
        preview_text += f"Size:    {qty if qty else '0.00'}\n"

        if otype == "MARKET":
            preview_text += "Price:   [i]Market execution[/i]\n"
        else:
            preview_text += f"Limit:   {price if price else '0.00'}\n"
            if otype == "STOP_LIMIT":
                preview_text += f"Trigger: {stop if stop else '0.00'} ({trigger})\n"

        self.query_one("#order-preview", Static).update(preview_text)

    def log_msg(self, message: str):
        self.query_one("#log", Log).write_line(f"[codex@binance ~]$ {message}")

    def action_clear(self):
        self.query_one("#log", Log).clear()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "execute-btn":
            otype = self.query_one("#order_type", Select).value
            side = self.query_one("#side", Select).value
            
            try:
                qty_val = self.query_one("#qty", Input).value
                if not qty_val:
                    self.log_msg("ERROR: Quantity is required.")
                    return
                qty = float(qty_val)

                self.log_msg(f"Initiating {otype} {side} order for {self.active_symbol}...")

                if otype == "LIMIT":
                    p = float(self.query_one("#price", Input).value)
                    res = self.bot.create_futures_limit_order(self.active_symbol, side, 'LIMIT', qty, p)
                elif otype == "MARKET":
                    res = self.bot.create_futures_market_order(self.active_symbol, side, 'MARKET', qty)
                elif otype == "STOP_LIMIT":
                    p = float(self.query_one("#price", Input).value)
                    s = float(self.query_one("#stop_price", Input).value)
                    t_source = self.query_one("#trigger_source", Select).value
                    # Algo routing implementation
                    res = self.bot.create_stop_limit_order(self.active_symbol, side, s, p, qty, t_source)

                if res.get('success'):
                    order_id = res['data'].get('orderId') or res['data'].get('clientAlgoId')
                    self.log_msg(f"SUCCESS! ID: {order_id}")
                else:
                    self.log_msg(f"FAILED: {res.get('error')}")

            except ValueError:
                self.log_msg("ERROR: Invalid number format in Price/Quantity.")
            except Exception as e:
                self.log_msg(f"SYSTEM ERROR: {str(e)}")

if __name__ == "__main__":
    app = CodexBinanceTUI()
    app.run()