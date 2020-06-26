# Pova--my-part

Moja časť práce do jedného z týmových  projektov v tomto roku magisterského študia. Mojou úlohou bolo z dostupných šablón značiek a fotiek z ciest ktoré neobsahovali značky vytvoriť dva datasety (jeden pre klasifikáciu a jeden pre detekciu) s rovnomerným rozdelením a dostatočným množstvom dát.

Popis modulov:

- generate_ran_bg.py - Generovanie náhodných výrozov z vstupného datasetu. Mali sme malú množinu obrázkov ciest vo veľkom (4K) rozlíšení. Na trénovanie sme potrebovali veľké množstvo v malom rozlíšení.
- generate_aug_tmp.py - Aplikuje rôzne transformácie (affine, farebné) na obrázky z vstupného datasetu. Mali sme šablóny značiek. Z každej bolo nutné vytvoriť väčšie množstvo unikátnych vzoriek.
- insert_templates_to_bg.py - Vkladanie značiek do pozadia. Vytvorenie datasetov s vhodnou štruktúrou a korektným zápisom GT.
