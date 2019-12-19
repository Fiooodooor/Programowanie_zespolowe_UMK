# Repozytorium Programowania Zespołowego NSI 2017 - gr. 4 <br/> <br/>
## Spis treści
### 1. Struktura katalogów repozytorium. <br/>
### 2. Praca z repozytorium. <br/>
### 2.1. Podział na główne gałęzie w repozytorium.
### 2.2. Oznaczenie repozytorium.
### 2.3. Zmiany w repozytorium.
### 2.4. Nazewnictwo gałęzi.
### 2.5. Code Review. <br/>
### 3. Konwencje pracy z kodem.
### 3.1 Dokumentacja. <br/> <br/> <br/>

### 1. Struktura katalogów repozytorium:
<pre>
 /
│     README.md         plik readme
│     CHANGELOG.md      plik changelog służący do monitorowania poważnych zmian w strukturze repozytorium
│
│──── backend           zawiera zasoby związane z warstwą dostępu do danych
│   │
│   │───
│   │
│   │───
|
│─── dbms               zawiera zasoby związane z bazą danych i zarządzaniem nią
|
│─── docs               pliki dokumentacji projektu
│
│─── frontend           zawiera zasoby związane z warstwą prezentacji
│   │
│   │───
│   │
│   │───
│
│─── homepage           zawiera zasoby związane ze stroną projektu na maszynie wydziałowej
│
│─── mobile             zawiera zasoby związane z aplikacją mobilną
|
│─── uix                zawiera zasoby związane z opracowaniem interfejsu
│
│─── temp               pliki tymczasowe
</pre>
<br/>
<br/>

## 2. Praca z repozytorium
- praca z repozytorium odbywa się na zasadach ogólnej pracy z kontrolą wersji GIT,
- nic nie stoi na przeszkodzie, aby używać zautoamtyzowanej kontroli wersji póki jest ona zgodna z niniejszym README.md,
- członkowie projektu pracują w obrębie swoich zadań wpisanych w Trello.

### 2.1. Podział na główne gałęzie w repozytorium:
- master - instancja produkcyjna,
- test - instancja testowa,
- devel - instancja deweloperska.

Gałęzie są chronione - merge zmian jest możliwy dopiero po jego akceptacji w drodze Code Review.<br/>

### 2.2. Oznaczenie repozytorium.
Większe zmiany oraz numer aktualnej wersji będą zawierane w pliku CHANGELOG.md. <br/>

### 2.3. Zmiany w repozytorium.
Zmiana to jakiekolwiek działanie na repozytorium polegające na zmianie jego zawartości lub struktury.<br/>
- zmiany muszą być wykonywane przez wydzielanie branchy z docelowej gałęzi instancyjnej i następnie, po zakończeniu pracy na branchu, przez skorzystanie z mechanizmu Merge Request (bezpośrednie wypychanie zmian do jednego z branchy instancyjnych bez akceptacji jest możliwe tylko w wyjątkowych sytuacjach),
- Merge Request polega na ocenie zmian (kodu, plików binarnych, wpisów do dokumentacji, plików graficznych etc.) z danego brancha i spokojnej wymianie pomysłów na ewentualne poprawki pracy,
- wydzielenie następuje z tej gałęzi instancyjnej, do której mają trafić zmiany (szerzej w kolejnych akapitach),
- Merge Request musi być tak przygotowany, aby nie tworzył konfliktu przy Merge oraz powinien być stosownie opisany,
- w związku z potencjalnie dużą ilością zmian, rozsądnym będzie zrezygnować z podziału innego niż trzy instancje i zbiorowe gałęzie, ponieważ już na etapie deweloperskim rodzi to potrzebę mergowania osobnego brancha złożonego z 'n' branchy do brancha devel, gdzie możemy bezpośrednio mergować je do niego (zamiast devel <- backend (branche x, y, z,), devel <- (branche x, y, z)).

### 2.4. Nazewnictwo gałęzi
Nazwa gałęzi tworzonej przez programistę musi być postaci: <br/>
> [numer\_zadania]\_[directory\_w\_repozytorium]\_[bardzo\_zwiezly\_opis] 

