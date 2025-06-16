# Trading Engine (TE)

## Umgebung auf dem Rechner einrichten

Der TE legt alle Dateien auf dem Dateisystem unter einem bestimmten Ordner `krypto-java` ab. Dieser befindet sich unter
Windows bei `C:\Users\<user>\AppData\Roaming\krypto-java` und unter Linux bei `/home/<user>/.config/krypto-java`.

Hier werden unter anderem die Krypto-Kurse, Vorhersagen, etc. abgespeichert.

Unter `https://drive.google.com/file/d/1fN5TlU3URzT8cGHEuzIoku6Bm_gNrRnN/view?usp=sharing` ist ein Ordner abgelegt,
welcher die Initiale Struktur enthält, welche für die ByBit-Backtests benötigt wird. Diesen einmal entpacken und unter
`krypto-java` ablegen. WICHTIG: `krypto-java` darf nicht doppelt im Pfad vorkommen.

Da der Ordner mit allen trainierten Modellen gezippt 34 GB hat, werde ich nur die relevanten Modelle mit in den Ordner
fügen.

## Python Installation

Poetry kann leider nicht mit Build-Tags umgehen. Dies ist aber für PyTorch mit GPU-Unterstützung relevant. Per Standard
wird deshalb PyTorch ohne GPU-Unterstützung von Poetry installiert. Falls diese benötigt wird, muss es manuell
nachinstalliert werden.

Dazu muss der Befehl `poetry run pip install torch==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121`
ausgeführt werden. Die CUDA-Version (`cu121`) muss an die des Systems angepasst werden.

## Plugin-Architektur

An mehreren stellen im TE wurde eine Plugin-Architektur verwendet, um möglichst Flexibel zu sein. Dies ist zum Beispiel
bei dem Modul `data-source` der Fall.

Im Untermodul `data-source/datasource-api` wird definiert welche Schnittstellen der TE benötigt. Die anderen Module
implementieren diese API und können dann in einer App als Maven-Dependency (Scope: Runtime) hinzugenommen werden. Der TE
lädt dann zur laufzeit über den Java `ServiceLoader` die aktuell benötigte Implementierung. So kann man auch, als
externer Benutzer ohne Maintainer des Git-Repos zu sein, sich selbst Adapter zu anderen Brokern schreiben und diese
benutzen ohne den Hauptcode anpassen zu müssen.

Module, welche diesem Prinzip folgen werden in dieser Doku mit (Plugin-Architektur) gekennzeichnet.

## Module

### Apps

Enthält alle ausführbaren Applikationen.

1. Für einen Lokalen Backtest muss die Klasse `com.becker.freelance.app.backtest.BacktestApp` unter `local-backtest-app`
   ausgeführt werden. Falls der `krypto-java` Ordner richtig eingerichtet wurde funktioniert diese App von alleine.
    1. Die Ergebnisse werden unter `krypto-java/results/<strategie-name>/` gespeichert.
2. Die Ergebnisse aus den lokalen Backtests können mit der Klasse
   `com.becker.freelance.backtest.resultviewer.app.ResultViewerApp` unter `backtest-result-viewer-app` angesehen werden.
3. Für eine Remote-Ausführung mit ByBit muss die Klasse `com.becker.freelance.app.remote.RemoteExecutionApp` unter
   `remote-execution-app` gestartet werden. Die App benötigt folgende Umgebungsvariablen (Strategien und Pairs können
   geändert werden):
    1. APPMODE=BYBIT_REMOTE_DEMO
    2. BYBIT_API_KEY=<...>
    3. BYBIT_DEMO_URL=https://api-demo.bybit.com
    4. BYBIT_SECRET=<...>
    5. PAIRS=ETHUSDT_1
    6. STRATEGIES=Best_Hard_TP_and_SL

### Trading-Strategien

In dem Modul `trading-strategies-impl/bachelor-strategies-impl` findet sich die Implementierung der Strategie für die
Regressions-KI-Modelle. (Genauere Erklärung in der Klasse
`com.becker.freelance.strategies.regression.sequence.SequenceRegressionStrategy`).

Im Modul `trading-strategies-impl/other-strategies-impl` finden sich Implementierungen von klassischen
Trading-Strategien.

### Trading-Engine

Hier befinden sich die Ausführungslogik, sowie die Adapter zu Brokern. Ich erkläre erst die weniger Interessanten Module
kurz und dann die Interessanteren ausführlicher.

1. `commons`: Allgemeine Dinge, wie zusätzliche TA-Indikatoren, Konfigurationssachen oder allgemeine Dinge zum Thema
   Trading.
