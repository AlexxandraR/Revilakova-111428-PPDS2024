# Dokumentácia k zadaniu číslo 2

Cieľom tohto zadanie bolo implementovať riešenie problému hodujúcich
divochov pomocou **jednoduchej bariéry** alebo **kombinačného stromu**. 
V súbore **main1.py** sa nachádza implementácia pomocou **jednoduchej bariéry**
a v súbore **main2.py** sa nachádza implementácia pomocou **kombinačného stromu**.

## Problém hodujúcich divochov
Divosi radi jedia spolu, a preto sa stále pred jedlom počkajú.
Na realizáciu tejto vlastnosti som využila základný synchronizačný
vzor **bariéru**. Keďže toto hodovanie sa neustále opakuje, bariéra musela
byť **znovupoužiteľná**. Skutočnosť, že v jednom čase si môže z hrnca naberať
práve jeden divoch som implementovala pomocou **zámku**. Ak sa všetko z hrnca
zje, nasledujúci divoch informuje kuchára, ktorý po doplnení hrnca 
spätne informuje divocha. V tomto prípade som využila **obojstrannú 
signalizáciu** pomocou **dvoch semaforov**.

V oboch kódoch využívam 2 globálne premenné **D** a **H**. **D** predstavuje 
celkový počet divochov a **H** predstavuje maximálnu kapacitu hrnca. V zdieľanej
pamäti uchovávam **mutex** - zámok pre počítadlo, **portion** - počítadlo zjedených
porcií, **fullPot** semafor so stavom 0 pre signalizáciu, že hrniec bol naplnený, 
**emptyPot** semafor so stavom 0 na signalizáciu, že hrniec je prázdny. 
Naviac implementácia s jednoduchou znovupoužiteľnou bariérou obsahuje 2 inštancie 
triedy SimpleBarrier, kdežto implementácia kombinačného stromu obsahuje iba 1 
inštanciu triedy CombiningTreeBarrier. Počet vlákien je o 1 väčší ako je počet 
divochov, pretože divosi potrebujú kuchára. Všetky vlákna reprezentujúce divochov
vykonávajú funkciu **savage(i, shared)**, kde **i** predstavuje identifikačné číslo
divocha a **shared** reprezentuje zdieľanú pamäť. Vlákno reprezentujúce kuchára 
vykonáva v nekonečnom cykle funkciu **serving_food(shared)**. Každý divoch opakovane
vykonáva nasledujúcu postupnosť funkcií:
1. **wait** na inštanciu bariéry - príchod k bariére a čakanie na posledného,
2. **eat** - postupné naberanie jedla a jedenie, prípadné upozornenie kuchára,
3. **wait** na inštanciu bariéry - opäť príchod k bariére a čakanie na posledného.

V kóde som 2-krát použila funkciu sleep(), na znázornenie vykonávania danej funkcie.
Konkrétne jeden sleep je využitý pri procese jedenia porcie divochom a druhý pri 
procese varenia a dopĺňania jedla kuchárom.

Výpisy som využila pri nasledujúcich situáciách:
 - divoch príde k bariére,
 - všetci divosi sú pri bariére,
 - divoch opustil bariéru,
 - divoch si zobral porciu a koľko porcií ostalo,
 - hrniec je prázdny,
 - hrniec je opäť plný.

## Zámok
Zámok som využila vo funkcii **eat**, ktorú môžete vidieť v 
nasledujúcom okne. Keďže sa vlákna vykonávajú naraz, mohli by chcieť v tom istom 
momente jesť, teda pristupovať a dekrementovať zdieľanú premennú **portion**, čo 
by mohlo viesť ku nesprávnej dekrementácii. Kvôli týmto skutočnostiam som 
využila zámok a serializovala vykonávanie tejto funkcie.
```
def eat(i, shared):
    shared.mutex.lock()
    if shared.portion == 0:
        print(f"The pot is empty. Savage {i} will wake up the cook.")
        shared.emptyPot.signal()
        shared.fullPot.wait()
    shared.portion -= 1
    print(f"Savage {i} eats. The remaining portions: {shared.portion}")
    sleep(2)
    shared.mutex.unlock()
```

