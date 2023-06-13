# FDA food defect levels handbook
How many rat hairs in your macaroni before the FDA considers it adulterated? The [FDA food defect levels handbook](https://www.fda.gov/food/ingredients-additives-gras-packaging-guidance-documents-regulatory-information/food-defect-levels-handbook) can tell you!

This little project [scrapes](https://github.com/cjwinchester/fda-food-defect-action-levels/blob/main/scrape.py) the main data table from this handbook into [a JSON file](https://github.com/cjwinchester/fda-food-defect-action-levels/blob/main/fda-food-defect-levels.json).

Each record in the JSON array includes:
- `commodity`: The name of the commodity
- `defect_action_levels`: An array of objects showing each defect action level for this commodity
- `defect_action_levels.defect_name`: The name of the defect, e.g. "Insect Filth"
- `defect_action_levels.action_level`: The level at which the FDA considers the commodity adulturated by this defect, e.g. "Average of 30 or more insect fragments per 10 grams"
- `defect_action_levels.method`: The FDA's code for the analytical methodology used to measure the defect, e.g. "AOAC 981.21"
- `defect_action_levels.method_link`: If available, a link to an FDA page with more detail on the methodology
- `defect_source`: Where the defect is typically discovered, e.g. "Insect fragments - pre/post harvest and processing insect infestation. Rodent hair - post harvest and/or processing contamination with animal hair or excreta"
- `significance`: Per FDA, "the real or potential impact on the consumer due to the presence of a particular defect," e.g. "Aesthetic"