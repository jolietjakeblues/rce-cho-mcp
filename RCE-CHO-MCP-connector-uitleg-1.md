RIJKSDIENST VOOR HET CULTUREEL ERFGOED 

# **De RCE CHO MCP-connector** 

### Wat het is, waarom het nodig is en hoe het werkt 

_Achtergrondnotitie · juli 2026 Opgesteld voor collega's zonder technische achtergrond_ Joop Vanderheiden 

## 1. In het kort 

De RCE CHO MCP-connector is een zelfgebouwde softwarekoppeling die een AI-assistent, bijvoorbeeld Mistral, ChatGPT of Claude, rechtstreeks toegang geeft tot de beschikbare cultureel-erfgoeddata van de Rijksdienst voor het Cultureel Erfgoed. Zonder toegang tot een externe bron werkt een taalmodel met de context uit het gesprek en met kennis uit zijn training. Het kan dan niet zelfstandig vaststellen wat op dit moment in de RCE-data staat. Met de connector kan dezelfde AI gericht vragen stellen aan het echte RCEsysteem en de antwoorden benutten voor analyses, rapportages en kaarten. 

Dit document legt uit welk probleem de connector oplost, waarom linked open data daarvoor geschikt is, hoe de verbinding werkt en welke gereedschappen beschikbaar zijn. 

## 2. Het probleem dat dit oplost 

Een taalmodel bevat geen actuele, volledige kennis van het rijksmonumentenregister of Archis. Het weet niet vanzelf welke monumenten precies zijn geregistreerd, welke gegevens daarbij horen of hoe die zich verhouden tot andere registraties. Dat is geen tekortkoming. Zulke informatie verandert voortdurend en hoort niet in het statische geheugen van een taalmodel thuis. 

De gebruikelijke werkwijze vraagt vaak om exports naar Excel, een ETL-traject of een tussenstap via GISsoftware. Elke schakel kost tijd en kan fouten introduceren. Bovendien kan een afzonderlijke gegevenskopie verouderen. 

De MCP-connector maakt veel handmatige exports en technische tussenstappen voor verkennende vragen en analyses overbodig. De AI kan de vraag rechtstreeks aan de beschikbare bron voorleggen. Voor bulkverwerking, archivering, reproduceerbare analyses en zware ruimtelijke bewerkingen kunnen exports, ETL of GIS nog steeds nodig zijn. 

## 3. Wat is het Model Context Protocol? 

Het Model Context Protocol, afgekort MCP, is een open standaard voor de communicatie tussen AItoepassingen en externe systemen. Het protocol is eind 2024 door Anthropic geïntroduceerd en eind 2025 ondergebracht bij een onafhankelijke stichting onder de Linux Foundation. 

MCP pakt het zogeheten N-maal-M-probleem aan. Zonder gezamenlijke standaard moet elke combinatie van een AI-toepassing en een databron afzonderlijk worden geprogrammeerd. Bij tien AI-toepassingen en tien databronnen kunnen zo honderd onderhoudsgevoelige koppelingen ontstaan. 

MCP spreekt één gedeelde manier af waarop een databron zich aan een AI kan presenteren: welke acties zijn mogelijk, welke gegevens zijn daarvoor nodig en welk resultaat komt terug. De vergelijking met USB helpt: vóór standaarden zoals USB had ieder apparaat zijn eigen stekker en besturingssoftware. MCP probeert voor AI-koppelingen een vergelijkbare gemeenschappelijke aansluiting te bieden. 

In de praktijk bestaat een MCP-verbinding uit twee kanten: 

- **De client:** de AI-toepassing die namens de gebruiker een vraag wil stellen, bijvoorbeeld Claude, ChatGPT of een ontwikkelomgeving. 

- **De server:** een zelfstandig programma dat een specifieke databron kan bevragen en daarvoor een menu van acties aanbiedt. Binnen MCP heten die acties tools. 

Elke tool is een vooraf ontworpen en geteste handeling, zoals een zoekopdracht uitvoeren, een telling opvragen of coördinaten omrekenen. De client hoeft niet te weten hoe de tool intern werkt. Hij moet wel de juiste tool kiezen en de benodigde parameters invullen. 

In beginsel kan iedere MCP-geschikte client dezelfde tools gebruiken. In de praktijk verschillen clients in hun ondersteuning voor verbindingen, authenticatie, rechten, limieten en presentatie van resultaten. 

