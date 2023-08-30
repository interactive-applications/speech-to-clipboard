import re
import json


class Replacer():
    
    regex_flags_mapping = {
        "IGNORECASE": re.IGNORECASE,
        "DOTALL": re.DOTALL,
        "MULTILINE": re.MULTILINE,
        "VERBOSE": re.VERBOSE,
        "UNICODE": re.UNICODE,
        "LOCALE": re.LOCALE,
        "ASCII": re.ASCII
    }
    
    def __init__(self, file: str = "replacements.json") -> None:
        self.replacements = {}
        self.flags = re.IGNORECASE
        try:
            with open(file, "r", encoding="utf-8") as replacements_file:
                content = json.load(replacements_file)
                
                # read variables, replacements, and flags
                self.variables = content["variables"]
                self.replacements = content["replacements"]
                self.raw_flags = content["flags"]
                
                # replace variables in variables and replacements
                self._replace_variables_in_variables()
                self._replace_variables_in_replacements()
                self._parse_regex_flags()
        
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Replacements file '{file}' not found."
            ) from exc
        except json.JSONDecodeError as exc:
            raise json.JSONDecodeError(
                f"Replacements file '{file}' is not a valid JSON file.",
                exc.doc, exc.pos
            ) from exc
        except TypeError as exc:
            raise TypeError(
                f"Replacements file '{file}' is not a valid JSON file."
            ) from exc
        except KeyError as exc:
            raise KeyError(
                f"Replacements file '{file}' must contain 'variables', 'replacements', and 'flags' keys."
            ) from exc
    
    def _replace_variables_in_variables(self) -> None:
        """
        Replace variables in variables
        """
        change = True
        while change:
            change = False
            for variable, value in self.variables.items():
                for var, val in self.variables.items():
                    if var is not variable:
                        self.variables[variable] = value.replace(var, val)
                        if self.variables[variable] != value:
                            change = True
    
    def _replace_variables_in_replacements(self) -> None:
        """
        Replace variables in replacements
        """
        for replacement in self.replacements:
            for i in range(len(self.replacements[replacement])):
                for variable, value in self.variables.items():
                    self.replacements[replacement][i] = self.replacements[
                        replacement][i].replace(variable, value)
    
    def _parse_regex_flags(self) -> None:
        """
        Parse regex flags from string to regex flags.
        """
        for flag in self.raw_flags:
            try:
                self.flags |= self.regex_flags_mapping[flag]
            except KeyError as e:
                raise KeyError(
                    f"Invalid flag '{flag}' found in replacements file."
                ) from e
    
    def replace(self, text: str) -> str:
        """
        Replace all regexes in text with their replacements.
        """
        for replacement, regexes in self.replacements.items():
            for regex in regexes:
                text = re.sub(regex, replacement, text, flags=self.flags)
        return text
    
    def __str__(self) -> str:
        return json.dumps(self.replacements, indent=4, ensure_ascii=False)
