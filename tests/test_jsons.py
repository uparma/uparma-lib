#!/usr/bin/env python3
import json
import glob
import os

parameters_defined_fields = [
    "_id",
    "name",
    "triggers_rerun",
    "description",
    "default_value",
    "value_type",
    "tag",
    "value_translations",
    "key_translations"

]

styles_defined_fields = [
    'style',
    'name',
    'versions',
    'reference',
]

def uprint(msg, ok=True):
    if ok:
        indicator = '[   OK!   ]'
    else:
        indicator = '[ WARNING ]'
    if len(msg) > 65:
        msg = msg[:62] + '...'
    print('{0:65}{1}'.format(msg, indicator))
    return

def jsons_are_readable(rcode, jsons):
    """
    Read and validate jsons are formatted correctly
    """
    local_rcode = 0
    for json_file in glob.glob(os.path.join('./jsons/','*.json')):
        json_file_basename = os.path.basename(json_file)
        try:
            jsons[json_file_basename] = json.load(open(json_file,'r'))
            uprint('File {0} readable'.format(json_file_basename))
        except Exception as e:
            uprint('File {0} corrupt'.format(json_file_basename), ok=False)
            local_rcode = 1
    rcode += local_rcode
    return jsons, rcode

def parameter_ids_are_unique(rcode, jsons):
    """
    Check if _ids are unique
    """
    local_rcode = 0
    all_ids = set()
    for pos, entry in enumerate(jsons['parameters.json']):
        if entry['_id'] in all_ids:
            uprint(
                '{_id} already exists in parameters.json'.format(**entry),
                ok=False
            )
            local_rcode = 2
        all_ids.add(entry['_id'])
    if len(all_ids) == pos:
        uprint('All _ids are unique')
    rcode += local_rcode
    return jsons, rcode

def param_styles_exist_in_styles(rcode, jsons):
    '''
    Check if all styles in parameters.json are defined in styles.json
    '''
    local_rcode = 0
    all_styles = set()
    for style in jsons['styles.json']:
        all_styles.add(style['style'])
    for pos, entry in enumerate(jsons['parameters.json']):
        for field in entry.keys():
            if field not in parameters_defined_fields:
                if field not in all_styles:
                    uprint(
                        'Style {0} (in _id {_id}) is not defined in styles.json'.format(
                            field,
                            **entry
                        ),
                        ok=False
                    )
                    local_rcode = 4
    if local_rcode == 0:
        uprint('All styles in parameters.json are defined in styles.json')
    rcode += local_rcode
    return jsons, rcode

def params_have_defined_fields(rcode, jsons):
    '''
    Check if each entry in parameters.json has all defined fields (listed in parameters_defined_fields).
    NOTE:
        Not checking if additional/undefined fields are present
    '''
    local_rcode = 0
    for entry in jsons['parameters.json']:
        for field in parameters_defined_fields:
            if field not in entry.keys():
                uprint(
                    'Parameter {_id} is missing {0}'.format(
                        field,
                        **entry,
                    ),
                    ok=False
                )
                local_rcode = 8
    if local_rcode == 0:
        uprint('All parameters have all defined fields')
    rcode += local_rcode
    return jsons, rcode

def styles_have_defined_fields(rcode, jsons):
    '''
    Check if each entry in styles.json has all defined fields (listed in styles_defined_fields).
    NOTE:
        Not checking if additional/undefined fields are present
    '''
    local_rcode = 0
    for entry in jsons['styles.json']:
        for field in styles_defined_fields:
            if field not in entry.keys():
                uprint(
                    'Style {style} is missing {0}'.format(
                        field,
                        **entry,
                    ),
                    ok=False
                )
                local_rcode = 16
    if local_rcode == 0:
        uprint('All styles have all defined fields')
    rcode += local_rcode
    return jsons, rcode

def styles_have_citation(rcode, jsons):
    local_rcode = 0
    for entry in jsons['styles.json']:
        if len(entry.get('versions', [])) != 0:
            if len(entry.get('reference', '')) == 0:
                # Better> could be nice citation regex!
                uprint('Style {name} haz no reference!'.format(**entry), ok=False)
                local_rcode = 32
    if local_rcode == 0:
        uprint('All styles af references')
    rcode += local_rcode
    return jsons, rcode

def main():
    """
    Check overall integrity of uparma jsons
    """
    rcode = 0 # success
    jsons = {}
    jsons, rcode = jsons_are_readable(rcode, jsons)
    jsons, rcode = parameter_ids_are_unique(rcode, jsons)
    jsons, rcode = param_styles_exist_in_styles(rcode, jsons)
    jsons, rcode = params_have_defined_fields(rcode, jsons)
    jsons, rcode = styles_have_defined_fields(rcode, jsons)
    jsons, rcode = styles_have_citation(rcode, jsons)
    return rcode

if __name__ == '__main__':
    exit(main())
