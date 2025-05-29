# In the name of Allah

from Grammar import Grammar
# from DPDA import DPDA
from LL1ToDPDA import LL1_2_DPDA

LL1_grammar = Grammar()
LL1_grammar.load_grammar('grammar.txt')
# print(LL1_grammar)

# Example: aⁿb²ⁿ
# dpda = DPDA(
#     all_states={'q0', 'q1', 'q2', 'q3'},
#     input_alphabet={'a', 'b'},
#     stack_alphabet={'Z', 'A'},
#     initial_stack_symbol='Z',
#     start_state='q0',
#     accept_states={'q3'},
#     transition_function={
#         ('q0', 'a', 'Z'): ('q0', ['A', 'A', 'Z']),
#         ('q0', 'a', 'A'): ('q0', ['A', 'A', 'A']),
#         ('q0', 'b', 'A'): ('q1', ['eps']),
#         ('q1', 'b', 'A'): ('q0', ['eps']),
#         ('q0', 'eps', 'Z'): ('q3', ['Z'])
#     }
# )
# print(dpda)
# accepted, logs = dpda.accepts_input("aabbb")
# print(logs)
# print(accepted)
# accepted, logs = dpda.accepts_input("abb")
# print(logs)
# print(accepted)

L2D = LL1_2_DPDA()
dpda = L2D.convert_ll1_to_dpda(LL1_grammar)
print(dpda)

