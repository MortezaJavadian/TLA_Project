from graphviz import Digraph

class Node():
    def __init__(self, symbol, children=[], is_Leaf=False):
        self.symbol = symbol
        self.children = children
        self.is_Leaf = is_Leaf

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
        self.root_parse_tree = None

        self._validate_dpda()

    def __str__(self):
        lines = []
        lines.append(f"\n  ======  DPDA  ======  ")
        lines.append(f"\nStates: {self.all_states}")
        lines.append(f"\nInput Alphabet: {self.input_alphabet}")
        lines.append(f"\nStack Alphabet: {self.stack_alphabet}")
        lines.append(f"\nInitial Stack symbol: '{self.initial_stack_symbol}'")
        lines.append(f"\nStart State: {self.start_state}")
        lines.append(f"\nAccept States: {self.accept_states}")
        lines.append(f"\nEpsilon symbol: '{self.epsilon_symbol}'")

        lines.append("\nTransition Function:")
        if self.transition_function:
            for (current_state, input_symbol, stack_top_symbol), (next_s, push_symbols) in self.transition_function.items():
                lines.append(f"  δ({current_state}, {input_symbol}, {stack_top_symbol}) -> ({next_s}, PUSH={push_symbols})")
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

                if not push_symbols and stack_top == current_input_symbol_on_tape : 
                    return "MATCH_CONSUME", next_state, push_symbols
                else: 
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
        logs.append(f"\nInput Tokens: {input_tokens}")

        step = 0
        max_steps = input_length * 8 + 35

        while step < max_steps:
            step += 1
            
            consumed_input = input_tokens[:token_index] if token_index < input_length else input_tokens
            logs.append(f"\n{step}. Consumed input=\"{consumed_input}\", Stack={stack}")

            if not stack:
                logs.append("   Halting: Stack is empty (and not in accept state or before consuming all input).")
                break

            current_input_symbol = None
            if token_index < input_length:
                current_input_symbol = input_tokens[token_index]

            stack_top = stack[-1]
            
            result_transition_type, next_state, push_symbols = self._find_transition(
                current_state, current_input_symbol, stack_top
            )

            if result_transition_type != "NO_TRANSITION":
                use_symbol = current_input_symbol if result_transition_type == "Use input symbol." else self.epsilon_symbol
                logs.append(f"  Transition: δ({current_state}, '{use_symbol}', Pop={stack_top}) -> ({next_state}, Push={push_symbols})")
                current_state = next_state
                stack.pop() 
                
                if push_symbols: 
                    for symbol_to_push in reversed(push_symbols):
                        stack.append(symbol_to_push)
                    
                if result_transition_type == "MATCH_CONSUME":
                    token_index += 1
               
            else: 
                logs.append(f"  Halting: No valid transition from State='{current_state}' with Stack_Top='{stack_top}'")
                break

        is_accepted = False
        if token_index == input_length and current_state in self.accept_states:
            if not stack:
                is_accepted = True

        logs.append("\n    ======  Parsing Finished  ======    ")
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
                 
            logs.append(f"Input REJECTED!\nReasons: {' '.join(reason)}")

            return False, "\n".join(logs)
        
    def _plot_parse_tree(self):
        def plot_recurse(node, parent_id=None):
            nid = str(id(node))

            if node.is_Leaf:
                dot.node(nid, label=node.symbol, shape='box', style='filled', color='lightgreen')
            else:
                dot.node(nid, label=node.symbol, shape='ellipse', style='filled', color='yellow')

            if parent_id:
                dot.edge(parent_id, nid)

            for child in node.children:
                plot_recurse(child, nid)
        
        dot = Digraph()
        dot.attr('node', shape='circle')
        dot.node_attr.update(fontsize='30', fontname='Arial')

        plot_recurse(self.root_parse_tree)

        dot.render('parse_tree', format='png')
    
    def create_parse_tree(self, input_tokens, input_string):
        current_state = self.start_state
        token_index = 0
        input_length = len(input_tokens)

        stack_symbols = [self.initial_stack_symbol]
        root = Node(self.initial_stack_symbol)
        stack_nodes = [root]

        while stack_symbols:
            lookahead = input_tokens[token_index] if token_index < input_length else None
            stack_top = stack_symbols[-1]
            node_top = stack_nodes[-1]

            trans_type, next_state, push_symbols = self._find_transition(
                current_state, lookahead, stack_top
            )
            if trans_type == "NO_TRANSITION":
                break

            stack_symbols.pop()
            stack_nodes.pop()
            current_state = next_state

            if trans_type == "MATCH_CONSUME":
                node_top.is_Leaf = False
                leaf_value = input_string[token_index] if token_index < len(input_string) else ""
                leaf_node = Node(leaf_value, is_Leaf=True)
                node_top.children = [leaf_node]
                token_index += 1

            else:
                node_top.is_Leaf = False
                node_top.children = []

                if not push_symbols:
                    eps_node = Node(self.epsilon_symbol, is_Leaf=True)
                    node_top.children = [eps_node]

                else:
                    for symbol in push_symbols:
                        child = Node(symbol, children=[], is_Leaf=False)
                        node_top.children.append(child)

                    for child in reversed(node_top.children):
                        stack_symbols.append(child.symbol)
                        stack_nodes.append(child)

            if token_index == input_length and current_state in self.accept_states:
                break

        self.root_parse_tree = root.children[0] if root.children else root
        self._plot_parse_tree()