# pos-tagging-tool
Mörkunartólið er ætlað til að laga mörkun og lemmun á textum. 

INNTAKSSKRÁ / ÚTTAKSSKRÁ:
Hver lína inniheldur eitt þar sem orð og tengdar upplýsignar (mark, lemma o.fl) eru aðskilin með dálkabili (e. tab). 
Með sjálfgefnum stillingum er gert ráð fyrr eftirfarandi:

dálkur 1: orð 
dálkur 2: mark 
dálkur 3: lemma
dálkur 4: athugasemdir
dálkur 5: lokið (0 eða 1)

Hægt er að breyta þessu með því að breyta markari.py (lína 1941 og áfram).
Mögulegt er að bæta við einum eða fleiri hnöppum með líklegu marki (t.d. sem aðrir markarar hafa lagt til). 
Þá er hægt að smella á þá til að breyta marki. Það er gert með því að rita vísi (e. index) í fylkið taggers_i 
(lína 1945) sem bendir á stöðu marks í línunni. 
Þannig myndi vísirinn 5 benda á dálk 6 í línu. [Stefnt er að því að gera þessar stillingar einfaldari]

Setningar eru aðskildar með línubili.

MARKAMENGI:

Mörkunartólið les upplýsingar úr þremur skjölum sem það notar til villugreiningar og til að birta möguleg mörk.
- markamengi.txt inniheldur upplýsingar um það markamengi sem notað er.
- ord_og_mork.txt  inniheldur upplýsingar um hvaða mörk einstaka orð geta fengið (þær eru fengnar úr tveimur 
gullstöðlum, MÍM-GULL og OTB-GULL.)
- valid_tags.txt inniheldur python-orðabók (dict) sem geymir upplýsingar um mögulega samsetningu marka og 
upplýsingar um merkingu hvers stafs í marki.

NOTKUN:
Ítarlegar upplýsingar um notkun tólsins er að finna í skjalinu hjalp.html.







