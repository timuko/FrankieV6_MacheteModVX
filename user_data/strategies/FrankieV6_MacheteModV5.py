import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
import talib.abstract as ta
from freqtrade.strategy import IStrategy, merge_informative_pair, stoploss_from_open, IntParameter, DecimalParameter, CategoricalParameter
from freqtrade.persistence import Trade
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from cachetools import TTLCache
from functools import reduce
from pandas import DataFrame


"""
Original strat by @Fiber modded by @Machete 
Custom stoploss and dynamic roi based on godly work of @werkkrew
"""
class FrankieV6_MacheteModV5(IStrategy):

    INTERFACE_VERSION = 2

    startup_candle_count: int = 300
    custom_current_price_cache = TTLCache(maxsize=100, ttl=300)
    process_only_new_candles = True
    use_sell_signal = True
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_only_offset_is_reached = False
    trailing_stop_positive_offset = 0.047

    stoploss = -0.085
    
    timeframe = '5m'
    inf_1h = '1h' 


    protections_should_optimize_max_drawdown = False
    
    buy_should_optimize_scores = True
    buy_should_optimize_guards = False
    buy_should_optimize_condition_common = False
    buy_should_optimize_condition_1 = False
    buy_should_optimize_condition_2 = False
    buy_should_optimize_condition_3 = False
    buy_should_optimize_condition_4 = False
    buy_should_optimize_condition_5 = False
    buy_should_optimize_condition_6 = False
    buy_should_optimize_condition_7 = False
    buy_should_optimize_condition_8 = False
    buy_should_optimize_condition_9 = False
    buy_should_optimize_condition_10 = False
    buy_should_optimize_condition_11 = False
    buy_should_optimize_condition_12 = False
    buy_should_optimize_condition_13 = False
    buy_should_optimize_condition_14 = False
    buy_should_optimize_condition_15 = False
    buy_should_optimize_condition_16 = False
    buy_should_optimize_condition_17 = False
    buy_should_optimize_condition_18 = False
    buy_should_optimize_condition_19 = False
    buy_should_optimize_condition_20 = False
    buy_should_optimize_condition_21 = False
    buy_should_optimize_condition_22 = False
    buy_should_optimize_condition_23 = False
    buy_should_optimize_condition_24 = False
    buy_should_optimize_condition_25 = False
    buy_should_optimize_condition_26 = False
    buy_should_optimize_condition_27 = False
    
    sell_should_optimize_custom_sell = False
    

    protections_max_drawdown_max_allowed_drawdown = DecimalParameter(0.01, 0.20, default=0.10, load=True, space='protection', decimals=2, optimize=protections_should_optimize_max_drawdown)

    buy_min_score = IntParameter(3, 10, default=5, load=True, space='buy', optimize=False)

    buy_guard_ewo_low = DecimalParameter(-20.0, -8.3, default=-20.0, load=True, space='buy', optimize=buy_should_optimize_guards) 
    buy_guard_ewo_high = DecimalParameter(2.0, 12.0, default=6.0, load=True, space='buy', optimize=buy_should_optimize_guards) 
    buy_guard_fast_ewo = IntParameter(10, 50, default=50, load=True, space='buy', optimize=buy_should_optimize_guards)
    buy_guard_slow_ewo = IntParameter(100, 200, default=200, load=True, space='buy', optimize=buy_should_optimize_guards)

    buy_guard_pump_24h_pull_threshold_1 = DecimalParameter(1.5, 3.0, default=1.75, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_24h_threshold_1 = DecimalParameter(0.4, 1.0, default=0.5, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_pull_threshold_2 = DecimalParameter(1.5, 3.0, default=1.75, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_threshold_2 = DecimalParameter(0.4, 1.0, default=0.56, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_pull_threshold_3 = DecimalParameter(1.5, 3.0, default=1.75, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_threshold_3 = DecimalParameter(0.4, 1.0, default=0.85, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_24h_strict_pull_threshold_4 = DecimalParameter(1.5, 3.0, default=2.2, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_24h_strict_threshold_4 = DecimalParameter(0.4, 1.0, default=0.4, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_strict_pull_threshold_5 = DecimalParameter(1.5, 3.0, default=2.0, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_strict_threshold_5 = DecimalParameter(0.4, 1.0, default=0.56, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_strict_pull_threshold_6 = DecimalParameter(1.5, 3.0, default=2.0, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_strict_threshold_6 = DecimalParameter(0.4, 1.0, default=0.68, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_24h_loose_pull_threshold_7 = DecimalParameter(1.5, 3.0, default=1.7, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_24h_loose_threshold_7 = DecimalParameter(0.4, 1.0, default=0.66, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_loose_pull_threshold_8 = DecimalParameter(1.5, 3.0, default=1.7, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_36h_loose_threshold_8 = DecimalParameter(0.4, 1.0, default=0.7, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_loose_pull_threshold_9 = DecimalParameter(1.5, 3.0, default=1.4, space='buy', decimals=2, load=True, optimize=buy_should_optimize_guards)
    buy_guard_pump_48h_loose_threshold_9 = DecimalParameter(0.4, 1.8, default=0.68, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)

    buy_guard_dip_normal_threshold_1 = DecimalParameter(0.001, 0.05, default=0.02, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_normal_threshold_2 = DecimalParameter(0.01, 0.2, default=0.14, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_normal_threshold_3 = DecimalParameter(0.05, 0.4, default=0.32, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_normal_threshold_4 = DecimalParameter(0.2, 0.5, default=0.5, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_strict_threshold_5 = DecimalParameter(0.001, 0.05, default=0.015, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_strict_threshold_6 = DecimalParameter(0.01, 0.2, default=0.06, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_strict_threshold_7 = DecimalParameter(0.05, 0.4, default=0.24, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_strict_threshold_8 = DecimalParameter(0.2, 0.5, default=0.4, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_loose_threshold_9 = DecimalParameter(0.001, 0.05, default=0.026, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_loose_threshold_10 = DecimalParameter(0.01, 0.2, default=0.24, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_loose_threshold_11 = DecimalParameter(0.05, 0.4, default=0.42, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)
    buy_guard_dip_loose_threshold_12 = DecimalParameter(0.2, 0.5, default=0.66, space='buy', decimals=3, load=True, optimize=buy_should_optimize_guards)


    buy_voting_ensemble = IntParameter(1, 6, default=1, load=True, space='buy', optimize=buy_should_optimize_condition_common)

    buy_condition_1_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_1)
    buy_condition_score_1 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_min_inc_1 = DecimalParameter(0.01, 0.05, default=0.032, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_1)
    buy_rsi_14_1h_min_1 = DecimalParameter(25.0, 40.0, default=38.4, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_1)
    buy_rsi_14_1h_max_1 = DecimalParameter(70.0, 90.0, default=81.1, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_1)
    buy_rsi_1 = DecimalParameter(20.0, 40.0, default=39.5, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_1)
    buy_mfi_1 = DecimalParameter(20.0, 40.0, default=39.2, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_1)

    buy_condition_2_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_2)
    buy_condition_score_2 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_2 = DecimalParameter(1.0, 10.0, default=2.6, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_2)
    buy_rsi_14_1h_min_2 = DecimalParameter(30.0, 40.0, default=32.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_2)
    buy_rsi_14_1h_max_2 = DecimalParameter(70.0, 95.0, default=84.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_2)
    buy_rsi_14_1h_diff_2 = DecimalParameter(30.0, 50.0, default=39.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_2)
    buy_mfi_2 = DecimalParameter(30.0, 56.0, default=49.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_2)
    buy_bb_offset_2 = DecimalParameter(0.97, 0.999, default=0.983, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_2)

    buy_condition_3_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_3)
    buy_condition_score_3 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_bb40_bbdelta_close_3 = DecimalParameter(0.005, 0.06, default=0.057, space='buy', load=True, optimize=buy_should_optimize_condition_3)
    buy_bb40_closedelta_close_3 = DecimalParameter(0.01, 0.03, default=0.023, space='buy', load=True, optimize=buy_should_optimize_condition_3)
    buy_bb40_tail_bbdelta_3 = DecimalParameter(0.15, 0.45, default=0.418, space='buy', load=True, optimize=buy_should_optimize_condition_3)
    buy_ema_rel_3 = DecimalParameter(0.97, 0.999, default=0.986, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_3)

    buy_condition_4_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_4)
    buy_condition_score_4 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_bb20_close_bblowerband_4 = DecimalParameter(0.96, 0.99, default=0.979, space='buy', load=True, optimize=buy_should_optimize_condition_4)
    buy_bb20_volume_4 = DecimalParameter(1.0, 20.0, default=10.0, space='buy', decimals=2, load=True, optimize=buy_should_optimize_condition_4)

    buy_condition_5_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_5)
    buy_condition_score_5 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_ema_open_mult_5 = DecimalParameter(0.016, 0.03, default=0.019, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_5)
    buy_bb_offset_5 = DecimalParameter(0.98, 1.0, default=0.999, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_5)
    buy_ema_rel_5 = DecimalParameter(0.97, 0.999, default=0.982, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_5)

    buy_condition_6_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_6)
    buy_condition_score_6 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_ema_open_mult_6 = DecimalParameter(0.02, 0.03, default=0.025, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_6)
    buy_bb_offset_6 = DecimalParameter(0.98, 0.999, default=0.984, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_6)

    buy_condition_7_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_7)
    buy_condition_score_7 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_7 = DecimalParameter(1.0, 10.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_7)
    buy_ema_open_mult_7 = DecimalParameter(0.02, 0.04, default=0.03, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_7)
    buy_rsi_7 = DecimalParameter(24.0, 50.0, default=36.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_7)
    buy_ema_rel_7 = DecimalParameter(0.97, 0.999, default=0.986, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_7)

    buy_condition_8_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_8)
    buy_condition_score_8 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_8 = DecimalParameter(1.0, 6.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_8)
    buy_rsi_8 = DecimalParameter(36.0, 40.0, default=20.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_8)
    buy_tail_diff_8 = DecimalParameter(3.0, 10.0, default=3.5, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_8)

    buy_condition_9_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_9)
    buy_condition_score_9 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_9 = DecimalParameter(1.0, 4.0, default=1.0, space='buy', decimals=2, load=True, optimize=buy_should_optimize_condition_9)
    buy_ma_offset_9 = DecimalParameter(0.94, 0.99, default=0.97, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_9)
    buy_bb_offset_9 = DecimalParameter(0.97, 0.99, default=0.985, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_9)
    buy_rsi_14_1h_min_9 = DecimalParameter(26.0, 40.0, default=30.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_9)
    buy_rsi_14_1h_max_9 = DecimalParameter(70.0, 90.0, default=88.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_9)
    buy_mfi_9 = DecimalParameter(36.0, 65.0, default=30.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_9)

    buy_condition_10_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_10)
    buy_condition_score_10 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_10 = DecimalParameter(1.0, 8.0, default=2.4, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_10)
    buy_ma_offset_10 = DecimalParameter(0.93, 0.97, default=0.944, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_10)
    buy_bb_offset_10 = DecimalParameter(0.97, 0.99, default=0.994, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_10)
    buy_rsi_14_1h_10 = DecimalParameter(20.0, 40.0, default=37.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_10)

    buy_condition_11_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_11)
    buy_condition_score_11 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_ma_offset_11 = DecimalParameter(0.93, 0.99, default=0.939, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_11)
    buy_min_inc_11 = DecimalParameter(0.005, 0.05, default=0.022, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_11)
    buy_rsi_14_1h_min_11 = DecimalParameter(40.0, 60.0, default=56.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_11)
    buy_rsi_14_1h_max_11 = DecimalParameter(70.0, 90.0, default=84.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_11)
    buy_rsi_11 = DecimalParameter(30.0, 48.0, default=48.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_11)
    buy_mfi_11 = DecimalParameter(36.0, 56.0, default=38.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_11)

    buy_condition_12_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_12)
    buy_condition_score_12 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)   
    buy_volume_12 = DecimalParameter(1.0, 10.0, default=1.7, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_12)
    buy_ma_offset_12 = DecimalParameter(0.93, 0.97, default=0.936, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_12)
    buy_rsi_12 = DecimalParameter(26.0, 40.0, default=30.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_12)
    buy_ewo_12 = DecimalParameter(2.0, 6.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_12)

    buy_condition_13_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_13)
    buy_condition_score_13 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_13 = DecimalParameter(1.0, 10.0, default=1.6, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_13)
    buy_ma_offset_13 = DecimalParameter(0.93, 0.98, default=0.978, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_13)
    buy_ewo_13 = DecimalParameter(-14.0, -7.0, default=-10.4, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_13)

    buy_condition_14_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_14)
    buy_condition_score_14 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_14 = DecimalParameter(1.0, 10.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_14)
    buy_ema_open_mult_14 = DecimalParameter(0.01, 0.03, default=0.014, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_14)
    buy_bb_offset_14 = DecimalParameter(0.98, 1.0, default=0.986, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_14)
    buy_ma_offset_14 = DecimalParameter(0.93, 0.99, default=0.97, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_14)

    buy_condition_15_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_15)
    buy_condition_score_15 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_15 = DecimalParameter(1.0, 10.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_15)
    buy_ema_open_mult_15 = DecimalParameter(0.02, 0.04, default=0.018, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_15)
    buy_ma_offset_15 = DecimalParameter(0.93, 0.99, default=0.954, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_15)
    buy_rsi_15 = DecimalParameter(30.0, 50.0, default=28.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_15)
    buy_ema_rel_15 = DecimalParameter(0.97, 0.999, default=0.988, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_15)

    buy_condition_16_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_16)
    buy_condition_score_16 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_16 = DecimalParameter(1.0, 10.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_16)
    buy_ma_offset_16 = DecimalParameter(0.93, 0.97, default=0.952, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_16)
    buy_rsi_16 = DecimalParameter(26.0, 50.0, default=31.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_16)
    buy_ewo_16 = DecimalParameter(4.0, 8.0, default=2.8, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_16)

    buy_condition_17_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_17)
    buy_condition_score_17 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_17 = DecimalParameter(0.5, 8.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_17)
    buy_ma_offset_17 = DecimalParameter(0.93, 0.98, default=0.958, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_17)
    buy_ewo_17 = DecimalParameter(-18.0, -10.0, default=-12.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_17)

    buy_condition_18_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_18)
    buy_condition_score_18 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_18 = DecimalParameter(1.0, 6.0, default=2.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_18)
    buy_rsi_18 = DecimalParameter(16.0, 32.0, default=26.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_18)
    buy_bb_offset_18 = DecimalParameter(0.98, 1.0, default=0.982, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_18)

    buy_condition_19_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_19)
    buy_condition_score_19 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_rsi_14_1h_min_19 = DecimalParameter(40.0, 70.0, default=65.3, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_19) 
    buy_chop_min_19 = DecimalParameter(20.0, 60.0, default=58.2, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_19) 

    buy_condition_20_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_20)
    buy_condition_score_20 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_20 = DecimalParameter(0.5, 6.0, default=1.2, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_20)
    buy_rsi_20 = DecimalParameter(20.0, 36.0, default=26.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_20)
    buy_rsi_14_1h_20 = DecimalParameter(14.0, 30.0, default=20.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_20)

    buy_condition_21_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_21)
    buy_condition_score_21 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_volume_21 = DecimalParameter(0.5, 6.0, default=3.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_21)
    buy_rsi_21 = DecimalParameter(10.0, 28.0, default=23.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_21)
    buy_rsi_14_1h_21 = DecimalParameter(18.0, 40.0, default=24.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_21)

    buy_condition_22_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_22)
    buy_condition_score_22 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_rsi_22 =  DecimalParameter(10.0, 50.0, default=45.0, space='buy', decimals=1, load=True, optimize=buy_should_optimize_condition_22) 
    buy_ewo_high_22 = DecimalParameter(2.000, 3.000, default=2.327, space='buy', decimals=3, load=True, optimize=buy_should_optimize_condition_22) 

    buy_condition_23_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_23)
    buy_condition_score_23 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_multi_offset_low_offset_sma = DecimalParameter(0.9, 0.99, default=0.955, load=True, space='buy', optimize=buy_should_optimize_condition_23) 
    
    buy_condition_24_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_24)
    buy_condition_score_24 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)   
    buy_multi_offset_low_offset_ema = DecimalParameter(0.9, 0.99, default=0.929, load=True, space='buy', optimize=buy_should_optimize_condition_24) 
    
    buy_condition_25_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_25)
    buy_condition_score_25 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_multi_offset_low_offset_trima = DecimalParameter(0.9, 0.99, default=0.949, load=True, space='buy', optimize=buy_should_optimize_condition_25) 
    
    buy_condition_26_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_26)
    buy_condition_score_26 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_multi_offset_low_offset_t3 = DecimalParameter(0.9, 0.99, default=0.975, load=True, space='buy', optimize=buy_should_optimize_condition_26) 
    
    buy_condition_27_enable = CategoricalParameter([True, False], default=True, space='buy', load=True, optimize=buy_should_optimize_condition_27)
    buy_condition_score_27 = IntParameter(0, 5, default=1, load=True, space='buy', optimize=buy_should_optimize_scores)
    buy_multi_offset_low_offset_kama = DecimalParameter(0.9, 0.99, default=0.972, load=True, space='buy', optimize=buy_should_optimize_condition_27) 
 
    buy_multi_offset_base_nb_candles_buy = IntParameter(5, 80, default=72, load=True, space='buy', optimize=buy_should_optimize_condition_common)  
    

    order_types = {
        'buy': 'market',
        'sell': 'market',
        'trailing_stop_loss': 'market',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    minimal_roi = {
        "0": 0.213,
        "39": 0.103,
        "96": 0.037,
        "166": 0
    }

    plot_config = {
        'main_plot': {
            'bb_lowerband_20_1': {'color': 'blue'},
            'bb_middleband_20_1': {'color': 'orange'},
            'bb_upperband_20_1': {'color': 'blue'},
            'bb_lowerband_20_2': {'color': 'blue'},
            'bb_middleband_20_2': {'color': 'orange'},
            'bb_upperband_20_2': {'color': 'blue'},
            'bb_lowerband_20_1_1h': {'color': 'blue'},
            'bb_middleband_20_1_1h': {'color': 'orange'},
            'bb_upperband_20_1_1h': {'color': 'blue'},
            'bb_lowerband_20_2_1h': {'color': 'blue'},
            'bb_middleband_20_2_1h': {'color': 'orange'},
            'bb_upperband_20_2_1h': {'color': 'blue'},
        },
    }

    custom_trade_info = {}


    @property
    def protections(self):
        return  [
            {
                "method": "MaxDrawdown",
                "lookback_period": 1440, # 24h
                "trade_limit": 1,
                "stop_duration": 720, # 12h
                "max_allowed_drawdown": self.protections_max_drawdown_max_allowed_drawdown.value # % of account
            }
        ]


    def custom_sell(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float, current_profit: float, **kwargs):

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        sell_reason = None

        if (last_candle is not None):

            if ((current_profit > 0.0) 
                & (last_candle['close'] > last_candle['bb_middleband_20_2_1h'])
            ):
                sell_reason = 'bb_middleband_20_2_1h_win'

            elif ((current_profit < 0.0) 
                & (last_candle['close'] > last_candle['bb_middleband_20_2_1h'])
            ):
                sell_reason = 'bb_middleband_20_2_1h_loss'

        return sell_reason


    def informative_pairs(self):

        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.inf_1h) for pair in pairs]
        return informative_pairs


    def informative_1h_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        assert self.dp, "DataProvider is required for multiple timeframes."
        
        informative_1h = self.dp.get_pair_dataframe(pair=metadata['pair'], timeframe=self.inf_1h)

        informative_1h['ema_15'] = ta.EMA(informative_1h, timeperiod=15)
        informative_1h['ema_50'] = ta.EMA(informative_1h, timeperiod=50)
        informative_1h['ema_100'] = ta.EMA(informative_1h, timeperiod=100)
        informative_1h['ema_200'] = ta.EMA(informative_1h, timeperiod=200)

        informative_1h['sma_200'] = ta.SMA(informative_1h, timeperiod=200)

        informative_1h['rsi_14'] = ta.RSI(informative_1h, timeperiod=14)

        bb_20_1 = qtpylib.bollinger_bands(qtpylib.typical_price(informative_1h), window=20, stds=1)
        informative_1h['bb_lowerband_20_1'] = bb_20_1['lower']
        informative_1h['bb_middleband_20_1'] = bb_20_1['mid']
        informative_1h['bb_upperband_20_1'] = bb_20_1['upper']

        bb_20_2 = qtpylib.bollinger_bands(qtpylib.typical_price(informative_1h), window=20, stds=2)
        informative_1h['bb_lowerband_20_2'] = bb_20_2['lower']
        informative_1h['bb_middleband_20_2'] = bb_20_2['mid']
        informative_1h['bb_upperband_20_2'] = bb_20_2['upper']

        informative_1h['protection_pump_24'] = (
            (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / informative_1h['close'].rolling(24).min()) < self.buy_guard_pump_24h_threshold_1.value) 
            | (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / self.buy_guard_pump_24h_pull_threshold_1.value) > (informative_1h['close'] - informative_1h['close'].rolling(24).min()))
        )
        informative_1h['protection_pump_36'] = (
            (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / informative_1h['close'].rolling(36).min()) < self.buy_guard_pump_36h_threshold_2.value) 
            | (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / self.buy_guard_pump_36h_pull_threshold_2.value) > (informative_1h['close'] - informative_1h['close'].rolling(36).min()))
        )
        informative_1h['protection_pump_48'] = (
            (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / informative_1h['close'].rolling(48).min()) < self.buy_guard_pump_48h_threshold_3.value) 
            | (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / self.buy_guard_pump_48h_pull_threshold_3.value) > (informative_1h['close'] - informative_1h['close'].rolling(48).min()))
        )
        informative_1h['protection_pump_24_strict'] = (
            (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / informative_1h['close'].rolling(24).min()) < self.buy_guard_pump_24h_strict_threshold_4.value) 
            | (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / self.buy_guard_pump_24h_strict_pull_threshold_4.value) > (informative_1h['close'] - informative_1h['close'].rolling(24).min()))
        )
        informative_1h['protection_pump_36_strict'] = (
            (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / informative_1h['close'].rolling(36).min()) < self.buy_guard_pump_36h_strict_threshold_5.value) 
            | (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / self.buy_guard_pump_36h_strict_pull_threshold_5.value) > (informative_1h['close'] - informative_1h['close'].rolling(36).min()))
        )
        informative_1h['protection_pump_48_strict'] = (
            (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / informative_1h['close'].rolling(48).min()) < self.buy_guard_pump_48h_strict_threshold_6.value) 
            | (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / self.buy_guard_pump_48h_strict_pull_threshold_6.value) > (informative_1h['close'] - informative_1h['close'].rolling(48).min()))
        )
        informative_1h['protection_pump_24_loose'] = (
            (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / informative_1h['close'].rolling(24).min()) < self.buy_guard_pump_24h_loose_threshold_7.value) 
            | (((informative_1h['open'].rolling(24).max() - informative_1h['close'].rolling(24).min()) / self.buy_guard_pump_24h_loose_pull_threshold_7.value) > (informative_1h['close'] - informative_1h['close'].rolling(24).min()))
        )
        informative_1h['protection_pump_36_loose'] = (
            (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / informative_1h['close'].rolling(36).min()) < self.buy_guard_pump_36h_loose_threshold_8.value) 
            | (((informative_1h['open'].rolling(36).max() - informative_1h['close'].rolling(36).min()) / self.buy_guard_pump_36h_loose_pull_threshold_8.value) > (informative_1h['close'] - informative_1h['close'].rolling(36).min()))
        )
        informative_1h['protection_pump_48_loose'] = (
            (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / informative_1h['close'].rolling(48).min()) < self.buy_guard_pump_48h_loose_threshold_9.value) 
            | (((informative_1h['open'].rolling(48).max() - informative_1h['close'].rolling(48).min()) / self.buy_guard_pump_48h_loose_pull_threshold_9.value) > (informative_1h['close'] - informative_1h['close'].rolling(48).min()))
        )

        return informative_1h


    def normal_tf_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        bb_40_2 = qtpylib.bollinger_bands(dataframe['close'], window=40, stds=2)
        dataframe['bb_lowerband_40_2'] = bb_40_2['lower']
        dataframe['bb_middleband_40_2'] = bb_40_2['mid']
        dataframe['bb_upperband_40_2'] = bb_40_2['upper']
        dataframe['bbdelta'] = (bb_40_2['mid'] - bb_40_2['lower']).abs()
        dataframe['closedelta'] = (dataframe['close'] - dataframe['close'].shift()).abs()
        dataframe['tail'] = (dataframe['close'] - dataframe['low']).abs()

        bb_20_1 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband_20_1'] = bb_20_1['lower']
        dataframe['bb_middleband_20_1'] = bb_20_1['mid']
        dataframe['bb_upperband_20_1'] = bb_20_1['upper']

        bb_20_2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband_20_2'] = bb_20_2['lower']
        dataframe['bb_middleband_20_2'] = bb_20_2['mid']
        dataframe['bb_upperband_20_2'] = bb_20_2['upper']

        dataframe['ema_14'] = ta.EMA(dataframe['close'], timeperiod = 14)
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        dataframe['ema_50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema_100'] = ta.EMA(dataframe, timeperiod=100)
        dataframe['ema_200'] = ta.EMA(dataframe, timeperiod=200)
                 
        dataframe['sma_9'] = ta.SMA(dataframe, timeperiod=9)
        dataframe['sma_30'] = ta.SMA(dataframe, timeperiod=30)
        dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)

        dataframe['sma_200_dec'] = dataframe['sma_200'] < dataframe['sma_200'].shift(20)

        dataframe['mfi_14'] = ta.MFI(dataframe)

        dataframe['ewo_x'] = EWO(dataframe, self.buy_guard_fast_ewo.value, self.buy_guard_slow_ewo.value)

        dataframe['rsi_14'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_4'] = ta.RSI(dataframe, timeperiod=4)
        dataframe['rsi_20'] = ta.RSI(dataframe, timeperiod=20)

        dataframe['chop_14']= qtpylib.chopiness(dataframe, 14)

        dataframe['protection_dips'] = (
            (((dataframe['open'] - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_normal_threshold_1.value) &
            (((dataframe['open'].rolling(2).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_normal_threshold_2.value) &
            (((dataframe['open'].rolling(12).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_normal_threshold_3.value) &
            (((dataframe['open'].rolling(144).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_normal_threshold_4.value)
        )

        dataframe['protection_dips_strict'] = (
            (((dataframe['open'] - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_strict_threshold_5.value) &
            (((dataframe['open'].rolling(2).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_strict_threshold_6.value) &
            (((dataframe['open'].rolling(12).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_strict_threshold_7.value) &
            (((dataframe['open'].rolling(144).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_strict_threshold_8.value)
        )

        dataframe['protection_dips_loose'] = (
            (((dataframe['open'] - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_loose_threshold_9.value) &
            (((dataframe['open'].rolling(2).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_loose_threshold_10.value) &
            (((dataframe['open'].rolling(12).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_loose_threshold_11.value) &
            (((dataframe['open'].rolling(144).max() - dataframe['close']) / dataframe['close']) < self.buy_guard_dip_loose_threshold_12.value)
        )

        dataframe['volume_mean_4'] = dataframe['volume'].rolling(4).mean().shift(1)
        dataframe['volume_mean_30'] = dataframe['volume'].rolling(30).mean()

        dataframe['sma_offset_buy'] = (ta.SMA(dataframe, self.buy_multi_offset_base_nb_candles_buy.value) * self.buy_multi_offset_low_offset_sma.value)
        dataframe['ema_offset_buy'] = (ta.EMA(dataframe, self.buy_multi_offset_base_nb_candles_buy.value) * self.buy_multi_offset_low_offset_ema.value)
        dataframe['trima_offset_buy'] = (ta.TRIMA(dataframe, self.buy_multi_offset_base_nb_candles_buy.value) * self.buy_multi_offset_low_offset_trima.value)
        dataframe['t3_offset_buy'] = (ta.T3(dataframe, self.buy_multi_offset_base_nb_candles_buy.value) * self.buy_multi_offset_low_offset_t3.value)
        dataframe['kama_offset_buy'] = (ta.KAMA(dataframe, self.buy_multi_offset_base_nb_candles_buy.value) * self.buy_multi_offset_low_offset_kama.value)

        return dataframe


    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        informative_1h = self.informative_1h_indicators(dataframe, metadata)
        dataframe = merge_informative_pair(dataframe, informative_1h, self.timeframe, self.inf_1h, ffill=True)       
        dataframe = self.normal_tf_indicators(dataframe, metadata)
 
        return dataframe


    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        conditions = []

        dataframe.loc[:, 'buy_tag'] = ''
        dataframe.loc[:, 'buy_condition_score_sum'] = 0

        dataframe['buy_condition_1'] = (
            (
                self.buy_condition_1_enable.value &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['sma_200'] > dataframe['sma_200'].shift(50)) &

                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_1h']) &

                (((dataframe['close'] - dataframe['open'].rolling(36).min()) / dataframe['open'].rolling(36).min()) > self.buy_min_inc_1.value) &
                (dataframe['rsi_14_1h'] > self.buy_rsi_14_1h_min_1.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_max_1.value) &
                (dataframe['rsi_14'] < self.buy_rsi_1.value) &
                (dataframe['mfi_14'] < self.buy_mfi_1.value) &

                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_1'], 'buy_tag'] += '1 '
        dataframe.loc[dataframe['buy_condition_1'], 'buy_condition_score_sum'] += self.buy_condition_score_1.value

        dataframe['buy_condition_2'] = (
            (
                self.buy_condition_2_enable.value &

                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(50)) &
                (dataframe['protection_pump_24_strict_1h']) &
                (dataframe['volume_mean_4'] * self.buy_volume_2.value > dataframe['volume']) &
                (dataframe['rsi_14_1h'] > self.buy_rsi_14_1h_min_2.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_max_2.value) &
                (dataframe['rsi_14'] < dataframe['rsi_14_1h'] - self.buy_rsi_14_1h_diff_2.value) &
                (dataframe['mfi_14'] < self.buy_mfi_2.value) &
                (dataframe['close'] < (dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_2.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_2'], 'buy_tag'] += '2 '
        dataframe.loc[dataframe['buy_condition_2'], 'buy_condition_score_sum'] += self.buy_condition_score_2.value

        dataframe['buy_condition_3'] = (
            (
                self.buy_condition_3_enable.value &

                (dataframe['close'] > (dataframe['ema_200_1h'] * self.buy_ema_rel_3.value)) &
                (dataframe['ema_100'] > dataframe['ema_200']) &
                (dataframe['ema_100_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_pump_36_strict_1h']) &
                dataframe['bb_lowerband_40_2'].shift().gt(0) &
                dataframe['bbdelta'].gt(dataframe['close'] * self.buy_bb40_bbdelta_close_3.value) &
                dataframe['closedelta'].gt(dataframe['close'] * self.buy_bb40_closedelta_close_3.value) &
                dataframe['tail'].lt(dataframe['bbdelta'] * self.buy_bb40_tail_bbdelta_3.value) &
                dataframe['close'].lt(dataframe['bb_lowerband_40_2'].shift()) &
                dataframe['close'].le(dataframe['close'].shift()) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_3'], 'buy_tag'] += '3 '
        dataframe.loc[dataframe['buy_condition_3'], 'buy_condition_score_sum'] += self.buy_condition_score_3.value

        dataframe['buy_condition_4'] = (
            (
                self.buy_condition_4_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_1h']) &
                (dataframe['close'] < dataframe['ema_50']) &
                (dataframe['close'] < self.buy_bb20_close_bblowerband_4.value * dataframe['bb_lowerband_20_2']) &
                (dataframe['volume'] < (dataframe['volume_mean_30'].shift(1) * self.buy_bb20_volume_4.value))
            )
        )
        dataframe.loc[dataframe['buy_condition_4'], 'buy_tag'] += '4 '
        dataframe.loc[dataframe['buy_condition_4'], 'buy_condition_score_sum'] += self.buy_condition_score_4.value

        dataframe['buy_condition_5'] = (
            (
                self.buy_condition_5_enable.value &

                (dataframe['ema_100'] > dataframe['ema_200']) &
                (dataframe['close'] > (dataframe['ema_200_1h'] * self.buy_ema_rel_5.value)) &
                (dataframe['protection_dips']) &
                (dataframe['protection_pump_36_strict_1h']) &
                (dataframe['ema_26'] > dataframe['ema_12']) &
                ((dataframe['ema_26'] - dataframe['ema_12']) > (dataframe['open'] * self.buy_ema_open_mult_5.value)) &
                ((dataframe['ema_26'].shift() - dataframe['ema_12'].shift()) > (dataframe['open'] / 100)) &
                (dataframe['close'] < (dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_5.value)) &

                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_5'], 'buy_tag'] += '5 '
        dataframe.loc[dataframe['buy_condition_5'], 'buy_condition_score_sum'] += self.buy_condition_score_5.value

        dataframe['buy_condition_6'] = (
            (
                self.buy_condition_6_enable.value &

                (dataframe['ema_100_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_loose']) &
                (dataframe['protection_pump_36_strict_1h']) &
                (dataframe['ema_26'] > dataframe['ema_12']) &
                ((dataframe['ema_26'] - dataframe['ema_12']) > (dataframe['open'] * self.buy_ema_open_mult_6.value)) &
                ((dataframe['ema_26'].shift() - dataframe['ema_12'].shift()) > (dataframe['open'] / 100)) &
                (dataframe['close'] < (dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_6.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_6'], 'buy_tag'] += '6 '
        dataframe.loc[dataframe['buy_condition_6'], 'buy_condition_score_sum'] += self.buy_condition_score_6.value

        dataframe['buy_condition_7'] = (
            (
                self.buy_condition_7_enable.value &

                (dataframe['ema_100'] > dataframe['ema_200']) &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_strict']) &
                (dataframe['volume'].rolling(4).mean() * self.buy_volume_7.value > dataframe['volume']) &
                (dataframe['ema_26'] > dataframe['ema_12']) &
                ((dataframe['ema_26'] - dataframe['ema_12']) > (dataframe['open'] * self.buy_ema_open_mult_7.value)) &
                ((dataframe['ema_26'].shift() - dataframe['ema_12'].shift()) > (dataframe['open'] / 100)) &
                (dataframe['rsi_14'] < self.buy_rsi_7.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_7'], 'buy_tag'] += '7 '
        dataframe.loc[dataframe['buy_condition_7'], 'buy_condition_score_sum'] += self.buy_condition_score_7.value

        dataframe['buy_condition_8'] = (
            (
                self.buy_condition_8_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_loose']) &
                (dataframe['protection_pump_24_1h']) &
                (dataframe['rsi_14'] < self.buy_rsi_8.value) &
                (dataframe['volume'] > (dataframe['volume'].shift(1) * self.buy_volume_8.value)) &
                (dataframe['close'] > dataframe['open']) &
                ((dataframe['close'] - dataframe['low']) > ((dataframe['close'] - dataframe['open']) * self.buy_tail_diff_8.value)) &

                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_8'], 'buy_tag'] += '8 '
        dataframe.loc[dataframe['buy_condition_8'], 'buy_condition_score_sum'] += self.buy_condition_score_8.value

        dataframe['buy_condition_9'] = (
            (
                self.buy_condition_9_enable.value &

                (dataframe['ema_50'] > dataframe['ema_200']) &
                (dataframe['ema_100'] > dataframe['ema_200']) &
                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_loose_1h']) &
                (dataframe['volume_mean_4'] * self.buy_volume_9.value > dataframe['volume']) &
                (dataframe['close'] < dataframe['ema_20'] * self.buy_ma_offset_9.value) &
                (dataframe['close'] < dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_9.value) &
                (dataframe['rsi_14_1h'] > self.buy_rsi_14_1h_min_9.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_max_9.value) &
                (dataframe['mfi_14'] < self.buy_mfi_9.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_9'], 'buy_tag'] += '9 '
        dataframe.loc[dataframe['buy_condition_9'], 'buy_condition_score_sum'] += self.buy_condition_score_9.value

        dataframe['buy_condition_10'] = (
            (
                self.buy_condition_10_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_100_1h']) &
                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(24)) &
                (dataframe['protection_dips_loose']) &
                (dataframe['protection_pump_24_loose_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_10.value) > dataframe['volume']) &
                (dataframe['close'] < dataframe['sma_30'] * self.buy_ma_offset_10.value) &
                (dataframe['close'] < dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_10.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_10.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_10'], 'buy_tag'] += '10 '
        dataframe.loc[dataframe['buy_condition_10'], 'buy_condition_score_sum'] += self.buy_condition_score_10.value

        dataframe['buy_condition_11'] = (
            (
                self.buy_condition_11_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_100_1h']) &
                (dataframe['protection_dips_loose']) &
                (dataframe['protection_pump_24_loose_1h']) &
                (dataframe['protection_pump_36_1h']) &
                (dataframe['protection_pump_48_loose_1h']) &
                (((dataframe['close'] - dataframe['open'].rolling(36).min()) / dataframe['open'].rolling(36).min()) > self.buy_min_inc_11.value) &
                (dataframe['close'] < dataframe['sma_30'] * self.buy_ma_offset_11.value) &
                (dataframe['rsi_14_1h'] > self.buy_rsi_14_1h_min_11.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_max_11.value) &
                (dataframe['rsi_14'] < self.buy_rsi_11.value) &
                (dataframe['mfi_14'] < self.buy_mfi_11.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_11'], 'buy_tag'] += '11 '
        dataframe.loc[dataframe['buy_condition_11'], 'buy_condition_score_sum'] += self.buy_condition_score_11.value

        dataframe['buy_condition_12'] = (
            (
                self.buy_condition_12_enable.value &

                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(24)) &
                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_12.value) > dataframe['volume']) &
                (dataframe['close'] < dataframe['sma_30'] * self.buy_ma_offset_12.value) &
                (dataframe['ewo_x'] > self.buy_ewo_12.value) &
                (dataframe['rsi_14'] < self.buy_rsi_12.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_12'], 'buy_tag'] += '12 '
        dataframe.loc[dataframe['buy_condition_12'], 'buy_condition_score_sum'] += self.buy_condition_score_12.value

        dataframe['buy_condition_13'] = (
            (
                self.buy_condition_13_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_100_1h']) &
                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(24)) &
                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_loose_1h']) &
                (dataframe['protection_pump_36_loose_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_13.value) > dataframe['volume']) &
                (dataframe['close'] < dataframe['sma_30'] * self.buy_ma_offset_13.value) &
                (dataframe['ewo_x'] < self.buy_ewo_13.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_13'], 'buy_tag'] += '13 '
        dataframe.loc[dataframe['buy_condition_13'], 'buy_condition_score_sum'] += self.buy_condition_score_13.value

        dataframe['buy_condition_14'] = (
            (
                self.buy_condition_14_enable.value &

                (dataframe['sma_200'] > dataframe['sma_200'].shift(30)) &
                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(50)) &
                (dataframe['protection_dips_loose']) &
                (dataframe['protection_pump_24_1h']) &
                (dataframe['volume_mean_4'] * self.buy_volume_14.value > dataframe['volume']) &
                (dataframe['ema_26'] > dataframe['ema_12']) &
                ((dataframe['ema_26'] - dataframe['ema_12']) > (dataframe['open'] * self.buy_ema_open_mult_14.value)) &
                ((dataframe['ema_26'].shift() - dataframe['ema_12'].shift()) > (dataframe['open'] / 100)) &
                (dataframe['close'] < (dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_14.value)) &
                (dataframe['close'] < dataframe['ema_20'] * self.buy_ma_offset_14.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_14'], 'buy_tag'] += '14 '
        dataframe.loc[dataframe['buy_condition_14'], 'buy_condition_score_sum'] += self.buy_condition_score_14.value

        dataframe['buy_condition_15'] = (
            (
                self.buy_condition_15_enable.value &

                (dataframe['close'] > dataframe['ema_200_1h'] * self.buy_ema_rel_15.value) &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips']) &
                (dataframe['protection_pump_36_strict_1h']) &
                (dataframe['ema_26'] > dataframe['ema_12']) &
                ((dataframe['ema_26'] - dataframe['ema_12']) > (dataframe['open'] * self.buy_ema_open_mult_15.value)) &
                ((dataframe['ema_26'].shift() - dataframe['ema_12'].shift()) > (dataframe['open'] / 100)) &
                (dataframe['rsi_14'] < self.buy_rsi_15.value) &
                (dataframe['close'] < dataframe['ema_20'] * self.buy_ma_offset_15.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_15'], 'buy_tag'] += '15 '
        dataframe.loc[dataframe['buy_condition_15'], 'buy_condition_score_sum'] += self.buy_condition_score_15.value

        dataframe['buy_condition_16'] = (
            (
                self.buy_condition_16_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_strict_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_16.value) > dataframe['volume']) &
                (dataframe['close'] < dataframe['ema_20'] * self.buy_ma_offset_16.value) &
                (dataframe['ewo_x'] > self.buy_ewo_16.value) &
                (dataframe['rsi_14'] < self.buy_rsi_16.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_16'], 'buy_tag'] += '16 '
        dataframe.loc[dataframe['buy_condition_16'], 'buy_condition_score_sum'] += self.buy_condition_score_16.value

        dataframe['buy_condition_17'] = (
            (
                self.buy_condition_17_enable.value &

                (dataframe['protection_dips_strict']) &
                (dataframe['protection_pump_24_loose_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_17.value) > dataframe['volume']) &
                (dataframe['close'] < dataframe['ema_20'] * self.buy_ma_offset_17.value) &
                (dataframe['ewo_x'] < self.buy_ewo_17.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_17'], 'buy_tag'] += '17 '
        dataframe.loc[dataframe['buy_condition_17'], 'buy_condition_score_sum'] += self.buy_condition_score_17.value

        dataframe['buy_condition_18'] = (
            (
                self.buy_condition_18_enable.value &

                (dataframe['close'] > dataframe['ema_200_1h']) &
                (dataframe['ema_100'] > dataframe['ema_200']) &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['sma_200'] > dataframe['sma_200'].shift(20)) &
                (dataframe['sma_200'] > dataframe['sma_200'].shift(44)) &
                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(36)) &
                (dataframe['sma_200_1h'] > dataframe['sma_200_1h'].shift(72)) &
                (dataframe['protection_dips']) &
                (dataframe['protection_pump_24_strict_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_18.value) > dataframe['volume']) &
                (dataframe['rsi_14'] < self.buy_rsi_18.value) &
                (dataframe['close'] < (dataframe['bb_lowerband_20_2'] * self.buy_bb_offset_18.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_18'], 'buy_tag'] += '18 '
        dataframe.loc[dataframe['buy_condition_18'], 'buy_condition_score_sum'] += self.buy_condition_score_18.value

        dataframe['buy_condition_19'] = (
            (
                self.buy_condition_19_enable.value &

                (dataframe['ema_100_1h'] > dataframe['ema_200_1h']) &
                (dataframe['sma_200'] > dataframe['sma_200'].shift(36)) &
                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips']) &
                (dataframe['protection_pump_24_1h']) &
                (dataframe['close'].shift(1) > dataframe['ema_100_1h']) &
                (dataframe['low'] < dataframe['ema_100_1h']) &
                (dataframe['close'] > dataframe['ema_100_1h']) &
                (dataframe['rsi_14_1h'] > self.buy_rsi_14_1h_min_19.value) &
                (dataframe['chop_14'] < self.buy_chop_min_19.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_19'], 'buy_tag'] += '19 '
        dataframe.loc[dataframe['buy_condition_19'], 'buy_condition_score_sum'] += self.buy_condition_score_19.value

        dataframe['buy_condition_20'] = (
            (
                self.buy_condition_20_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips']) &
                (dataframe['protection_pump_24_loose_1h']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_20.value) > dataframe['volume']) &
                (dataframe['rsi_14'] < self.buy_rsi_20.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_20.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_20'], 'buy_tag'] += '20 '
        dataframe.loc[dataframe['buy_condition_20'], 'buy_condition_score_sum'] += self.buy_condition_score_20.value

        dataframe['buy_condition_21'] = (
            (
                self.buy_condition_21_enable.value &

                (dataframe['ema_50_1h'] > dataframe['ema_200_1h']) &
                (dataframe['protection_dips_strict']) &
                ((dataframe['volume_mean_4'] * self.buy_volume_21.value) > dataframe['volume']) &
                (dataframe['rsi_14'] < self.buy_rsi_21.value) &
                (dataframe['rsi_14_1h'] < self.buy_rsi_14_1h_21.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_21'], 'buy_tag'] += '21 '
        dataframe.loc[dataframe['buy_condition_21'], 'buy_condition_score_sum'] += self.buy_condition_score_21.value
        
        dataframe['buy_condition_22'] = (
            (
                self.buy_condition_22_enable.value &

                (dataframe['sma_9'] < dataframe['ema_14']) &
                (dataframe['rsi_4'] < dataframe['rsi_20']) &
                (dataframe['rsi_4'] < 35) &
                (dataframe['rsi_4'] > 4) &
                (dataframe['ewo_x'] > self.buy_ewo_high_22.value) &
                (dataframe['close'] < dataframe['ema_14'] * 0.970) &
                (dataframe['rsi_14'] < self.buy_rsi_22.value) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_22'], 'buy_tag'] += '22 '
        dataframe.loc[dataframe['buy_condition_22'], 'buy_condition_score_sum'] += self.buy_condition_score_22.value
        
        dataframe['buy_condition_23'] = (
            (
                self.buy_condition_23_enable.value &

                (dataframe['close'] < dataframe['sma_offset_buy']) &
                ((dataframe['ewo_x'] < self.buy_guard_ewo_low.value) | (dataframe['ewo_x'] > self.buy_guard_ewo_high.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_23'], 'buy_tag'] += '23 '
        dataframe.loc[dataframe['buy_condition_23'], 'buy_condition_score_sum'] += self.buy_condition_score_23.value
        
        dataframe['buy_condition_24'] = (
            (
                self.buy_condition_24_enable.value &

                (dataframe['close'] < dataframe['ema_offset_buy']) &
                ((dataframe['ewo_x'] < self.buy_guard_ewo_low.value) | (dataframe['ewo_x'] > self.buy_guard_ewo_high.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_24'], 'buy_tag'] += '24 '
        dataframe.loc[dataframe['buy_condition_24'], 'buy_condition_score_sum'] += self.buy_condition_score_24.value
        
        dataframe['buy_condition_25'] = (
            (
                self.buy_condition_25_enable.value &

                (dataframe['close'] < dataframe['trima_offset_buy']) &
                ((dataframe['ewo_x'] < self.buy_guard_ewo_low.value) | (dataframe['ewo_x'] > self.buy_guard_ewo_high.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_25'], 'buy_tag'] += '25 '
        dataframe.loc[dataframe['buy_condition_25'], 'buy_condition_score_sum'] += self.buy_condition_score_25.value
        
        dataframe['buy_condition_26'] = (
            (
                self.buy_condition_26_enable.value &

                (dataframe['close'] < dataframe['t3_offset_buy']) &
                ((dataframe['ewo_x'] < self.buy_guard_ewo_low.value) | (dataframe['ewo_x'] > self.buy_guard_ewo_high.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_26'], 'buy_tag'] += '26 '
        dataframe.loc[dataframe['buy_condition_26'], 'buy_condition_score_sum'] += self.buy_condition_score_26.value
        
        dataframe['buy_condition_27'] = (
            (
                self.buy_condition_27_enable.value &

                (dataframe['close'] < dataframe['kama_offset_buy']) &
                ((dataframe['ewo_x'] < self.buy_guard_ewo_low.value) | (dataframe['ewo_x'] > self.buy_guard_ewo_high.value)) &
                (dataframe['volume'] > 0)
            )
        )
        dataframe.loc[dataframe['buy_condition_27'], 'buy_tag'] += '27 '
        dataframe.loc[dataframe['buy_condition_27'], 'buy_condition_score_sum'] += self.buy_condition_score_27.value

        conditions.append(
            (dataframe['buy_condition_score_sum'] >= self.buy_min_score.value)
            & (dataframe['close'] < dataframe['bb_middleband_20_1_1h'])
        )
            
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'
            ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(),'sell'] = 0
        return dataframe


def RMI(dataframe, *, length=20, mom=5):
    """
    Source: https://github.com/freqtrade/technical/blob/master/technical/indicators/indicators.py#L912
    """
    df = dataframe.copy()

    df['maxup'] = (df['close'] - df['close'].shift(mom)).clip(lower=0)
    df['maxdown'] = (df['close'].shift(mom) - df['close']).clip(lower=0)

    df.fillna(0, inplace=True)

    df["emaInc"] = ta.EMA(df, price='maxup', timeperiod=length)
    df["emaDec"] = ta.EMA(df, price='maxdown', timeperiod=length)

    df['RMI'] = np.where(df['emaDec'] == 0, 0, 100 - 100 / (1 + df["emaInc"] / df["emaDec"]))

    return df["RMI"]

def SSLChannels_ATR(dataframe, length=7):
    """
    SSL Channels with ATR: https://www.tradingview.com/script/SKHqWzql-SSL-ATR-channel/
    Credit to @JimmyNixx for python
    """
    df = dataframe.copy()

    df['ATR'] = ta.ATR(df, timeperiod=14)
    df['smaHigh'] = df['high'].rolling(length).mean() + df['ATR']
    df['smaLow'] = df['low'].rolling(length).mean() - df['ATR']
    df['hlv'] = np.where(df['close'] > df['smaHigh'], 1, np.where(df['close'] < df['smaLow'], -1, np.NAN))
    df['hlv'] = df['hlv'].ffill()
    df['sslDown'] = np.where(df['hlv'] < 0, df['smaHigh'], df['smaLow'])
    df['sslUp'] = np.where(df['hlv'] < 0, df['smaLow'], df['smaHigh'])

    return df['sslDown'], df['sslUp']

# Elliot Wave Oscillator
def EWO(dataframe, sma1_length=5, sma2_length=35):
    df = dataframe.copy()
    sma1 = ta.EMA(df, timeperiod=sma1_length)
    sma2 = ta.EMA(df, timeperiod=sma2_length)
    smadif = (sma1 - sma2) / df['close'] * 100
    return smadif
