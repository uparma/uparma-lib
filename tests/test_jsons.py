#!/usr/bin/env python3
import json
import glob
import os
from collections import defaultdict as ddict

parameters_defined_fields = [
    "_id",
    "name",
    "triggers_rerun",
    "description",
    "default_value",
    "value_type",
    "tag",
    "value_translations",
    "key_translations",
]

styles_defined_fields = [
    "style",
    "name",
    "versions",
    "reference",
]


def uprint(msg, ok=True):
    if ok:
        indicator = "[   OK!   ]"
    else:
        indicator = "[ WARNING ]"
    if len(msg) > 65:
        msg = msg[:62] + "..."
    print("{0:65}{1}".format(msg, indicator))
    return


def jsons_are_readable(rcode, jsons):
    """
    Read and validate jsons are formatted correctly
    """
    local_rcode = 0
    for json_file in glob.glob(os.path.join("./jsons/", "*.json")):
        json_file_basename = os.path.basename(json_file)
        try:
            jsons[json_file_basename] = json.load(open(json_file, "r"))
            uprint("File {0} readable".format(json_file_basename))
        except Exception as e:
            uprint("File {0} corrupt".format(json_file_basename), ok=False)
            local_rcode = 1
    rcode += local_rcode
    return jsons, rcode


def parameter_ids_are_unique(rcode, jsons):
    """
    Check if _ids are unique
    """
    local_rcode = 0
    all_ids = set()
    for pos, entry in enumerate(jsons["parameters.json"]):
        if entry["_id"] in all_ids:
            uprint(
                "{_id} already exists in parameters.json".format(**entry),
                ok=False,
            )
            local_rcode = 2
        all_ids.add(entry["_id"])
    if len(all_ids) == pos:
        uprint("All _ids are unique")
    rcode += local_rcode
    return jsons, rcode


def param_styles_exist_in_styles(rcode, jsons):
    """
    Check if all styles in parameters.json are defined in styles.json
    """
    local_rcode = 0
    all_styles = set()
    for style in jsons["styles.json"]:
        all_styles.add(style["style"])
    for pos, entry in enumerate(jsons["parameters.json"]):
        for style in entry["key_translations"].keys():
            if style not in all_styles:
                uprint(
                    "Style {0} (in _id {_id}) is not defined in styles.json".format(
                        style, **entry
                    ),
                    ok=False,
                )
                local_rcode = 4
    if local_rcode == 0:
        uprint("All styles in parameters.json are defined in styles.json")
    rcode += local_rcode
    return jsons, rcode


def params_have_defined_fields(rcode, jsons):
    """
    Check if each entry in parameters.json has all defined fields (listed in parameters_defined_fields).
    NOTE:
        Not checking if additional/undefined fields are present
    """
    local_rcode = 0
    for entry in jsons["parameters.json"]:
        for field in parameters_defined_fields:
            if field not in entry.keys():
                uprint(
                    "Parameter {_id} is missing {0}".format(
                        field,
                        **entry,
                    ),
                    ok=False,
                )
                local_rcode = 8
    if local_rcode == 0:
        uprint("All parameters have all defined fields")
    rcode += local_rcode
    return jsons, rcode


def styles_have_defined_fields(rcode, jsons):
    """
    Check if each entry in styles.json has all defined fields (listed in styles_defined_fields).
    NOTE:
        Not checking if additional/undefined fields are present
    """
    local_rcode = 0
    for entry in jsons["styles.json"]:
        for field in styles_defined_fields:
            if field not in entry.keys():
                uprint(
                    "Style {style} is missing {0}".format(
                        field,
                        **entry,
                    ),
                    ok=False,
                )
                local_rcode = 16
    if local_rcode == 0:
        uprint("All styles have all defined fields")
    rcode += local_rcode
    return jsons, rcode


def styles_have_citation(rcode, jsons):
    local_rcode = 0
    for entry in jsons["styles.json"]:
        if len(entry.get("versions", [])) != 0:
            if len(entry.get("reference", "")) == 0:
                # Better> could be nice citation regex!
                uprint("Style {name} haz no reference!".format(**entry), ok=False)
                local_rcode = 32
    if local_rcode == 0:
        uprint("All styles af references")
    rcode += local_rcode
    return jsons, rcode


def key_translations_are_unique(rcode, jsons):
    local_rcode = 0
    key_translations = {}

    for entry in jsons["parameters.json"]:
        for style, translated_key in entry["key_translations"].items():
            if style not in key_translations.keys():
                key_translations[style] = ddict(list)
            # print(style, translated_key)
            if isinstance(translated_key, list):
                translated_key = tuple(translated_key)
            key_translations[style][translated_key].append(entry["name"])

    for style in key_translations.keys():
        for translated_key, names in key_translations[style].items():
            if len(names) > 1:
                uprint(
                    f"Style {style} has translated key {translated_key} that maps,",
                    ok=False,
                )
                uprint(
                    f"    onto multiple names {names} hence no mapping can be done.",
                    ok=False,
                )
                local_rcode = 2 ** 6

    if local_rcode == 0:
        uprint("All mapped keys are unique")
    rcode += local_rcode
    return jsons, rcode


def key_translations_in_list_form_have_single_entries(rcode, jsons):
    local_rcode = 0
    list_entries = set()
    single_entries = set()

    for entry in jsons["parameters.json"]:
        for style, translated_key in entry["key_translations"].items():
            if isinstance(translated_key, list):
                for e in translated_key:
                    list_entries.add((style, e))
            else:
                single_entries.add((style, translated_key))
    overlap = list_entries - single_entries
    if len(overlap) == 0:
        uprint(f"all key translations in list form have single entries as well", ok=True)
    else:
        uprint("Those list key translations do not exist as single entries:", ok=False)
        for e in sorted(list(overlap)):
            uprint(
                f"{e}",
                ok=False,
            )
        local_rcode = 2 ** 7
    rcode += local_rcode
    return jsons, rcode


def main():
    """
    Check overall integrity of uparma jsons
    """
    rcode = 0  # success
    jsons = {}
    jsons, rcode = jsons_are_readable(rcode, jsons)
    jsons, rcode = parameter_ids_are_unique(rcode, jsons)
    jsons, rcode = param_styles_exist_in_styles(rcode, jsons)
    jsons, rcode = params_have_defined_fields(rcode, jsons)
    jsons, rcode = styles_have_defined_fields(rcode, jsons)
    jsons, rcode = styles_have_citation(rcode, jsons)
    jsons, rcode = key_translations_are_unique(rcode, jsons)
    # jsons, rcode = key_translations_in_list_form_have_single_entries(rcode, jsons)
    return rcode


if __name__ == "__main__":
    exit(main())
