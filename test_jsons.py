#!/usr/bin/env python3
import json
import glob
import os


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
    for json_file in glob.glob(os.path.join('.','*.json')):
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


def styles_are_consistent(rcode, jsons):
    local_rcode = 0
    if False:
        local_rcode = 4

    rcode += local_rcode
    return jsons, rcode

def styles_have_citation(rcode, jsons):
    local_rcode = 0
    for entry in jsons['styles.json']:
        if len(entry.get('versions', [])) != 0:
            if len(entry.get('reference', '')) == 0:
                # Better> could be nice citation regex!
                uprint('Style {name} haz no reference!'.format(**entry), ok=False)
                local_rcode = 8
    if local_rcode == 0:
        uprint('All styles af references')
    rcode += local_rcode
    return jsons, rcode

def main():
    """
    Check over all integrity of uparma jsons
    """
    rcode = 0 # success
    jsons = {}
    jsons, rcode = jsons_are_readable(rcode, jsons)
    jsons, rcode = parameter_ids_are_unique(rcode, jsons)
    jsons, rcode = styles_are_consistent(rcode, jsons)
    jsons, rcode = styles_have_citation(rcode, jsons)
    return rcode

if __name__ == '__main__':
    exit(main())
