class DPDA:
    def __init__(self, all_states, input_alphabet, stack_alphabet, initial_stack_symbol,
                 start_state, accept_states, transition_function, epsilon_symbol='eps'):
        self.all_states = set(all_states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.initial_stack_symbol = initial_stack_symbol
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
        lines.append(f"\nEpsilon Symbol: '{self.epsilon_symbol}'")

        lines.append("\nTransition Function:")
        if self.transition_function:
            for (current_state, input_symbol, stack_top), (next_state, push_symbols) in self.transition_function.items():
                lines.append(f"  δ({current_state}, {input_symbol}, {stack_top}) -> ({next_state}, PUSH={push_symbols})")
        else:
            lines.append("  Transition Function not defined.")
        return "\n".join(lines)

    def _validate_dpda(self):

        if self.start_state not in self.all_states:
            raise ValueError(f"Start state '{self.start_state}' isn't in set of states!")
        
        if not self.accept_states.issubset(self.all_states):
            invalid_accept_states = self.accept_states - self.all_states
            raise ValueError(f"Invalid accept states: {invalid_accept_states}.\nMust be a subset of states!")
        
        for (current_state, input_symbol, stack_top), (next_state, push_symbols) in self.transition_function.items():

            if current_state not in self.all_states:
                raise ValueError(f"Invalid state '{current_state}' in transition function!")
            
            if input_symbol != self.epsilon_symbol and input_symbol not in self.input_alphabet:
                raise ValueError(f"Invalid input symbol '{input_symbol}' in transition function!")
            
            if stack_top not in self.stack_alphabet:
                raise ValueError(f"Invalid stack symbol '{stack_top}' as top of stack in transition function!")
            
            if next_state not in self.all_states:
                raise ValueError(f"Invalid next state '{next_state}' in transition function!")
            
            for s_push in push_symbols:
                if s_push not in self.stack_alphabet and s_push != self.epsilon_symbol:
                    raise ValueError(f"Invalid stack symbol '{s_push}' as push symbol in transition function!")
                
        seen_transitions = set()
        for key in self.transition_function:
            if key in seen_transitions:
                raise ValueError(f"Non-deterministic transition found for {key}!")
            seen_transitions.add(key)
    
    def _find_transition(self, current_state, input_symbol, stack_top):
        if input_symbol is not None:
            transition_key = (current_state, input_symbol, stack_top)
            if transition_key in self.transition_function:
                next_state, push_symbols = self.transition_function[transition_key]
                return "Use input symbol.", next_state, push_symbols

        transition_key_epsilon = (current_state, self.epsilon_symbol, stack_top)
        if transition_key_epsilon in self.transition_function:
            next_state, push_symbols = self.transition_function[transition_key_epsilon]
            return "Use epsilon symbol.", next_state, push_symbols

        return "No transition found!", None, None

    def accepts_input(self, input_tokens):
        current_state = self.start_state
        stack = [self.initial_stack_symbol]
        token_index = 0
        input_length = len(input_tokens)
        logs = []
        logs.append(f"\nInput: \"{input_tokens}\"")

        step = 0
        while True:
            step += 1
            consumed_input = input_tokens[:token_index] if token_index < input_length else input_tokens
            logs.append(f"\n{step}. Consumed input=\"{consumed_input}\", Stack={stack}")

            if not stack:
                logs.append("   Stack is empty!")
                break

            stack_top = stack[-1]

            current_input_symbol = None
            if token_index < input_length:
                current_input_symbol = input_tokens[token_index]
            
            result_transition, next_state, push_symbols= self._find_transition(
                current_state, current_input_symbol, stack_top
            )

            if next_state is not None:
                use_symbol = current_input_symbol if result_transition == "Use input symbol." else self.epsilon_symbol
                logs.append(f"  Transition: δ({current_state}, '{use_symbol}', Pop={stack_top}) -> ({next_state}, Push={push_symbols})")

                current_state = next_state
                stack.pop()
                
                for symbol_to_push in reversed(push_symbols):
                    if symbol_to_push != self.epsilon_symbol:
                        stack.append(symbol_to_push)
                
                if result_transition == "Use input symbol.":
                    token_index += 1
            
            else:
                logs.append(f"  Halting: No valid transition found in state={current_state}!")
                break
        
        if token_index == input_length and current_state in self.accept_states:
            logs.append(f"\nFinish in state={current_state} with stack={stack}.")
            logs.append(f"Input Accepted!")

            return True, "\n".join(logs)
        else:
            logs.append(f"\nFinish in state={current_state} with stack={stack}.")
            reason = ""
            if token_index != input_length:
                reason = "Not all input was consumed! "
            if current_state not in self.accept_states:
                reason += "Not in an accept state!"
            logs.append(f"Input Rejected! {reason}")

            return False, "\n".join(logs)