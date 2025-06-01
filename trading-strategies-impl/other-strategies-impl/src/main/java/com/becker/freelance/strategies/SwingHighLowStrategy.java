package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.indicators.ta.swing.SwingHighIndicator;
import com.becker.freelance.indicators.ta.swing.SwingHighPoint;
import com.becker.freelance.indicators.ta.swing.SwingLowIndicator;
import com.becker.freelance.indicators.ta.swing.SwingLowPoint;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.Indicator;

import java.util.Optional;

public class SwingHighLowStrategy extends BaseStrategy {


    private final Indicator<Optional<SwingHighPoint>> swingHighIndicator;
    private final Indicator<Optional<SwingLowPoint>> swingLowIndicator;
    private SwingHighPoint lastSwingHighOrNull;
    private SwingLowPoint lastSwingLowOrNull;
    private int index;

    public SwingHighLowStrategy(StrategyCreator strategyCreator, Pair pair, int swingPeriod) {
        super(strategyCreator, pair);

        swingHighIndicator = new SwingHighIndicator(swingPeriod, closePrice);
        swingLowIndicator = new SwingLowIndicator(swingPeriod, closePrice);
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {
            return Optional.of(entrySignalFactory.fromAmount(new Decimal("1"), Direction.SELL, new Decimal(20), new Decimal(15), PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        } else if (lastSwingLowOrNull.index() == index - 1) {
            return Optional.of(entrySignalFactory.fromAmount(new Decimal("1"), Direction.BUY, new Decimal(20), new Decimal(15), PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        updateData();

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.BUY));
        } else if (lastSwingLowOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.SELL));
        }

        return Optional.empty();
    }

    private void updateData() {
        index = barSeries.getBarCount() - 1;

        Optional<SwingLowPoint> optionalSwingLowPoint = swingLowIndicator.getValue(index);
        Optional<SwingHighPoint> optionalSwingHighPoint = swingHighIndicator.getValue(index);

        lastSwingHighOrNull = optionalSwingHighPoint.orElse(null);
        lastSwingLowOrNull = optionalSwingLowPoint.orElse(null);
    }
}
