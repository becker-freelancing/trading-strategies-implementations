package com.becker.freelance.strategies.rl;

import java.time.LocalDateTime;

public record RLPrediction(LocalDateTime closeTime,
                           RLAction rlAction) {

}
