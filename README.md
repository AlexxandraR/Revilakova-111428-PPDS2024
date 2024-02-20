# Dokumentácia k zadaniu číslo 1

Cieľom zadania bolo simulovať rannú rutinu Jana a Fera. Táto rutina mala podmienku, 
že Fero mohol začať jesť raňajky až po tom, čo sa Jano najedol a zavolal mu.

V implementácii som vytvorila dve samostatné vlákna. Jedno pre simuláciu Janovej 
rutiny a druhé pre Ferovu. Rutiny pozostávajú z vykonávania nasledujúcich 
postupností: 
- Jano - sleeps, hygiene, eat, call,
- Fero - sleeps, hygiene, receive call, eat.

Aby som zabezpečila, že Fero neprijme hovor pred tým, ako mu Jano zavolá, využila 
som abstraktný údajový typ Semafor, ktorého stav som nastavila na 0. Konkrétne 
som použila funkciu wait, na vlákne reprezentujúcom Fera, pri vykonávaní receive 
call a funkciu signal, na vlákne reprezentujúcom Jana, pri vykonávaní call.

## Ukážka výstupu:

Jano sleeps. <br>
Fero sleeps. <br>
Fero´s hygiene. <br>
Jano´s hygiene. <br>
Jano eats. <br>
Jano calls. <br>
Fero receives call. <br>
Fero eats. <br>
Both finished their tasks.

## Zdroje:
- prednáška číslo 1 z predmetu PPDS
- zdrojové kódy z 1. seminára predmetu PPDS dostupné na nasledujúcom linku:
<https://github.com/tj314/ppds-seminars>