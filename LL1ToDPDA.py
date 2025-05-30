# In the name of Allah
from DPDA import DPDA

class LL1_2_DPDA:
    def __init__(self, grammar):
        self.first = {}
        self.follow = {}
        self.parsing_table = {}
        self.grammar = grammar
        self.dpda = None

    def _compute_first_follow(self):
        epsilon = self.grammar.epsilon_symbol
        
        for terminal in self.grammar.terminals:
            self.first[terminal] = {terminal}
        
        for non_terminal in self.grammar.non_terminals:
            self.first[non_terminal] = set()
            self.follow[non_terminal] = set()
        
        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                if production == [epsilon]:
                    self.first[non_terminal].add(epsilon)
        
        changed = True
        while changed:
            changed = False
            for non_terminal, productions in self.grammar.productions.items():
                for production in productions:
                    for symbol in production:
                        if symbol == epsilon:
                            continue
                        if symbol in self.grammar.terminals:
                            if symbol not in self.first[non_terminal]:
                                self.first[non_terminal].add(symbol)
                                changed = True
                            break
                        else:
                            prev_len = len(self.first[non_terminal])
                            self.first[non_terminal] |= self.first[symbol] - {epsilon}
                            if len(self.first[non_terminal]) != prev_len:
                                changed = True
                            if epsilon not in self.first[symbol]:
                                break
                    else:
                        if epsilon not in self.first[non_terminal]:
                            self.first[non_terminal].add(epsilon)
                            changed = True
        
        self.follow[self.grammar.start_symbol].add('$')
        changed = True
        while changed:
            changed = False
            for non_terminal, productions in self.grammar.productions.items():
                for production in productions:
                    trailer = self.follow[non_terminal].copy()
                    for symbol in reversed(production):
                        if symbol in self.grammar.non_terminals:
                            prev_len = len(self.follow[symbol])
                            self.follow[symbol] |= trailer
                            if len(self.follow[symbol]) != prev_len:
                                changed = True
                            if epsilon in self.first.get(symbol, set()):
                                trailer |= self.first[symbol] - {epsilon}
                            else:
                                trailer = self.first.get(symbol, set()).copy()
                        elif symbol in self.grammar.terminals:
                            trailer = {symbol}

    def _build_parsing_table(self):
        self._compute_first_follow()
        epsilon = self.grammar.epsilon_symbol
        
        for non_terminal, productions in self.grammar.productions.items():
            for production in productions:
                first_of_production = set()
                for symbol in production:
                    if symbol == epsilon:
                        first_of_production.add(epsilon)
                        break
                    if symbol in self.grammar.terminals:
                        first_of_production.add(symbol)
                        break
                    first_of_production |= self.first[symbol] - {epsilon}
                    if epsilon not in self.first[symbol]:
                        break
                else:
                    first_of_production.add(epsilon)
                
                for terminal in first_of_production - {epsilon}:
                    self.parsing_table[(non_terminal, terminal)] = production
                
                if epsilon in first_of_production:
                    for terminal in self.follow[non_terminal]:
                        self.parsing_table[(non_terminal, terminal)] = production
                    if '$' in self.follow[non_terminal]:
                        self.parsing_table[(non_terminal, '$')] = production
        
    def convert_ll1_to_dpda(self, initial_stack_symbol='Z0'):
        self._build_parsing_table()
        
        states = {'q0', 'q', 'f'}
        input_alphabet = self.grammar.terminals | {'$'} 
        stack_alphabet = self.grammar.terminals | self.grammar.non_terminals | {initial_stack_symbol}
        start_state = 'q0'
        accept_states = {'f'}
        epsilon_symbol = self.grammar.epsilon_symbol
        transition_function = {}
        
        transition_function[('q0', epsilon_symbol, initial_stack_symbol)] = ('q', [self.grammar.start_symbol, initial_stack_symbol])
        
        for (non_terminal, terminal), production in self.parsing_table.items():
            key = ('q', terminal, non_terminal)
            transition_function[key] = ('q', production)
        
        for terminal in self.grammar.terminals:
            key = ('q', terminal, terminal)
            transition_function[key] = ('q', [])
        
        transition_function[('q', epsilon_symbol, initial_stack_symbol)] = ('f', [])

        self.dpda = DPDA(
            all_states=states,
            input_alphabet=input_alphabet,
            stack_alphabet=stack_alphabet,
            initial_stack_symbol=initial_stack_symbol,
            start_state=start_state,
            accept_states=accept_states,
            transition_function=transition_function,
            epsilon_symbol=epsilon_symbol
        )

        return self.dpda