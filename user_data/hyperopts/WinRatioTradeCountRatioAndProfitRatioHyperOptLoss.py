from datetime import datetime
from math import exp
from typing import Dict

from pandas import DataFrame

from freqtrade.optimize.hyperopt import IHyperOptLoss


class WinRatioTradeCountRatioAndProfitRatioHyperOptLoss(IHyperOptLoss):


    @staticmethod
    def hyperopt_loss_function(results: DataFrame, trade_count: int,
                                min_date: datetime, max_date: datetime,
                                config: Dict, processed: Dict[str, DataFrame],
                                *args, **kwargs) -> float:

        EXPECTED_TRADE_COUNT = 500
        EXPECTED_WIN_RATE = 0.9
        EXPECTED_AVG_PROFIT = 0.6

        WEIGHT_WIN_RATE = 1
        WEIGHT_AVG_PROFIT = 1
        WEIGHT_TRADE_COUNT = 1


        wins = len(results[results['profit_ratio'] > 0])
        avg_profit = results['profit_ratio'].sum()
    
        result = 0
        win_ratio = WEIGHT_WIN_RATE * (wins / trade_count / EXPECTED_WIN_RATE) * 100
        result -= win_ratio 
        
        if win_ratio >= 85:

            trade_count_ratio = WEIGHT_TRADE_COUNT * (trade_count / EXPECTED_TRADE_COUNT) * 100
            result -= trade_count_ratio 
                
            avg_profit_ratio = WEIGHT_AVG_PROFIT * (avg_profit / EXPECTED_AVG_PROFIT) * 100
            result -= avg_profit_ratio

        return result
