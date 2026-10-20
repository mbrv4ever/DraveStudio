DraveStudio v0.5  —  een Dravenlock product
=================================================

Een lichte fotobewerker met lagen (Photoshop-achtig), in Dravenlock-stijl.
Taal: Nederlands, met automatische computertaal-detectie (omschakelbaar in
Instellingen). Gebouwd met PyQt6.


SNEL STARTEN (zonder bouwen)
----------------------------
1. Zet je 'logo.png' en 'icon.ico' in deze map (optioneel; anders tekent de
   app zelf een logo).
2. Dubbelklik 'run.bat'. De eerste keer installeert hij alles automatisch
   (kan even duren); daarna start de app meteen.


EEN .EXE BOUWEN (alles in een bestand)
--------------------------------------
1. Zet 'logo.png' en 'icon.ico' in deze map.
2. Dubbelklik 'bouw-exe.bat'.
3. Klaar -> dist\DraveStudio.exe  (een enkel bestand).


GEBRUIK
-------
Gereedschap (links): Penseel, Gum, Vullen (emmer), Pipet, Verplaatsen, Selectie,
Rechthoek, Ovaal, Lijn, Tekst. Met 'Vorm vullen' kies je gevuld of alleen
omtrek; de lijndikte volgt de penseelgrootte.
Tekst: kies het gereedschap, klik op het canvas, typ je tekst en kies lettertype
en grootte (in de huidige kleur).
Selectie: sleep een rechthoek; tekenen/gum/vullen werken dan alleen binnen
die selectie. Deselecteren met de knop, Ctrl+D of Escape.
Kies een kleur en een penseelgrootte.

Lagen (rechts): nieuwe laag, dupliceren, verwijderen, omhoog/omlaag.
Per laag: zichtbaar (vinkje), dekking en overvloeimodus. De geselecteerde
laag is de actieve laag waarop je tekent.

Onderaan: knoppen Ongedaan (↶) en Opnieuw (↷), plus zoom (➖ ➕ / 100% /
Passend). Sneltoetsen: Ctrl+Z en Ctrl+Y.

Opslaan bewaart je project mét lagen (eigen .dravestudio-bestand).
Exporteren maakt een platte PNG of JPG.


NOG TE KOMEN (volgende versies)
-------------------------------
Lasso/toverstaf-selecties, en aanpassingen/filters
(helderheid/contrast, curven, tint/verzadiging).
