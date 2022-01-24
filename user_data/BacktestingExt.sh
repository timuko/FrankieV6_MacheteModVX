#!/bin/bash

# global vars
CONFIG='user_data/config-backtesting.json'
EXCHANGE='binance'
TIMEFRAME=''
startEpoch=''
endEpoch=''
START_TIMERANGE=''
LEAD_START_TIMERANGE=''
END_TIMERANGE=''
STRATEGY=''
DURATION=''
LEAD_TIME=''

# output colors
BIBlue="\033[1;94m"   # Blue
BBlue="\033[1;34m"    # Blue
Green="\033[0;32m"    # Green
BICyan="\033[1;96m"   # Cyan
Cyan="\033[0;36m"     # Cyan
BIYellow="\033[1;93m" # Yellow
ColorOff="\033[0m"    # Text Reset

function_printOutput() {
    printf "${Cyan}"
    printf "* $1\n"
    printf "${ColorOff}"
}

function_optimizeBot() {
    START_TIMERANGE=${startEpoch}
    LEAD_START_TIMERANGE=$((${START_TIMERANGE}-(60*${LEAD_TIME})))
    END_TIMERANGE=${endEpoch}

    function_printOutput "Starting Optimization"
    startDatetime=$(date -d @${START_TIMERANGE})
    leadStartDatetime=$(date -d @${LEAD_START_TIMERANGE})
    endDatetime=$(date -d @${END_TIMERANGE})

    #function_printOutput "Downloading data for timerange between ${leadStartDatetime} and ${endDatetime}" 
    docker-compose run --rm freqtrade download-data -c ${CONFIG} --exchange ${EXCHANGE} --timeframes ${TIMEFRAME} --timerange=${LEAD_START_TIMERANGE}-${END_TIMERANGE}

    function_printOutput "Backtesting initial timerange between ${startDatetime} and ${endDatetime}"
    docker-compose run --rm freqtrade backtesting -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE}  --breakdown month day --enable-protections  --export trades

    #function_printOutput "Plotting profits for timerange between ${startDatetime} and ${endDatetime}"
    #docker-compose run --rm freqtrade plot-dataframe -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE} -p BTC/USDT
    #docker-compose run --rm freqtrade plot-profit -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE} --timeframe 5m #${TIMEFRAME}

    function_printOutput "Commands to reproduce:"
    function_printOutput "- docker-compose run --rm freqtrade download-data -c ${CONFIG} --exchange ${EXCHANGE} --timeframes ${TIMEFRAME} --timerange=${LEAD_START_TIMERANGE}-${END_TIMERANGE}"
    function_printOutput "- docker-compose run --rm freqtrade backtesting -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE} --enable-protections"
    function_printOutput "Hyperopt command:"
    function_printOutput "- docker-compose run --rm freqtrade hyperopt -c ${CONFIG} --strategy ${STRATEGY} --hyperopt-loss ShortTradeDurHyperOptLoss, OnlyProfitHyperOptLoss, SharpeHyperOptLoss, SharpeHyperOptLossDaily, SortinoHyperOptLoss, SortinoHyperOptLossDaily, CalmarHyperOptLoss, MaxDrawDownHyperOptLoss --spaces buy sell roi stoploss trailing protection --timerange=${START_TIMERANGE}-${END_TIMERANGE} --disable-param-export  --enable-protections --print-all -e 100"
    function_printOutput "Etc."
    function_printOutput "- docker-compose run --rm freqtrade plot-dataframe -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE} -p ???/USDT "
    function_printOutput "- docker-compose run --rm freqtrade edge -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE}"
    function_printOutput "- docker-compose run --rm freqtrade backtesting -c ${CONFIG} --strategy-list ${STRATEGY} --timeframe ${TIMEFRAME} --timerange=${START_TIMERANGE}-${END_TIMERANGE}"
    function_printOutput "- docker-compose run --rm freqtrade plot-profit -c ${CONFIG} --strategy ${STRATEGY} --timerange=${START_TIMERANGE}-${END_TIMERANGE} --timeframe ${TIMEFRAME}"
}

function_displayHelp() {
    echo 'e.g. -s MyStrat "5m 1h" 1440 2021-01-05 22:00:00 2021-01-06 08:30:00'
    echo "--help  displays this"
}

case $1 in
    "-s")
        function_printOutput "Parameters:"

        STRATEGY=$2
        function_printOutput "- Strategy: $2"

        TIMEFRAME=$3
        function_printOutput "- Timeframe: $3"

        LEAD_TIME=$4
        function_printOutput "- Leadtime in minutes: $4"

        startDateString="$5 $6"
        startEpoch=$(date -d "${startDateString}" +"%s")
        function_printOutput "- Datetime under Test: ${startDateString}"

        endDateString="$7 $8"
        endEpoch=$(date -d "${endDateString}" +"%s")
        function_printOutput "- Datetime under Test: ${endDateString}"
        ;;
    "--help")
        function_displayHelp
        break
        ;;
    *)
        function_printOutput "invalid option, see --help"
        break
        ;;
esac
function_optimizeBot
