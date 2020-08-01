import yfinance as yf
import numpy as np
import requests
import statistics
import csv
import matplotlib.pyplot as plt
from symbols import SP500_symbol, nasdaq_symbols

def getSingleDayDifferences(hist):
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    dayOfTheWeek = diffsInPercentage.index.dayofweek
    aggregatedDiffs = clusterDiffsToDays(diffsInPercentageValues, dayOfTheWeek);
    return aggregatedDiffs


def filterEmptyArr(arr):
    return arr.length != 0


def getDiffsInPercentage(hist):
    open_price = hist.Open
    close_price = hist.Close
    diffs = close_price - open_price
    diffsInPercentage = (diffs / open_price) * 100
    for i in range(len(diffsInPercentage)):
        if np.isinf(diffsInPercentage[i]):
            diffsInPercentage[i] = 0

    return diffsInPercentage


# returns single stock data by month.
def clusterDiffsToMonths(diffsInPercentageValues, related_month_array):
    aggregatedDiffs = np.zeros(12, dtype=float)
    for i in range(len(related_month_array)):
        curMonth = related_month_array[i]
        # -1 because month is 1-12 and arr is 0-11
        aggregatedDiffs[curMonth - 1] += diffsInPercentageValues[i]
    return aggregatedDiffs;


def clusterDiffsToDays(diffsInPercentageValues, dayOfTheWeek):
    aggregatedDiffs = np.zeros(6, dtype=float)
    for i in range(len(dayOfTheWeek)):
        curDay = dayOfTheWeek[i]
        aggregatedDiffs[curDay] += diffsInPercentageValues[i]
    # now aggregatedDiffs contains all the data by Day.
    return aggregatedDiffs;


def getTickers(stock_symbols_arr):
    delimiter = " "
    stocks_string = delimiter.join(stock_symbols_arr)
    tickers = yf.Tickers(stocks_string)
    return tickers


