import re

class Grammar:
    def __init__(self, epsilon_symbol="eps"):
        self.start_symbol = None
        self.epsilon_symbol = epsilon_symbol
        self.non_terminals = set()
        self.terminals = set()
        self.productions = {}
        self.terminal_definitions = {}

    def __repr__(self):
        lines = []
        lines.append(f"\nStart Symbol: {self.start_symbol}")
        lines.append(f"\nEpsilon Symbol: {self.epsilon_symbol}")
        lines.append(f"\nNon-Terminals: {self.non_terminals}")
        lines.append(f"\nTerminals: {self.terminals}")

        lines.append("\nGrammar Productions:")
        for non_terminal, expression in self.productions.items():
            for exp in expression:
                lines.append(f"  {non_terminal} -> {' '.join(exp)}")

        lines.append("\nLexical Definitions:")
        for terminal, reg in self.terminal_definitions.items():
                lines.append(f"  {terminal} -> {reg}")

        return "\n".join(lines)

    def _parse_line(self, line):
        line = line.strip()

        if not line or line.startswith("#"):
            return None, "Comment"

        if "->" in line:
            parts = line.split("->", 1)
            left_hand = parts[0].strip()
            right_hand = parts[1].strip()
            return left_hand, right_hand
        elif "=" in line:
            parts = line.split("=", 1)
            left_hand = parts[0].strip()
            right_hand = parts[1].strip()
            return left_hand, right_hand
        
        return None, "Error"
    
    def load_grammar(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                all_lines = file.readlines()

        except FileNotFoundError:
            print("Error: File not found!")
            return False

        for line_num, line in enumerate(all_lines):

            left_hand, right_hand = self._parse_line(line)

            if left_hand is None:
                if right_hand == "Comment":
                    continue
                elif right_hand == "Error":
                    print(f"Warning: The format of line number {line_num + 1} is unknown!")
                    continue

            if "=" in line:
                if left_hand == "START":
                    self.start_symbol = right_hand
                    continue

                elif left_hand == "NON_TERMINALS":
                    self.non_terminals = set([nt.strip() for nt in right_hand.split(",")])
                    continue

                elif left_hand == "TERMINALS":
                    self.terminals = set([t.strip() for t in right_hand.split(",")])
                    continue

            if "->" in line:
                if left_hand in self.non_terminals:
                    if left_hand not in self.productions:
                        self.productions[left_hand] = []
                    
                    expressions = right_hand.split("|")
                    for exp in expressions:
                        symbols_in_production = [symbol.strip() for symbol in exp.strip().split()]
                        if symbols_in_production:
                           self.productions[left_hand].append(symbols_in_production)

                elif left_hand in self.terminals:
                    regex_pattern = right_hand

                    match_slash_format = re.fullmatch(r"/(.*)/", right_hand)
                    if match_slash_format:
                        regex_pattern = match_slash_format.group(1)
                    
                    self.terminal_definitions[left_hand] = regex_pattern

                else:
                    print(f"Warning: The symbol '{left_hand}' on line {line_num + 1} isn't in terminals or non-terminals symbols!")            
            
        if not self.start_symbol:
            print("Error: The start symbol isn't defined in the grammar file!")
            return False
        if not self.non_terminals:
            print("Error: The non-terminals symbols isn't defined in the grammar file!")
            return False
        if not self.terminals:
            print("Error: The terminals symbols isn't defined in the grammar file!")
            return False
        if not self.productions:
            print("Warning: The productions isn't defined in the grammar file!")

        all_symbols_in_productions = set()
        for expressions in self.productions.values():
            for exp in expressions:
                for symbol in exp:
                    if symbol != self.epsilon_symbol:
                        all_symbols_in_productions.add(symbol)

        all_defined_symbols = self.non_terminals.union(self.terminals)
        undefined_symbols = all_symbols_in_productions - all_defined_symbols
        if undefined_symbols:
            print(f"Warning: The following symbols use on the right hand of the rules but aren't defined in terminal or non-terminal:\n{undefined_symbols}")
        
        print("Grammar loading was successful.")
        return True