# In the name of Allah
from Grammar import Grammar
from LL1ToDPDA import LL1_2_DPDA

LL1_grammar = Grammar()
LL1_grammar.load_grammar('grammar1.txt')
print(LL1_grammar)

L2D = LL1_2_DPDA(LL1_grammar)
dpda = L2D.convert_ll1_to_dpda()
print(dpda)

accepted, logs = dpda.accepts_input(LL1_grammar.tokenize_input("( a + b ) * ( c + d + ( 123 ) )"))
print(logs)
print(accepted)