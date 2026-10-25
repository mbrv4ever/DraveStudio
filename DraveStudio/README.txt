DraveStudio v0.19  —  een Dravenlock product
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
Rechthoek, Ovaal, Lijn, Tekst.
Selectie-gereedschap: rechthoek, Lasso (vrije vorm) en Toverstaf (klik op een
kleur; tolerantie instelbaar links). Aanpassingen/tekenen werken binnen de selectie.
Deselecteren: knop Deselecteren, Ctrl+D, Escape, of rechterklik op het canvas. Met 'Vorm vullen' kies je gevuld of alleen
omtrek; de lijndikte volgt de penseelgrootte.
Tekst: kies het gereedschap, klik op het canvas, typ je tekst en kies lettertype,
grootte, vet en schuin (in de huidige kleur).
Selectie: sleep een rechthoek; tekenen/gum/vullen werken dan alleen binnen
die selectie. Deselecteren met de knop, Ctrl+D of Escape.
Kies een kleur en een penseelgrootte.

Lagen (rechts): nieuwe laag, dupliceren, verwijderen, omhoog/omlaag.
Per laag: zichtbaar (vinkje), dekking en overvloeimodus. De geselecteerde
laag is de actieve laag waarop je tekent.

Onderaan: knoppen Ongedaan (↶) en Opnieuw (↷), plus zoom (➖ ➕ / 100% /
Passend). Sneltoetsen: Ctrl+Z en Ctrl+Y.

Penselen (paneel links, boven Grootte): kies uit een keuzelijst met o.a.
Zacht rond, Hard rond, Krijt, Spray, Marker en vormen (Vierkant, Driehoek,
Zeshoek, Ster, Hart). Werkt ook voor de Gum.
 - 'Nieuw...': maak een eigen penseel (vorm + hardheid, tussenafstand,
   spreiding) en geef het een naam; het wordt bewaard.
 - 'Importeren...': kies een PNG als penseelvorm; deze komt in de map
   'penselen' naast de app en verschijnt in de lijst.

Aanpassingen (knop bovenin): Helderheid/Contrast, Tint/Verzadiging, Vervagen,
Verscherpen, Curven, Grijswaarden, Kleuren omkeren. Met schuiven zie je een live
voorbeeld; werkt op de actieve laag, of binnen de selectie als die er is.

Afbeelding (knop bovenin): werkt op alle lagen tegelijk, met één Ongedaan-stap.
 - Bijsnijden naar selectie: maak eerst een selectie (rechthoek, lasso of
   toverstaf); de afbeelding wordt bijgesneden tot de rechthoek eromheen.
 - 90° rechtsom / 90° linksom / 180° draaien.
 - Horizontaal / Verticaal spiegelen.

Vectormodus (SVG) — knop bovenin '✏️ Vectormodus' schakelt tussen Raster en
Vector. In vectormodus teken je objecten (geen pixels):
 - Gereedschap: Selecteren, Rechthoek, Ovaal, Lijn, Pen (pad), Tekst.
 - Stijl: vul- en lijnkleur, lijndikte, vulling/lijn aan-uit; 'Stijl op
   selectie toepassen' verandert het gekozen object.
 - Object: naar voren/achteren, verwijderen. Rechterklik = niets selecteren.
   Met de Pen klik je punten; dubbelklik of 'Pad afronden/sluiten' rondt af.
   Tekst aanpassen: dubbelklik op de tekst (of klik erop met het
   Tekst-gereedschap) om de inhoud te bewerken.
 - Vergroten/verkleinen: selecteer een object en sleep aan de witte
   grepen rondom.
 - Zoomen kan met het muiswiel op het canvas (ook in rastermodus).
 - Opslaan bewaart als .svg; Openen laadt een .svg; Exporteren rastert de
   tekening naar PNG/JPG/BMP/WEBP/TIFF/GIF/ICO.

Acties & presets (knop bovenin, 🎬 Acties): venster met tabbladen.
 - Acties: neem een reeks aanpassingen/filters op en speel ze met één klik
   af op de actieve laag. Opslaan onder een naam, hernoemen, verwijderen.
 - Looks: kant-en-klare looks (Zwart-wit, Warm, Koel, Hoog contrast...) plus
   je eigen opgeslagen looks. Eén klik = toepassen.
 - Palet: bewaar favoriete kleuren en stel ze met één klik in.
 - Penselen: beheer en importeer je eigen penselen.
 - Exporteren/Importeren: bewaar alles in één .dravepreset-bestand om te
   delen of te back-uppen.

Opslaan bewaart je project mét lagen (eigen .dravestudio-bestand).
Exporteren maakt een platte afbeelding in PNG, JPG, BMP, WEBP, TIFF, GIF of ICO.


NOG TE KOMEN (volgende versies)
-------------------------------
(de kernfuncties zijn compleet)
