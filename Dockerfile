FROM openjdk:17-jdk-slim

WORKDIR /app

COPY apps/remote-backtest-app/target/remote-backtest-app-1.0-SNAPSHOT.jar app.jar

COPY apps/remote-backtest-app/target/libs/ libs/


CMD ["java", "-cp", "app.jar:libs/*", "com.becker.freelance.app.backtest.RemoteBacktestApp"]