## Semafor
Obojstrannú signalizáciu som v tomto zadaní využila pri informovaní kuchára 
o prázdnom hrnci a divocha o plnom hrnci. Na nasledujúcich vzorkách kódu je 
vidieť, že kuchár čaká na semafore **emptyPot**, kým divoch nevyšle signál 
na tento semafor po zistení, že hrniec je prázdny. Následne divoch čaká na 
semafore **fullPot** kým kuchár nedovarí a nevyšle signál na tento semafor, 
informujúc o plnom hrnci.

```
# Divoch
if shared.portion == 0:
    print(f"The pot is empty. Savage {i} will wake up the cook.")
    shared.emptyPot.signal()
    shared.fullPot.wait()
```
```
# Kuchár
while True:
    shared.emptyPot.wait()
    shared.portion = H
    sleep(3)
    print(f"The cook added {H} portions to the pot.")
    shared.fullPot.signal()
```

## Jednoduchá bariéra
V súbore **main1.py** sa nachádza riešenie zadania pomocou jednoduchej bariéry. 
Vytvorila som si triedu **SimpleBarrier** reprezentujucu jednoduchú bariéru. Medzi jej 
atribúty patria: zámok **mutex**, semafor **barrier** a počet vlákien v bariére
**barrierCount**. Táto trieda má jednu metódu a to wait, ktorá pustí vlákna až keď 
budú všetky pri bariére - teda hodnota atribútu **barrierCount** nebude rovná počtu 
divochov. Vlákna teda čakajú na semafore **barrier**, kým nepríde posledné vlákno 
a nespraví signál s voliteľným parametrom určujúcim koľko krát sa má metóda **signal**
na semafore vykonať. Potom sa všetky vlákna dostanú z bariéry.

```
class SimpleBarrier:
    def __init__(self):
        """Initializes the barrier."""
        self.mutex = Mutex()
        self.barrier = Semaphore(0)
        self.barrierCount = 0

    def wait(self, i, barrier_num):
        self.mutex.lock()
        self.barrierCount += 1
        print(f"Savage {i} came to barrier {barrier_num}. Total number at barrier {barrier_num}: {self.barrierCount}.")
        if self.barrierCount == D:
            if barrier_num == 1:
                print(f"All savages are at barrier {barrier_num} and are starting to eat.")
            else:
                print(f"All savages are at barrier {barrier_num} and are leaving for barrier 1.")
            self.barrier.signal(D)
            self.barrierCount = 0
        self.mutex.unlock()
        self.barrier.wait()
```

Na to, aby bola bariéra znovupoužiteľná musíme použiť dve inštancie triedy
**SimpleBarrier**. Ak by sa použila iba jedna inštancia, mohlo by sa stať, 
že jedno vlákno (1) bude rýchlejšie, druhý krát vojde do bariéry a obehne iné vlákno (2), 
ktoré nestihlo spraviť wait a to vlákno (2) uviazne v bariére.

