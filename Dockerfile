FROM openjdk:17-jdk-slim

WORKDIR /app

COPY apps/remote-execution-app/target/remote-execution-app-1.0-SNAPSHOT.jar app.jar

COPY apps/remote-execution-app/target/libs/ libs/


CMD ["java", "-cp", "app.jar:libs/*", "com.becker.freelance.app.remote.RemoteExecutionApp"]
