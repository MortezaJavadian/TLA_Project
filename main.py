# In the name of Allah
from Grammar import Grammar
from LL1ToDPDA import LL1_2_DPDA

LL1_grammar = Grammar()
LL1_grammar.load_grammar('grammar1.txt')
print(LL1_grammar)

L2D = LL1_2_DPDA(LL1_grammar)
print(L2D.dpda)

L2D.parse('( a + b ) * ( c + d + ( 123 ) )')
# function main ( ) { x = 42 ; y = 3.14 ; z = ( x + y ) * 2 ; if ( z ) { result = z / 1.5 ; } while ( x ) { x = x - 1 ; } return result ; }