MCP bevat zelf geen inhoudelijke data. Het protocol regelt alleen hoe client en server met elkaar communiceren. De inhoudelijke waarde komt uit de databronnen en uit de tools die daarop zijn gebouwd. 

#### **Kort gezegd** 

Zonder een bronkoppeling kan een AI niet zelfstandig vaststellen wat nu in het RCE-systeem staat. Met de MCP-connector kan de AI de bron tijdens het gesprek bevragen en het resultaat direct verwerken. 

## 4. Waarom dit juist op linked open data goed werkt 

Een MCP-koppeling is de transportlaag. Of een AI er zinvol mee kan werken, hangt af van de manier waarop de onderliggende data is georganiseerd. Veel open overheidsinformatie staat in pdf-bestanden, vrije tekst of spreadsheets zonder eenduidig vastgelegde betekenis. Een AI kan daar tekst uit halen, maar moet de structuur en betekenis deels afleiden. 

Bij de RCE ligt dat anders. De cultureel-erfgoeddata wordt als linked open data gepubliceerd. Objecten en begrippen krijgen een unieke identiteit, meestal in de vorm van een URI. Relaties tussen objecten liggen expliciet vast in een datamodel. Daardoor kan software niet alleen woorden herkennen, maar ook vaststellen welk object of begrip bedoeld wordt en hoe gegevens met elkaar samenhangen. 

De structuur volgt niet alleen uit lijsten met termen, definities en synoniemen. Zulke begrippenlijsten horen bij thesauri, zoals de CHT of het ABR in het landelijke Termennetwerk. De structuur van CHO wordt daarbij beschreven door een ontologie: een formeel datamodel dat vastlegt welke soorten objecten bestaan, welke eigenschappen en relaties zij kunnen hebben en welk type waarden daarbij hoort. 

Een ontologie beschrijft niet alleen de technische structuur van de data. Zij legt ook domeinkennis vast: welke soorten erfgoedobjecten en gebeurtenissen worden onderscheiden, welke relaties betekenisvol zijn en welke gevolgtrekkingen uit die relaties mogelijk zijn. De feitelijke kennis over een afzonderlijk monument staat in de data, bijvoorbeeld welke functie het heeft, bij welke gebeurtenis een datering hoort 

en van welk complex het deel uitmaakt. De ontologie bepaalt hoe die feiten betekenis krijgen en hoe software ze in samenhang kan interpreteren. 

Een triple zoals “<monument-1234> ceo:heeftMonumentnummer ‘87154563’” past dit model toe (een fictief voorbeeld, niet een bestaand monument of monumentnummer). De eigenschap ceo:heeftMonumentnummer is geen los begrip met alleen een omschrijving. Zij legt formeel vast dat een monument een monumentnummer kan hebben. Die voorspelbare structuur maakt gerichte SPARQL-vragen en controleerbare antwoorden mogelijk. 

Dit is het principe dat het project draagt en dat ook richting het management, tot en met CIO-niveau, is toegelicht: open, zorgvuldig gemodelleerde linked data vormt een belangrijke voorwaarde voor betrouwbare AI-ondersteuning. Zonder gedeelde ontologie, duurzame identificatie en bevraagbare brondata blijft een AI-koppeling sterk afhankelijk van losse tekst en interpretatie. 

## 5. Drie koppelingen, drie databronnen 

Er zijn drie zelfgebouwde MCP-verbindingen actief. Ze volgen hetzelfde basisprincipe, maar blijven bewust van elkaar gescheiden. Elke bron heeft eigen technische kenmerken, releases en foutscenario's. Kleine connectors zijn eenvoudiger te bouwen, testen en onderhouden dan één grote koppeling waarin alle bronlogica verweven raakt. 

##### **INTERNE BRON** 

#### **RCE CHO MCP-connector** 

Deze connector staat centraal in dit document. Hij richt zich op de cultureel-erfgoeddata van de RCE, waaronder rijksmonumenten en andere cultuurhistorische objecten. 

##### **EXTERNE BRONNEN** 

#### **NL-GOV-MCP** 

NL-GOV-MCP, ook aangeduid als NL-MCP, ontsluit verschillende Nederlandse overheidsbronnen via een uniforme interface. Voorbeelden zijn de Basisregistratie Adressen en Gebouwen, energielabelgegevens uit EP-Online, cijfers van het CBS, weergegevens van het KNMI en documenten van de Tweede Kamer. Hierdoor kunnen gegevens uit meerdere bronnen binnen één vraag worden geraadpleegd en gecombineerd. 

