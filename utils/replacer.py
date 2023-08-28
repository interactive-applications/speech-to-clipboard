import re
import json


class Replacer():
    
    def __init__(self, file: str = "replacements.json") -> None:
        self.replacements = {}
        self.flags = re.IGNORECASE
        try:
            with open(file, "r", encoding="utf-8") as replacements_file:
                content = json.load(replacements_file)
                try:
                    self.variables = content["variables"]
                    self.replacements = content["replacements"]
                    self.raw_flags = content["flags"]
                except KeyError as e:
                    raise KeyError(
                        f"Replacements file '{file}' must contain 'variables', 'replacements', and 'flags' keys."
                    ) from e
                
                # replace variables in variables
                change = True
                while change:
                    change = False
                    for variable, value in self.variables.items():
                        for var, val in self.variables.items():
                            if var is not variable:
                                self.variables[variable] = value.replace(
                                    var, val
                                )
                                if self.variables[variable] != value:
                                    change = True
                
                # replace variables in replacements
                for replacement in self.replacements:
                    for i in range(len(self.replacements[replacement])):
                        for variable, value in self.variables.items():
                            self.replacements[replacement][
                                i] = self.replacements[replacement][i].replace(
                                    variable, value
                                )
                
                # convert raw flags to re flags
                for flag in self.raw_flags:
                    if flag == "IGNORECASE":
                        self.flags |= re.IGNORECASE
                    elif flag == "DOTALL":
                        self.flags |= re.DOTALL
                    elif flag == "MULTILINE":
                        self.flags |= re.MULTILINE
                    elif flag == "VERBOSE":
                        self.flags |= re.VERBOSE
                    elif flag == "UNICODE":
                        self.flags |= re.UNICODE
                    elif flag == "LOCALE":
                        self.flags |= re.LOCALE
                    elif flag == "ASCII":
                        self.flags |= re.ASCII
                    else:
                        raise ValueError(
                            f"Invalid flag '{flag}' in replacements file '{file}'."
                        )
        
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Replacements file '{file}' not found."
            ) from exc
    
    def replace(self, text: str) -> str:
        for replacement, regexes in self.replacements.items():
            for regex in regexes:
                text = re.sub(regex, replacement, text, flags=self.flags)
        return text
    
    def __str__(self) -> str:
        return json.dumps(self.replacements, indent=4, ensure_ascii=False)
