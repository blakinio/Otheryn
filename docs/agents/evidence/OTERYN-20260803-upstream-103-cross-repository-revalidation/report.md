# Audyt krzyżowy 103 elementów upstream

## Konkluzja wykonawcza

Audyt utrzymuje dokładnie 103 kanoniczne elementy. Piętnaście wierszy ma statycznie potwierdzoną lukę w dokładnym Otheryn, w tym cztery wysokiego ryzyka błędy C++ i jedną krytyczną lukę atomowości zakupu NPC. Nie znaleziono elementu już naprawionego w Otheryn. Dwadzieścia jeden elementów nie wymaga działania w Otheryn, ponieważ są poza zakresem produktu/architektury albo zostały zastąpione. Pozostałe elementy wymagają reprodukcji, decyzji kontraktowej albo dokładniejszych dowodów; nie są przedstawiane jako potwierdzone defekty.

## Dokładne bazowe rewizje

| Repozytorium | Rewizja |
|---|---|
| `blakinio/Otheryn` | task-start audited snapshot `1f316400053f489e58608d13961069835871ab0e`; final drift head `3186099e69b05ba17966f1ebe8caeedc3302ae51` |
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` |

Cztery repozytoria porównawcze nie zmieniły głównego SHA względem końca poprzedniego audytu. Po starcie zadania Otheryn przeszedł z `1f316400…` do `3186099e…` przez PR `#285` (PRS-004C durable writer-fence CAS). Zmiana dotyczy nowego repozytorium CAS, migracji 60, schematu, testów i workflow; nie pokrywa się z dokładnymi ścieżkami 15 potwierdzonych luk. Dla wierszy multiworld i binary player persistence ponownie sprawdzono granicę: nowy writer-fence nie definiuje world identity/routingu i nie zastępuje player persistence, więc decyzje pozostają niezmienione.

Pola `otheryn_exact_revision` w dwóch inwentarzach zachowują dokładny snapshot, na którym wykonano pełną analizę wierszową (`1f316400…`). Późniejszy head `3186099e…` jest udokumentowany i zweryfikowany jako osobny target-drift, a nie retroaktywnie przedstawiany jako pierwotny snapshot.

## Odzyskanie zakresu kanonicznego

Poprzedni `inventory.json.gz` jest uszkodzony i pozostaje jawnym konfliktem dowodowym. Niezmienny plik towarzyszący `inventory.csv.gz` jest poprawnym gzipem i daje dokładnie:

- 103 wiersze;
- 103 unikalne klucze;
- 14 PR upstream Canary;
- 60 Issues upstream Canary;
- 20 PR CrystalServer;
- 9 Issues CrystalServer.

Odzyskano wyłącznie tożsamość i pola poprzednich wierszy. Nie zastąpiono zakresu bieżącymi otwartymi elementami. Nowy upstream Canary Issue `#4059` jest wyłącznie dodatkiem driftowym.

## Metodyka

Dla każdego wiersza zachowano bieżący stan źródła, poprzednią klasyfikację, pięć perspektyw repozytoryjnych, status dowodu i decyzję właściciela. PR-y zostały ponownie sprawdzone: wszystkie 34 są nadal otwarte i wszystkie 34 zachowały dokładny kanoniczny head. Wszystkie 69 kanonicznych Issues pozostają otwarte. Konektor nie dostarczył wiarygodnej różnicy komentarzy/aktywności Issue między punktem kanonicznym a bieżącym, dlatego raport nie twierdzi, że dyskusje Issues są niezmienione.

Statyczny dowód `PROVEN` wymaga dokładnego symbolu/ścieżki lub bezpośredniej architektonicznej nieaplikowalności. Sam tytuł, podobna ścieżka, opis Issue albo donor PR nie są dowodem. Pozostałe wiersze zachowują `PARTIALLY_PROVEN`, `UNPROVEN` albo `BLOCKED_BY_DECISION` i dokładnie opisują brakujący dowód.

## Wyniki

| Decyzja właściciela | Liczba |
|---|---:|
| `CONFIRMED_OTHERYN_GAP` | 15 |
| `ALREADY_FIXED_IN_OTHERYN` | 0 |
| `NO_OTHERYN_ACTION` | 21 |
| `RUNTIME_REPRODUCTION_REQUIRED` | 49 |
| `ARCHITECTURE_DECISION_REQUIRED` | 4 |
| `CLIENT_CONTRACT_DECISION_REQUIRED` | 1 |
| `PERSISTENCE_MIGRATION_DECISION_REQUIRED` | 2 |
| `INSUFFICIENT_EVIDENCE` | 11 |

