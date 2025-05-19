import tkinter as tk
from tkinter import messagebox
import yfinance as yf
import pandas as pd
import threading
import time
import smtplib
from email.mime.text import MIMEText

#function to calculate RSI (Relative strength index)
def calculate_rsi(prices, period=14):
    delta = prices.diff() # price changes
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean() #average gains
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean() #average losses
    rs = gain / loss #relative strength
    rsi = 100 - (100 / (1 + rs)) # RSI formula
    return rsi

#main trading bot application
class StockTradingBotApp:
    def __init__(self, master):
        self.master = master
        master.title("Stock RSI Trading Indicator")

        #label and entry for stock ticker
        self.ticker_label = tk.Label(master, text="Enter stock ticker:", font=("Arial", 14))
        self.ticker_label.pack(pady=5)

        self.ticker_entry = tk.Entry(master, font=("Arial", 14))
        self.ticker_entry.insert(0, "AAPL") # default value: apple stock
        self.ticker_entry.pack(pady=5)

        #labels for showing current price, RSI, and trading signal
        self.price_label = tk.Label(master, text="Price: ", font=("Arial", 20))
        self.price_label.pack(pady=10)

        self.rsi_label = tk.Label(master, text="RSI: ", font=("Arial", 20))
        self.rsi_label.pack(pady=10)

        self.signal_label = tk.Label(master, text="Signal: ", font=("Arial", 20, 'bold'))
        self.signal_label .pack(pady=10)

        #buttons to start and stop the bot
        self.start_button = tk.Button(master, text="Start Bot", command=self.start_bot)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.running = False #flag to control the loop

    def start_bot(self):
        #start the bot
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.run_bot, daemon=True).start() #run in background thread
        
    def stop_bot(self):
        #stop the bot
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_bot(self):
        #main loop: keeps checking stock every minute
        while self.running:
            ticker = self.ticker_entry.get().upper() # get ticker from ticker entry box
            try:
                #fetch recent stock data (1-day, 1-minute intervals)
                data = yf.download(ticker, period='1d', interval='1m', auto_adjust=False)
                data['RSI'] = calculate_rsi(data['Close']) #calculate RSI based on close price

                #get latest RSI and price
                latest_rsi = data['RSI'].iloc[-1].item()
                latest_price = data['Close'].iloc[-1].item()

                #print to console for monitoring
                print(f"{ticker} Price: {latest_price:.2f} | RSI: {latest_price:.2f}")

                #update GUI labels
                self.price_label.config(text=f"Price: {latest_price:.2f}")
                self.rsi_label.config(text=f"RSI: {latest_rsi:.2f}")

                #check for trading signals
                if latest_rsi < 30:
                    signal = "BUY SIGNAL"
                    color = "green"

                elif latest_rsi > 70:
                    signal = "SELL SIGNAL"
                    color = "red"

                else:
                    signal = "No signal"
                    color = "black"

                #update the signal label color and text
                self.signal_label.config(text=f"Signal: {signal}", fg=color)

            except Exception as e:
                #show error and stop bot if something goes wrong
                messagebox.showerror("Error", str(e))
                self.stop_bot()

            #wait for 60 seconds before checking again
            time.sleep(60)

#run the tkinter GUI app
root = tk.Tk()
app = StockTradingBotApp(root)
root.mainloop()
