# Dokumentácia k zadaniu číslo 3
Cieľom tohto zadania bolo modifikovať program **násobenia matíc**
nasledovne:
1. Umožnite **ľubovoľnému počtu pracovných uzlov** vykonávať program.
To znamená, že počet riadkov matice A nebude musieť byť deliteľný
bezo zvyšku počtom uzlov výpočtu.
2. Na distribúciu podmatíc A_i jednotlivým uzlom a poskladanie výslednej
matice C nepoužívajte P2P komunikáciu, ale **metódy kolektívnej komunikácie
scatter()/gather()**.

## Popis implementácie
Využila som implementáciu **cv.mat_parsg.py** zo seminára číslo 7. 
Modifikovať bolo potrebné rozdelenie matice A. Ak počet pracovných uzlov
delí počet riadkov matice A bezo zvyšku, každý uzol dostane rovnako veľkú
podmaticu matice A. Ak je zvyšok po delení väčší ako 0, toľko pracovných
uzlov bude mať podmaticu o 1 riadok väčšiu. Toto rozdelenie realizuje 
funkcia **initialise_matrix_a(rows, offsets)**.
Podmatice sú ukladané do poľa a následne odoslané všetkým pracovným 
uzlom pomocou funkcie **scatter()**. Po vykonaní operácie násobenia sú 
zas zhromadžené v uzle **MASTER** pomocou funkcie **gather()**.

## Bonus
Bonusom v tomto zadaní bolo definovanie vlastných údajových typov MPI 
a využívanie natívnych metód MPI. Ako vlastné údajové typy som si definovala
**a_row/b_row** na reprezentáciu riadkov matice **A**/**B**. Na distribúciu matice A som 
využila funkciu **Scatterv()** a na zhromaždenie jednotlivých podmatíc matice C
som použila funkciu **Gatherv()**. Tieto funkcie vyžadovali aj informácie o veľkostiach
a offsetoch jednotlivých podmatíc, ktoré som posielala v premenných **rows a offsets**.


## Experimenty
Úlohou zadania bolo aj vykonanie experimentov porovnania implementácií
s **P2P** kominukáciou, metódami kolektívnej komunikácie **scatter()/gather()** a 
s **natívnymi metódami MPI**.
Experimenty som vykonala s 3 pracovnými uzlami, preto som si upravila aj 
implementáciu s P2P komunikáciu, ktorá sa nachádza v súbore **p2p.py**.
Postupne som zväčšovala rozmery matíc **A** a **B**. Pre jednu kombináciu 
rozmerov som program spustila **100-krát** a vypočítala priemerný čas behu.
Priemerné časy pre jednotlivé rozmery matíc sú zaznamenané v 
nasledujúcej **tabuľke** a znázornené na nasledujúcom **grafe**.

| Rozmery matíc (NRA, NCA, NCB) | Čas - P2P | Čas - scatter()/gather() | Čas - Scatterv()/Gatherv() |
|-------------------------------|-----------|--------------------------|----------------------------|
| (32, 15, 7)                   | 0,002546  | 0,001855                 | 0,001760                   |
| (52, 15, 7)                   | 0,003881  | 0,002810                 | 0,002798                   |
| (52, 25, 7)                   | 0,006476  | 0,005374                 | 0,004498                   |
| (52, 25, 17)                  | 0,014713  | 0,007840                 | 0,010746                   |
| (72, 25, 17)                  | 0,021450  | 0,014789                 | 0,013476                   |
| (72, 45, 17)                  | 0,035718  | 0,027385                 | 0,025179                   |
| (72, 45, 27)                  | 0,061406  | 0,043807                 | 0,037795                   |
| (102, 75, 47)                 | 0,350285  | 0,272562                 | 0,244388                   |
| (152, 135,107)                | 1,608046  | 1,470555                 | 1,203138                   |
| (202, 185, 157)               | 3,041047  | 2,403920                 | 2,382729                   |
| (252, 205, 197)               | 5,389868  | 4,330555                 | 4,149160                   |

<img src="graf.png" alt="Graf" width="650" height="400">

Ako môžeme vidieť, či už v tabuľke alebo na grafe, pre **priemerné časy** behov programov
platí nasledujúci vzťah **Scatterv()/Gatherv() < scatter()/gather() < P2P**
pre všetky veľkosti matíc. Pri menších rozmeroch je rozdiel
minimálny a postupne sa zväčšuje spolu so zväčšujúcimi sa rozmermi matíc.
Pri rozmeroch matice **A 252x205** a matice **B 205x197** rozdiel časov implementácie 
s P2P komunikáciou a implementáciou pomocou scatter()/gather() alebo
Scatterv()/Gatherv() presiahol 1 sekundu.

## Zdroje
- zdrojové súbory zo seminára číslo 7 dostupné na: 
https://elearn.elf.stuba.sk/moodle/mod/folder/view.php?id=27376
- zdrojové kódy dostupné na stránke:
https://www.kth.se/blogs/pdc/2019/11/parallel-programming-in-python-mpi4py-part-2/