Statusy dowodowe: `PROVEN=36`, `PARTIALLY_PROVEN=7`, `UNPROVEN=54`, `BLOCKED_BY_DECISION=6`.

## Potwierdzone luki Otheryn

- `opentibiabr/canary#4058` i Issue `#3986`: Otheryn oraz CrystalServer nadal blokują `playerSaySpell` przez `walkExhausted`; `blakinio/canary` ma już wąską poprawkę.
- `opentibiabr/canary#4054`: zmiana nazwy potwora nadal używa odświeżenia tile zamiast pełnego reloadu znanej kreatury.
- `opentibiabr/canary#4053`: dokładny skrypt Storkusa w Otheryn zawiera stare błędy stroju, licznika i dialogu.
- `opentibiabr/canary#4045`: Otheryn ma stare ilości/ceny Prey Wildcards.
- `opentibiabr/canary#4044`: jedenaście NPC Djinn nadal odrzuca zwykłe powitanie mimo rozpoznanej frakcji.
- `opentibiabr/canary#4025`: stare granice rundy i liczniki Barbarian Mead pozostają w dwóch dokładnych ścieżkach.
- `zimbadev/crystalserver#851`: stash jest pomniejszany przed pełnym umieszczeniem bez zwrotu niedostarczonej części.
- `#850`: `exp / rawExp` nie chroni `rawExp == 0`.
- `#849`: `sendUpdateTileCreature` dereferencjonuje pusty tile.
- `#848`: deserializowane indeksy warunku nie są ograniczane przed zapisem do tablic.
- `#846`: warunek salda przy guild deposit jest odwrócony.
- `#845`: SoulCage dereferencjonuje pustego attacker.
- `#844`: stan `alreadyExecuted` blokuje ponowne wykonanie cyklicznej inwazji w tym samym procesie.
- `#122`: przed pobraniem zapłaty towary są już dostarczone; donor prevalidation nie daje pełnej atomowości, dlatego potrzebny jest rewrite.

## Najwyższe ryzyko

- Krytyczne: `zimbadev/crystalserver#122` — atomowość waluta/towar.
- Wysokie: `#851` — utrata przedmiotów ze stash; `#850` — dzielenie przez zero; `#849` — null dereference; `#848` — zapis poza zakresem.
- Wysokie, ale niepotwierdzone runtime: `opentibiabr/canary#3605`, `#3513`, `#3427`, `#3374`, CrystalServer `#785/#852`.
- Wysokie decyzje: rodzina Expert/Open PvP (`#4033/#810/#813/#445`) i multiworld (`#2826/#451`).

## Zmiany względem poprzedniej klasyfikacji

Nie zmieniono żadnego bucketu poprzedniego audytu bez nowego dowodu. Dwa wiersze rodziny paralyze/spell (`#4058`, `#3986`) zostały **wzmocnione**, ponieważ `blakinio/canary` ma już wąską poprawkę, podczas gdy Otheryn i CrystalServer nadal zawierają defekt. Pozostałe wcześniejsze kandydatury są potwierdzone; niepewne wiersze pozostają jawnie niepotwierdzone albo wymagają reprodukcji/kontraktu.

## Jawne nie-claimy

- Nie wykonano implementacji i nie zmieniono ścieżek wykonywalnych.
- Nie stwierdzono produkcyjnej gotowości żadnej poprawki.
- Nie użyto samego PR/Issue jako autorytetu.
- Nie wykonano runtime E2E tego audytu; jest `NOT_APPLICABLE`, ponieważ wynik jest wyłącznie dokumentacją/dowodem.
- Nie stwierdzono braku nowej aktywności komentarzowej Issues; konektor nie dostarczył wiarygodnego delta-metadata.
- Nie utworzono ani nie zmieniono Issues `#313`–`#326`.

## Drift

Wszystkie 34 kanoniczne PR-y pozostają otwarte z niezmienionymi headami. Wszystkie 69 kanonicznych Issues pozostają otwarte. Upstream Canary `#4059` pojawił się po zamrożeniu zakresu i nie jest częścią 103 wierszy. Otheryn main przeszedł do `3186099e69b05ba17966f1ebe8caeedc3302ae51`; jego jedyny nowy pakiet PRS-004C został zintegrowany z gałęzią audytu i nie zmienił żadnej klasyfikacji.

Szczegółowe 103 wiersze znajdują się w `matrix.md`, a pełne pola dowodowe w deterministycznych `inventory.json.gz` i `inventory.csv.gz`.
