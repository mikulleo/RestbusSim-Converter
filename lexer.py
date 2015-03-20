#
# Copyright 2015 Leos Mikulka
#
# This file is part of RestbusSim-Converter.

# RestbusSim-Converter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# RestbusSim-Converter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with RestbusSim-Converter.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Leos Mikulka"
__copyright__ = "Copyright 2015, Leos Mikulka"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "mikulkal@hotmail.com"


import io
from ply import *
import ply.lex as lex
from ply.lex import TOKEN

class Lexer:

    
    # states
    #states = (
    #    ('state','exclusive'),
    #    )

    reserved_words = {            # reserved keywords
        'char' : 'CHAR',
        'byte' : 'BYTE',
        'int' : 'INT',
        'word' : 'WORD',
        'long' : 'LONG',
        'dword' : 'DWORD',
        'float' : 'FLOAT',
        'double' : 'DOUBLE',
        'message' : 'MESSAGE',
        'timer' : 'TIMER',
        'msTimer' : 'MSTIMER',
        'void' : 'VOID',
        'if' : 'IF',
        'else' : 'ELSE',
        'switch': 'SWITCH',
        'case' : 'CASE',
        'while' : 'WHILE',
        'do' : 'DO',
        'for' : 'FOR',
        'break' : 'BREAK',
        'continue' : 'CONTINUE',
        'return' : 'RETURN',
        'default' : 'DEFAULT',
        'this' : 'THIS',
        }

    reserved_numbers = {
        'dec_num' : 'DEC_NUM',
        'float_num' : 'FLOAT_NUM',
        'hex_num' : 'HEX_NUM',
        }

    # list of tokens
    tokens = [
        # arithmetic operators
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'MOD',
        'INCREMENT',
        'DECREMENT',

        # assignment operators
        'EQ',
        'ADD_EQ',
        'SUB_EQ',
        'MULT_EQ',
        'DIV_EQ',
        'MOD_EQ',
        'LSHIFT_EQ',
        'RSHIFT_EQ',
        'AND_EQ',
        'OR_EQ',
        'XOR_EQ',

        # boolean operators
        'NOT',
        'OR',
        'AND',

        # bitwise operators
        'COMPLEMENT',
        'BIT_AND',
        'BIT_OR',
        'BIT_XOR',
        'LSHIFT',
        'RSHIFT',

        # relation operators
        'EQ_TEST',
        'NOT_EQ_TEST',
        'GT',
        'GTE',
        'LT',
        'LTE',

        # misc operatprs
        'DOT',
        'COND_QUAT',    # quatation mark
        'COL',          # colon
            
        'WS',
        'COM',      # comma
        'SMC',      # semicolon
        'RCBR',     # right curly brace
        'LCBR',     # left curly brace 
        'RBRK',     # right bracket 
        'LBRK',     # left bracket
        'LPAR',     # left parenthese
        'RPAR',     # right parenthese
        'NUM',      # number
        'STRING',
        'CHARC',    # single character
        'KEY',      # single key, used during on key event, e.g. 'a'
        'ID',       # identifier
        'DCOL',     # double colon
        'COMMENT',      # normal comment
        'CppCOMMENT',   # C++ style comment
        'CAPLBEGIN',    # CAPL begin section, e.g. /*@@var: */
        'CAPLFUNCBEGIN', # CAPL function begin, e.g. /*@@caplFunc:function(int x) */
        'CAPLEND',      # CAPL end, i.e. /*@@end */
        'ARRAY',        # single or multi-dimensional array
        'RESERVED',     # int, float, ...
        'CAPLEVENT',    # CAPL event 
        'CAPLEVENT_word',  # reserved keywords for CAPL event
        'VARS',         # keyword 'variables'
        ] + list(reserved_words.values()) + list(reserved_numbers.values())

    t_WS = r'[ \t\n]'

    vars_keyword = r'variables(' + t_WS + r')+'

    @TOKEN(vars_keyword)            # must be before declaring ID! -- precedence
    def t_VARS(self,t):
        return t

    # regular expressions

    # arithmetic operators
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'\%'
    t_INCREMENT = r'\+\+'
    t_DECREMENT = r'--'

    # assignment operators
    t_EQ = r'\='
    t_ADD_EQ = r'\+\='
    t_SUB_EQ = r'\-\='
    t_MULT_EQ = r'\*\='
    t_LSHIFT_EQ = r'\<\<\='
    t_RSHIFT_EQ = r'\>\>\='
    t_AND_EQ = r'\&\='
    t_OR_EQ = r'\|\='
    t_XOR_EQ = r'\^\='

    # boolean operators
    t_NOT = r'\!'
    t_OR = r'\|\|'
    t_AND = r'\&\&'

    # bitwise operators
    t_COMPLEMENT = r'\~'
    t_BIT_AND = r'\&'
    t_BIT_OR = r'\|'
    t_BIT_XOR = r'\^'
    t_LSHIFT = r'\<\<'
    t_RSHIFT = r'\>\>'

    # relation operators
    t_EQ_TEST = r'\=\='
    t_NOT_EQ_TEST = r'\!\='
    t_GT = r'\>'
    t_GTE = r'\>\='
    t_LT = r'\<'
    t_LTE = r'\<\='

    # misc operators
    t_DOT = r'\.'
    t_COND_QUAT = r'\?'
    t_COL = r'\:'

    t_COM = r'\,'
    t_SMC = r'\;'
    t_LCBR = r'\{'
    t_RCBR = r'\}'
    t_LBRK = r'\['
    t_RBRK = r'\]'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_NUM = r'[0-9]+'
    t_STRING = r'\"(\\.|[^\\"])(\\.|[^\\"])+\"'
    t_CHARC = r'\"(.)\"'
    t_KEY = r'\'(.)\''
    t_ID = r'[a-zA-Z_][a-zA-Z0-9_-]*'
    t_DCOL = r'\:\:'
    t_COMMENT = r'/\*([^\*]|\*[^*/])*\*/'     # manual - sec. 8.4. - comments
    t_CppCOMMENT = r'//.*'
    t_CAPLEVENT_word =r'preStart|start|stopMeasurement|busOff|timer|key|message|errorActive|errorPassive|warningLimit|errorFrame|envVar|preStop'
    #t_DATATYPE = r'(char|byte|int|word|dword|long|float|double|message|timer|msTimer)'
    #t_VAR = r'(' + t_DATATYPE + r')+(' + t_WS + r')*(' + t_ID + r')*(' + t_WS + r')*\;'

    float_const = r'(' + t_NUM + r')\.(' + t_NUM + r')'
    hex_const = r'(0[xX][0-9a-fA-F]+)'

    array_decl = r'((' + t_LBRK + r')[a-zA-Z0-9]*(' + t_RBRK + r'))+'

    on_event_declar = r'(on' + t_WS + r')+(' + t_CAPLEVENT_word + r')+'
    capl_begin = r'\/\*\@\@(' + t_ID + r')*(\:)' + r'(' + t_WS + r')*(' + t_ID + r'|' + t_KEY+ r')?(\:)?(' + t_WS + r')*\*\/'
    capl_func_begin = r'\/\*\@\@caplFunc\:(' + t_ID + r')+\((' + t_ID + r'|' + t_COM + r'|' + array_decl +  r'|' + t_WS + r')*\)\:(' + t_WS + r')*\*\/'

    #capl_func_begin = r'\/\*\@\@caplFunc\:(' + t_ID + r')+\((' + t_ID + r')*\)(' + t_WS + r')*\*\/'
    capl_end = r'\/\*\@\@end(' + t_WS + r')*\*\/'

    
    #array_decl = r'(' + t_LBRK + r')[0-9]*(' + t_RBRK + r')((' + t_LBRK + r')[0-9]*(' + t_RBRK + r'))*'
    
    @TOKEN(hex_const)
    def t_HEX_NUM(self,t):
        return t

    @TOKEN(float_const)            # with decimal point (have precedence of DEC)
    def t_FLOAT_NUM(self,t):
        return t

    @TOKEN(t_NUM)
    def t_DEC_NUM(self,t):
        return t

    @TOKEN(on_event_declar)
    def t_CAPLEVENT(self,t):
        return t

    @TOKEN(t_ID)
    def t_RESERVED(self,t):                 # get reserved word
        t.type = self.reserved_words.get(t.value, 'ID')
        return t

    @TOKEN(array_decl)
    def t_ARRAY(self,t):
        return t

    @TOKEN(capl_begin)
    def t_CAPLBEGIN(self,t):
        return t   

    @TOKEN(capl_func_begin)
    def t_CAPLFUNCBEGIN(self,t):
        return t
    
    @TOKEN(capl_end)
    def t_CAPLEND(self,t):
        return t    

    def getTokens(self):
        return self.tokens;
   
    t_ignore = ' \t'              # ignore 
    
    # new line rule
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)      # count lines

    # error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self,filename):
        data = open(filename).read()
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()            # take next token
            if not tok: break                   # EOF reached
            print(tok)

    def __init__(self):
       print("Lexer initialized.")