#### **Kadaster MCP** 

De Kadaster MCP-connector verbindt met de Kadaster Kennisgraaf. Deze bron bevat onder meer perceelen beperkingengegevens en vormt een aanvulling op de RCE-data. Een toepassing is het vergelijken van rijksmonumenten met kadastrale beperkingenregistraties. 

Voor de gebruiker kunnen de drie connectors als één samenhangend geheel aanvoelen. Een AI-client kan tijdens één gesprek tussen de bronnen schakelen, afhankelijk van de vraag en van de beschikbare tools. 

## 6. De RCE CHO MCP-connector nader bekeken 

De connector is zelf ontwikkeld en online gehost op Render. De broncode is openbaar in te zien op GitHub, zodat anderen de werking kunnen bekijken. 

CHO staat voor ‘cultuurhistorisch object’: de gedeelde, domeinneutrale aanduiding voor het object waarover de RCE publiceert — een rijksmonument, een archeologische vondst, een vondstlocatie, een complex of een archeologisch onderzoeksgebied, ongeacht of dat object nu vanuit de archeologie, het gebouwde erfgoed, het landschap of het roerend erfgoed wordt beschreven. De gegevens over die objecten worden gepubliceerd in de dataset CHO-KENNIS, onderdeel van de Linked Data Voorziening (LDV) van de RCE. 

De structuur en betekenis van die gegevens worden bepaald door de Cultureel Erfgoed Ontologie, afgekort CEO. Deze ontologie beschrijft welke soorten objecten worden onderscheiden, zoals Monument, Gebeurtenis en Complex, en welke eigenschappen en relaties mogelijk zijn. Voorbeelden zijn een monumentnummer, een functie, een datering of een relatie met een gemeente. 

Technisch bestaat de dataset uit miljoenen verbonden feiten, triples genoemd. Iedere triple heeft een onderwerp, een relatie en een waarde of ander object. Samen vormen deze triples een kennisgraaf. SPARQL is de vraagtaal waarmee die graaf wordt bevraagd, vergelijkbaar met de rol van SQL bij tabelvormige databases. 

## 7. Hoe werkt het, stap voor stap 

1. Een gebruiker stelt in gewone taal een vraag aan een AI-client, bijvoorbeeld: “Hoeveel rijksmonumenten staan er in Gouda zonder energielabel?” 

2. De AI kiest een passende tool en vult de benodigde parameters in. 

3. Afhankelijk van de tool bouwt de connector de technische zoekopdracht op of voert hij een aangeleverde SPARQL-query uit. 

4. De connector stuurt de zoekopdracht naar de beschikbare RCE-server of, wanneer de vraag daarom vraagt, naar een andere gekoppelde bron. 

5. De bron verwerkt de zoekopdracht en stuurt het resultaat terug. 

6. De connector geeft het resultaat door aan de AI-client, die het kan vertalen naar een leesbaar antwoord, een tabel, een rapport of een kaart. 

De connector houdt geen afzonderlijke lokale kopie van de volledige brondata bij. Een vraag wordt rechtstreeks aan de beschikbare bron voorgelegd. Het antwoord weerspiegelt daardoor de stand van die bron op het moment van bevragen, rekening houdend met de beschikbaarheid en actualisering van de bron zelf. 

## 8. De tools van de RCE CHO-connector 

De RCE CHO-connector biedt op dit moment 23 acties aan. De NL-GOV- en Kadaster-connectors hebben een vergelijkbare set, toegespitst op hun eigen bronnen. Elke tool vormt een vaste bouwsteen voor een specifieke taak. De tools van de RCE CHO-connector vallen in vier groepen uiteen. 

### A. De data en ontologie verkennen 

Deze tools helpen om vast te stellen welke objecttypen, eigenschappen, relaties en deelverzamelingen beschikbaar zijn voordat een concrete datavraag wordt uitgevoerd. 

- **Ontology search:** zoekt een klasse of eigenschap op naam of trefwoord. 

- **Ontology describe class en Ontology describe property:** beschrijven hoe een klasse of eigenschap in het datamodel is gedefinieerd. 

