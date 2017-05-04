# Python Customizable Stock Backtester
Python project for backtesting stock trading techniques.

# What it is Used For
This repository hosts code to download historical financial data from Yahoo Finance. You can then utilize that data, or any other source of 
historical stock data to test your buying and selling techniques to optimize your strategy.

# How to Use
1. Download historical stock data using `YahooDownload.py`
2. Run `backtest.py` with buy and sell conditions
3. Analyze output data located in the output directory

## backtest.py Commandline Parameters
- -h, --help (Help). Show help information.
- -d DIRECTORY, --directory DIRECTORY. Directory containing csv files of stock data.
-  -b BUY_CONDITIONS, --buy_conditions BUY_CONDITIONS. Conditions under which a stock should be purchased (already owned stocks will not be purchased again.
-  -s SELL_CONDITIONS, --sell_conditions SELL_CONDITIONS. Conditions under which an owned stock should be sold.
-  -df CSV_DATE_FORMAT, --csv_date_format CSV_DATE_FORMAT. Python string format for date. Ex. "%Y%m%d" for dates like 19900223.
-  -oc OPEN_COLUMN, --open_column OPEN_COLUMN. Zero-indexed CSV column for the open price.
-  -cc CLOSE_COLUMN, --close_column CLOSE_COLUMN. Zero-indexed CSV column for the close price.
-  -dc DATE_COLUMN, --date_column DATE_COLUMN. Zero-indexed CSV column for the date.

## Detail on Buy/Sell Conditions
Conditionals are not Python style. You can write a combination of conditions as such: 
`stock:decrease_rank <= 20 && stock:price <= 100`. Supported boolean operations are AND (&&), OR (||), and NOT (~).

### Membership
Some of the variables support membership as part of the conditions. For example, if you only want to buy certain stocks you could write
 the following condition: `stock in {'AAPL', 'GOOG', 'GOOGL'}` which will be true only for stock symbols AAPL, GOOG, and GOOGL.

### Arithmetic
For numeric variables arithmetic can be performed. For example you could write a sell condition like this: `stock:price > stock:buy_price*2`
 which will only sell once the stock price has doubled.

Arithmetic can also be used for dates. For example, if you want to sell after 3 months this sell condition will work: 
`date:today >= date:buy+[3*date:months]`

Instead of parenthesis, use brackets ([, ]). Parenthesis only work for the boolean, not for math.

### Array Variables
Some variables support array-type indexing for history. That means you can check the variable values for previous days. A query like 
`date:days_of_history >= 5 && stock:price:5 < 30` will select stocks whose price was less than 30 5 days ago. An index of 0 is today. Indexes greater than 0 go back in history. Indexes less than 0 are not supported because you cannot trade based on future information.

All array variable conditions must be combined with `date:days_of_history` by '&&' like the example above because there is a time when 
no history is available. The days_of_history condition must come first so that the array variable is not evaluated. If you neglect to include this, the program will crash.

### Supported Variables
#### Stock Variables
- "stock" or "stock:symbol" - Is the stock symbol. Can be checked for equality or membership, not inequality or arithmetic.
- "stock:open_price" - The openning price for the stock on the current day. Supports array indexing.
- "stock:close_price" - The closing price for the stock on the current day. This is the price that will be used as the purchase price. Supports array indexing.
- "stock:price" - Same as close_price. Supports array indexing.
- "stock:buy_price" - The price paid to buy the stock. Only to be used for sell conditions, not buy conditions.
- "stock:owned" - Boolean, true when the stock is owned. To be used in future versions. Currenly it works, but is essentially pointless.
- "stock:increase_rank" - The rank of this stock in descending order, ordered by percent change in the current day. 
i.e. a stock with an increase_rank of 0 had the greatest increase by percent for that day. Supports array indexing.
- "stock:decrease_rank" - The rank of this stock in ascending order, ordered by percent change in the current day. 
i.e. a stock with a decrease_rank of 0 had the greatest decrease by percent for that day. Supports array indexing.
- "stock:change_percent" - The decimal percentage change for thist stock for today. Decimal percent means that 10% will be 0.1. Supports array indexing.

#### Date Variables
- "date" or "date:today" - Today's date in Unix epoch time.
- "date:days_of_history" - Number of days of previous data available for the stock, (i.e. days since the stock was listed). To be used with array variables.
- "date:buy" - The Unix epoch time that the stock was purchased (if it was). Only to be used for sell conditions, not buy conditions.
- "date:day_of_week" - Today's day of the week as an integer from 1 to 7, where 1 is Monday.
- "date:month" - The month that today is in. 1 is January.
- "date:days" - Constant value to be used in arithmetic. If you want to sell after 10 days the sell condition would be 
`date >= date:buy+[10*date:days]`.
- "date:months" - Constant value to be used in arithmetic. Similar to "date:days".
- "date:years" - Constant value to be used in arithmetic. Similar to "date:months" and "date:days".

# Examples
## Example Buy Conditions
#### Buy 5 Worst Performing Stocks For Today
`stock:decrease_rank < 5`
#### Buy 5 Best Performing Stocks For Today
`stock:increase_rank < 5`
#### Buy Stocks That Have Lost Value For 2 Days
`date:date_of_history >= 1 && stock:change_percent:1 < 0 && stock:change_percent < 0`
#### Buy Specific Stocks
`stock in {'AAPL', 'GOOG', 'SPX', 'CSX'}`

`stock in {'AAPL', 'GOOG', 'SPX', 'CSX'} && (stock:change_percent > 0.05 || stock:change_percent < 0)`
## Example Sell Conditions
#### Sell After 3 Months
`date >= date:buy+[3*date:months]`
#### Sell If Stock Price Increase Is Slowing
`(stock:price > stock:buy_price) && (stock:increase_rank < stock:increase_rank:1)`
