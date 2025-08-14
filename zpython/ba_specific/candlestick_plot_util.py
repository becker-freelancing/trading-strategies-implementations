def plot_candlesticks(ax, stock_prices, col1='green', col2='red'):
    up = stock_prices.loc[stock_prices.closeBid >= stock_prices.openBid]
    down = stock_prices.loc[stock_prices.closeBid < stock_prices.openBid]
    width = .9
    width2 = .1
    ax.bar(up.index, up.closeBid - up.openBid, width, bottom=up.openBid, color=col1, alpha=0.4)
    ax.bar(up.index, up.highBid - up.closeBid, width2, bottom=up.closeBid, color=col1, alpha=0.4)
    ax.bar(up.index, up.lowBid - up.openBid, width2, bottom=up.openBid, color=col1, alpha=0.4)

    ax.bar(down.index, down.closeBid - down.openBid, width, bottom=down.openBid, color=col2, alpha=0.4)
    ax.bar(down.index, down.highBid - down.openBid, width2, bottom=down.openBid, color=col2, alpha=0.4)
    ax.bar(down.index, down.lowBid - down.closeBid, width2, bottom=down.closeBid, color=col2, alpha=0.4)
