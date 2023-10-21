import streamlit as st
questions = ['Wat is psychopathologie?', 'Wat betekent etiologie in de context van psychologie?', 'Wat is het Research Domain Criteria (RDoC) model?', "Wat houdt een 'assessment' in binnen de psychologie?", 'Wat is het diathese-stress model?', 'Wat is het family systems model?', 'Wat is het socioculturele model?', 'Wat is de cognitief-gedragsmatige benadering?', 'Wat zijn angststoornissen?', 'Wat is gegeneraliseerde angststoornis (GAD)?', 'Wat is agorafobie?', 'Wat is een ernstige depressieve stoornis?', 'Wat is aanhoudende depressieve stoornis?', 'Wat is aangeleerde hulpeloosheid?', 'Wat is bipolaire I-stoornis?', 'Wat is bipolaire II-stoornis?', 'Wat is schizofrenie?', 'Wat zijn delusies?', 'Wat zijn hallucinaties?', 'Wat is gedesorganiseerde spraak?', 'Wat is gedesorganiseerd gedrag?', 'Wat zijn negatieve symptomen?', 'Wat is een obsessief-compulsieve stoornis (OCD)?', 'Wat is anorexia nervosa?', 'Wat is bulimia nervosa?', 'Wat is een binge-eating disorder?', 'Wat is maladaptief gedrag?', 'Wat zijn de criteria voor psychopathologisch gedrag?', 'Wat is het doel van het Diagnostisch en Statistisch Handboek van Geestesziekten (DSM)?', 'Wat is de DSM-5?', 'Wat betekent een categorische benadering in de psychopathologie?', 'Wat is een dimensionale benadering in de psychopathologie?', 'Wat is comorbiditeit in de context van psychopathologie?', 'Wat zijn de twee hoofdtypen van psychopathologie?', 'Wat zijn internaliserende stoornissen?', 'Wat zijn externaliserende stoornissen?', 'Wat is een specifieke fobie?', 'Wat zijn paniekaanvallen?', 'Wat zijn depressieve stoornissen?', 'Wat is de cognitieve triade?', 'Wat is manie?', 'Wat zijn manische episodes?', 'Wat is hypomanie in de context van een bipolaire stoornis?', 'Wat is het risico op zelfmoord volgens Thomas Joiner?', 'Wat zijn de fundamentele behoeften om zelfmoord te willen plegen?', 'Wat betekent de behoefte om ergens bij te horen?', 'Wat betekent de behoefte aan competentie?', 'Wat betekent in staat zijn om zelfmoord te plegen?', 'Wat zijn positieve symptomen van schizofrenie?', 'Wat zijn negatieve symptomen van schizofrenie?', 'Wat is catatonisch gedrag bij schizofrenie?', 'Wat is echolalie bij schizofrenie?', 'Wat is de invloed van biologie en omgeving op schizofrenie?', 'Wat zijn obsessies?', 'Wat zijn compulsies?']
answers = ['Psychopathologie verwijst naar ziektes of stoornissen van de geest, ook wel psychologische stoornissen genoemd. Dit kan variëren van depressie en angststoornissen tot schizofrenie en bipolaire stoornis.', 'Etiologie in de psychologie heeft betrekking op de factoren die bijdragen aan de ontwikkeling van een stoornis. Dit kan genetische predisposities, omgevingsinvloeden of traumatische gebeurtenissen omvatten.', 'Het RDoC is een onderzoeksmethode die kijkt naar de basismanieren waarop mensen functioneren, van onze genen tot onze hersenen en hoe we ons gedragen (bijvoorbeeld hoe we aandacht geven, communiceren met anderen of angst ervaren). Deze methode wordt vooral gebruikt om meer te begrijpen over psychische aandoeningen.', "Een 'assessment' in de psychologie is een onderzoek naar de cognitieve, gedragsmatige of emotionele functies van een persoon om mogelijke psychologische stoornissen te diagnosticeren. Dit kan gesprekken, tests of observaties omvatten.", 'Het diathese-stress model is een diagnosemodel dat stelt dat een stoornis kan ontstaan wanneer een onderliggende kwetsbaarheid gekoppeld wordt aan een uitlokkende gebeurtenis. Bijvoorbeeld een persoon met een genetische kwetsbaarheid voor depressie die een zware levensgebeurtenis doormaakt.', 'Het family systems model is een diagnosemodel dat problemen binnen een individu ziet als een indicatie van problemen binnen de familie. Het is gebaseerd op de gedachte dat familiesystemen een grote invloed hebben op het welzijn van de individuele leden.', 'Het socioculturele model is een diagnosemodel dat psychopathologie ziet als het resultaat van de interactie tussen individuen en hun culturen. Hierbij wordt rekening gehouden met culturele normen, waarden en verwachtingen.', 'De cognitief-gedragsmatige benadering is een diagnosemodel dat psychopathologie ziet als het resultaat van aangeleerde, onaangepaste gedachten en overtuigingen. Cognitieve gedragstherapie is een veelgebruikte behandelmethode binnen dit model.', 'Angststoornissen zijn psychologische aandoeningen die gekenmerkt worden door overmatige angst en vrees, zelfs als er geen echt gevaar aanwezig is. Een voorbeeld hiervan is paniekstoornis, waarbij iemand terugkerende en onverwachte paniekaanvallen heeft.', 'Gegeneraliseerde angststoornis is een constante staat van angst die niet gekoppeld is aan een specifiek object of gebeurtenis. Mensen met GAD maken zich vaak overmatig zorgen over alledaagse dingen.', 'Agorafobie is een angststoornis waarbij men bang is voor situaties waaruit ontsnappen moeilijk of onmogelijk kan zijn. Mensen met agorafobie vermijden vaak plaatsen zoals winkelcentra of openbare vervoermiddelen.', 'Ernstige depressieve stoornis is een aandoening die gekenmerkt wordt door ernstige negatieve stemmingen of een gebrek aan interesse in normaal gesproken plezierige activiteiten. Dit wordt ook wel klinische depressie genoemd.', 'Aanhoudende depressieve stoornis is een vorm van depressie die minder ernstig is dan een ernstige depressieve stoornis, maar langer duurt. Deze aandoening wordt ook wel dysthymie genoemd.', 'Aangeleerde hulpeloosheid is een cognitief model van depressie waarbij mensen zich niet in staat voelen om gebeurtenissen in hun leven te beïnvloeden. Dit kan leiden tot gevoelens van machteloosheid en hopeloosheid.', 'Bipolaire I-stoornis is een aandoening die gekenmerkt wordt door extreem verhoogde stemmingen tijdens manische episodes en vaak ook door depressieve episodes. Tijdens een manische episode kan iemand zich bijvoorbeeld ongewoon energiek, vrolijk of prikkelbaar voelen.', 'Bipolaire II-stoornis is een aandoening die gekenmerkt wordt door afwisselende periodes van extreem depressieve en mild verhoogde stemmingen. Het belangrijkste verschil met bipolaire I-stoornis is dat de manische episodes niet zo extreem zijn.', 'Schizofrenie is een psychische stoornis die gekenmerkt wordt door veranderingen in gedachten, waarnemingen of bewustzijn, wat resulteert in psychose. Het kan bijvoorbeeld leiden tot hallucinaties of delusies.', 'Delusies zijn valse overtuigingen gebaseerd op verkeerde interpretaties van de realiteit. Bijvoorbeeld, iemand kan geloven dat ze constant in de gaten worden gehouden, ondanks dat er geen bewijs voor is.', 'Hallucinaties zijn valse zintuiglijke waarnemingen die worden ervaren zonder een externe bron. Iemand kan bijvoorbeeld stemmen horen die er niet zijn.', 'Gedesorganiseerde spraak betreft incoherente spraakpatronen die vaak wisselen van onderwerp en vreemde of ongepaste dingen uiten. Een persoon kan bijvoorbeeld beginnen over het weer en abrupt overschakelen naar een heel ander onderwerp.', 'Gedesorganiseerd gedrag omvat vreemd of ongebruikelijk gedrag, zoals vreemde bewegingen van ledematen, bizarre spraak of ongepast zelfzorg, zoals niet goed aankleden of zichzelf niet wassen.', 'Negatieve symptomen zijn kenmerken van schizofrenie die worden gekenmerkt door tekorten in functioneren, zoals apathie, gebrek aan emotie, en vertraagde spraak en beweging. Iemand kan bijvoorbeeld moeite hebben om motivatie te vinden voor dagelijkse activiteiten.', 'Een obsessief-compulsieve stoornis (OCD) is een stoornis die gekenmerkt wordt door frequente opdringerige gedachten en dwangmatige handelingen. Bijvoorbeeld, iemand kan het gevoel hebben dat ze hun handen voortdurend moeten wassen, zelfs als ze weten dat ze niet vuil zijn.', 'Anorexia nervosa is een eetstoornis gekenmerkt door een excessieve angst om dik te worden en dus het beperken van energie-inname om een significant laag lichaamsgewicht te bereiken. Een persoon kan bijvoorbeeld zelfs bij ernstig ondergewicht nog steeds het gevoel hebben dat ze moeten afvallen.', 'Bulimia nervosa is een eetstoornis die zich kenmerkt door een cyclus van diëten, eetaanvallen, en compenseren (zelf-opgewekt braken). Het is een ernstige psychische aandoening die zowel fysieke als psychologische schade kan veroorzaken.', 'Een binge-eating disorder is een eetstoornis die wordt gekenmerkt door eetaanvallen die ernstige stress veroorzaken. Het verschilt van bulimia nervosa in die zin dat er geen compensatie plaatsvindt na de eetaanvallen.', 'Maladaptief gedrag is gedrag dat de capaciteit van een persoon om passend te reageren in sommige situaties verstoort. Bijvoorbeeld, iemand die bang is om het huis te verlaten, vermijdt angstgevoelens door binnen te blijven, wat het vermogen van die persoon om te werken of een sociaal leven te hebben kan belemmeren.', 'Psychopathologisch gedrag wordt bepaald door vier criteria: (1) wijkt het gedrag af van culturele normen voor acceptabel gedrag? (2) Is het gedrag maladaptief? (3) Is het gedrag zelfdestructief, veroorzaakt het persoonlijk leed aan het individu of bedreigt het anderen in de gemeenschap? (4) Veroorzaakt het gedrag ongemak en zorgen bij anderen, waardoor de sociale relaties van een persoon worden aangetast?', 'Het hoofddoel van de DSM is beschrijving. Het groepeert stoornissen op basis van gelijkenis in symptomen, waardoor wetenschappers en professionals een gemeenschappelijke taal en classificatieschema hebben. Een ander doel is om zorgverleners in staat te stellen zorgverzekeraars te factureren voor behandelingen.', 'De DSM-5 is de huidige editie van het Diagnostisch en Statistisch Handboek van Geestesziekten, uitgebracht in 2013. Het bestaat uit drie delen: een inleiding met instructies voor het gebruik van het handboek; diagnostische criteria voor alle stoornissen; en een gids voor toekomstig onderzoek naar psychopathologie. Stoornissen worden beschreven in termen van meetbare symptomen en een cliënt moet aan specifieke criteria voldoen om een bepaalde diagnose te krijgen.', 'Een categorische benadering impliceert dat iemand ofwel een psychische stoornis heeft, ofwel niet. Deze benadering houdt geen rekening met de ernst van een stoornis en suggereert ten onrechte dat er een duidelijke scheidslijn is tussen het wel of niet hebben van psychopathologie.', 'De dimensionale benadering ziet psychische stoornissen als een continuüm waarop mensen in gradaties variëren. Het erkent dat veel psychische stoornissen extreme versies van normale gevoelens zijn. De diagnose is relatief eenvoudig aan de uitersten, maar in het middengebied ambigu.', 'Comorbiditeit betekent dat psychische stoornissen vaak overlappen. Bijvoorbeeld, middelenmisbruik komt vaak voor bij psychische stoornissen, en mensen met ernstige depressie hebben vaak ook angststoornissen.', 'Psychologen hebben twee hoofdtypen van psychopathologie geïdentificeerd: internaliserende en externaliserende stoornissen.', 'Internaliserende stoornissen worden gekenmerkt door negatieve emoties zoals angst en stress, en omvatten stoornissen zoals depressie, gegeneraliseerde angststoornis en paniekstoornis. Deze stoornissen worden vaak geassocieerd met intense interne emotionele strijd.', 'Externaliserende stoornissen worden gekenmerkt door impulsief of oncontroleerbaar gedrag. Voorbeelden van deze stoornissen zijn alcoholisme, antisociale persoonlijkheidsstoornis en gedragsstoornissen. Ze uiten zich vaak in acties die schade kunnen toebrengen aan anderen of de maatschappij.', 'Een specifieke fobie is een buitensporige en irrationele angst voor een specifiek object of situatie, zoals slangen (ophidiofobie), gesloten ruimtes (claustrofobie) of hoogtes (acrofobie). Deze diagnose wordt gesteld op basis van het object van de angst in DSM-5.', 'Paniekaanvallen zijn plotselinge, overweldigende aanvallen van angst en zorgen, vaak gekenmerkt door symptomen zoals zweten, trillen, hartkloppingen, kortademigheid, pijn op de borst, duizeligheid en gevoelloosheid in handen en voeten. Ze kunnen ogenschijnlijk uit het niets komen of worden getriggerd door externe prikkels of interne gedachteprocessen.', 'Depressieve stoornissen, gecategoriseerd in DSM-5, worden gekenmerkt door een aanhoudende sombere, lege of prikkelbare stemming, samen met lichamelijke symptomen en cognitieve problemen die het dagelijks leven verstoren.', 'Volgens Aaron Beck hebben mensen met depressie negatieve percepties over zichzelf, hun situaties en de toekomst. Deze percepties beïnvloeden elkaar en dragen bij aan de stoornis met gedachten zoals "Ik ben waardeloos", "Ik ben een mislukking", "Ik ben lelijk", "Iedereen haat me", "De wereld is oneerlijk" en "Dingen zijn hopeloos", "Ik kan niet veranderen".', 'Manie verwijst naar een verhoogde stemming die voelt alsof men "op de top van de wereld" is. Deze positieve stemming gaat vaak gepaard met een grote toename van energie en fysieke activiteit, maar kan voor sommige mensen ook een gevoel van agitatie en rusteloosheid met zich meebrengen.', 'Manische episodes, die een rol spelen in de bipolaire stoornis 1, zijn perioden van abnormaal verhoogde stemming en activiteit die ten minste een week duren. Tijdens deze episodes kunnen mensen risicovolle gedragingen vertonen, zoals seksuele onbesuisdheid, koopverslavingen en riskante zakelijke ondernemingen, die ze achteraf vaak betreuren.', 'Hypomanie speelt een rol in bipolaire stoornis 2 en wordt vaak gekenmerkt door verhoogde creativiteit en productiviteit. Hoewel deze minder extreme positieve stemmingen iemands leven enigszins kunnen verstoren, veroorzaken ze niet noodzakelijk een significante beperking in het dagelijks leven of vereisen ze ziekenhuisopname.', 'Thomas Joiner stelt dat de personen die het meest risico lopen op zelfmoord zowel de wens als het vermogen hebben om zelfmoord te plegen.', 'De eerste fundamentele behoefte is de behoefte om ergens bij te horen, om verbonden te zijn met anderen. De tweede fundamentele behoefte is de behoefte aan competentie.', 'De behoefte om ergens bij te horen wordt gedwarsboomd als we niet geloven dat we genoeg positieve interacties hebben met mensen die om ons geven.', 'Deze behoefte wordt gedwarsboomd als we ons niet competent voelen in de wereld. Volgens Joiner verlangen we naar de dood als zowel de behoefte om ergens bij te horen als de behoefte aan competentie gefrustreerd zijn.', 'Om de pijn of angst voor de dood te overwinnen, is doorgaans enige vorm van herhaalde zelfvoorbereiding nodig. Bijvoorbeeld, iemand die roekeloos rijdt, zichzelf snijdt en/of experimenteert met drugs, is meer geoefend in zelfbeschadiging dan iemand die geen van deze gedragingen vertoont, en is daardoor waarschijnlijk beter in staat om dodelijk zelfletsel toe te brengen.', 'Positieve symptomen zijn kenmerken die aanwezig zijn in schizofrenie, maar niet in typisch gedrag.', 'Negatieve symptomen zijn kenmerken die ontbreken in schizofrenie, maar die doorgaans deel uitmaken van dagelijks functioneren. Negatieve symptomen kunnen apathie, gebrek aan emotie, en vertraagde spraak en beweging omvatten.', 'Catatonisch gedrag verwijst naar een verminderde responsiviteit op de omgeving bij mensen met schizofrenie, bijvoorbeeld urenlang geïmmobiliseerd blijven in één positie. Ook kunnen ze een starre, maskerachtige gezichtsuitdrukking hebben terwijl ze in de verte staren.', 'Echolalie is een gedrag waarbij mensen met schizofrenie de woorden die ze horen herhalen. Het is een soort dwangmatige nabootsing van de taal van anderen.', 'Een kind met een genetisch risico op schizofrenie en opgegroeid in een disfunctionele gezinsomgeving heeft een hoog risico op het ontwikkelen van de aandoening. Daarentegen heeft een kind zonder genetisch risico, ongeacht de gezinsomgeving, een laag risico op het ontwikkelen van schizofrenie.', 'Obsessies zijn terugkerende, opdringerige en ongewenste gedachten, ideeën of mentale beelden die angst verhogen. Ze omvatten vaak angst voor besmetting, ongelukken of eigen agressie. Personen proberen deze gedachten doorgaans te negeren of onderdrukken, maar soms voeren ze gedragingen uit om de obsessies te neutraliseren en de emotionele stress die ze veroorzaken te verminderen.', 'Compulsies zijn bepaalde handelingen die mensen met OCD zich gedwongen voelen om herhaaldelijk uit te voeren om angst te verminderen. De meest voorkomende compulsieve gedragingen zijn schoonmaken, controleren en tellen. Bijvoorbeeld, een persoon kan voortdurend controleren of een deur op slot is vanwege een obsessie dat hun huis misschien wordt binnengedrongen, of iemand kan zich bezighouden met bijgelovig tellen om ongelukken te voorkomen.']


