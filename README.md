# Dokumentácia k zadaniu číslo 5

Cieľom tohto zadania bolo:
- implementovať algoritmus **samplesort** pre Numba CUDA, 
- **porovnať** paralelný samplesort so zodpovedajúcim sériovým 
triediacim algoritmom na troch rádovo odlišných vstupoch,
- **vysvetliť** implementáciu a **zdôvodniť** vybrané hodnoty pre 
počet blokov a počet vlákien.

## Popis implementácie
Implementácia Samplesortu pozostáva z nasledujúcich krokov:
1. Ak je veľkosť vstupného poľa **menšia** ako **4**, vykoná sa sekvenčný 
bubblesort a skončí.
2. Ak je veľkosť vstupného poľa **väčšia** alebo **rovná** **4**, 
vykonajú sa nasledujúce kroky.
3. Vypočíta sa počet **pivotov** ako odmocnina z veľkosti vstupného poľa.
4. Vyberú sa **pivoty** zo vstupného poľa tak, aby vzdialenosti medzi ich 
indexami boli rovnaké.
5. Do prvého pomocného poľa sa pre každú hodnotu uloží **index**, 
do ktorého **bucketu** patrí. Do druhého sa uloží počet prvkov
patriacich do jednotlivých bucketov. Tento krok sa vykonáva paralelne 
vo funkcii **partition_kernel()** na toľkých vláknach, koľko je prvkov 
vo vstupnom poli.
6. Sekvenčne sa vypočítajú **offsety** jednotlivých **bucketov**.
7. Vytvorí sa nové pole, do ktorého sa vložia prvky zo vstupného poľa
**podľa bucketov**. Teda v novom poli budú najprv prvky, ktoré patria do 
bucketu 0, potom 1 a tak ďalej. Tento krok sa vykoná paralelne vo
funkcií **bucket_kernel()** na toľkých vláknach, koľko je bucketov.
8. Paralelne sa vykoná sekvenčný bublesort vo funkcii 
**sort_buckets_kernel()** na toľkých vláknach, koľko je **bucketov**. Každé
vlákno má priradený bucket podľa svojho identifikačného čísla, a teda
zo vstupného poľa zotriedi prislúchajúce podpole.

Z prednášky vieme, že **veľkosť bloku**, teda **počet vlákien v bloku**, má byť násobkom veľkosti **warpu**, čiže 32. Ideálne je zvoliť deliteľa
1024, preto som si zvolila **256** vlákien v bloku. Následne počet blokov 
som vypočítala ako **hornú celú časť z veľkosti vstupného poľa / počet vlákien v bloku** pre funkciu **partition_kernel()**. Pre funkcie 
**bucket_kernel()** a **sort_buckets_kernel()** je počet blokov vypočítaný
ako **horná celá časť z počtu bucketov / počet 
vlákien v bloku**.

## Porovnanie algoritmov
Paralelnú implementáciu **samplesortu** som porovnala so sekvenčnou
verziou **bubblesortu**. Pri jednotlivých meraniach som prvky poľa 
generovala náhodne v rozmedzí -500 až 500. Veľkosť poľa som postupne
zväčšovala od 50 až po 30 000. Pre každú veľkosť poľa som realizovala
20 meraní a z nich vypočítala priemerný čas pre oba algoritmy. Výsledky
porovnania sú znázornené v nasledujúcej tabuľke a grafe.

| Veľkosť poľa    | Čas - sekvenčného bubblesortu [ms] | Čas - paralelného samplesortu [ms] |
|-----------------|------------------------------------|------------------------------------|
| 50              | 0,3                                | 379,8                              |
| 100             | 1,1                                | 382,5                              |
| 500             | 25,4                               | 398,4                              |
| 1 000           | 113                                | 408,7                              |
| 2 000           | 466,7                              | 397,8                              |
| 5 000           | 2882,1                             | 397,7                              |
| 10 000          | 11642,2                            | 396,3                              |
| 20 000          | 46869,4                            | 411,6                              |
| 30 000          | 104907,7                           | 447,7                              |

<img src="graf.png" alt="Graf" width="650" height="300">

Ako môžeme vidieť, čas **paralelného samplesortu** narastá veľmi pomaly
so zväčšujúcou sa veľkosťou vstupného poľa. Zatiaľ čo čas **sekvenčného 
bubblesortu** narastá oveľa rýchlejšie. Pri veľkosti poľa menšej ako 2 000
čísel bol **sekvenčný bubblesort** výrazne lepší ako **paralelný samplesort**.
Avšak pre veľkosti poľa nad a vrátane 20 000 sa karta obrátila a časovo
menej náročný sa stal **paralelný samplesort**. 

## Zdroje
- zdrojové kódy z prednášky číslo 8, dostupné na:
https://github.com/tj314/ppds-seminars/tree/ppds2024/lecture8
- zdrojové kódy zo seminára číslo 8, dostupné na:
https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar8
- sekvenčný bublesort, dostupný na:
https://www.geeksforgeeks.org/python-program-for-bubble-sort/