## Kombinačný strom
V súbore **main2.py** sa nachádza riešenie zadania pomocou kombinačného stromu. 
Trieda **CombiningTreeBarrier** reprezentuje kombinačný strom. Jej atribúty sú: 
**num_threads** - počet divochov, **in_semaphores** a **out_semaphores**, ktoré 
reprezentujú polia semaforov nastavených na 0. Táto trieda má dve statické 
metódy a jednu nestatickú metódu. Metóda **get_children(tid)** vracia indexy uzlov, 
ktoré sú potomkami uzla s daným tid. **is_leaf(tid, num_threads)** vracia boolean 
hodnotu hovoriacu o tom, či je daný uzol listom. Metóda **wait** reprezentuje chod 
bariéry. Pomocou semaforov v poli **in_semaphores** sa signalizuje prítomnosť od
listov ku koreňu. A naopak pomocou semaforov z poľa **out_semaphores** sa signalizuje 
otvorenie bariéry od koreňa ku listom. Teda ak príde uzol ku bariére spraví **wait** na
semafory z **in_semaphores** na indexoch jeho detí. Ak obe deti spravili **signal** 
na svojich semaforoch, rodič môže spraviť **signal** na svojom semafore a zároveň **wait** na
svojom semafore ale z poľa **out_semaphores**. Takýmto spôsobom sa informácia o 
prítomnosti uzlov šíri od listov ku koreňu. Keď koreň dostane informáciu, že obe 
jeho deti sú pri bariére, znamená to, že všetky vlákna sú pri bariére a môže vyslať
informáciu o otvorení bariéry pomocou volania **signal** na semafory svojich detí z poľa 
**out_semaphores**.
```
class CombiningTreeBarrier:
    def __init__(self, num_threads):
        if not log(num_threads + 1, 2).is_integer():
            print(f"Number threads N must be 2^k - 1")
            raise ValueError
        self.num_threads = num_threads
        self.in_semaphores = [Semaphore(0) for _ in range(num_threads)]
        self.out_semaphores = [Semaphore(0) for _ in range(num_threads)]

    @staticmethod
    def get_children(tid):
        return 2*tid + 1, 2*tid + 2

    @staticmethod
    def is_leaf(tid, num_threads):
        return 2*tid + 1 >= num_threads

    def wait(self, tid):
        if CombiningTreeBarrier.is_leaf(tid, self.num_threads):  # leaf node
            self.in_semaphores[tid].signal()
            self.out_semaphores[tid].wait()
        elif tid == 0:  # root node
            left_child, right_child = CombiningTreeBarrier.get_children(tid)
            self.in_semaphores[left_child].wait()
            self.in_semaphores[right_child].wait()
            print(f"All savages are at barrier and are starting to eat.")
            self.out_semaphores[left_child].signal()
            self.out_semaphores[right_child].signal()
        else:  # in between node
            left_child, right_child = CombiningTreeBarrier.get_children(tid)
            self.in_semaphores[left_child].wait()
            self.in_semaphores[right_child].wait()
            self.in_semaphores[tid].signal()
            self.out_semaphores[tid].wait()
            self.out_semaphores[left_child].signal()
            self.out_semaphores[right_child].signal()
```

Ako si môžeme všimnúť na všetky semafory z oboch polí sa práve raz volá **signal** ako aj
**wait**, to znamená, že po odídení všetkých vlákien z bariéry je bariéra v pôvodnom stave.
Z toho vyplýva, že bariéra je znovupoužiteľná. Ak by aj jedno z vlákien (1) bolo 
rýchlejšie a dostalo by sa do bariéry druhý krát, zatiaľ čo iné vlákno (2) by z bariéry 
ešte neodišlo, nič zlé by sa nestalo, pretože rýchlejšie vlákno (1) by muselo počkať
kým pomalšie vlákno (2) z bariéry odíde a znova sa vráti.

## Ukážka výstupu

#### main1.py

V nasledujúcom okne je ukážka výpisu z programu **main1.py**. Ako môžeme vidieť
najprv všetci divosi prídu k prvej bariére, následne sa bariéra otvorí. Prvý divoch vide
a informuje kuchára o prázdnom hrnci. Zatiaľ čo kuchár varí jedlo aj zvyšní divosi 
opustia bariéru a čakajú kým si naberie prvý divoch. Potom si naberie druhý, tretí 
a tak ďalej. Po dojedení sa divosi zbierajú pri druhej bariére. Keď sa nazbierajú 
všetci druhá bariéra sa otvorí a všetci odchádzajú ku prvej bariére. Potom sa celý 
proces opakuje.

