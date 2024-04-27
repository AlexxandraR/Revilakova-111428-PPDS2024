# Dokumentácia k zadaniu číslo 6
Cieľom tohto zadania bolo implementovať **plánovač pre 
koprogramy** založené na rozšírených generátoroch. 
Koprogramy mali byť plánované metódou **ide pieseň 
dokola** (round-robin). Potrebné bolo implementovať 
metódy:
- add_job(it), ktorá vytvorí novú úlohu koprogramu 
pre generátorový iterátor it,
- start(), ktorá spustí beh plánovača.

Plánovač by mal reagovať na ukončenie koprogramu
(zachytiť výnimku **StopIteration**) informačným 
**výpisom**.

## Popis implementácie
Plánovač som implementovala ako objekt triedy 
**Scheduler**, ktorý má jeden atribút **jobs**.
Metóda **add_job(it)** pridáva generátorové iterátory 
do poľa **jobs**. Metóda **start(data)** postupne spúšťa
generátory v poradí, ako sú uložené v atribúte **jobs**
a posiela do nich požadované dáta pomocou funkcie 
**send**. Keď už nie sú žiadne dáta dostupné, ukončí 
sa činnosť jednotlivých generátorov.

Ďalej som implementovala 3 koprogramy: **coroutine1()**,
**coroutine2()** a **coroutine3()**. Koprogram 
**coroutine1()** vypíše veľkými písmenami, čo mu 
plánovač poslal. **coroutine2()** vypíše na striedačku 
veľkými a malými písmenami, čo mu plánovač poslal. 
**coroutine3()** nahradí medzery podčiarkovníkom a 
zároveň pridá do prijatých dát na začiatok a koniec 
podčiarkovník, výsledok vypíše.

Do **main()** funkcie som pripravila ukážku, ktorá 
naplánuje všetky tri koprogramy na vykonanie a do 
metódy **start(data)** som poslala pole stringov. 
Naplánovaných môže byť ľubovoľný počet koprogramov 
a pole stringov môže mať ľubovoľnú dĺžku.

## Ukážka výstupu
Koprogramy som naplánovala v poradí **coroutine1(), 
coroutine2(), coroutine3()** a dáta, ktoré boli 
distribuované medzi koprogramy, vyzerali nasledovne:
data = ["Ide", "piesen", "dokola", "okolo", "stola",
"-la -la ...", "tralala"]. Výstup je nasledovný:

```
Coroutine 1: IDE
Coroutine 2: PiEsEn
Coroutine 3: _dokola_
Coroutine 1: OKOLO
Coroutine 2: StOlA
Coroutine 3: _-la_-la_..._
Coroutine 1: TRALALA
Stops coroutine 2
Job 2 finished.
Stops coroutine 3
Job 3 finished.
Stops coroutine 1
Job 1 finished.
All jobs finished.
```

Ako môžeme vidieť, koprogramy sa striedali v 
zadanom poradí, pokiaľ neboli rozdistribuované
všetky dáta, potom sa koprogramy postupne ukončili.

## Zdroje
- zdrojové kódy z prednášky číslo 11, dostupné na: 
https://github.com/tj314/ppds-seminars/tree/ppds2024/lecture11
- zdrojové kódy zo seminára číslo 11, dostupné na:
https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar11