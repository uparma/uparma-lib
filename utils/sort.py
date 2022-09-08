import json

sortable_types = (list, dict)


def dynamic_sort(input, depth=0):
    if isinstance(input, dict):
        if any([isinstance(v, sortable_types) for v in input.values()]):
            return dict(
                sorted(
                    {k: dynamic_sort(v, depth + 1) for k, v in input.items()}.items()
                )
            )
        else:
            return dict(sorted(input.items()))
    if isinstance(input, list):
        if any([isinstance(v, sortable_types) for v in input]):
            next_list = [dynamic_sort(v, depth + 1) for v in input]
            if depth == 0:
                return list(sorted(next_list, key=lambda k: k["name"]))
            elif not any(isinstance(n, dict) for n in next_list):
                return list(sorted(next_list))
            else:
                return next_list
    return input


if __name__ == "__main__":
    # Do it for both parameters and styles json
    for file in ("parameters", "styles"):
        # Read
        with open(f"jsons/{file}.json") as f:
            j = json.load(f)
        # Sort
        sorted_j = dynamic_sort(j)
        # Write
        with open(f"jsons/{file}.json", "w") as f:
            json.dump(sorted_j, f, indent=4)