def getAllDayDifferences(stock_hists_arr):
    all_tickers_differences_sum = np.zeros(6)
    for hist in stock_hists_arr:
        single_stock_data = getSingleDayDifferences(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
        # else:
        #     print("diff is nan")
    stocks_count = len(stock_hists_arr)
    avgDiffs = all_tickers_differences_sum / stocks_count
    return avgDiffs;


def getSingleStockMonthDifference(hist):
    if hist.empty:
        print("Problem occured: empty hist!!!")
        return np.zeros(6)
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    related_months = diffsInPercentage.index.month
    aggregatedDiffs = clusterDiffsToMonths(diffsInPercentageValues, related_months)
    return aggregatedDiffs


def clusterDiffsToWeeks(diffsInPercentageValues, related_weeks):
    aggregatedDiffs = np.zeros(53, dtype=float)
    for i in range(len(related_weeks)):
        cur_week = related_weeks[i]
        # -1 because week is 1-53 and arr is 0-52
        aggregatedDiffs[cur_week - 1] += diffsInPercentageValues[i]
    return aggregatedDiffs


def getSingleStockWeeklyDifference(hist):
    diffsInPercentage = getDiffsInPercentage(hist)
    diffsInPercentageValues = diffsInPercentage.values
    related_weeks = diffsInPercentage.index.week
    aggregatedDiffs = clusterDiffsToWeeks(diffsInPercentageValues, related_weeks)
    return aggregatedDiffs


def getAllWeeklyDifferences(hists):
    all_tickers_differences_sum = np.zeros(53)
    for hist in hists:
        single_stock_data = getSingleStockWeeklyDifference(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
        elif np.isinf(single_stock_data).any():
            print("Unexpected inf value!")
    stocks_count = len(hists)
    avgDiffs = all_tickers_differences_sum / stocks_count  # [k/stocks_count for k in sum(differences_data)]
    return avgDiffs;


def getAllMonthDifferences(stock_hists_arr):
    all_tickers_differences_sum = np.zeros(12)
    for hist in stock_hists_arr:
        single_stock_data = getSingleStockMonthDifference(hist)
        if not np.isnan(single_stock_data).any():
            all_tickers_differences_sum += single_stock_data
    stocks_count = len(stock_hists_arr)
    avgDiffs = all_tickers_differences_sum / stocks_count
    return avgDiffs;


def filterBrokenTags(stock_tag, period):
    ticker = yf.Ticker(stock_tag)
    hist = ticker.history(period=period)
    return hist.empty == False


def getHistObjects(stock_tag, period):
    ticker = yf.Ticker(stock_tag)
    hist = ticker.history(period=period)
    return hist


def writeToExcel(daily, monthly, period):
    with open('stocks_file.csv', mode='w') as stocks_file:
        stocks_writer = csv.writer(stocks_file, delimiter=',')  # lineterminator='\n'
        stocks_writer.writerow([period])
        stocks_writer.writerow(daily)
        stocks_writer.writerow(monthly)


# SP500_symbol = ['AAPL', 'ABT', 'ABBV', 'ACN', 'ADBE', 'ADT', 'AAP', 'AES', 'AFL',
#                 'AMG', 'A', 'GAS', 'ARE', 'APD', 'AKAM', 'AA', 'ALXN', 'ALLE', 'ADS', 'ALL', 'ALTR', 'MO',
#                 'AMZN', 'AEE', 'AAL', 'AEP', 'AXP', 'AIG', 'AMT', 'AMP', 'ABC', 'AME', 'AMGN', 'APH', 'APC', 'ADI',
#                 'AON', 'APA', 'AIV', 'AMAT', 'ADM', 'AIZ', 'T', 'ADSK', 'ADP', 'AN', 'AZO', 'AVGO', 'AVB', 'AVY', 'BHI',
#                 'BLL', 'BAC', 'BK', 'BCR', 'BXLT', 'BAX', 'BBT', 'BDX', 'BBBY', 'BRK.B', 'BBY', 'BLX', 'HRB', 'BA',
#                 'BWA', 'BXP', 'BSX', 'BMY', 'BRCM', 'BF.B', 'CHRW', 'CA', 'CVC', 'COG', 'CAM', 'CPB', 'COF', 'CAH',
#                 'HSIC', 'KMX', 'CCL', 'CAT', 'CBG', 'CBS', 'CELG', 'CNP', 'CTL', 'CERN', 'CF', 'SCHW', 'CHK', 'CVX',
#                 'CMG', 'CB', 'CI', 'XEC', 'CINF', 'CTAS', 'CSCO', 'C', 'CTXS', 'CLX', 'CME', 'CMS', 'COH', 'KO', 'CCE',
#                 'CTSH', 'CL', 'CMCSA', 'CMA', 'CSC', 'CAG', 'COP', 'CNX', 'ED', 'STZ', 'GLW', 'COST', 'CCI', 'CSX',
#                 'CMI', 'CVS', 'DHI', 'DHR', 'DRI', 'DVA', 'DE', 'DLPH', 'DAL', 'XRAY', 'DVN', 'DO', 'DTV', 'DFS',
#                 'DISCA', 'DISCK', 'DG', 'DLTR', 'D', 'DOV', 'DOW', 'DPS', 'DTE', 'DD', 'DUK', 'DNB', 'ETFC', 'EMN',
#                 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'EMC', 'EMR', 'ENDP', 'ESV', 'ETR', 'EOG', 'EQT', 'EFX',
#                 'EQIX', 'EQR', 'ESS', 'EL', 'ES', 'EXC', 'EXPE', 'EXPD', 'ESRX', 'XOM', 'FFIV', 'FB', 'FAST', 'FDX',
#                 'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'FLIR', 'FLS', 'FLR', 'FMC', 'FTI', 'F', 'FOSL', 'BEN', 'FCX',
#                 'FTR', 'GME', 'GPS', 'GRMN', 'GD', 'GE', 'GGP', 'GIS', 'GM', 'GPC', 'GNW', 'GILD', 'GS', 'GT', 'GOOGL',
#                 'GOOG', 'GWW', 'HAL', 'HBI', 'HOG', 'HAR', 'HRS', 'HIG', 'HAS', 'HCA', 'HCP', 'HCN', 'HP', 'HES', 'HPQ',
#                 'HD', 'HON', 'HRL', 'HSP', 'HST', 'HCBK', 'HUM', 'HBAN', 'ITW', 'IR', 'INTC', 'ICE', 'IBM', 'IP', 'IPG',
#                 'IFF', 'INTU', 'ISRG', 'IVZ', 'IRM', 'JEC', 'JBHT', 'JNJ', 'JCI', 'JOY', 'JPM', 'JNPR', 'KSU', 'K',
#                 'KEY', 'GMCR', 'KMB', 'KIM', 'KMI', 'KLAC', 'KSS', 'KRFT', 'KR', 'LB', 'LLL', 'LH', 'LRCX', 'LM', 'LEG',
#                 'LEN', 'LVLT', 'LUK', 'LLY', 'LNC', 'LLTC', 'LMT', 'L', 'LOW', 'LYB', 'MTB', 'MAC', 'M', 'MNK', 'MRO',
#                 'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MAT', 'MKC', 'MCD', 'MCK', 'MJN', 'MMV', 'MDT', 'MRK', 'MET',
#                 'KORS', 'MCHP', 'MU', 'MSFT', 'MHK', 'TAP', 'MDLZ', 'MON', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MUR',
#                 'MYL', 'NDAQ', 'NOV', 'NAVI', 'NTAP', 'NFLX', 'NWL', 'NFX', 'NEM', 'NWSA', 'NEE', 'NLSN', 'NKE', 'NI',
#                 'NE', 'NBL', 'JWN', 'NSC', 'NTRS', 'NOC', 'NRG', 'NUE', 'NVDA', 'ORLY', 'OXY', 'OMC', 'OKE', 'ORCL',
#                 'OI', 'PCAR', 'PLL', 'PH', 'PDCO', 'PAYX', 'PNR', 'PBCT', 'POM', 'PEP', 'PKI', 'PRGO', 'PFE', 'PCG',
#                 'PM', 'PSX', 'PNW', 'PXD', 'PBI', 'PCL', 'PNC', 'RL', 'PPG', 'PPL', 'PX', 'PCP', 'PCLN', 'PFG', 'PG',
#                 'PGR', 'PLD', 'PRU', 'PEG', 'PSA', 'PHM', 'PVH', 'QRVO', 'PWR', 'QCOM', 'DGX', 'RRC', 'RTN', 'O', 'RHT',
#                 'REGN', 'RF', 'RSG', 'RAI', 'RHI', 'ROK', 'COL', 'ROP', 'ROST', 'RLD', 'R', 'CRM', 'SNDK', 'SCG', 'SLB',
#                 'SNI', 'STX', 'SEE', 'SRE', 'SHW', 'SPG', 'SWKS', 'SLG', 'SJM', 'SNA', 'SO', 'LUV', 'SWN', 'SE', 'STJ',
#                 'SWK', 'SPLS', 'SBUX', 'HOT', 'STT', 'SRCL', 'SYK', 'STI', 'SYMC', 'SYY', 'TROW', 'TGT', 'TEL', 'TE',
#                 'TGNA', 'THC', 'TDC', 'TSO', 'TXN', 'TXT', 'HSY', 'TRV', 'TMO', 'TIF', 'TWX', 'TWC', 'TJX', 'TMK',
#                 'TSS', 'TSCO', 'RIG', 'TRIP', 'FOXA', 'TSN', 'TYC', 'UA', 'UNP', 'UNH', 'UPS', 'URI', 'UTX', 'UHS',
#                 'UNM', 'URBN', 'VFC', 'VLO', 'VAR', 'VTR', 'VRSN', 'VZ', 'VRTX', 'VIAB', 'V', 'VNO', 'VMC', 'WMT',
#                 'WBA', 'DIS', 'WM', 'WAT', 'ANTM', 'WFC', 'WDC', 'WU', 'WY', 'WHR', 'WFM', 'WMB', 'WEC', 'WYN', 'WYNN',
#                 'XEL', 'XRX', 'XLNX', 'XL', 'XYL', 'YHOO', 'YUM', 'ZBH', 'ZION', 'ZTS']
#
# nasdaq_symbols = ['ATVI', 'ADBE', 'AMD',
#                   'ALGN', 'ALXN', 'AMZN', 'AMGN', 'AAL', 'ADI', 'AAPL', 'AMAT', 'ASML', 'ADSK',
#                   'ADP', 'AVGO', 'BIDU', 'BIIB', 'BMRN', 'CDNS', 'CERN', 'CHKP', 'CHTR', 'TCOM', 'CTAS', 'CSCO', 'CTXS',
#                   'CMCSA', 'COST', 'CSX', 'CTSH', 'DLTR', 'EA', 'EBAY', 'EXC', 'EXPE', 'FAST', 'FB', 'FISV', 'GILD',
#                   'GOOG', 'GOOGL', 'HAS', 'HSIC', 'ILMN', 'INCY', 'INTC', 'INTU', 'ISRG', 'IDXX', 'JBHT', 'JD', 'KLAC',
#                   'KHC', 'LRCX', 'LBTYA', 'LBTYK', 'LULU', 'MELI', 'MAR', 'MCHP', 'MDLZ', 'MNST', 'MSFT', 'MU', 'MXIM',
#                   'MYL', 'NTAP', 'NFLX', 'NTES', 'NVDA', 'NXPI', 'ORLY', 'PAYX', 'PCAR', 'BKNG', 'PYPL', 'PEP', 'QCOM',
#                   'REGN', 'ROST', 'SIRI', 'SWKS', 'SBUX', 'NLOK', 'SNPS', 'TTWO', 'TSLA', 'TXN', 'TMUS', 'ULTA', 'UAL',
#                   'VRSN', 'VRSK', 'VRTX', 'WBA', 'WDC', 'WDAY', 'WYNN', 'XEL', 'XLNX']


def plotGraphs(aggregated_day_diffs, aggregated_weekly_diffs, aggregated_month_diff):
    # print("Daily change as function of the day in the week: from monday to saturday.")
    # print(aggregated_day_diffs);
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    plt.figure(1)
    plt.bar(days, aggregated_day_diffs)
    plt.title("Change by day in the week")


    # print("Weekly change as function of the week in the year")
    # print(aggregated_weekly_diffs)
    weeks = range(53)
    plt.figure(2)
    plt.bar(weeks, aggregated_weekly_diffs)
    plt.title("Change by week in the year")


    # print("Monthly change as function of the day in the month in the year: from January to December.")
    # print(aggregated_month_diff)
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    plt.figure(3)
    plt.bar(months, aggregated_month_diff)
    plt.title("Change by month in the year")
    plt.show()


def generateGraphsFromSymbols(wanted_time_range, symbols_array):
    symbols_hists = list(map(lambda x: getHistObjects(x, wanted_time_range), symbols_array))
    hists_filtered = list(filter(lambda hist: hist.empty == False, symbols_hists))
    aggregated_day_diffs = getAllDayDifferences(hists_filtered)
    aggregated_weekly_diffs = getAllWeeklyDifferences(hists_filtered)
    aggregated_month_diff = getAllMonthDifferences(hists_filtered)
    plotGraphs(aggregated_day_diffs, aggregated_weekly_diffs, aggregated_month_diff)


generateGraphsFromSymbols("10y", nasdaq_symbols)
