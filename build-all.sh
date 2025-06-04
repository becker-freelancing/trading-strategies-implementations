cd trading-engine || exit
mvn clean install
cd ../trading-strategies-impl || exit
mvn clean install
cd ../apps || exit
mvn clean install