def change_card_index(index):
    # Select first element and re-insert at index
    st.session_state.questions.insert(index, st.session_state.questions[0])
    st.session_state.answers.insert(index, st.session_state.answers[0])

    # Delete the first duplicate card
    del st.session_state.questions[0]
    del st.session_state.answers[0]

    return


def evaluate_graduation(current_card):
    if current_card in st.session_state.easy_count:
        st.session_state.easy_count[current_card] += 1
    else:
        st.session_state.easy_count[current_card] = 1

    # Delete card if graduated
    if st.session_state.easy_count[current_card] >= 2:
        del st.session_state.questions[0]
        del st.session_state.answers[0]
    else:
        change_card_index(20)

    return


def reset_easy_count(current_card):
    st.session_state.easy_count[current_card] = 0


# -------------------------SESSION STATES----------------------------- #

if 'easy_count' not in st.session_state:
    st.session_state.easy_count = {}

if 'questions' not in st.session_state:
    st.session_state.questions = None

if 'answers' not in st.session_state:
    st.session_state.answers = None

if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

if 'previous_page_name' not in st.session_state:
    st.session_state.previous_page_name = None

if 'current_page_name' not in st.session_state:
    st.session_state.current_page_name = __file__

# -------------------------------MAIN---------------------------------- #


