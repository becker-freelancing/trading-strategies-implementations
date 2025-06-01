package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.candles.*;
import org.ta4j.core.num.DecimalNum;

import java.util.List;
import java.util.Optional;

public class ChartPatternStrategy extends BaseStrategy {

    private static final Logger logger = LoggerFactory.getLogger(ChartPatternStrategy.class);

    private final Decimal size;
    private final Decimal stop;
    private final Decimal limit;
    private final List<Indicator<Boolean>> bullishIndicator;
    private final List<Indicator<Boolean>> bearischIndicator;


    public ChartPatternStrategy(StrategyCreator strategyCreator, Pair pair, Decimal stop, Decimal limit, Decimal size) {
        super(strategyCreator, pair);

        this.stop = stop;
        this.limit = limit;
        this.size = size;

        bullishIndicator = List.of(
                new BullishEngulfingIndicator(barSeries),
                new BullishHaramiIndicator(barSeries),
                new InvertedHammerIndicator(barSeries),
                new HammerIndicator(barSeries),
                new ThreeWhiteSoldiersIndicator(barSeries, 5, DecimalNum.valueOf(0.2))
        );

        bearischIndicator = List.of(
                new BearishEngulfingIndicator(barSeries),
                new BearishHaramiIndicator(barSeries),
                new ThreeBlackCrowsIndicator(barSeries, 5, 0.2),
                new HangingManIndicator(barSeries),
                new ShootingStarIndicator(barSeries)
        );
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

        int index = barSeries.getBarCount() - 1;
        for (Indicator<Boolean> bullish : bullishIndicator) {
            if (bullish.getValue(index)) {
                logger.info("Try to open buy position on {} bullish indicator {} is true", entryParameter.pair().technicalName(), bullish.getClass().getName());
                return Optional.of(
                        entrySignalFactory.fromDistance(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT, entryParameter.currentPrice())
                );
            }
        }

        for (Indicator<Boolean> baerish : bearischIndicator) {
            if (baerish.getValue(index)) {
                logger.info("Try to open sell position on {} baerish indicator {} is true", entryParameter.pair().technicalName(), baerish.getClass().getName());
                return Optional.of(
                        entrySignalFactory.fromDistance(size, Direction.SELL, stop, limit, PositionType.HARD_LIMIT, entryParameter.currentPrice())
                );
            }
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}