- **Ontology statistics:** geeft een overzicht van het aantal klassen en eigenschappen in de ontologie. 

- **Explore class:** onderzoekt welke relaties er vanuit een klasse vertrekken en waar die naartoe leiden. 

- **Explore incoming:** onderzoekt vanuit welke klassen, en via welke relaties, er naar instanties van een klasse of resource wordt verwezen. 

- **Graphs list:** toont de named graphs waarin de data is verdeeld. 

- **Dataset statistics, Class instance counts en Property usage counts:** geven tellingen van objecten, typen en gebruikte eigenschappen. 

- **Describe resource uri:** toont de beschikbare gegevens van één specifieke resource. 

### B. Vragen stellen aan de data 

Deze tools voeren zoekopdrachten uit op de beschikbare databank. 

- **Query sparql:** voert een SPARQL-query uit en geeft het resultaat in een leesbare vorm terug. 

- **Query sparql json:** voert dezelfde soort query uit en levert technische JSON-uitvoer voor verdere verwerking. 

- **Query sparql geojson:** levert geografische resultaten in GeoJSON, zodat ze op een kaart kunnen worden getoond. 

### C. Begrippen herkennen en vertalen 

Deze tools ondersteunen de koppeling tussen woorden van gebruikers, officiële begrippen en URI's. Dat is nodig wanneer registraties verschillende labels, afkortingen of identificaties gebruiken. 

- **Resolve concept label:** vertaalt een label naar de officiële conceptvermelding binnen een gekozen deelverzameling. 

- **Lookup termennetwerk uri en Zoek concept termennetwerk:** zoeken begrippen en URI's in het landelijke Termennetwerk. 

- **Semantics describe topic en Semantics list topics:** geven uitleg over de interpretatie van onderdelen van de dataset, zoals dubbel voorkomende objecten of de betekenis van dateringen. 

### D. Kwaliteit en querybetrouwbaarheid 

Deze tools verkleinen de kans op zoekvragen die technisch geldig lijken, maar door bekende model- of queryfouten een leeg, onvolledig of misleidend resultaat opleveren. 

- **Validate query en Validate query structured:** controleren een zoekvraag vooraf op bekende valkuilen en veelgemaakte fouten. 

- **Convert rd to wgs84:** rekent Nederlandse rijksdriehoekscoördinaten om naar WGS84-coördinaten voor kaartgebruik. 

- **Ping:** controleert of de verbinding met de connector beschikbaar is. 

## 9. Betrouwbaarheid als ontwerpprincipe 

Betrouwbaarheid begint bij de kwaliteit en structuur van de brondata. Daarnaast biedt de connector tools waarmee zoekvragen gecontroleerd kunnen worden op bekende technische en semantische valkuilen. Juist een query die geen foutmelding geeft, maar stilzwijgend niets of iets verkeerds retourneert, vormt een risico. 

De validate-tools kunnen daarom een expliciete controlestap uitvoeren voordat een zoekvraag wordt uitgevoerd. Het is aan de AI-client om die stap daadwerkelijk aan te roepen; de connector dwingt dit niet standaard af. Deze validatie verkleint de kans op bekende fouten. Zij garandeert niet dat ieder antwoord inhoudelijk juist of volledig is en vervangt geen beoordeling van de vraagstelling, de brondata en de uitkomst. 

Andere aandachtspunten blijven bestaan, zoals onvolledige brondata, verschillen tussen registraties, onverwachte modellering of een technisch correcte query die niet precies de bedoelde selectie uitvoert. De connector maakt zulke analyses sneller en beter controleerbaar, maar neemt de verantwoordelijkheid voor interpretatie niet weg. 

## 10. Beheer en randvoorwaarden 

Beheer, verantwoordelijkheden en randvoorwaarden zijn op het moment van schrijven nog niet vastgelegd; dit traject is voorzien voor het najaar van 2026. Voor collega's en management zijn dit logische vragen die deze sectie op dat moment zal beantwoorden: 

- Wie beheert de connector? 

- Wie beheert de tools? 

- Wie beoordeelt wijzigingen? 

- Welke beschikbaarheid wordt nagestreefd? 

- Wat gebeurt er wanneer een bron verandert? 

- Welke resultaten mogen als beslisinformatie worden gebruikt? 

- Worden vragen of resultaten gelogd? 

- Zijn er privacy- of beveiligingsrisico's? 

