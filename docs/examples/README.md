# Examples

Real-world examples and sample outputs for the OSRS Wiki Page Tool.

## Table of Contents

- [Slayer Task Weight Extraction](#slayer-task-weight-extraction)
- [Calculator Page Analysis](#calculator-page-analysis)
- [Template and Module Discovery](#template-and-module-discovery)
- [Category Exploration](#category-exploration)
- [Output Format Examples](#output-format-examples)

## Slayer Task Weight Extraction

The primary use case - extracting complete slayer task weight data from the wiki's calculator system.

### 1. Main Calculator Configuration

Extract the JavaScript calculator configuration:

```bash
python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates --format text
```

**Output snippet:**
```
{{external|rs=calculator:Slayer}}{{Calc use|Calculator:Slayer/Slayer task weight/Template}}

{{JSCalculator}}
<pre class="jcConfig">
template = Calculator:Slayer/Slayer task weight/Template
form = slayWeightCalcForm
result = slayWeightCalcResult
param = master|Slayer Master|Turael|buttonselect|Turael,Krystilia,Mazchna,Vannaka,Chaeldar,Konar,Nieve,Duradel|Turael=combatLevel,slayerLevel,priestInPeril,porcineOfInterest;Krystilia=slayerLevel...
```

### 2. Complete Weight Tables

Extract the Lua module containing all slayer master weight tables:

```bash
python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text
```

**Output snippet:**
```lua
local turael = {
[SlayerConsts.TASK_BANSHEES] = { name = "[[Banshee]]s", requirements = {Slayer = 15, Combat = 20, Quest = SlayerConsts.QUEST_PRIEST_IN_PERIL}, weight = 8},
[SlayerConsts.TASK_BATS] = { name = "[[Bat]]s", requirements = {Combat = 5}, weight = 7},
[SlayerConsts.TASK_BIRDS] = { name = "[[Bird]]s", requirements = {}, weight = 6},
...
}

local duradel = {
[SlayerConsts.TASK_ABERRANT_SPECTRES] = { name = "[[Aberrant spectre]]", requirements= {Slayer= 60, Combat= 65, Quest= SlayerConsts.QUEST_PRIEST_IN_PERIL}, weight= 7},
[SlayerConsts.TASK_ABYSSAL_DEMONS] = { name = "[[Abyssal demon]]", requirements= {Slayer= 85, Combat= 85, Quest= SlayerConsts.QUEST_PRIEST_IN_PERIL}, weight= 12},
...
}
```

### 3. Calculation Logic

Extract the calculation algorithm:

```bash
python wiki_tool.py source "Module:Slayer weight calculator" --format text
```

**Output snippet:**
```lua
function p.calculate_percents(effectiveTable, unavailableTable)
    local totalWeight = 0
    for k, v in pairs(effectiveTable) do
        totalWeight = totalWeight + v['weight']
    end

    local percentageTable = {}
    for k, v in pairs(effectiveTable) do
        percentageTable[v['name']] = v['weight']/totalWeight
    end
    return percentageTable
end
```

### Key Data Extracted

From this process, you can extract:

- **8 Slayer Masters:** Turael, Krystilia, Mazchna, Vannaka, Chaeldar, Konar, Nieve, Duradel
- **Task Weights:** Complete probability weights for each monster
- **Requirements:** Combat/Slayer levels, quest completions, unlocks
- **Boss Subtables:** Special boss task distributions for some masters
- **Configuration Parameters:** All form inputs and validation rules

## Calculator Page Analysis

### Combat Level Calculator

```bash
python wiki_tool.py source "Calculator:Combat level" --templates --format json
```

**Output:**
```json
{
  "page_title": "Calculator:Combat level",
  "wikitext": "{{Calc use|Template:Calculator/Combat level}}\n\n{{JSCalculator}}\n<pre class=\"jcConfig\">\ntemplate = Template:Calculator/Combat level\nform = combatForm\nresult = combatResult\nparam = attack|Attack|1|int|1-99\nparam = strength|Strength|1|int|1-99\nparam = defence|Defence|1|int|1-99\nparam = ranged|Ranged|1|int|1-99\nparam = prayer|Prayer|1|int|1-99\nparam = magic|Magic|1|int|1-99\nparam = hitpoints|Hitpoints|10|int|10-99\nautosubmit = enabled\n</pre>",
  "templates": [
    "Template:Calc use",
    "Template:JSCalculator",
    "Template:Calculator/Combat level"
  ],
  "modules": []
}
```

### Experience Table Calculator

```bash
python wiki_tool.py source "Calculator:Experience table" --format text
```

This reveals the XP calculation formulas and level progression tables used throughout the game.

## Template and Module Discovery

### Find All Slayer-Related Content

```bash
python wiki_tool.py category "Modules" --format json
```

Then filter for slayer content:
- `Module:SlayerConsts`
- `Module:Slayer weight calculator`  
- `Module:Slayer task library`
- `Module:SlayerConsts/MasterTables`

### Calculator Templates

```bash
python wiki_tool.py category "Calculator templates" --limit 20 --format csv
```

**Output:**
```csv
title,pageid,ns
"Template:Calculator/Combat level",12345,10
"Template:Calculator/Experience table",12346,10
"Template:Calculator/Melee max hit",12347,10
```

### Infobox Templates

```bash
python wiki_tool.py source "Template:Infobox Monster" --format text
```

This reveals the structure used for all monster pages, useful for understanding data organization.

## Category Exploration

### Discover Calculator Categories

```bash
python wiki_tool.py category "Calculators" --limit 10 --format json
```

**Output:**
```json
{
  "category": "Category:Calculators",
  "pages": [
    {
      "title": "Calculator:Combat level",
      "pageid": 12345,
      "ns": 0
    },
    {
      "title": "Calculator:Slayer/Slayer task weight", 
      "pageid": 12346,
      "ns": 0
    },
    {
      "title": "Calculator:Experience table",
      "pageid": 12347,
      "ns": 0
    }
  ],
  "count": 3
}
```

### Module Categories

```bash
python wiki_tool.py category "Modules" --limit 50 --format csv
```

Reveals all available Lua modules for data processing.

### Template Categories

```bash
python wiki_tool.py category "Templates" --limit 25 --format text
```

**Output:**
```
Template:Infobox Item
Template:Infobox Monster
Template:Infobox NPC
Template:Calculator/Combat level
Template:JSCalculator
...
```

## Output Format Examples

### JSON Format (Detailed)

```bash
python wiki_tool.py source "Template:Documentation" --templates --format json
```

**Complete Output:**
```json
{
  "page_title": "Template:Documentation",
  "wikitext": "<includeonly>{{#invoke:documentation|main|_content={{ {{#invoke:documentation|contentTitle}}}}}}</includeonly><noinclude>\n{{documentation|content=\nThis template automatically generates documentation for templates by transcluding a /doc subpage.\n\n== Usage ==\nSimply add {{t|documentation}} to the bottom of a template.\n}}\n</noinclude>",
  "templates": [
    "Template:T"
  ],
  "modules": [
    "Module:Documentation"
  ]
}
```

### CSV Format (Tabular)

```bash
python wiki_tool.py category "Skill calculators" --format csv
```

**Output:**
```csv
title,pageid,ns
"Calculator:Combat level",45621,0
"Calculator:Experience table",45622,0  
"Calculator:Melee max hit",45623,0
"Calculator:Magic max hit",45624,0
"Calculator:Ranged max hit",45625,0
```

### Text Format (Clean)

```bash
python wiki_tool.py source "Module:Coins" --format text
```

**Output:**
```lua
local p = {}

--[[
Determines if a value is an integer.
--]]
function p._isInteger(value)
    return type(value) == 'number' and value == math.floor(value)
end

function p.isInteger(frame)
    local value = frame.args[1]
    if value == nil then
        return 'false'
    end
    return p._isInteger(tonumber(value)) and 'true' or 'false'
end

return p
```

## Data Processing Workflow

### Complete Slayer Data Pipeline

1. **Extract calculator configuration:**
   ```bash
   python wiki_tool.py source "Calculator:Slayer/Slayer task weight" --templates > slayer_config.json
   ```

2. **Extract weight tables:**
   ```bash
   python wiki_tool.py source "Module:SlayerConsts/MasterTables" --format text > weight_tables.lua
   ```

3. **Extract constants:**
   ```bash
   python wiki_tool.py source "Module:SlayerConsts" --format text > constants.lua
   ```

4. **Process the Lua data** into your preferred format (JSON, CSV, database, etc.)

### Integration with Other Tools

The extracted data integrates well with:

- **sqlite-utils:** `sqlite-utils insert slayer.db tasks weight_tables.csv --csv`
- **pandas:** `pd.read_csv('slayer_data.csv')` for analysis
- **jq:** `jq '.wikitext' slayer_config.json` for JSON processing

---

**Previous:** [Development Guide](../development/README.md) | **Back to:** [Main README](../../README.md)