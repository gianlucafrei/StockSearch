# Tutorial

In diesem Tutorial lernen Sie wie man StockSearch verwendet und damit Abfragen auf die vorhandenen Aktiendaten ausführt.

## Schnellstart

In Stocksearch schrieben Sie Abfragen in der SSQL-Sprache und Stocksearch führt diese dann aus und zeigt Ihnen das Resultat an.

```all shares where value >= 10 and change since 5 days > 0```
<a href="/tryit?q=all shares where value >= 10 and change since 5 days > 0"><button>Try it</button></a>

Dieses Abfrage zeigt ihnen alle Aktien derren wert mindestens 10 ist und in den letzten fünf Tagen insgesammt an dert zugelegt haben.

## SSQL

Jetzt wo Sie Ihre erste SSQL-Abfrage durchgeführt haben schauen wir uns die verschiedenen möglichen Statements genauer an.
Stocksearch unterstützt fünf verschiedene Funktionen. Die verschiedenen Funktionen können beliebig miteinander kombiniert werden, allerdings schauen wir uns dies in einem späteren Abschnitt dieses Tutorials an.

### Funktionen

#### Value

Mit der Value funktion können Sie nach dem Wert an einem bestimmten Zeitpunkt filtern. Beispielweise liefert ihnen folgendes Statement alle Aktien die am 01.01.2017 einen Wert kleiner als 100 hatten.

```all shares where value on 01-01-2017 < 100```
<a href="/tryit?q=all shares where value on 01-01-2017 < 100"><button>Try it</button></a>

Das Datum ist dabei optional, wenn Sie keines angeben wird einfach das heutige Datum verwendet.

```all shares where value < 100```
<a href="/tryit?q=all shares where value < 100"><button>Try it</button></a>

Dieses Statement liefert Ihnen folglich alle Aktiendaten welche heute weniger als 100 wert sind.

#### Change

Mit der Change Funktion können Sie nach der Veränderung einer Aktie in einem bestimmten Zeitraum filtern.

Die Funktion kommt dabei in zwei verschiedenen varianten.

**Relative Veränderung:**

```all shares where change since 10 days > 0.1```
<a href="/tryit?q=all shares where change since 10 days > 0.1"><button>Try it</button></a>

Dieses Statement liefert Ihnen alle Aktien welche in den letzten 10 Tagen um mehr als 10% gestiegen sind. 

**Absolute Veränderung:**

Wenn Sie allerdings die absolute veränderung interessiert können Sie das absolute keywork verwenden.

```all shares where absolute change since 10 days < 100```
<a href="/tryit?q=all shares where absolute change since 10 days < 100"><button>Try it</button></a>

Dieses Statement liefert Ihnen alle Aktien derren absolute Wertzunahme, also der heutige Wert minus der Wert vor zehn Tagen, kleiner als 100 ist.

**Zeitspanne**

Die Zeitspanne können Sie auf drei verschiedene Arten angeben.

- `since x days` liefert ihnen die Zeitspanne in den letzte x Tagen
- `since yyyy-mm-dd` liefert ihnen die Zeitspanne von dem angegebenen Datum bis heute.
- `from yyyy-mm-dd to yyyy-mm-dd` giebt ihnen den Zeitraum zwischen den angegebenen Daten.

Folgende Abfragen sind also alle gültige SSQL Statements.

```all shares where change since 10 days <= 0```
<a href="/tryit?q=all shares where change since 10 days <= 0"><button>Try it</button></a>

```all shares where change since 2017-01-01 > 0```
<a href="/tryit?q=all shares where change since 2017-01-01 > 0"><button>Try it</button></a>

```all shares where change from 2017-01-01 to 2017-12-31 > 0```
<a href="/tryit?q=all shares where change from 2017-01-01 to 2017-12-31 > 0"><button>Try it</button></a>

#### Average

Mit der Average Funktion kann der durchschnittliche Wert einer Aktie in einem bestimmten Zeitraum untersucht werden. Dabei werden jeweils alle Tage gleich gewichtet. Die Angabe der Zeitspanne funktioniert wie bei der Change-Funktion.

Folgende Abfragen sind also alle gültige SSQL Statements.

```all shares where average since 100 days > 100```
<a href="/tryit?q=all shares where average since 100 days > 100"><button>Try it</button></a>

#### Variance

Die Variance Funktion gibt ein Mass zurück, wie sehr der Aktienkurs nach oben und unten geht. Damit Aktientitel mit höherem Wert nicht sofort eine höhere Varianz haben, werden alle Werte im gegebenen Zeitraum durch den Durchschnitsswert (Average-Funktion) dividiert. Die Varianz berechnet sich also folgendermasen:

```
avg = Average(wert1, wert2, ...)
v = Varianz(wert1 / avg, wert2 / avg, ...)
```

Beispiele:

```all shares where variance from 2017-01-01 to 2018-01-01 > 0.03```
<a href="/tryit?q=all shares where variance from 2017-01-01 to 2018-01-01 > 0.03"><button>Try it</button></a>

```all shares where variance > 0.1```
<a href="/tryit?q=all shares where variance > 0.1"><button>Try it</button></a>

#### Longest grow

Diese Funktioniert liefert die längste Anzahl Tage zurück in welcher eine Aktien von Tag zu Tag gestiegen ist.

Beispiele:

```all shares where longest grow > 5```
<a href="/tryit?q=all shares where longest grow > 5"><button>Try it</button></a>

```all shares where longest grow since 10 days > 2```
<a href="/tryit?q=all shares where longest grow since 10 days > 2"><button>Try it</button></a>

#### Kombinieren von Filtern

Verschiedene Filter können beliebig logisch verknüpft werden. Dazu verwenden Sie `AND` damit die Aktie beide Bedingungen erfüllen muss, oder `OR` woei entweder die eine oder andere Bedingung erfüllt werden muss.

Beispiele:

```all shares where (true OR false) OR (false AND true)```
<a href="/tryit?q=all shares where (true OR false) OR (false AND true)"><button>Try it</button></a>

```all shares where value > 10 and change since 10 days > 0```
<a href="/tryit?q=all shares where value > 10 and change since 10 days > 0"><button>Try it</button></a>