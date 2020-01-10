# pos-tagging-tool

### ICELANDIC ###

Mörkunartólið nýtist til að laga mörkun og lemmun á textum í höndunum. 

UPPSETNING:

Afritið skjölin í eina möppu og ritið python3 markari.py í skipanalínu. Tkinter þarf að vera uppsett á tölvunni.
 
 apt-get install python-tk

INNTAKSSKRÁ / ÚTTAKSSKRÁ:

Hver lína inniheldur eitt orð og tengdar upplýsignar (mark, lemma o.fl) og er þau aðskilin með dálkabili (e. tab). 
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



### ENGLISH ###

The annotation tool can be used for correcting pos-tagging and lemmatization of a corpus.

INSTALLATOIN:
Copy the files to a folder and write python3 markari.py in the command line. Tkinter need to be installed.
 
 apt-get install python-tk

INPUT / OUPPUT

It takes as an input a file with one word per line, sentences separated by line-break. In default mode each word is followed by pos-tag, lemma, comments and a boolean variable indicating if the word has been corrected, all separated by a tab

column 1: word
column 2: tag
column 3: lemma
column 4: comments
column 5: finished (0 or 1)

This can be modified by changing the file markari.py (line 1941-1945).

It is possible to add columns to file 1 that contains other possible tags, i.e. retrieved from other taggers.
Then one or more buttons appears behind each word that you can click on to change the value of the field containing 
the main tag. This is done by writine the index into the array taggers_i lína 1945 which indicates the position of the tag in each line. We plan to make those settings easier to handle in the near future.

MARKAMENGI:

The tool reads data from three files that is used for validation and error checking as well as to display possible tags for each word.

- markamengi.txt contains the tag-set in use.
- ord_og_mork.txt contains a list of words and possible pos-tags for each of them (that can be created from a gold standard)
- valid_tags.txt contains a python dictionary of the tags, where each tag has been separated into letters and where the meaning of each letter is written out (i.e. n = ‘nafnorð’). 

USAGE:

Further instructions can be found in the file hjalp.html.







