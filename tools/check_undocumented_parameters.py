import argparse
import glob
import re
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--moris-root", type=str, default="~/codes/moris")

regex_moris = r"insert\(\s?\"(.*?)\"\s*,\s*(.*?)\s\);"
regex_sublist = r"create_(.*?)_.*?\(.*?\).*?\}"
regex_tex = r"name\s*=\s*\{(.*?)}"


def find_moris_parameters(moris_root):
    prm_root = Path(moris_root) / "projects" / "PRM" / "src"
    found = {}
    for filename in prm_root.glob("fn_PRM_*_Parameters.hpp"):
        module = filename.stem.split("_")[2].lower()
        found[module] = {}
        with open(filename, "r") as f:
            content = f.read()
            single_line = content.replace("\n", "")
            for sublist in re.finditer(regex_sublist, single_line, re.DOTALL):
                sublist_name = sublist.group(1)
                found[module][sublist_name] = []
                for match in re.finditer(regex_moris, sublist.group(0), re.MULTILINE):
                    # print(f"{module} - found parameter: {match.group(1)} with default value
                    # {match.group(2)}")
                    # found[module].append(match.group(1))
                    found[module][sublist_name].append((match.group(1), match.group(2)))
    return found


def find_tex_parameters():
    tex_root = Path.cwd() / "parameters"
    found = {}
    for filename in tex_root.glob("*.tex"):
        module = filename.stem.lower()
        found[module] = []
        with open(filename, "r") as f:
            content = f.read()
            for match in re.finditer(regex_tex, content, re.MULTILINE):
                # print(f"{module} - found parameter: {match.group(1)}")
                found[module].append(match.group(1))
                # found[module].append((match.group(1), match.group(2)))
    return found


def match_documented_and_found(documented, found):
    for module in found:
        undocumented = []
        deprecated = []
        module_undocumented = False
        for sublist in found[module].keys():
            for parameter in found[module][sublist]:
                try:
                    if parameter[0] not in documented[module]:
                        undocumented.append(parameter)
                except KeyError:
                    module_undocumented = True
                    break

        for parameter in documented.get(module, []):
            for sublist in found[module].keys():
                found_names = [x[0] for x in found[module][sublist]]
                if not parameter in found_names:
                    deprecated.append(parameter)

        if module_undocumented:
            print(f"{module} is not documented!!")
        else:
            if len(undocumented) == 0:
                print(f"{module}: All parameters are documented!")
            else:
                print(f"{module}: undocumented parameters: {undocumented}")
            if len(deprecated) > 0:
                print(
                    f"{module}: deprecated (but still documented) parameters: {deprecated}"
                )


def parameter_block(name, default):
    template = """% --- {0} --- %
\\begin{{parameter}}{{
    name    = {{{0}}},
    default = {{{1}}},
}}
\\end{{parameter}}

"""
    return template.format(name, default)


def write_to_tex(found):
    for module, sublists in found.items():
        print(module)
        with open(f"modules/{module}_gen.tex", "w") as f:
            for sublist, params in sublists.items():
                f.write(f"\\subsection{{{sublist}}}\n\n")
                # sort params by first match
                params.sort(key=lambda x: x[0])
                for param in params:
                    print(param)
                    f.write(parameter_block(param[0], param[1]))


def main():
    args = parser.parse_args()
    parameters_found = find_moris_parameters(args.moris_root)
    # parameters_documented = find_tex_parameters()
    # match_documented_and_found(parameters_documented, parameters_found)
    # # print(parameters_found)
    # write_to_tex(parameters_found)


if __name__ == "__main__":
    main()
