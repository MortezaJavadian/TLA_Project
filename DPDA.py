class DPDA:
    def __init__(self, all_states, input_alphabet, stack_alphabet, initial_stack_symbol,
                 start_state, accept_states, transition_function, epsilon_symbol='eps'):
        self.all_states = set(all_states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.initial_stack_symbol = initial_stack_symbol
        if self.initial_stack_symbol not in self.stack_alphabet:
            self.stack_alphabet.add(self.initial_stack_symbol)

        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.transition_function = transition_function
        self.epsilon_symbol = epsilon_symbol

        self._validate_dpda()

    def __str__(self):
        lines = []
        lines.append(f"\n  ======  DPDA  ======  ")
        lines.append(f"\nStates: {self.all_states}")
        lines.append(f"\nInput Alphabet: {self.input_alphabet}")
        lines.append(f"\nStack Alphabet: {self.stack_alphabet}")
        lines.append(f"\nInitial Stack Symbol: '{self.initial_stack_symbol}'")
        lines.append(f"\nStart State: {self.start_state}")
        lines.append(f"\nAccept States: {self.accept_states}")
        lines.append(f"\nEpsilon Symbol (for DPDA moves): '{self.epsilon_symbol}'")

        lines.append("\nTransition Function:")
        if self.transition_function:
            for (current_state, input_sym, stack_top_sym), (next_s, push_syms) in self.transition_function.items():
                lines.append(f"  δ({current_state}, {input_sym}, {stack_top_sym}) -> ({next_s}, PUSH={push_syms})")
        else:
            lines.append("  Transition Function not defined.")
        return "\n".join(lines)

    def _validate_dpda(self):
        if self.start_state not in self.all_states:
            raise ValueError(f"Start state '{self.start_state}' isn't in set of states!")
        if not self.accept_states.issubset(self.all_states):
            invalid_accept_states = self.accept_states - self.all_states
            raise ValueError(f"Invalid accept states: {invalid_accept_states}. Must be subset of states!")

        for (current_s, input_s, stack_s), (next_s, push_s_list) in self.transition_function.items():
            if current_s not in self.all_states:
                raise ValueError(f"Invalid current state '{current_s}' in transition key { (current_s, input_s, stack_s) }")
            if next_s not in self.all_states:
                raise ValueError(f"Invalid next state '{next_s}' in transition value for key { (current_s, input_s, stack_s) }")
            if input_s != self.epsilon_symbol and input_s not in self.input_alphabet:
                 raise ValueError(f"Input symbol '{input_s}' in transition key { (current_s, input_s, stack_s) } not in DPDA input alphabet or not epsilon.")
            if stack_s not in self.stack_alphabet:
                raise ValueError(f"Stack symbol '{stack_s}' in transition key { (current_s, input_s, stack_s) } not in DPDA stack alphabet.")
            for p_s in push_s_list:
                if p_s not in self.stack_alphabet: 
                    raise ValueError(f"Push symbol '{p_s}' in {push_s_list} for key { (current_s, input_s, stack_s) } not in DPDA stack alphabet.")

    def _find_transition(self, current_state, current_input_symbol_on_tape, stack_top):
        
        if current_input_symbol_on_tape is not None:
            key = (current_state, current_input_symbol_on_tape, stack_top)
            if key in self.transition_function:
                next_state, push_symbols = self.transition_function[key]
                is_stack_top_terminal = stack_top in self.input_alphabet and stack_top != '$' 

                if not push_symbols and stack_top == current_input_symbol_on_tape : 
                    return "MATCH_CONSUME", next_state, push_symbols
                else: 
                    return "EXPAND_NO_CONSUME", next_state, push_symbols

        if current_input_symbol_on_tape is None: 
            key_for_eof_lookahead = (current_state, '$', stack_top) 
            if key_for_eof_lookahead in self.transition_function:
                next_state, push_symbols = self.transition_function[key_for_eof_lookahead]
                return "EXPAND_NO_CONSUME", next_state, push_symbols 

        key_epsilon_move = (current_state, self.epsilon_symbol, stack_top)
        if key_epsilon_move in self.transition_function:
            next_state, push_symbols = self.transition_function[key_epsilon_move]
            return "EPSILON_NO_CONSUME", next_state, push_symbols
            
        return "NO_TRANSITION", None, None

    def accepts_input(self, input_tokens):
        current_state = self.start_state
        stack = [self.initial_stack_symbol]
        token_index = 0
        input_length = len(input_tokens)
        logs = []
        logs.append(f"Input Tokens: {input_tokens}")

        step = 0
        max_steps = input_length * 5 + 20 

        while step < max_steps:
            step += 1
            
            current_lookahead_for_find = None
            if token_index < input_length:
                current_lookahead_for_find = input_tokens[token_index]

            consumed_str = ' '.join(input_tokens[:token_index])
            remaining_str = ' '.join(input_tokens[token_index:])
            log_entry = (f"\n{step}. State='{current_state}', "
                         f"Consumed='{consumed_str}', Remaining='{remaining_str}', "
                         f"Stack={stack}, Lookahead='{current_lookahead_for_find if current_lookahead_for_find is not None else '$ (EOF)'}'")
            logs.append(log_entry)

            if not stack:
                logs.append("   Halting: Stack is empty (and not in accept state or before consuming all input).")
                break

            stack_top = stack[-1]
            
            result_transition_type, next_state, push_symbols_list = self._find_transition(
                current_state, current_lookahead_for_find, stack_top
            )

            if result_transition_type != "NO_TRANSITION":
                logged_input_for_delta = self.epsilon_symbol
                if result_transition_type == "MATCH_CONSUME":
                    logged_input_for_delta = current_lookahead_for_find
                elif result_transition_type == "EXPAND_NO_CONSUME":
                    logged_input_for_delta = current_lookahead_for_find if current_lookahead_for_find is not None else '$'
                
                logs.append(f"  Action: Pop '{stack_top}'. Transition Type: {result_transition_type}.")
                logs.append(f"  Found: δ({current_state}, '{logged_input_for_delta}', '{stack_top}') -> ({next_state}, PUSH={push_symbols_list})")

                current_state = next_state
                stack.pop() 
                
                if push_symbols_list: 
                    for symbol_to_push in reversed(push_symbols_list):
                        stack.append(symbol_to_push)
                    logs.append(f"  New Stack Top after push: '{stack[-1] if stack else 'EMPTY'}'")
                else:
                    logs.append(f"  No symbols pushed. Stack Top: '{stack[-1] if stack else 'EMPTY'}'")

                
                if result_transition_type == "MATCH_CONSUME":
                    logs.append(f"  Consumed input token: '{input_tokens[token_index]}'")
                    token_index += 1
                else:
                    logs.append(f"  Input token not consumed by this step.")
            
            else: 
                actual_lookahead_for_log = current_lookahead_for_find if current_lookahead_for_find is not None else '$ (EOF)'
                logs.append(f"  Halting: No valid transition from State='{current_state}' with Stack_Top='{stack_top}' and Lookahead='{actual_lookahead_for_log}'")
                break

            if token_index == input_length and current_state in self.accept_states and (not stack or stack == [self.initial_stack_symbol]):
                pass 


        is_accepted = False
        if token_index == input_length and current_state in self.accept_states:
            if not stack:
                is_accepted = True

        logs.append("\n--- Parsing Finished ---")
        if is_accepted:
            logs.append(f"Final State: '{current_state}', Stack: {stack}, Tokens Consumed: {token_index}/{input_length}")
            logs.append("Input ACCEPTED!")
            return True, "\n".join(logs)
        else:
            logs.append(f"Final State: '{current_state}', Stack: {stack}, Tokens Consumed: {token_index}/{input_length}")
            reason = []
            if token_index != input_length:
                reason.append(f"Not all input tokens were consumed (remaining: {' '.join(input_tokens[token_index:])}).")
            if current_state not in self.accept_states:
                reason.append(f"Ended in a non-accept state ('{current_state}'). Accept states: {self.accept_states}.")
            if stack: 
                reason.append(f"Stack is not empty at the end: {stack}.")
            if not reason:
                 reason.append("General parsing failure.")
            logs.append(f"Input REJECTED! Reasons: {' '.join(reason)}")
            return False, "\n".join(logs)