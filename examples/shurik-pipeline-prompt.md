# Пример полного пайплайна Шурика

```text
/shurik
Артикул: Ц0081444
Поставщик: https://33komoda.ru/catalog/shkafy_raspashnye/shkaf_mori_msh900_1_2dveri_2_yashchika_belyy/
Производитель: https://dsv-mebel.ru/mebel/modul-mori-s-90-d2sz2/
Конкурент Ozon: https://www.ozon.ru/product/...
Комната: Детская

Сначала: `py scripts/card_registry.py check Ц0081444` (если DUPLICATE — только обновление, без новых фото)

Сделай:
1) /core по нише «шкаф белый 90 см распашной» если нет готового research/semantic-core-runs
2) artyom → Ц0081444.research.md
3) карточку + фото + row.json + Excel
4) zhenya-ozon — вычитка названия и аннотации
```

Серия:

```text
/shurik серия Mori
Артикулы: Ц0081444, Ц0081445
Общее: бренд ДСВ, серия Mori, детская
(на каждый артикул — свои ссылки поставщика)
```
