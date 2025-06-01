package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.Rule;
import org.ta4j.core.indicators.RSIIndicator;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.StochasticOscillatorDIndicator;
import org.ta4j.core.indicators.StochasticOscillatorKIndicator;
import org.ta4j.core.indicators.helpers.TransformIndicator;
import org.ta4j.core.indicators.helpers.VolumeIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.rules.OverIndicatorRule;
import org.ta4j.core.rules.UnderIndicatorRule;

import java.util.Optional;

public class FreqStrategy extends BaseStrategy {

    private final Rule entryRule;
    private final Decimal size;
    private final Decimal stop;
    private final Decimal limit;


    public FreqStrategy(StrategyCreator strategyCreator, int smaPeriod, int rsiPeriod, int stochKPeriod, Decimal size, Decimal stop, Decimal limit) {
        super(strategyCreator);

        VolumeIndicator volume = new VolumeIndicator(barSeries);
        SMAIndicator sma40 = new SMAIndicator(closePrice, smaPeriod);
        RSIIndicator rsi = new RSIIndicator(closePrice, rsiPeriod);
        StochasticOscillatorKIndicator stochK = new StochasticOscillatorKIndicator(barSeries, stochKPeriod);
        StochasticOscillatorDIndicator stochD = new StochasticOscillatorDIndicator(stochK);

        entryRule = new OverIndicatorRule(closePrice, Decimal.valueOf(0.00000200)) // Preis > 0.00000200
                .and(new OverIndicatorRule(volume, new TransformIndicator(new SMAIndicator(volume, 40), d -> d.multipliedBy(DecimalNum.valueOf(4))))) // Volumen > 4x Durchschnitt
                .and(new UnderIndicatorRule(closePrice, sma40)) // Preis < SMA(40)
                .and(new OverIndicatorRule(stochD, stochK)) // Stoch-D > Stoch-K
                .and(new OverIndicatorRule(rsi, Decimal.valueOf(30))) // RSI > 30
                .and(new OverIndicatorRule(stochD, Decimal.valueOf(30))); // Stoch-D > 30


        this.size = size;
        this.stop = stop;
        this.limit = limit;
    }


    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {
        int index = barSeries.getBarCount() - 1;

        if (entryRule.isSatisfied(index)) {
            return Optional.of(
                    entrySignalFactory.fromAmount(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT, entryParameter.currentPrice())
            );
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {

        return Optional.empty();
    }

}
