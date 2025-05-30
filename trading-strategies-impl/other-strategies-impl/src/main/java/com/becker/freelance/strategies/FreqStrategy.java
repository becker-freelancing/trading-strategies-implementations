package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.Rule;
import org.ta4j.core.indicators.*;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.indicators.helpers.TransformIndicator;
import org.ta4j.core.indicators.helpers.VolumeIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.rules.OverIndicatorRule;
import org.ta4j.core.rules.UnderIndicatorRule;

import java.util.Map;
import java.util.Optional;

public class FreqStrategy extends BaseStrategy {

    public FreqStrategy() {
        super("freq_strategy", new PermutableStrategyInitParameter(FreqStrategy::stopLessThanLimit,
                new StrategyInitParameter("size", 1),//, 0.2, 1.2, 0.2),
                new StrategyInitParameter("sma", 40, 30, 50, 10),
                new StrategyInitParameter("rsi", 14, 10, 18, 4),
                new StrategyInitParameter("stochk", 14, 10, 18, 4),
                new StrategyInitParameter("macd_short", 12, 10, 14, 2),
                new StrategyInitParameter("macd_long", 26, 24, 28, 2),
                new StrategyInitParameter("ema", 9, 7, 11, 2),
                new StrategyInitParameter("minusdi", 14, 12, 16, 2),
                new StrategyInitParameter("stop", 10, 10, 40, 15),
                new StrategyInitParameter("limit", 20, 20, 60, 15)
        ));
    }

    private BarSeries series;
    private Rule entryRule;
    private Decimal size;
    private Decimal stop;
    private Decimal limit;
    private EntrySignalFactory entrySignalFactory;

    private static boolean stopLessThanLimit(Map<String, Decimal> parameters) {
        return parameters.get("limit").isLessThanOrEqualTo(parameters.get("stop"));
    }

    public FreqStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        series = new BaseBarSeries();
        ClosePriceIndicator closePrice = new ClosePriceIndicator(series);
        VolumeIndicator volume = new VolumeIndicator(series);
        SMAIndicator sma40 = new SMAIndicator(closePrice, parameters.get("sma").intValue());
        RSIIndicator rsi = new RSIIndicator(closePrice, parameters.get("rsi").intValue());
        StochasticOscillatorKIndicator stochK = new StochasticOscillatorKIndicator(series, parameters.get("stochk").intValue());
        StochasticOscillatorDIndicator stochD = new StochasticOscillatorDIndicator(stochK);
        MACDIndicator macd = new MACDIndicator(closePrice, parameters.get("macd_short").intValue(), parameters.get("macd_long").intValue());

        entryRule = new OverIndicatorRule(closePrice, Decimal.valueOf(0.00000200)) // Preis > 0.00000200
                .and(new OverIndicatorRule(volume, new TransformIndicator(new SMAIndicator(volume, 40), d -> d.multipliedBy(DecimalNum.valueOf(4))))) // Volumen > 4x Durchschnitt
                .and(new UnderIndicatorRule(closePrice, sma40)) // Preis < SMA(40)
                .and(new OverIndicatorRule(stochD, stochK)) // Stoch-D > Stoch-K
                .and(new OverIndicatorRule(rsi, Decimal.valueOf(30))) // RSI > 30
                .and(new OverIndicatorRule(stochD, Decimal.valueOf(30))); // Stoch-D > 30


        size = parameters.get("size");
        stop = parameters.get("stop");
        limit = parameters.get("limit");
        entrySignalFactory = new EntrySignalFactory();
    }


    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        int index = series.getBarCount() - 1;

        if (entryRule.isSatisfied(index)) {
            return Optional.of(
                    entrySignalFactory.fromAmount(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT, entryParameter.currentPrice())
            );
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        series.addBar(exitParameter.currentPriceAsBar());

        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new FreqStrategy(parameters);
    }
}
