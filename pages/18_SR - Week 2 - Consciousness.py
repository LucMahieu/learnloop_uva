import streamlit as st

solid_list_questions = ['Wat is het begrip bewustzijn?', 'Wat is change blindness?', 'Wat is endogene aandacht?', 'Wat is exogene aandacht?', 'Wat is priming?', 'Wat is subliminale perceptie?', 'Wat is meditatie?', 'Wat is hypnose?', 'Wat zijn circadiane ritmes?', 'Wat is REM-slaap?', 'Wat zijn dromen?', 'Wat is de activatie-synthese hypothese?', 'Wat is slapeloosheid?', 'Wat is obstructieve slaapapneu?', 'Wat is narcolepsie?', 'Wat is shadowing volgens Cherry?', 'Wat is een Freudian slip?', 'Wat is automatische verwerking?', 'Wat is gecontroleerde verwerking?', 'Wat is concentratieve meditatie?', 'Wat is mindfulness meditatie?', 'Wat is de "runner\'s high"?', 'Wat is religieuze extase?', "Wat is flow?", "Wat is escapist entertainment?", "Wat is de suprachiasmatic nucleus?", "Wat is de pineal gland?", "Wat is melatonine?", "Wat zijn theta waves?", "Wat zijn sleep spindles?", "Wat zijn k-complexes?", 'Wat zijn delta golven of slow-wave slaap?', 'Wat zijn beta golven?', 'Wat gebeurt er in stadium 1 van de slaap?', 'Wat gebeurt er in stadium 2 van de slaap?', 'Wat gebeurt er in stadium 3 en 4 van de slaap?', 'Wat is paradoxale slaap?', "Wat houdt Freuds interpretatie van dromen in?", "Wat is 'Manifest content' in Freud's interpretatie van dromen?", "Wat is 'Latent content' in Freud's interpretatie van dromen?", 'Wat zijn de theorieën over slaap?', "Wat is de 'Restorative theory' van slaap?", "Wat is de 'Circadian rhythm theory' van slaap?", "Wat is de 'Facilitation of learning theory' van slaap?", "Wat is het 'REM Behavior disorder'?", 'Wat is een hersenschudding?', 'Wat is een coma?', 'Wat is het onresponsieve waakheidssyndroom?', 'Wat is de minimaal bewuste toestand?', 'Wat betekent hersendood?', 'Wat zijn de soorten psychoactieve drugs?', 'Wat zijn stimulerende middelen?', 'Wat zijn Depressants?', 'Wat zijn Opioids (narcotics)?', 'Wat zijn Hallucinogens (psychedelics)?', 'Wat is een Combination drug?', 'Wat is verslaving?', 'Wat is tolerantie voor drugs?', 'Wat is ontwenning?', 'Wat is binge drinking?']
solid_list_answers = ['Bewustzijn verwijst naar iemands moment-tot-moment subjectieve ervaring van de wereld. Het omvat alles waar je je op een bepaald moment bewust van bent.', 'Change blindness is het onvermogen om grote veranderingen in je omgeving op te merken. Het gebeurt bijvoorbeeld wanneer je niet merkt dat een vriend een nieuwe bril draagt.', 'Endogene aandacht is de vrijwillige richting van onze aandacht, zoals wanneer je je concentreert op het lezen van een boek.', 'Exogene aandacht is de aandacht die onvrijwillig wordt geleid door een stimulus, zoals wanneer een plotselinge harde knal je aandacht trekt.', 'Priming is een versnelling van de reactie op een stimulus door recente ervaring met die stimulus of een gerelateerde stimulus. Bijvoorbeeld, na het zien van het woord "geel", ben je sneller geneigd om "banaan" te herkennen.', 'Subliminale perceptie is de verwerking van informatie door zintuiglijke systemen zonder bewuste waarneming. Bijvoorbeeld, je zou een bericht kunnen verwerken van een reclame die te snel flitst om bewust waar te nemen.', 'Meditatie is een mentale procedure die de aandacht richt op een extern object, een intern evenement, of een gevoel van bewustzijn. Het wordt vaak gebruikt voor ontspanning en stressvermindering.', 'Hypnose is een sociale interactie waarbij een persoon, reagerend op suggesties, veranderingen ervaart in geheugen, perceptie en/of vrijwillige actie. Het wordt soms gebruikt in therapeutische situaties.', "Circadiane ritmes zijn biologische patronen die zich op regelmatige tijdstippen voordoen, afhankelijk van het tijdstip van de dag. Bijvoorbeeld, het slaap-waakritme dat ons helpt om 's nachts te slapen en overdag wakker te zijn.", 'REM-slaap is een slaapfase gekenmerkt door snelle oogbewegingen, verlamming van de motorische systemen en dromen. Het is in deze fase dat de meest levendige dromen vaak optreden.', 'Dromen zijn producten van een veranderde bewustzijnstoestand waarin beelden en fantasieën worden verward met de realiteit. Een droom kan ervaren worden als een werkelijke gebeurtenis, hoewel deze slechts in de geest plaatsvindt.', 'De activatie-synthese hypothese stelt dat de hersenen proberen om willekeurige hersenactiviteit die tijdens de slaap optreedt, te interpreteren door deze te combineren met opgeslagen herinneringen. Hierdoor ontstaan dromen.', 'Insomnie is een slaapstoornis gekenmerkt door een onvermogen om te slapen, wat significante problemen veroorzaakt in het dagelijks leven. Het kan bijvoorbeeld leiden tot vermoeidheid overdag en verminderde concentratie.', 'Obstructieve slaapapneu is een stoornis waarbij mensen tijdens het slapen stoppen met ademen omdat hun keel sluit, wat resulteert in frequent ontwaken tijdens de nacht. Dit kan leiden tot ernstige vermoeidheid overdag en andere gezondheidsproblemen.', 'Narcolepsie is een slaapstoornis waarbij mensen overdag overmatige slaperigheid ervaren, soms zelfs slap worden en ineenzakken. Het is alsof de REM-slaap op ongepaste tijden optreedt.', 'Shadowing is een techniek waarbij een deelnemer koptelefoons draagt die twee verschillende berichten leveren aan elk oor. De deelnemer wordt gevraagd om zich op één van de twee berichten te concentreren en dit na te zeggen. Dit helpt Cherry om te bestuderen hoe het brein omgaat met informatie die niet direct de aandacht krijgt.', 'Een Freudian slip is een fout waarbij een onbewuste gedachte plotseling wordt geuit op een ongepast moment of in een ongepaste sociale context. Het is een voorbeeld van hoe Freud geloofde dat het onbewuste gedrag beïnvloedt, hoewel zijn specifieke interpretaties tegenwoordig door veel psychologen in twijfel worden getrokken.', 'Automatische verwerking vindt plaats wanneer een taak zo goed is aangeleerd dat we deze kunnen uitvoeren zonder er veel aandacht aan te besteden. Een voorbeeld is het lezen van een tekstboek, waarbij de woorden automatisch naar voren springen en je je bewuste inspanningen kunt wijden aan volledig begrip.', 'Gecontroleerde verwerking is nodig voor moeilijke of onbekende taken en vereist dat mensen aandacht besteden. Hoewel het langzamer is dan automatische verwerking, helpt het mensen om te presteren in complexe of nieuwe situaties. Een voorbeeld is het rijden in een regenstorm, waarbij je meer aandacht moet besteden aan je rijgedrag en bewust moet zijn van de wegcondities.', 'Concentratieve meditatie houdt in dat je je aandacht richt op één ding, zoals je ademhalingspatroon, een mentaal beeld of een specifieke zin (soms een mantra genoemd).', 'Bij mindfulness meditatie laat je je gedachten vrij stromen, je besteedt aandacht aan ze maar probeert niet te reageren op ze. Je hoort de inhoud van je innerlijke stem, maar je laat ze van het ene onderwerp naar het andere stromen zonder hun betekenis te onderzoeken of op enige manier te reageren.', 'De "runner\'s high" is een staat waarin een persoon na het voelen van pijn en vermoeidheid plotseling euforie en een glorieuze energie-uitbarsting ervaart. Dit wordt gedeeltelijk bemiddeld door fysiologische processen en resulteert in een verandering van bewustzijn.', 'Religieuze extase is een verschuiving in bewustzijn vergelijkbaar met de "runner\'s high", die vaak voorkomt tijdens religieuze ceremonies. Het vermindert het bewustzijn van de buitenwereld en creëert gevoelens van euforie. Net als meditatie, leidt religieuze extase de aandacht af van het zelf door middel van chanten, dansen, en/of andere gedragingen, waardoor een persoon zich kan concentreren op de religieuze ervaring.', "Flow is een type ervaring die zo boeiend en plezierig is dat het de moeite waard is om te doen omwille van de ervaring zelf, zelfs als het geen externe gevolgen heeft. Het is een optimale ervaring waarbij de activiteit volledig absorberend en bevredigend is en automatisch lijkt te gebeuren. Bijvoorbeeld, atleten die 'in de zone' zijn, ervaren een staat van flow.", "'Escapist Entertainment' is eenvoudig vermaak, zoals het spelen van videogames, dat voordelen kan hebben. Echter, wanneer dergelijke activiteit naar obsessie neigt, kan het negatieve effecten hebben.", 'De suprachiasmatic nucleus is een klein deel van de hypothalamus dat informatie over licht, gedetecteerd door de ogen, ontvangt en vervolgens signalen naar de pijnappelklier stuurt.', 'De pijnappelklier is een kleine structuur die melatonine afscheidt nadat het signalen van de suprachiasmatic nucleus heeft ontvangen.', 'Melatonine is een hormoon dat door de bloedstroom reist en verschillende receptoren in het lichaam beïnvloedt, waaronder de hersenen. Het is noodzakelijk voor circadiane cycli die de slaap reguleren. Bijvoorbeeld, het nemen van melatonine kan helpen bij het omgaan met jetlag.', 'Theta golven zijn korte uitbarstingen van onregelmatige golven, vaak geassocieerd met slaap en meditatie.', 'Slaapspoeltjes zijn incidentele uitbarstingen van activiteit, voornamelijk gezien tijdens fasen van lichte slaap.', 'K-complexen zijn grote golven in de hersenactiviteit. Sommige onderzoekers geloven dat slaapspoeltjes en K-complexen signalen zijn van hersenmechanismen die betrokken zijn bij het uitsluiten van de buitenwereld en het in slaap houden van mensen.', 'Delta golven of Slow-wave slaap worden gekenmerkt door grote, regelmatige hersenpatronen. Dit komt vaak voor tijdens diepe slaap.', 'Beta golven zijn korte, onregelmatige hersengolven. Ze zijn normaal gesproken een teken van een wakker, alert brein.', 'Stadium 1 van de slaap bestaat uit Theta golven. Je bent in lichte slaap en wordt gemakkelijk gewekt. Je kunt fantastische beelden of geometrische vormen zien en het gevoel hebben dat je valt of dat je ledematen schokken.', 'Stadium 2 van de slaap bestaat uit Theta golven, slaapspoelen en K-complexen. Dit is een diepere slaapfase dan stadium 1.', 'Stadium 3 en 4 van de slaap bestaan uit Delta golven. Je bent in diepe slaap en het is moeilijk om wakker te worden. Je verwerkt nog steeds wat informatie om de omgeving te evalueren op mogelijk gevaar.', 'Paradoxale slaap wordt zo genoemd vanwege de tegenstrijdigheid van een slapend lichaam met een actief brein. Sommige neuronen zijn actiever tijdens de REM-slaap dan tijdens het wakker zijn. De meeste lichaamsspieren zijn verlamd en er is sprake van seksuele opwinding.', "'The Interpretation of Dreams' is een theorie van Freud die suggereert dat dromen verborgen inhoud bevatten die onbewuste conflicten in de geest van de dromer vertegenwoordigen. Hoewel er weinig bewijs is voor Freud's ideeën dat dromen verborgen conflicten vertegenwoordigen, is er wel bewijs dat dagelijkse ervaringen de inhoud van dromen beïnvloeden.", "De 'Manifest content' is het deel van de droom zoals de dromer zich deze herinnert. Dit is de directe inhoud en verhaallijn van de droom.", "De 'Latent content' is wat de droom symboliseert; het is het materiaal dat gecamoufleerd is om de dromer te beschermen tegen directe confrontatie met een conflict.", 'De belangrijkste theorieën over slaap zijn de Restorative theory, Circadian rhythm theory en de Facilitation of learning theory.', "De 'Restorative theory' stelt dat slaap het lichaam toestaat om te rusten en zichzelf te repareren. Slaaptekort vermindert je vermogen en je immuunrespons wordt slechter, waardoor je kwetsbaarder wordt voor infecties.", "De 'Circadian rhythm theory' stelt dat slaap is geëvolueerd omdat dieren 's nachts niet wakker willen zijn, omdat de wereld dan een gevaarlijke plek wordt. De hoeveelheid slaap van een dier hangt af van hoeveel tijd het dier nodig heeft om voedsel te vinden, hoe gemakkelijk het zich kan verbergen, en hoe kwetsbaar het is voor aanvallen.", "De 'Facilitation of learning theory' stelt dat slaap nodig is om neurale communicatie en verbindingen te versterken. Dit is nodig voor leren. Bijvoorbeeld, tijdens examenweek zijn studenten meer in REM-slaap.", "Het 'REM Behavior disorder' is een aandoening waarbij de normale verlamming die REM-slaap begeleidt, is uitgeschakeld. Mensen met deze aandoening handelen hun dromen uit tijdens het slapen, vaak slaan ze hun slapende partners. Er bestaat geen behandeling voor deze zeldzame aandoening, die wordt veroorzaakt door een neurologisch tekort en die het meest voorkomt bij oudere mannen.", "Een hersenschudding, ook bekend als een lichte traumatisch hersenletsel, kan ondanks de term 'licht' verre van onbeduidend zijn omdat de zwelling van de hersenen en de daaruit voortvloeiende hersenschade langdurige effecten kunnen hebben, zoals mentale verwarring, duizeligheid, geheugenproblemen en soms tijdelijk bewustzijnsverlies.", 'Een coma is een toestand waarin medische behandeling ervoor zorgt dat de hersenen kunnen rusten na een ernstig letsel. Dit is vaak het geval bij overlevenden van traumatische hersenletsel door bijvoorbeeld auto-ongelukken of gevechten.', 'Het onresponsieve waakheidssyndroom is een toestand waarin mensen lijken te zijn ontwaakt uit een coma (hun ogen zijn open en ze hebben slaap/waakcycli), maar ze reageren niet op externe prikkels voor meer dan een maand. In deze toestand komt er geen normale hersenactiviteit voor.', 'De minimaal bewuste toestand is een situatie waarin mensen die uit een coma ontwaken in staat zijn om doelbewuste bewegingen te maken, zoals het volgen van een object met hun ogen of pogingen tot communicatie. De prognose is in deze toestand beter dan in het onresponsieve waakheidssyndroom.', 'Hersendood is de onomkeerbare verlies van hersenfunctie. In tegenstelling tot patiënten met het onresponsieve waakheidssyndroom, die nog steeds activiteit in delen van de hersenstam vertonen, wordt bij hersendood geen activiteit gevonden in enig deel van de hersenen.', 'De soorten psychoactieve drugs omvatten stimulerende middelen, depressiva, opioïden, hallucinogenen/psychedelica en combinaties.', 'Stimulerende middelen verhogen de gedrags- en mentale activiteit. Voorbeelden zijn amfetaminen, methamfetamine, cocaïne, nicotine en cafeïne. Ze werken voornamelijk op de neurotransmittersystemen van dopamine, norepinefrine en acetylcholine (nicotine).', 'Depressants verlagen de gedrags- en mentale activiteit. Voorbeelden hiervan zijn anti-angst medicijnen zoals barbituraten en benzodiazepines, maar ook alcohol. Deze werken op het GABA neurotransmitter systeem.', 'Opioids verminderen de pijnbeleving. Voorbeelden zijn heroïne, morfine en codeïne. Ze werken op het endorfine neurotransmitter systeem.', 'Hallucinogenen veranderen gedachten of percepties. Voorbeelden zijn LSD, PCP, Peyote, Psilocybin en paddenstoelen. Ze werken op het serotonine en glutamaat neurotransmitter systeem.', 'Combination drugs hebben gemengde effecten. Voorbeelden zijn Marihuana en MDMA, die werken op het Cannabinoid (marihuana) en Serotonine, dopamine, norepinephrine (MDMA) neurotransmitter systeem.', 'Verslaving is het gebruik van drugs dat dwangmatig blijft, ondanks de negatieve gevolgen. Het kan zowel een fysieke als een psychische afhankelijkheid omvatten.', 'Tolerantie is wanneer er steeds meer van een drug nodig is om het beoogde effect te bereiken. Dit kan leiden tot overmatig gebruik en afhankelijkheid.', 'Ontwenning is een fysiologische en psychologische toestand die wordt gekenmerkt door gevoelens van angst, spanning en verlangen naar de verslavende stof.', 'Binge drinking is het drinken van vijf of meer drankjes in één zitting. Dit kan leiden tot ernstige gezondheidsproblemen zoals alcoholvergiftiging en leverziekte.']

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
    st.session_state.questions = solid_list_questions.copy()
    st.session_state.answers = solid_list_answers.copy()
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
    st.session_state.questions = solid_list_questions.copy()
    st.session_state.answers = solid_list_answers.copy()
    st.session_state.easy_count = {}

st.subheader(st.session_state.questions[0])
if st.session_state.show_answer:
    st.write(st.session_state.answers[0])

card_progress.progress(int(sum(st.session_state.easy_count.values()) / (2 * len(solid_list_questions)) * 100))