def initialise_new_page():
    st.session_state.questions = questions.copy()
    st.session_state.answers = answers.copy()
    st.session_state.easy_count = {}
    return


# Read and store current file name
st.session_state.current_page_name = __file__

# Check if a new page is opened
if st.session_state.current_page_name != st.session_state.previous_page_name:
    # Change lists in session state with current week lists
    initialise_new_page()
    st.session_state.previous_page_name = st.session_state.current_page_name


card_progress = st.progress(0)
main_container = st.container()

with main_container:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Easy', use_container_width=True):
            # Count executive times the user found current card easy
            evaluate_graduation(st.session_state.questions[0])
            st.session_state.show_answer = False

    with col2:
        if st.button('Medium', use_container_width=True):
            st.session_state.show_answer = False
            reset_easy_count(st.session_state.questions[0])
            change_card_index(5)

    with col3:
        if st.button('Hard', use_container_width=True):
            st.session_state.show_answer = False
            reset_easy_count(st.session_state.questions[0])
            change_card_index(2)


if st.button('Show Answer', use_container_width=True):
    st.session_state.show_answer = not st.session_state.show_answer

if len(st.session_state.questions) == 0:
    st.session_state.questions = questions.copy()
    st.session_state.answers = answers.copy()
    st.session_state.easy_count = {}

st.subheader(st.session_state.questions[0])
if st.session_state.show_answer:
    st.write(st.session_state.answers[0])

card_progress.progress(int(sum(st.session_state.easy_count.values()) / (2 * len(questions)) * 100))