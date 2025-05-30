package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.candles.*;
import org.ta4j.core.num.DecimalNum;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class ChartPatternStrategy extends BaseStrategy {

    private static final Logger logger = LoggerFactory.getLogger(ChartPatternStrategy.class);

    private Decimal size;
    private Decimal stop;
    private Decimal limit;
    private BarSeries barSeries;
    private List<Indicator<Boolean>> bullishIndicator;
    private List<Indicator<Boolean>> bearischIndicator;
    private EntrySignalFactory entrySignalFactory;

    public ChartPatternStrategy() {
        super("chart_pattern", new PermutableStrategyParameter(
                new StrategyParameter("size", 1, 0.02, 0.02, 0.02),
                new StrategyParameter("stop", 50, 10, 100, 15),
                new StrategyParameter("limit", 120, 10, 100, 15),
                new StrategyParameter("bw_bull", 0.1, 0.1, 3., 0.5),
                new StrategyParameter("buw_bull", 0.1, 0.1, 3., 0.5),
                new StrategyParameter("bc_bull", 10, 2, 50, 10),
                new StrategyParameter("fac_bull", 1., 0.5, 4., 1.)
        ));
    }


    public ChartPatternStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        stop = parameters.get("stop");
        limit = parameters.get("limit");
        size = parameters.get("size");

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
        entrySignalFactory = new EntrySignalFactory();
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentPrice = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentPrice);
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
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new ChartPatternStrategy(parameters);
    }
}