**numer\_zadania** - pełna dowolność oznaczenia z uwzględnieniem, że zadanie powinno być identyfikowalne (np. numer, inicjały, pseudonim - tak, aby oznaczenie miało odzwierciedlenie w konkretnym zadaniu umieszczonym w karcie na Trello).<br/>
<br/>
**directory\_w\_repozytorium** - jest to ścieżka w repozytorium (ścieżka w nazwie nie wpływa na docelowe miejsce dodania zasobów do repozytorium, jest jedynie właściwością porządkującą). <br/>
<br/>
**bardzo\_zwiezly\_opis** - maksymalnie 100 znaków, na przykład nagłówek zadania na danej karcie Trello. <br/>

### Uwaga!
Nie należy oznaczać gałęzi, jak i commitów, nazwami typu "aazzz", "12345", "bebebebe", "fofo1212" - utrudnia to identyfikację zadań podczas Code Review oraz istnieje realne niebezpieczeństwo pokrycia nazwy brancha lub commita z hashem istniejącego działania w repozytorium, co będzie skutkować zablokowaniem niektórych operacji podczas pracy z kontrolą wersji (na szczęście odwracalnym). Nie należy także używać polskich znaków i zaleca się ograniczenie użycia znaków specjalnych innych niż te przyjęte jako interpunkcyjne.<br/>
<br/>
**Przykłady:** <br/>

> alusz2b\_backend\_dodanie\_mapowania\_tabeli\_users <br/>
> dszczu\_backend\_skrypt\_poprawiający\_szyfrowanie <br/>
> fiooodooor\_mobile\_dodanie\_nowych\_spinnerow <br/>
> om12\_dbms\_skrypty\_triggerow <br/>
> mw\_frontend\_skalowanie\_wyswietlania\_ekranu\_zespolow <br/>

### Hotfix / zmiany na teście:
W wypadku potrzeby dodania hotfixa lub poprawek w instancji testowej należy wydzielić tyle gałęzi ile jest to potrzebne (tj. 2-3) i wtedy dodać po oznaczeniu identyfikującym zadanie nazwę brancha instancyjnego: <br/>
> [numer\_zadania]\_[directory\_w\_repozytorium]\_[bardzo\_zwiezly\_opis]

**Przykłady:** <br/>

> alusz102a\_master\_poprawka\_w\_oknie\_formularza\_oceny <br/>
> alusz102a\_test\_poprawka\_w\_oknie\_formularza\_oceny <br/>
> alusz102a\_devel\_poprawka\_w\_oknie\_formularza\_oceny <br/>
> om12\_test\_dbms\_poprawki\_bezpieczenstwa <br/>
> om12\_devel\_dbms\_poprawki\_bezpieczenstwa <br/>

### Uwaga!
Branche bez nazwy brancha instancyjnego to domyślnie branche wydzielone deweloperskie (devel). <br/>

### Przykładowa ścieżka podczas pracy na instancji deweloperskiej:
- Dominik chce dodać skrypt optymalizujący dwie funkcje agregujące dane.
- Dominik przechodzi na DEVEL devel (pamiętając o komendzie **git pull*) i wydziela z niego przykładowego brancha dszczu32a\_backend\_optymalizacja\_funkcji\_foo\_i\_bar,
- po zakończeniu pracy dodaje pliki do poczekalni komendą **git add**, a następnie commituje zmiany (treść commita powinna zwięźle opisać zmiany).
- Dominik używając stosownej komendy wypycha zmiany do repozytorium zdalnego pamiętając o **squash-u** commitów.
- Ostatnim krokiem jest utworzenie na Githubie Merge Request celem Code Review zespołu.

