# In the name of Allah
from DPDA import DPDA

class LL1_2_DPDA:
    def __init__(self, grammar, initial_stack_symbol='Z0'):
        self.first = {}
        self.follow = {}
        self.parsing_table = {}
        self.grammar = grammar
        self.initial_stack_symbol = initial_stack_symbol
        self.dpda = None

        self._convert_ll1_to_dpda()

    def _compute_first_follow(self):
        epsilon = self.grammar.epsilon_symbol
        
        for terminal in self.grammar.terminals:
            self.first[terminal] = {terminal}
        
        for non_terminal in self.grammar.non_terminals:
            self.first[non_terminal] = set()
            self.follow[non_terminal] = set()
        
        for non_terminal, productions_list in self.grammar.productions.items():
            for production_rule in productions_list:
                if production_rule == [epsilon]: 
                    self.first[non_terminal].add(epsilon)
        
        changed = True
        while changed:
            changed = False
            for non_terminal, productions_list in self.grammar.productions.items():
                for production_rule in productions_list:
                    for symbol_in_rule in production_rule: 

                        if symbol_in_rule in self.grammar.terminals:
                            if symbol_in_rule not in self.first[non_terminal]:
                                self.first[non_terminal].add(symbol_in_rule)
                                changed = True
                            break
                        elif symbol_in_rule in self.grammar.non_terminals:
                            prev_len = len(self.first[non_terminal])
                            self.first[non_terminal].update(self.first[symbol_in_rule] - {epsilon})
                            if len(self.first[non_terminal]) != prev_len:
                                changed = True
                            if epsilon not in self.first[symbol_in_rule]:
                                break 
                    else: 
                        if epsilon not in self.first[non_terminal]:
                            self.first[non_terminal].add(epsilon)
                            changed = True
        
        changed = True
        while changed:
            changed = False
            for nt in self.grammar.non_terminals:
                for prod_rule in self.grammar.productions.get(nt, []):
                    rhs_first_set_added_epsilon = True
                    for symbol in prod_rule:
                        if symbol == epsilon: 
                            break 
                        
                        current_symbol_first = set()
                        if symbol in self.grammar.terminals:
                            current_symbol_first = {symbol}
                        elif symbol in self.grammar.non_terminals:
                            current_symbol_first = self.first[symbol]
                        
                        added_now = current_symbol_first - {epsilon}
                        old_len = len(self.first[nt])
                        self.first[nt].update(added_now)
                        if len(self.first[nt]) != old_len:
                            changed = True
                        
                        if epsilon not in current_symbol_first:
                            rhs_first_set_added_epsilon = False
                            break 
                    
                    if rhs_first_set_added_epsilon: 
                        if epsilon not in self.first[nt]:
                           self.first[nt].add(epsilon)
                           changed = True

        self.follow[self.grammar.start_symbol].add(self.grammar.epsilon_symbol)
        
        changed = True
        while changed:
            changed = False
            for non_terminal_A, productions_list in self.grammar.productions.items():
                for production_rule in productions_list: 
                    trailer = self.follow[non_terminal_A].copy() 
                    
                    for i in range(len(production_rule) - 1, -1, -1): 
                        symbol_B = production_rule[i]
                        
                        if symbol_B in self.grammar.non_terminals:
                            old_len_follow_B = len(self.follow[symbol_B])
                            self.follow[symbol_B].update(trailer)
                            if len(self.follow[symbol_B]) != old_len_follow_B:
                                changed = True
                            
                            if epsilon in self.first.get(symbol_B, set()):
                                trailer.update(self.first[symbol_B] - {epsilon})
                            else:
                                trailer = self.first.get(symbol_B, set()).copy()
                                
                        elif symbol_B in self.grammar.terminals:
                            trailer = {symbol_B} 

    def _build_parsing_table(self):
        self._compute_first_follow()
        epsilon = self.grammar.epsilon_symbol
        self.parsing_table = {}

        for non_terminal_A, productions_list in self.grammar.productions.items():
            for production_rule_alpha in productions_list:
                
                first_of_alpha = set()
                all_derive_epsilon = True
                for symbol_Y in production_rule_alpha:
                    if symbol_Y == epsilon:
                        break
                    
                    first_of_Y = set()
                    if symbol_Y in self.grammar.terminals:
                        first_of_Y = {symbol_Y}
                    elif symbol_Y in self.grammar.non_terminals:
                        first_of_Y = self.first.get(symbol_Y, set())
                    
                    first_of_alpha.update(first_of_Y - {epsilon})
                    if epsilon not in first_of_Y:
                        all_derive_epsilon = False
                        break
                
                if all_derive_epsilon:
                    first_of_alpha.add(epsilon)

                for terminal_a in first_of_alpha:
                    if terminal_a != epsilon:
                        self.parsing_table[(non_terminal_A, terminal_a)] = production_rule_alpha
                
                if epsilon in first_of_alpha:
                    for terminal_b in self.follow.get(non_terminal_A, set()):
                        self.parsing_table[(non_terminal_A, terminal_b)] = production_rule_alpha

    def _convert_ll1_to_dpda(self):
        self._build_parsing_table()
        
        states = {'q0', 'q', 'f'} 
        input_alphabet = self.grammar.terminals.copy()
        
        stack_alphabet = self.grammar.terminals.union(self.grammar.non_terminals)
        stack_alphabet.add(self.initial_stack_symbol)
        
        start_state = 'q0'
        accept_states = {'f'}
        epsilon_symbol_for_dpda = self.grammar.epsilon_symbol 

        transition_function = {}
        
        transition_function[('q0', epsilon_symbol_for_dpda, self.initial_stack_symbol)] = \
            ('q', [self.grammar.start_symbol, self.initial_stack_symbol])
        
        for (non_terminal, terminal_lookahead), production in self.parsing_table.items():
            key = ('q', terminal_lookahead, non_terminal)
            effective_production_to_push = [] if production == [self.grammar.epsilon_symbol] else production
            transition_function[key] = ('q', effective_production_to_push)
        
        for terminal in self.grammar.terminals:
            key = ('q', terminal, terminal)
            transition_function[key] = ('q', [])
        
        transition_function[('q', epsilon_symbol_for_dpda, self.initial_stack_symbol)] = ('f', [])

        self.dpda = DPDA(
            all_states=states,
            input_alphabet=input_alphabet, 
            stack_alphabet=stack_alphabet,
            initial_stack_symbol=self.initial_stack_symbol,
            start_state=start_state,
            accept_states=accept_states,
            transition_function=transition_function,
            epsilon_symbol=epsilon_symbol_for_dpda,
        )

    def parse(self, input_string):
        input_tokens = self.grammar.tokenize_input(input_string)

        accepted, logs = self.dpda.accepts_input(input_tokens)
        print(logs)

        if accepted:
            self.dpda.create_parse_tree(input_tokens, input_string.split())

            rename_id = int(input('Chose a ID from Parse Tree image to change name (0 to exit): '))
            if rename_id != 0:
                new_symbol = input(f'  Enter a new name for this ID {rename_id}: ')
                self.dpda.rename_block_by_ID(rename_id, new_symbol)
            else:
                print('Not changed in Parse Tree!')
        else:
            print("Not created Parse Tree!")