De broncode is openbaar in te zien op GitHub, maar de precieze voorwaarden daarvan zijn nog niet uitgewerkt. Zodra deze afspraken zijn vastgesteld, worden hier in elk geval opgenomen: 

- de repository; 

- de licentie; 

- de eigenaar of beheerder; 

- de status: prototype, pilot of productie; 

- de wijze van bijdragen; 

- het versiebeheer. 

_Deze notitie beschrijft de connector op hoofdlijnen. Het document legt uit wat de connector doet en waarom die aanpak relevant is. Het is geen technische handleiding of formele beheerbeschrijving._ 

## Bijlage A. Praktijkvoorbeelden 

De praktijkvoorbeelden zijn hier als bijlage opgenomen om de hoofdtekst compact te houden. Voor elk voorbeeld staat: wat het is, welke bronnen worden gecombineerd, waarom het relevant is, en een link naar de volledige versie. 

#### **1. Pand-oppervlakte-kaart** 

**Wat het is:** Eén statisch HTML-bestand waarmee je op adres of op rijksmonumentnummer kunt zoeken en direct naar het bijbehorende pand springt. 

**Bronnen:** de BAG-geometrie (voor de footprint-oppervlakte van een pand), het rijksmonumentenregister (om te zien of een pand een rijksmonument is, met een link naar het register) en EP-Online (voor een snelkoppeling naar het energielabel). 

**Waarom relevant:** één plek om oppervlakte, monumentstatus en energielabel van een pand te checken, zonder meerdere systemen te hoeven doorzoeken. 

**Link:** <u>htps://jolietjakeblues.github.io/footprint/</u> 

#### **2. Energielabelmonitor** 

**Wat het is:** een monitor die energielabels koppelt aan gebouwen. 

