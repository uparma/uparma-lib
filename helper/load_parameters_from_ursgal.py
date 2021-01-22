import ursgal.uparams_short as param_s
import ursgal.uparams as param
import json
from pathlib import Path

json_path = Path(__file__).parent.joinpath("new_parameters.json")

new_params = []
uparams = param.ursgal_params

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

fout = open(str(json_path), "w")
fout.write(json.dumps(new_params, indent=2))
fout.close()

print("Finished")

print(f"# parameters:       {len(new_params)}")
print(f"# unique tags:      {len(params_per_tag)}")
print(f"# tag combinations: {len(tag_sets)}")
print(f"# styles:           {len(styles)}")