### Przykładowa ścieżka podczas pilnej potrzeby zmian na branchach pozadeweloperskich:
- Olaf zdał sobie sprawę, że istnieje dość istotny problem związany z bezpieczeństwem, który jest zlokalizowany w skryptach automatycznie czyszczących cache maszyny.
- Odnalazł podatność i przystąpił do pracy, która polegała na modyfikacji skryptów pracujących automatycznie po uruchomieniu serwisów.
- Wydzieli z brancha MASTER (pamiętając o komendzie **git pull*) branch o nazwie omhf3\_master\_dbms\_poprawka\_skryptu\_cache\_w\_kronie i przejdzie do niego.
- Zakończy w nim prace, które doda do poczekalni i wykona commit.
- Następnie zmieni brancha na TEST, wydzieli z niego brancha o nazwie omhf3\_test\_dbms\_poprawka\_skryptu\_cache\_w\_kronie.
- Dokona mergu z branchem nadrzędnym komendą **git merge** omhf3\_master\_dbms\_poprawka\_skryptu\_cache\_w\_kronie.
- Następnie powtórzy operację z branchem DEVEL, czyli wydzieli z brancha devel brancha omhf3\_devel\_dbms\_poprawka\_skryptu\_cache\_w\_kronie i wykona **git merge** omhf3\_test\_dbms\_poprawka\_skryptu\_cache\_w\_kronie.
- Olaf ostatecznie wypycha wszystkie branche do repozytorium zdalnego i tworzy Merge Request celem Code Review zespołu.
- Github po zamieszczeniu Merge Requestów do Code Review powinien pokazać stosowną ilość zmian względem każdego brancha (1 na masterze i odpowiednią ilość nowych zmian z branchy test i devel).

### Uwaga!
Praca na branchach master i test należy do sytuacji wpadkowych i nie powinna być regułą. Aby zapewnić spójność aplikacji zmiany powinny przechodzić pełną drogę instancyjną: devel -> test -> master.<br/>
<br/>

### 2.5. Code Review.
Code Review jest wykonywane w zależności od danego modułu przez cały zespół lub przez osoby, które uczestniczą w jego tworzeniu na zasadzie wzajemnego informowania. Code Review mogą co do zasady wykonywać wszyscy, ale wskazane jest aby dla danego modułu uczestniczyły w nim obligatoryjnie następujące zestawy osób: <br/>
<br/>
Dla **backendu** Alicja, Dominik, Olaf, Miłosz, Mateusz. <br/>
Dla **frontendu** Alicja, Dominik, Mateusz. <br/>
Dla **bazy danych** Olaf, Miłosz, Dominik, Alicja. <br/>
Dla **aplikacji mobilnej** Alicja, Dominik, Miłosz. <br/>
Dla **UIX** Olaf, Miłosz, Mateusz. <br/>
<br/>
Dotyczy to zarówno kodu jak i dokumentacji. <br/>
<br/>
 
### 3. Konwencje pracy z kodem:
- co najistotniejsze CAŁY kod i dokumentacja jest tworzona w języku angielskim - jedynym odstępstwem od reguły jest niniejsze README.md,
- poruszamy się w ramach konwencji danego frameworku (np. dla Pythona konwencje snake_case, korzystanie z PyLint i Flake, dla bazy danych ANSI SQL),
- zwracamy uwagę na znaki końca lunii zgodne z Unix podczas przygotowania skryptów (aby kontrola wersji nie wariowała przy edytowaniu na różnych platformach i systemach),
- kodowanie UTF-8,
- nazwy skryptów są co do zasady dowolne, jednak powinny albo w nazwach własnych albo w dokumentacji (a najlepiej w obu miejscach) mieć oznaczenie w jakiej kolejności powiny być wykonywane,
- stosujemy komentarze w kodzie oprócz samej dokumentacji,
- zabronione jest pozostawianie segmentów zakomentowanego kodu celem powtórnego wykorzystania lub przeprowadzania quasi-testów jednostkowych - wszelkie notatki powinny być trzymane poza repozytorium (lub w dokumentacji, jeżeli miałby to być obszerniejszy in-line comment), a testy są oddzielnym zasobem.
<br/>

### 3.1 Dokumentacja:
- aby ułatwić kontrolę wersji dokumentacja będzie sporządzona w plikach TEX,
- dokumentacja powinna być prowadzona szczegółowo (z rozbiciem na poszczególne obiekty).
<br/>

###


