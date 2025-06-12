package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
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


    public ChartPatternStrategy(StrategyParameter parameter, Decimal stop, Decimal limit, Decimal size) {
        super(parameter);

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
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int index = barSeries.getBarCount() - 1;
        for (Indicator<Boolean> bullish : bullishIndicator) {
            if (bullish.getValue(index)) {
                logger.info("Try to open buy position on {} bullish indicator {} is true", entryParameter.pair().technicalName(), bullish.getClass().getName());

                return Optional.of(entrySignalBuilder()
                        .withOpenMarketRegime(currentMarketRegime())
                        .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                        .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(entryParameter.pair()))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limit))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stop)));
            }
        }

        for (Indicator<Boolean> baerish : bearischIndicator) {
            if (baerish.getValue(index)) {
                logger.info("Try to open sell position on {} baerish indicator {} is true", entryParameter.pair().technicalName(), baerish.getClass().getName());

                return Optional.of(entrySignalBuilder()
                        .withOpenMarketRegime(currentMarketRegime())
                        .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                        .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(entryParameter.pair()))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limit))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stop)));
            }
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

}