```
Savage 0 came to barrier 1. Total number at barrier 1: 1.
Savage 1 came to barrier 1. Total number at barrier 1: 2.
Savage 2 came to barrier 1. Total number at barrier 1: 3.
Savage 3 came to barrier 1. Total number at barrier 1: 4.
Savage 4 came to barrier 1. Total number at barrier 1: 5.
Savage 5 came to barrier 1. Total number at barrier 1: 6.
Savage 6 came to barrier 1. Total number at barrier 1: 7.
All savages are at barrier 1 and are starting to eat.
Savage 6 has passed the barrier 1.
The pot is empty. Savage 6 will wake up the cook.
Savage 2 has passed the barrier 1.
Savage 3 has passed the barrier 1.
Savage 4 has passed the barrier 1.
Savage 1 has passed the barrier 1.
Savage 5 has passed the barrier 1.
Savage 0 has passed the barrier 1.
The cook added 10 portions to the pot.
Savage 6 eats. The remaining portions: 9
Savage 6 came to barrier 2. Total number at barrier 2: 1.
Savage 2 eats. The remaining portions: 8
Savage 2 came to barrier 2. Total number at barrier 2: 2.
Savage 3 eats. The remaining portions: 7
Savage 3 came to barrier 2. Total number at barrier 2: 3.
Savage 4 eats. The remaining portions: 6
Savage 4 came to barrier 2. Total number at barrier 2: 4.
Savage 1 eats. The remaining portions: 5
Savage 1 came to barrier 2. Total number at barrier 2: 5.
Savage 5 eats. The remaining portions: 4
Savage 5 came to barrier 2. Total number at barrier 2: 6.
Savage 0 eats. The remaining portions: 3
Savage 0 came to barrier 2. Total number at barrier 2: 7.
All savages are at barrier 2 and are leaving for barrier 1.
```

#### main2.py

V nasledujúcom okne je ukážka výpisu z programu **main2.py**. Ako môžeme vidieť
najprv všetci divosi prídu k bariére, následne sa bariéra otvorí. Prvý divoch vide
a informuje kuchára o prázdnom hrnci. Zatiaľ čo kuchár varí jedlo aj zvyšní divosi 
opustia bariéru a čakajú kým si naberie prvý divoch. Potom si naberie druhý, tretí 
a tak ďalej. Po dojedení sa divosi zbierajú pri tej istej bariére ako predtým. Potom 
sa celý proces opakuje.

```
Savage 0 came to barrier.
Savage 1 came to barrier.
Savage 2 came to barrier.
Savage 3 came to barrier.
Savage 4 came to barrier.
Savage 5 came to barrier.
Savage 6 came to barrier.
All savages are at barrier and are starting to eat.
Savage 0 has passed the barrier.
The pot is empty. Savage 0 will wake up the cook.
Savage 2 has passed the barrier.
Savage 1 has passed the barrier.
Savage 4 has passed the barrier.
Savage 5 has passed the barrier.
Savage 3 has passed the barrier.
Savage 6 has passed the barrier.
The cook added 10 portions to the pot.
Savage 0 eats. The remaining portions: 9
Savage 0 came to barrier.
Savage 2 eats. The remaining portions: 8
Savage 2 came to barrier.
Savage 1 eats. The remaining portions: 7
Savage 1 came to barrier.
Savage 4 eats. The remaining portions: 6
Savage 4 came to barrier.
Savage 5 eats. The remaining portions: 5
Savage 5 came to barrier.
Savage 3 eats. The remaining portions: 4
Savage 3 came to barrier.
Savage 6 eats. The remaining portions: 3
Savage 6 came to barrier.
All savages are at barrier and are starting to eat.
```

## Zdroje
- prednáška číslo 2 z predmetu PPDS
- zdrojové kódy z 2. seminára predmetu PPDS dostupné na nasledujúcom linku: 
https://github.com/tj314/ppds-seminars/blob/ppds2024/seminar2/combining_tree_barrier.py