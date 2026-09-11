# sfr-services.de

Die Webseite der SFR Services GmbH. Eine statische Informationsseite ohne
Erzeuger, ohne Abhaengigkeiten und ohne Bauschritt: was hier liegt, ist das,
was ausgeliefert wird.

## Wie sie ins Netz kommt

Ueber **GitHub Pages** aus dem Zweig `main` dieses Projekts. Ein Push
veroeffentlicht — es gibt keine Freigabestufe dazwischen, und das Ausrollen
dauert etwa eine Minute. Wer unmittelbar nach dem Push prueft, sieht noch
einen 404; das ist die Ausrollzeit, kein Fehler.

Die Datei `CNAME` bindet die Domain `sfr-services.de` an die Pages-Auslieferung.
Der DNS-Eintrag liegt bei INWX, HTTPS stellt GitHub selbst.

## Was darin steckt — und was ausdruecklich nicht

Kein Cookie, kein Analyse- oder Tracking-Dienst, kein Werbenetzwerk, keine
eingebundene Schrift und kein Skript von Dritten, kein Social-Media-Plugin.
Nichts wird im Browser gespeichert, auch kein Local Storage. Das ist keine
Zurueckhaltung, sondern die Grundlage der Datenschutzerklaerung — wer hier
etwas hinzufuegt, aendert damit auch sie.

## Zweisprachigkeit

Jede Seite fuehrt beide Sprachen im selben Dokument, in Bloecken mit
`data-i18n="de"` und `data-i18n="en"`; `lang.js` blendet um und reicht die
Wahl als Parameter in der Adresszeile weiter. **Kein Text lebt nur in einer
Sprache.** Wer einen Absatz ergaenzt, ergaenzt zwei.

## Die Seiten

| Datei | Adresse | |
|---|---|---|
| `index.html` | `/` | Startseite |
| `impressum.html` | `/impressum` | Impressum nach §5 DDG und §18 Abs. 2 MStV |
| `datenschutz.html` | `/datenschutz` | Datenschutz der **Webseite** |
| `dumpling-party/datenschutz.html` | `/dumpling-party/datenschutz` | Datenschutz der **App** |

GitHub Pages liefert jede Seite auch ohne die Endung `.html` aus; die kurze
Form ist die, die nach aussen gegeben wird.

### Die App-Seite ist bewusst nicht verlinkt

`dumpling-party/datenschutz.html` gehoert zur App „Dumpling Party", nicht zur
Firmenwebseite. Sie wird hier nur **gehostet**, weil die Domain hier liegt.
Erreichbar ist sie ueber genau zwei Wege: den Verweis aus der App, und die
Pflichtangabe in App Store Connect. Sie traegt deshalb `noindex` und steht in
keiner Fusszeile.

Getrennt gehalten wird sie, weil die beiden sehr Verschiedenes beschreiben:
die Webseite erzeugt Server-Logfiles bei GitHub, die App uebertraegt gar
nichts. Ein gemeinsamer Text muesste beides vermischen und waere fuer beide
Seiten ungenau.

## Eine Seite ergaenzen

1. Kopf und Fusszeile einer bestehenden Seite uebernehmen — sie tragen die
   Navigation, die Sprachumschaltung und `style.css`.
2. Den Inhalt in **zwei** `data-i18n`-Bloecke legen, deutsch und englisch.
3. Liegt die Seite in einem Unterordner, zeigen die Verweise auf `style.css`,
   `lang.js`, `logo.png` und die Symbole mit `../` nach oben.
4. Rechtsseiten bekommen `<meta name="robots" content="noindex, follow">`.
