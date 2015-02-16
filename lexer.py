# lexer for the compiler 
#
# Author: Leos Mikulka (mikulkal@hotmail.com)
# Date:

__author__ = "Leos Mikulka"
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

    reserved = {            # reserved keywords
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
        }

    numbers = {
        'dec_num' : 'DEC_NUM',
        'float_num' : 'FLOAT_NUM',
        }
 
    # list of tokens
    tokens = [
        'WS',
        'EQ',       # equals
        'COM',      # comma
        'SMC',      # semicolon
        'RCBR',     # right curly bracket
        'LCBR',     # left curly bracket  
        'LPAR',     # left parenthese
        'RPAR',     # right parenthese
        'NUM',      # number
        'TIMES',    # multiply
        'STRING',
        'CHARC',    # single character
        'ID',       # identifier
        'DCOL',     # double colon
        'COMMENT',      # normal comment
        'CppCOMMENT',   # C++ style comment
        'CAPLBEGIN',    # CAPL begin sectin, e.g. /*@@var: */
        'CAPLEND',      # CAPL end, i.e. /*@@end */
        'DATATYPE',     # int, float, ...
        'CAPLEVENT',    # CAPL event 
        'CAPLEVENT_word',  # reserved keywords for CAPL event
        'VARS',         # keyword 'variables'
        ] + list(reserved.values()) + list(numbers.values())

    t_WS = r'[ \t\n]'

    vars_keyword = r'variables(' + t_WS + r')+'

    @TOKEN(vars_keyword)            # must be before declaring ID! -- precedence
    def t_VARS(self,t):
        return t

    # regular expressions
    
    t_EQ = r'\='
    t_COM = r'\,'
    t_SMC = r'\;'
    t_LCBR = r'\{'
    t_RCBR = r'\}'
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_NUM = r'[0-9]+'
    t_TIMES = r'\*'
    t_STRING = r'\"(\\.|[^\\"])(\\.|[^\\"])+\"'
    t_CHARC = r'\"(.)\"'
    t_ID = r'[a-zA-Z_][a-zA-Z0-9_-]*'
    t_DCOL = r'\:\:'
    t_COMMENT = r'/\*([^\*]|\*[^*/])*\*/'     # manual - sec. 8.4. - comments
    t_CppCOMMENT = r'//.*'
    t_CAPLEVENT_word =r'PreStart|Start|stopMeasurement|busOff|timer|key|message|errorActive|errorPassive|warningLimit|errorFrame|envVar|preStop'
    #t_DATATYPE = r'(char|byte|int|word|dword|long|float|double|message|timer|msTimer)'
    #t_VAR = r'(' + t_DATATYPE + r')+(' + t_WS + r')*(' + t_ID + r')*(' + t_WS + r')*\;'

    float_const = r'(' + t_NUM + r')\.(' + t_NUM + r')'

    on_event_declar = r'(on' + t_WS + r')+(' + t_CAPLEVENT_word + r')+'
    capl_begin = r'\/\*\@\@(' + t_ID + r')*(\:)' + r'(' + t_WS + r')*(' + t_ID + r')?(\:)?(' + t_WS + r')*\*\/'
    capl_end = r'\/\*\@\@end(' + t_WS + r')*\*\/'

    

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
    def t_DATATYPE(self,t):                 # get data type of a variable
        t.type = self.reserved.get(t.value, 'ID')
        return t

    @TOKEN(capl_begin)
    def t_CAPLBEGIN(self,t):
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