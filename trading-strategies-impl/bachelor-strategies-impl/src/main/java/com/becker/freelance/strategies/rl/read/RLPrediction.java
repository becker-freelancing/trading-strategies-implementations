package com.becker.freelance.strategies.rl.read;

import java.time.LocalDateTime;

public record RLPrediction(LocalDateTime closeTime,
                           RLAction rlAction) {

}
