from typing import (
    List,
    Tuple,
)

import pandas as pd
from scipy.stats import gmean

class Transformer:

    def __init__(self):
        self

    def read_orders(self) -> pd.DataFrame:
        orders = pd.read_csv('orders.csv', header=0)
        # these order amounts and times shouldn't be strings
        orders["amount"] = orders["amount"].astype(int)
        orders["date"] = pd.to_datetime(orders["date"])
        return orders

    def enrich_orders(self, orders: pd.DataFrame, col_name: str, value: List[str]) -> pd.DataFrame:
        """
        Adds a column to the data frame

        Args:
            orders (pd.Dataframe): The dataframe to be enriched
            col_name (str): Name of the new enriched column
            value (List[str]): Data to go into the new column

        Returns:
            The enriched dataframe
        """
        num_original_columns = len(orders.columns)
        orders.insert(num_original_columns, col_name, value)
        return orders

    def split_customers(self, orders: pd.DataFrame, threshold: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits customers into two groups based on a threshold

        Args:
            orders (pd.DataFrame): The dataframe to be split
            threshold (int): Value to split the customer base on

        Returns:
            Tuple containing the split dataframes
        """
        # cast this to int so we can sort via this column, in case left as string
        orders["amount"] = orders["amount"].astype(int)

        # the first part of the tuple contains orders with amount less than threshold
        orders = orders.sort_values(by=["amount"])
        splitIndex = orders["amount"].searchsorted(threshold)
        return (orders[0:splitIndex], orders[splitIndex:])


if __name__ == '__main__':
    transformer = Transformer()
    data = transformer.read_orders()

    countries = ['GBR', 'AUS', 'USA', 'GBR', 'RUS', 'GBR', 'KOR', 'NZ']
    data = transformer.enrich_orders(data, 'Country', countries)

    # ignore free orders and use the geometric mean for the threshold
    # the geometric mean is less swayed by outliers than the arithmetic mean
    # alternatively use the median
    threshold = gmean(data[data["amount"] > 0]["amount"])
    low_spending_orders, high_spending_orders = transformer.split_customers(data, threshold)

    print("A sample of low spending orders:")
    print(low_spending_orders.head(), "\n")

    print("A sample of high spending orders:")
    print(high_spending_orders.head(), "\n")

    data = data.sort_values(by=["amount"])

    print("The customer who placed the highest order amount was ", data.iloc[-1]["customer"] , ".")
    print("The customer who placed the lowest order amount was ", data.iloc[0]["customer"] , ".")
    print("The average order amount across all customers was ", data["amount"].mean() , ".")

    data = data.sort_values(by=["date"])
    print("The customer who placed the earliest order was ", data.iloc[0]["customer"] , ".")

    # use [0] to pick a specific mode
    most_common_month = data["date"].dt.month_name().mode()[0]
    print("Most orders happened in ", most_common_month, ".")