**Bronnen:** EP-Online (energielabels) en de BAG (verblijfsobject-id's). 

**Waarom relevant:** laat direct zien welke panden een verouderd of ontbrekend label hebben, per gemeente of wijk; relevant voor verduurzamingsopgaven en om te signaleren waar datakwaliteit in de basisregistraties tekortschiet. 

**Link:** <u>htps://jolietjakeblues.github.io/energielabel/</u> 

_Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/67d505f1-2900-4bfe-b8dd-074b25c45a9f</u> 

#### **3. Archeologiemonitor Zuid-Holland** 

**Wat het is:** een monitor van archeologische waarden en verwachtingen in Zuid-Holland. 

**Bronnen:** archeologische waarden- en verwachtingskaarten en gegevens over ruimtelijke ontwikkelingen in de provincie (concrete bronvermelding volgt zodra vastgesteld). 

**Waarom relevant:** maakt vroeg in planprocessen zichtbaar waar archeologisch onderzoek of bescherming nodig is, voordat een project vastloopt op vondsten in de grond. 

**Link:** <u>htps://jolietjakeblues.github.io/ArcheologieMonitorZuid-Holland/</u> _Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/8a27e3e0-d5bd-4892-80ee-b6bc9cbc4b12</u> 

#### **4. Stikstof Boerderijen Gelderland Natura2000** 

**Wat het is:** een monitor van werkende monumentale boerderijen in Gelderland. 

**Bronnen:** CHO (monumentale boerderijen) en de begrenzingen van Natura 2000-gebieden. 

**Waarom relevant:** toont welke boerderijen op korte afstand van beschermde natuurgebieden liggen; relevant voor het stikstofdossier en de relatie tussen agrarische activiteit en natuurbescherming. 

**Link:** <u>htps://jolietjakeblues.github.io/StkstofGelderland/</u> 

_Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/c6e34093-dbf7-4464-a493-90c1b5af3d96</u> 

#### **5. Verdichtingsmonitor Dordrecht** 

**Wat het is:** een monitor van bouwactiviteit binnen de beschermde stadsgezichten van Dordrecht. 

**Bronnen:** CHO (beschermde stadsgezichten) en gegevens over bouwactiviteit binnen dat gebied (concrete bronvermelding volgt zodra vastgesteld). 

**Waarom relevant:** brengt in beeld waar wordt bijgebouwd, verbouwd of gesloopt binnen beschermd gebied; belangrijk om de balans tussen verdichtingsopgave en erfgoedbescherming te bewaken en tijdig spanning te signaleren. 

**Link:** <u>htps://jolietjakeblues.github.io/StadsgezichtenDordrecht/</u> _Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/4432c591-a8a1-47ca-ad71-2131fac194c2</u> 

#### **6. Grondwatermonitor Gouda** 

**Wat het is:** een monitor van grondwaterstanden in de historische binnenstad van Gouda, inmiddels in twee versies: een eerste versie en een doorontwikkelde versie 2 met verbeterde weergave en aanvullende metingen. 

**Bronnen:** grondwatermeetgegevens en gegevens over bodemtype en ondergrond van de historische binnenstad. 

**Waarom relevant:** schommelende grondwaterstanden bedreigen de funderingen van monumentale panden op houten palen; te laag water betekent paalrot. Vroegtijdig signaleren maakt tijdige maatregelen mogelijk. 

#### **Versie 1** 

**Link:** <u>htps://jolietjakeblues.github.io/GrondwaterGouda_1/</u> 

_Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/82b3493b-636f-4dce-b815-581d60694bd1</u> 

#### **Versie 2 (doorontwikkeld)** 

**Link:** <u>htps://jolietjakeblues.github.io/GrondwaterGouda_2/</u> 

_Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/f3547312-0d4b-4a0b-ad81-66d96fee5d0</u> 

#### **7. Stapeling van publiekrechtelijke beperkingen op rijksmonumentpercelen** 

**Wat het is:** een analyse van rijksmonumentpercelen die naast de erfgoedbeperking ook nog andere wettelijke beperkingen dragen. 

**Bronnen:** CHO (rijksmonumentpercelen) en de BRK-PB (publiekrechtelijke beperkingenregistraties, zoals bodemsanering of natuurbescherming), samengebracht via de Kadaster Kennisgraaf. 

**Waarom relevant:** van de 88.621 percelen met een monumentbeperking heeft 18,5% nog minstens één andere beperking. Vooral het cluster bodem- en natuurbeperkingen (samen bijna 5.000 percelen) valt op; een mogelijke verklaring is dat dit samenhangt met industrieel erfgoed met een verontreinigingsverleden. Deze percelen vallen niet geïsoleerd onder het erfgoedregime maar onder meerdere wetten tegelijk, waardoor vergunning- en handhavingstrajecten al snel meerdere loketten raken. 

**Peildatum en bron:** 6 juli 2026; RCE CHO SPARQL-endpoint gecombineerd met de Kadaster Kennisgraaf (KKG). 

**Link:** <u>htps://jolietjakeblues.github.io/Stapeling-van-publiekrechtelijke-beperkingen-oprijksmonumentpercelen/</u> 

#### **8. Industriële monumenten en bodembeperkingen** 

**Wat het is:** een vervolganalyse op voorbeeld 7, die onderzoekt of rijksmonumenten met een bodemgerelateerde publiekrechtelijke beperking vaker een industriële functie hebben dan rijksmonumenten in het algemeen. 

**Bronnen:** het RCE CHO SPARQL-endpoint (functienaam en juridische status) en de bodem-subset uit de stapelingsanalyse van 6 juli 2026 (voorbeeld 7), die op zijn beurt op de Kadaster Kennisgraaf draait. 

**Waarom relevant:** van de 2.436 rijksmonumenten met een bodemgerelateerde beperking heeft 9,1% tot 16,1% een industriële functie, afhankelijk van een smalle of bredere afbakening van ‘industrieel’. Bij alle 63.097 rijksmonumenten met een geregistreerde functienaam is dat 3,6% tot 11,0%. Dit betekent dat industriële functies in deze groep duidelijk vaker voorkomen dan gemiddeld: een factor 2,5 respectievelijk 1,5 oververtegenwoordiging, in beide gevallen statistisch significant (getoetst met een tweeproporties z- toets). De afbakening van ‘industrieel’ is een eigen indeling, geen officiële RCE-typering, en het gaat om een samenhang, geen aangetoonde oorzaak: de beperking kan aan de locatie hangen, niet aan het gebouw zelf. **Peildatum en bron:** juli 2026; RCE CHO SPARQL-endpoint, vervolg op de stapelingsanalyse van 6 juli 2026. **Link:** <u>htps://jolietjakeblues.github.io/Bodembeperkingen/</u> 

_Ontwikkelversie (Claude-artifact):_ <u>htps://claude.ai/public/artfacts/44999b6b-5aee-4bb8-b4bf-485eab2300f7</u> 

