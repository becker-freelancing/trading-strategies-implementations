FROM openjdk:17-jdk-slim

WORKDIR /app

COPY ../target/local-backtest-app-1.0-SNAPSHOT.jar app.jar

COPY ../target/libs/ libs/


CMD ["java", "-cp", "app.jar:libs/*", "com.becker.freelance.app.backtest.BacktestApp"]
