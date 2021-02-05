import ursgal.uparams_short as param_s
import ursgal
import json
from pathlib import Path

# new files are generated in the helper directory with this code
param_json_path = Path(__file__).parent.joinpath("new_parameters.json")
styles_json_path = Path(__file__).parent.joinpath("new_styles.json")

new_params = []
uparams = ursgal.uparams.ursgal_params

tags_per_param = {0: 0, 1: 0, 2: 0, 3: 0}
params_per_tag = {}
params_per_tagset = {}
tag_sets = set()
styles = {"ursgal_style_1": 0}

for idx, ursgal_key in enumerate(uparams):
    summary = {
        "_id": idx + 1,
        "name": ursgal_key,
        "triggers_rerun": uparams[ursgal_key]["triggers_rerun"],
        "description": uparams[ursgal_key]["description"],
        "default_value": uparams[ursgal_key]["default_value"],
        "value_type": uparams[ursgal_key]["uvalue_type"]
    }

    utags = sorted(uparams[ursgal_key]["utag"])
    try:
        tags_per_param[len(utags)] += 1
    except KeyError:
        tags_per_param[len(utags)] = 1

    for utag_name in utags:
        try:
            params_per_tag[utag_name] += 1
        except KeyError:
            params_per_tag[utag_name] = 1

    tags_str = str(utags)
    tag_sets.add(tags_str)
    try:
        params_per_tagset[tags_str] += 1
    except KeyError:
        params_per_tagset[tags_str] = 1

    summary["tag"] = utags

    key_translation = {"ursgal_style_1": ursgal_key}
    value_translation = {}
    styles["ursgal_style_1"] += 1

    for ukey in uparams[ursgal_key]["ukey_translation"]:
        key_translation[ukey] = uparams[ursgal_key]["ukey_translation"][ukey]

        try:
            value_translation[ukey] = list(uparams[ursgal_key]["uvalue_translation"][ukey].items())
        except KeyError:
            pass

        try:
            styles[ukey] += 1
        except KeyError:
            styles[ukey] = 1

    summary["value_translations"] = value_translation
    summary["key_translations"] = key_translation
    #     summary.update(key_translation)

    new_params.append(summary)

# kick out all duplicate entries.
# analyse the data to ensure that all key_translations are unique
key_to_names = {}
duplicates = set()
for param in new_params:
    for style, key_t in param["key_translations"].items():
        try:
            key_to_names[style][key_t].append((param["name"], param["_id"]))
            # name is in multiple parameters
            duplicates.add((style, key_t))
        except KeyError:
            if not style in key_to_names:
                key_to_names[style] = {}

            key_to_names[style][key_t] = [(param["name"], param["_id"])]

# report duplicates and remove from new_params
if len(duplicates) > 0:
    print("ERROR: key translations found in multiple parameters")
    for d in duplicates:
        names = []
        for name_id in key_to_names[d[0]][d[1]]:
            names.append(name_id[0])
            print(f"removing: {d}, from {name_id}")
            assert d[0] in new_params[name_id[1] - 1]["key_translations"]
            del new_params[name_id[1] - 1]["key_translations"][d[0]]

            # also remove the style from the value_translations if present
            if d[0] in new_params[name_id[1] - 1]["value_translations"]:
                del new_params[name_id[1] - 1]["value_translations"][d[0]]

        # print(f"style: {d[0]}, key: {d[1]} found in {d}")
    print("\nAll instances have been removed from parameters.json")

fout = open(str(param_json_path), "w")
fout.write(json.dumps(new_params, indent=2))
fout.close()

# now fetch the style data
uc = ursgal.UController()
new_styles_dict = {
    "ursgal_style_1": {
        "style": "ursgal_style_1",
        "name": "Ursgal",
        "versions": [
            "0.6.0",
            "0.6.1"
        ],
        "reference": [
            "Kremer, L. P. M., Leufken, J., Oyunchimeg, P., Schulze, S. & Fufezan, C. (2016) Ursgal, Universal Python Module Combining Common Bottom-Up Proteomics Tools for Large-Scale Analysis. J. Proteome res. 15, 788-794."
        ]
    },
    "ucontroller_style_1": {
        "style": "ucontroller_style_1",
        "name": "Ursgal Controller",
        "versions": [
            "0.6.0",
            "0.6.1"
        ],
        "reference": [
            "Kremer, L. P. M., Leufken, J., Oyunchimeg, P., Schulze, S. & Fufezan, C. (2016) Ursgal, Universal Python Module Combining Common Bottom-Up Proteomics Tools for Large-Scale Analysis. J. Proteome res. 15, 788-794."
        ]
    }
}
# iterate over the unode data
for style in uc.unodes:
    if style.startswith("_"):
        continue
    meta = uc.unodes[style]["META_INFO"]
    utrans = meta["utranslation_style"]
    if utrans in styles:
        # this matches to a loaded style
        if utrans in new_styles_dict:
            # already found so add new versions only
            new_styles_dict[utrans]["versions"].append(meta["version"])
        else:
            new_styles_dict[utrans] = {
                "style": meta["utranslation_style"],
                "name": meta["name"],
                "versions": [meta["version"]],
                "reference": meta["citation"]
            }

new_styles = []
for s, meta in new_styles_dict.items():
    new_styles.append(meta)

fout = open(str(styles_json_path), "w")
fout.write(json.dumps(new_styles, indent=2))
fout.close()

print("Finished")

print(f"# parameters:       {len(new_params)}")
print(f"# unique tags:      {len(params_per_tag)}")
print(f"# tag combinations: {len(tag_sets)}")
print(f"# styles:           {len(styles)}")

