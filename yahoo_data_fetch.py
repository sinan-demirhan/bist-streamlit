import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pickle

# Function to fetch stock data
def fetch_stock_data():
    today = datetime.now()
    month = (today.month - 4) % 12 or 12
    year = today.year + ((today.month - 4) // 12)

    my_date = today.replace(year=year, month=month, day=1).strftime("%Y-%m-%d")

    with open("analysis_data.pickle", 'rb') as handle:
        output = pickle.load(handle)

    df = pd.DataFrame(output['TUM_FONLAR'])

    class Stock:
        def __init__(self, stock_id, stock_index):
            self.id = stock_id
            self.hisse_kodu = stock_index.split(".")[0]
            self.raw_data = yf.download(stock_index, start='2025-05-01')
            self.info_data = yf.Ticker(stock_index)
        def set_the_delivery_data(self):
            my_data = self.raw_data[['Close']].reset_index()
            my_data["hisse_kodu"] = self.hisse_kodu
            if 'sector' in self.info_data.info:
                my_data["sector"] = self.info_data.info['sector']
                my_data["industry"] = self.info_data.info['industry']
            else:
                my_data["sector"] = 'Unknown'
                my_data["industry"] = 'Unknown'
            self.data = my_data

    indeces = [f"{hisse.split('.')[0]}.IS" for hisse in df["hisse_kodu"].unique()]
    n_of_stocks = len(indeces)

    stock_objects = {}
    stock_close_data = pd.DataFrame()

    for ids in range(n_of_stocks):
        stock_objects[ids] = Stock(ids, indeces[ids])
        stock_objects[ids].set_the_delivery_data()
        stock_objects[ids].data.columns = ['Date', 'Close', 'hisse_kodu', 'sector', 'industry']
        stock_close_data = pd.concat([stock_close_data, stock_objects[ids].data], ignore_index=True)

    stock_close_data.to_csv("stock_close_data.csv", index=False)
    print(stock_close_data.columns)

    return stock_close_data

# Streamlit app
def main():
    st.title("Stock Data Fetcher and Downloader")

    if st.button("FETCH STOCK DATA"):
        st.write("Fetching stock data... Please wait.")
        try:
            fetch_stock_data()
            st.success("DATA is ready to download!")
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

    if st.button("Download data"):
        try:
            st.markdown("### Download File")
            st.markdown("Click below to download the data file.")
            with open("stock_close_data.csv", "rb") as file:
                data = file.read()
            st.download_button(
                label="Download CSV",
                data=data,
                file_name="stock_close_data.csv",
                mime="text/csv"
            )
        except FileNotFoundError:
            st.error("File not found. Please fetch data first.")

if __name__ == "__main__":
    main()

