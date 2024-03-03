# Dokumentácia k zadaniu číslo 3

V tomto zadaní sme mali implementovať simuláciu **húsenkovej dráhy**. Vlak
realizujúci jazdy má svoju **kapacitu C**. **Počet cestujúcich** je **N**, pričom 
platí, že **C < N**. Aby sa jazda začala, vlak musí byť plne obsadený. 
Keď vlak ukončí svoju jazdu, najprv musia všetci cestujúci vystúpiť, 
až potom môžu noví cestujúci nastúpiť.

## Popis implementácie

Na realizáciu tohto zadania som využila **4 semafory** nastavené na 0 a 
**2 jednoduché bariéry**. Na začiatku jazdy, vlak musel vykonať 
**signal(C)** na semafor s názvom **boardQ**, aby pasažieri začali nastupovať. 
Následne pasažieri postupne volali **wait()** na tento semafor a vchádzali 
do bariéry **boardB**. Keď bolo **C** pasažierov v bariére **boardB**, posledný
pasažier zavolal **signal()** na semafor **boarded**, aby signalizoval vlaku, že
jeho kapacita je plne obsadená, môže vykonať **wait()** na tento semafor a začať
jazdu. Podobne po ukončení jazdy vlak spraví **signal(C)** na semafor
**unboardQ**, aby signalizoval pasažierom, že môžu vystupovať. Pasažieri, 
ktorí volajú **wait()** na tento semafor sa následne dostanú do bariéry 
**unboardB**, kde posledný pasažier vykoná **signal()** na **unboarded**, ktorým 
signalizuje vlaku, že všetci pasažieri vystúpili a môže začať od začiatku.

Na realizáciu **jednoduchej bariéry** som využila implementáciu z 
predchádzajúceho zadania, ktorú som upravila. Pridala som vstupný 
parameter **boarding**, ktorý je typu **boolean**. Ak je jeho hodnota **True**,
bariéra predstavuje nástup pasažierov a informuje vlak, že kapacita
je plná. Naopak, ak je **False**, bariéra predstavuje výstup pasažierov
a signalizuje vlaku, že všetci pasažieri vystúpili.

```
if boarding:
    print(f"All passengers are on the train waiting to depart.")
    shared.boarded.signal()
else:
    print(f"All passengers got off the train.")
    shared.unboarded.signal()
```

## Problém tejto implementácie

Podobne ako pri úlohe **Filozofi** aj v tomto prípade môže dôjsť k 
**vyhladovaniu niektorých vlákien**. Konkrétne môže dôjsť k tomu, že 
niektorý pasažier sa **ani raz nezvezie** vlakom, zatiaľ čo iný pasažier
bude vo vlaku každú jazdu.

## Ukážka výstupu
Na nasledujúcej vzorke môžete vidieť výstup programu. Najprv vlak čaká na 
naplnenie. Pasažieri postupne nastupujú. Keď je kapacita naplnená, vlak 
realizuje cestu. Na konci cesty, vlak čaká kým pasažieri vystúpia. Keď 
vystúpi aj posledný pasažier vlak začína svoju rutinu od začiatku.

```
The train is waiting until its capacity is filled.
The passenger 0 boarded the train. Number of passengers on the train: 1.
The passenger 1 boarded the train. Number of passengers on the train: 2.
The passenger 2 boarded the train. Number of passengers on the train: 3.
The passenger 3 boarded the train. Number of passengers on the train: 4.
The passenger 4 boarded the train. Number of passengers on the train: 5.
All passengers are on the train waiting to depart.
The train is running.
The train is waiting for all passengers to get off.
The passenger 0 is ready to get off the train. Number of ready passengers: 1.
The passenger 2 is ready to get off the train. Number of ready passengers: 2.
The passenger 4 is ready to get off the train. Number of ready passengers: 3.
The passenger 3 is ready to get off the train. Number of ready passengers: 4.
The passenger 1 is ready to get off the train. Number of ready passengers: 5.
All passengers got off the train.
```

## Zdroje
- prednáška číslo 2 z predmetu PPDS, dostupná: https://elearn.elf.stuba.sk/moodle/pluginfile.php/77169/mod_resource/content/2/2024-02.mutex%20multiplex%20randezvouse%20bariera.pdf.
- cvičenie číslo 3 z predmetu PPDS