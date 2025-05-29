# In the name of Allah
from DPDA import DPDA

class LL1_2_DPDA:
    def compute_first_follow(self,grammar):
        first = {}
        follow = {}
        epsilon = grammar.epsilon_symbol
        
        for terminal in grammar.terminals:
            first[terminal] = {terminal}
        
        for non_terminal in grammar.non_terminals:
            first[non_terminal] = set()
            follow[non_terminal] = set()
        
        for non_terminal, productions in grammar.productions.items():
            for production in productions:
                if production == [epsilon]:
                    first[non_terminal].add(epsilon)
        
        changed = True
        while changed:
            changed = False
            for non_terminal, productions in grammar.productions.items():
                for production in productions:
                    for symbol in production:
                        if symbol == epsilon:
                            continue
                        if symbol in grammar.terminals:
                            if symbol not in first[non_terminal]:
                                first[non_terminal].add(symbol)
                                changed = True
                            break
                        else:
                            prev_len = len(first[non_terminal])
                            first[non_terminal] |= first[symbol] - {epsilon}
                            if len(first[non_terminal]) != prev_len:
                                changed = True
                            if epsilon not in first[symbol]:
                                break
                    else:
                        if epsilon not in first[non_terminal]:
                            first[non_terminal].add(epsilon)
                            changed = True
        
        follow[grammar.start_symbol].add('$')
        changed = True
        while changed:
            changed = False
            for non_terminal, productions in grammar.productions.items():
                for production in productions:
                    trailer = follow[non_terminal].copy()
                    for symbol in reversed(production):
                        if symbol in grammar.non_terminals:
                            prev_len = len(follow[symbol])
                            follow[symbol] |= trailer
                            if len(follow[symbol]) != prev_len:
                                changed = True
                            if epsilon in first.get(symbol, set()):
                                trailer |= first[symbol] - {epsilon}
                            else:
                                trailer = first.get(symbol, set()).copy()
                        elif symbol in grammar.terminals:
                            trailer = {symbol}
        
        return first, follow

    def build_parsing_table(self,grammar):
        first, follow = self.compute_first_follow(grammar)
        epsilon = grammar.epsilon_symbol
        table = {}
        
        for non_terminal, productions in grammar.productions.items():
            for production in productions:
                first_of_production = set()
                for symbol in production:
                    if symbol == epsilon:
                        first_of_production.add(epsilon)
                        break
                    if symbol in grammar.terminals:
                        first_of_production.add(symbol)
                        break
                    first_of_production |= first[symbol] - {epsilon}
                    if epsilon not in first[symbol]:
                        break
                else:
                    first_of_production.add(epsilon)
                
                for terminal in first_of_production - {epsilon}:
                    table[(non_terminal, terminal)] = production
                
                if epsilon in first_of_production:
                    for terminal in follow[non_terminal]:
                        table[(non_terminal, terminal)] = production
                    if '$' in follow[non_terminal]:
                        table[(non_terminal, '$')] = production
        
        return table

    def convert_ll1_to_dpda(self, grammar, initial_stack_symbol='Z0'):
        parsing_table = self.build_parsing_table(grammar)
        
        states = {'q0', 'q', 'f'}
        input_alphabet = grammar.terminals | {'$'} 
        stack_alphabet = grammar.terminals | grammar.non_terminals | {initial_stack_symbol}
        start_state = 'q0'
        accept_states = {'f'}
        epsilon_symbol = grammar.epsilon_symbol
        transition_function = {}
        
        transition_function[('q0', epsilon_symbol, initial_stack_symbol)] = ('q', [grammar.start_symbol, initial_stack_symbol])
        
        for (non_terminal, terminal), production in parsing_table.items():
            key = ('q', terminal, non_terminal)
            transition_function[key] = ('q', production)
        
        for terminal in grammar.terminals:
            key = ('q', terminal, terminal)
            transition_function[key] = ('q', [])
        
        transition_function[('q', epsilon_symbol, initial_stack_symbol)] = ('f', [])
        
        return DPDA(
            all_states=states,
            input_alphabet=input_alphabet,
            stack_alphabet=stack_alphabet,
            initial_stack_symbol=initial_stack_symbol,
            start_state=start_state,
            accept_states=accept_states,
            transition_function=transition_function,
            epsilon_symbol=epsilon_symbol
        )