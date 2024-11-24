import pandas as pd
import yfinance as yf
from datetime import datetime

def get_performance_data(ticker_file, output_file):
    """Reads ticker names from a CSV file, fetches performance data, and saves it to a new CSV file with desired column names."""
    
    # Read ticker names from CSV file
    tickers = pd.read_csv(ticker_file)['Ticker'].tolist()
    
    # Define performance periods in days
    performance_periods = {
        "1 Day": 1,
        "5 Days": 5,
        "10 Days": 10,
        "1 Month": 21,  # Approx. trading days in a month
        "3 Months": 63,  # Approx. trading days in 3 months
        "6 Months": 126,  # Approx. trading days in 6 months
        "Year to Date": 'ytd',
        "1 Year": 252,  # Approx. trading days in a year
        "2 Years": 504,  # Approx. trading days in 2 years
        "3 Years": 756,  # Approx. trading days in 3 years
        "5 Years": 1260,  # Approx. trading days in 5 years
        "10 Years": 2520  # Approx. trading days in 10 years
    }
    
    # Function to calculate performance
    def calculate_performance(data, periods):
        today = data['Close'].iloc[-1]
        performance = {}
        for period_name, period_days in periods.items():
            if period_days == 'ytd':
                start_of_year = datetime(datetime.now().year, 1, 1)
                ytd_data = data[data.index >= start_of_year]
                if len(ytd_data) > 0:
                    start_ytd = ytd_data['Close'].iloc[0]
                    performance[period_name] = ((today - start_ytd) / start_ytd) * 100
                else:
                    performance[period_name] = None
            else:
                if len(data) > period_days:
                    past = data['Close'].iloc[-period_days]
                    performance[period_name] = ((today - past) / past) * 100
                else:
                    performance[period_name] = None
        return performance
    
    # Fetch performance data for each ticker
    performance_data = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period="max")
            if data.empty:
                continue
            perf = calculate_performance(data, performance_periods)
            perf['Ticker'] = ticker
            performance_data.append(perf)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue
    
    # Create a DataFrame from the performance data
    df = pd.DataFrame(performance_data)
    df = df[['Ticker'] + [col for col in df.columns if col != 'Ticker']]  # Move 'Ticker' to the first column
    
    # Highlight function for styling
    def highlight_performance(val):
        if pd.isna(val):
            return ''
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'
    
    # Apply the highlighting
    styled_df = df.style.map(highlight_performance, subset=pd.IndexSlice[:, df.columns != 'Ticker'])
    
    # Save the DataFrame to an HTML file
    html_output_file = output_file.replace('.csv', '.html')
    styled_df.to_html(html_output_file, index=False)
    print(f"Performance data saved to {html_output_file}")


# Example usage
ticker_file = "E:/GAURAV/Stock_Test/Ticker.csv"
output_file = "E:/GAURAV/Stock_Test/Performance.csv"
get_performance_data(ticker_file, output_file)
