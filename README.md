uparma-lib: Lookup library for parameters for bioinformatic tools
=================================================================

[![image](https://github.com/uparma/uparma-lib/actions/workflows/json_integrity.yml/badge.svg)](https://github.com/uparma/uparma-lib/actions/workflows/json_integrity.yml)

Frequently, we encounter bioinformatics tools designed for identical functions. However, the absence of a 
unified set of parameters complicates the process of assessing a collection of tools addressing the same 
issue, as it requires the translation of parameters.

The Universal Parameter Mapper Project tackles this issue by providing a standard, independent framework for mapping between diverse styles.


APIs
----

Currently the following API exist
- [Python](https://github.com/uparma/uparma-py)
- ...


Rules
------
- All styles have to have a reference to the original work
- Each engine version can only be associated to one translation style

Parameter translations
------
 
All parameter translation have to be registered in the `parameter.json` file. The base design of a parameter is defined in a nested dict structure:

```
{
    "default_value": "some_value",
    "description": "Some useful description.",
    "key_translations": {
        "your_tool_style_1": "tool_parameter_name",
        "ursgal_style_1": "ursgal_parameter_name"
    },
    "name": "uparma_parameter_name",
    "tag": [
        "optional_tag_for_parameter"
    ],
    "triggers_rerun": false,
    "value_translations": {},
    "value_type": "str"
    }
```

### **Registering new parameters**

Before you register your parameter, make a quick search among the parameters if it might already exist in the list. If so, you can simply add your style to the key_translation dict, and if needed add/update value translations.

If you came to the conclusion that you require a new parameter defintion, copy the default block from above, or simply any other parameter in the list. Don't forget to update all fields to match the purpose and type of your parameter.

### **Updating value translations**

The main purpose of this project is to be able to map parameters across tools. Some tools also require a value translation to properly work with the provided parameter. A prominent example are boolean values, which have to be translated to 0/1 or even tool specific flags.

To add/update a value translation you have to add a list of translations into the value_translations dict:

```
{
        "default_value": false,
        "description": "Reduces the number of spurious junctions",
        "key_translations": {
            "star_style_1": "--outFilterType",
            "ursgal_style_1": "aligner_filter_spurious_junctions"
        },
        "name": "aligner_filter_spurious_junctions",
        "tag": [
            "alignment"
        ],
        "triggers_rerun": true,
        "value_translations": {
            "star_style_1": [
                [
                    false,
                    "Normal"
                ],
                [
                    true,
                    "BySJout"
                ]
            ],
            "ursgal_style_1": [
                [
                    false,
                    false
                ],
                [
                    true,
                    true
                ]
            ]
        },
        "value_type": "bool"
    }
```

the value translations are a list of lists for your desired style. Each individual value translation is a list of two elements: `[uparma_param_value, tool_param_value]`.
**Note:** to make the whole translation logic work in any direction, the value translations **MUST** also be provided for `ursgal_style_1`. As you can see in the example, the value is simply mapped to itself. 


### **Special cases**

Some key_translations values cannot be directly mapped to a tool specific parameter. This is due to the harmonization of parameters in this project and different parameter handling of the tools. For example, if considereing tolerance parameters some tools accept symmetric windows, while others can handle asymmetric windows. The representation of such can be either one parameter, where the tool internally applies it in both direction from the measured value (only for symmetric windows), or in turn a list of lower and upper boundary. 

These parameters require further tool specific processing, prior being injected e.g. into a command line. You can easily identify them, as they have a **\<tag\>** in their names. In the following example:
```
"cutadapt_style_1": "-u_<part_read_start>",
"cutadapt_style_1": "-u_<part2_read_end>",
```

the tool cutadapt expects two values following the **-u** parameter. For matter of harmonization, as other tools might expect it in a different format, these two parameters are separated and flagged as `<part1>` and `<part2>`. During command line preparation for cutadapt, these parameters will be caught and formatted to the expected format.

A special case are the parameters ending with a **\<DROP_KEY\>** key_translation. 

```
{
        "default_value": true,
        "description": "Disable grouping of bases for reads >50bp. All reports will 
                        show data for every base in the read.",
        "key_translations": {
            "fastqc_style_1": "disable_read_grouping_<DROP_KEY>",
            "ursgal_style_1": "disable_read_grouping"
        },
        "name": "disable_read_grouping",
        "tag": [
            "rnatool"
        ],
        "triggers_rerun": true,
        "value_translations": {
            "fastqc_style_1": [
                [
                    false,
                    ""
                ],
                [
                    true,
                    "--nogroup"
                ]
            ],
            "ursgal_style_1": [
                [
                    false,
                    false
                ],
                [
                    true,
                    true
                ]
            ]
        },
        "value_type": "bool"
    },
```

This tag should be used if the parameter is a command line flag. Hence, either to perform or not perform a certain task is a boolean decision mapping to a respective flag. This flag, is defined by the parameter value, hence making the key_translation obsolete. We generalized this behavior such that during parameter translation, the placeholder key_translation is set to `None` to further underline that it is not a meaningful parameter for the tool. The actual command line flag, defined by the parameter value, can then be used to append to the command list.


Team
----

# Core team:

- Johannes Leufken
- Stefan Schulze
- Artyom Vlasov
- Manuel Kösters
- Tristan Ranff
- Christian Fufezan

# Contributors:

- tbd;