2. `data-source`: Stellt eine Verbindung zu einem Broker (oder einer lokalen CSV-Datei) her und bietet somit
   Funktionalität zum Markt-Daten streamen, empfangen und abfragen (Plugin-Architektur).
3. `third-party-commons`: Allgemeines Modul für Commons um mit Remote-Brokern zu arbeiten.
4. `trading-abstract-app`: Enthält abstrakte Apps, welche vom User benutzt werden können. Aktuell ist das z.B. in `apps`
   der Fall.

#### Broker-Connectors

Das Modul enthält die Konnektoren zu Remote Brokern (Plugin-Architektur).

Für lokale Backtests wird das Modul `demo-connector` verwendet. Dieses mockt einen externen Broker und führt die Trades
aus und berechnet Gewinn und Verlust.

#### Management

Das Modul `management` (Plugin-Architektur) enthält Risiko- und Money-Management Komponenten.

Aktuell sind die Komponenten immer aktiv und können lediglich durch die Dateien unter `META-INF/services` ausgeschalten
werden (Mit # auskommentieren oder entfernen). Dies soll aber in Zukunft noch geändert werden. Die
Parameter-Konfiguration der Management-Komponenten erfolgt über Config-Dateien, welche im `resources` Ordner der
jeweiligen App abgelegt werden können.

*Adaptoren*:

Passen das Entry-Signal der Trading-Strategie nachträglich an.

1. `PositionSizeAdaptor`: Berechnet anhand der Distanz des Stop-Losses und des maximal zu riskierenden Kapitals die
   Positionsgröße.
2. `PositionTypeAdaptor`: Wandelt die Open-Order (Falls diese eine Market-Order ist) in eine Limit Order um, sodass
   Gebühren gespart werden.

*Validatoren*:

Prüfen, ob das Entry-Signal ausgeführt werden darf.

#### Strategien

Im Modul `strategies/strategies-api` (Plugin-Architektur) wird die API für die Strategien definiert. Diese werden dann
im Modul `trading-strategies-impl` implementiert.

Dort gibt es auch für jede Strategie einen Creator, welcher die Strategie bauen kann und die möglichen (zu
permutierenden) Parameter dieser angibt.

Das Modul `strategies/strategy-engine` führt Strategien, Management, Datenquellen und Tradeausführung zusammen und
koordiniert das Zusammenspiel.

Immer wenn eine neue Kerze von ankommt, wird folgender Workflow ausgeführt:

1. Offene Positionen werden angepasst, was nur für den lokalen Backtest relevant ist. Dazu gehört das Anpassen des Stops
   bei Trailing-Stop-Positionen, sowie das eventuelle Ausführen von noch offenen Limit-Orders. Dies ist Aufgabe des
   Broker-Connectors.
2. Falls bei Positionen der Take Profit oder das Stop Loss erreicht wurde, werden diese geschlossen und der
   Wallet-Betrag angepasst. Dies ist Aufgabe des Broker-Connectors.
3. Die Trading-Strategie wird gefragt, ob ein Exit passieren soll. Falls ja, wird das dem Broker-Connector mitgeteilt
   und es werden z.B. alle Short-Positionen geschlossen.
4. Die Trading-Strategie wird gefragt, obe ein Entry passieren soll. Falls ja, wird erst eine Kette von Adaptoren aus
   dem Management durchlaufen, welche das Entry-Signal nachträglich noch anpassen können. Anschließend wird das
   Entry-Signal von einigen Management-Validatoren validiert, ob es ausgeführt werden darf. Falls ja, wird das dem
   Broker-Connector mitgeteilt und dieser führt den Trade aus.

#### Execution-Engines

Der `StrategyEngine` ist Event-basiert, sodass er auch für gestreamte Daten ohne weitere Anpassungen funktioniert.

Bei einem lokalen Backtest muss das Streaming simuliert werden. Deshalb gibt es einen `StrategyDataSubscriber` welcher
das Interface `DataSubscriber` implementiert. Dieser fungiert als Observer für einen `SubscribableDataProvider`, welcher
die Daten aus einer CSV-Datei liest und alle `DataSubsciber` benachrichtigt. Um dies zu Koordinieren gibt es einen
`BacktestSynchronizer`, welcher die minimale und maximale Datumsuhrzeit des Backtests kennt und alle Daten dazwischen in
Minuten-Takt durchläuft.

## Noch Ausstehende TODOs

1. Strategien nur in bestimmten Regimen aktivierbar machen
2. Stresstesting
3. Strategien nur zu bestimmten Uhrzeiten und Wochentage aktivierbar machen