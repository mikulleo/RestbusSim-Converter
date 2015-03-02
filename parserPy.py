# parser file
#
# Author: Leos Mikulka (mikulkal@hotmail.com)
# Date: 

__author__ = "Leos Mikulka"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "mikulkal@hotmail.com"

from lexer import Lexer
import ply.lex as lex
import ply.yacc as yacc
import ast
import io
import string

class Node:
    def __init__(self,type,children=None,leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf

    def __repr__(self):
        return "{type: %s, children: %s, leaf: %s}" % (self.type,self.children,self.leaf)

    #def __str__(self):
    #    return "(type: %s, children: %s, leaf: %s)" % (self.type,self.children,self.leaf)


class Parser:
    
    string = ""
    inside = 0
    tokens = Lexer().tokens                     # define tokens

    precedence = (
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE','MOD'),
        ('left','EQ_TEST','NOT_EQ_TEST'),
        ('left','GT','GTE','LT','LTE'),
        ('left','BIT_AND','BIT_OR','BIT_XOR'),
        ('left','LSHIFT','RSHIFT'),
        ('left','AND','OR'),
    )

    def p_program(self,p):                          # lines of code
        ''' program : code_fragment
                    | program code_fragment '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[2]
            else:
                p[0] = p[1]+(p[2],)             # append to the tuple

    def p_code_fragment_1(self,p):
        ''' code_fragment : CAPLFUNCBEGIN user_function compound_statement CAPLEND '''
        p[0] = Node('Function_UD',p[3],p[2])

    def p_code_fragment_2(self,p):              
        ''' code_fragment : capl_event_declaration compound_statement CAPLEND'''
        p[0] = Node('CAPL_event',p[2],p[1])

    def p_code_fragment_3(self,p):
        ''' code_fragment : globalVars_declaration compound_statement CAPLEND'''
        p[0] = Node('GlobalVars_decl',p[2],p[1])

    def p_code_fragment_4(self,p):
        ''' code_fragment : comment '''
        p[0] = p[1]

    def p_user_function(self,p):
        ''' user_function : entry LPAR RPAR
                          | entry LPAR parameter_list RPAR
                          | declaration_type entry LPAR RPAR
                          | declaration_type entry LPAR parameter_list RPAR '''
        if len(p) == 4:
            p[0] = p[1]
        elif len(p) == 5 and p[1].type == 'ID':
            p[0] = p[1],p[3]
        elif len(p) == 5:
            p[0] = p[1],p[2]
        else:
            p[0] = p[1],p[2],p[4]

    def p_capl_event_declaration(self,p):           # e.g. on envVar initialize
        ''' capl_event_declaration : CAPLBEGIN on_event entry
                                   | CAPLBEGIN on_event const
                                   | CAPLBEGIN on_event '''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = p[2],p[3]

    def p_globalVars_declaration(self,p):
        ''' globalVars_declaration : CAPLBEGIN variables_keyword '''
        p[0] = p[2]

    def p_statement(self,p):
        ''' statement : capl_function
                      | compound_statement
                      | if_statement 
                      | while_statement
                      | do_while_statement
                      | for_statement 
                      | switch_statement
                      | jump_statement'''
        p[0] = p[1]

    def p_parameter_list(self,p):
        ''' parameter_list : parameter_declaration
                           | parameter_list comma parameter_declaration'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[3]
            else:
                p[0] = p[1]+(p[3],)                 # append to the tuple

    def p_parameter_declaration(self,p):
        ''' parameter_declaration : declaration_single
                                  | expression
                                  | char_string 
                                  | declaration_type declaration_single '''
        if len(p) == 2:
            p[0] = Node("PARAM",None,p[1])
        else:
            print(p[1])
            p[0] = Node("PARAM",None,(p[1],p[2]))

    def p_declaration(self,p):                      # terminated declaration with ;
        ''' declaration : declaration_body SMC
                        | declaration_message_body SMC'''
        p[0] = p[1]

    def p_declaration_body(self,p):
        ''' declaration_body : declaration_type declarations_list'''
        p[0] = Node('Declaration',p[2],p[1])
     
    def p_declaration_message_body(self,p):
        ''' declaration_message_body : declaration_message '''
        p[0] = p[1]

    def p_declaration_message(self,p):
        ''' declaration_message : MESSAGE entry entry
                                | MESSAGE const entry'''
        p[0] = Node('Decl-MSG',p[3],p[2])

    def p_declaration_type(self,p):                # data types - TODO! Change specific for declarations/functions
        ''' declaration_type : type'''
        p[0] = Node('Type',None,p[1])

    def p_declarations_list(self,p):                # sequence of declarations; e.g. abc, cde
        ''' declarations_list : declaration_single
                              | declarations_list comma declaration_single '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[3]
            else:
                p[0] = p[1]+(p[3],)

    def p_declaration_single_var(self,p):
        ''' declaration_single : entry
                               | entry equals expression
                               | entry assign_operator expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif p[2] == '=':
            p[0] = Node('Assign',p[1],p[3])
        else:
            p[0] = Node('Assign_OP',(p[1],p[3]),p[2])

    def p_declaration_single_array(self,p):
        ''' declaration_single : entry array_brackets
                               | entry array_brackets equals expression
                               | entry array_brackets equals initializer_array'''
        if len(p) == 3:
            p[0] = Node('Array',None,(p[1],p[2]))
        else:    
            p[0] = Node('Assign_Array',(p[1],p[2]),p[4])

    def p_assignment(self,p):
        ''' assignment : declaration_single SMC '''
        p[0] = p[1]

    def p_expression(self,p):
        ''' expression : logical_expression
                       | conditional_expression '''
        p[0] = p[1]

    def p_logical_expression(self,p):
        ''' logical_expression : binary_expression
                               | logical_expression AND logical_expression
                               | logical_expression OR logical_expression 
                               | LPAR logical_expression RPAR AND LPAR logical_expression RPAR
                               | LPAR logical_expression RPAR OR LPAR logical_expression RPAR'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node("Logic_EXPR",(p[1],p[3]),p[2])

    
    def p_conditional_expression(self,p):
       ''' conditional_expression : binary_expression
                                  | LPAR binary_expression RPAR COND_QUAT expression COL conditional_expression '''
       if len(p) == 2:
           p[0] = p[1]
       else:
           p[0] = Node("Cond_EXPR",(p[5],p[7]),p[2])

    def p_binary_expression(self,p):
        ''' binary_expression : unary_expression
                              | binary_expression PLUS binary_expression
                              | binary_expression MINUS binary_expression
                              | binary_expression TIMES binary_expression
                              | binary_expression DIVIDE binary_expression
                              | binary_expression MOD binary_expression
                              | binary_expression EQ_TEST binary_expression
                              | binary_expression NOT_EQ_TEST binary_expression
                              | binary_expression GT binary_expression
                              | binary_expression GTE binary_expression
                              | binary_expression LT binary_expression
                              | binary_expression LTE binary_expression
                              | binary_expression BIT_AND binary_expression
                              | binary_expression BIT_OR binary_expression
                              | binary_expression BIT_XOR binary_expression
                              | binary_expression LSHIFT binary_expression
                              | binary_expression RSHIFT binary_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('Expression',(p[1],p[3]),p[2])

    def p_initializer_array(self,p):
        ''' initializer_array : char_string
                              | const_compound
                              | LCBR const_compound_list RCBR
                              | LCBR string_list RCBR '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[2]

    def p_block_item(self,p):                   # item inside compound statement
        ''' block_item : declaration
                       | assignment 
                       | statement
                       | case_statement
                       | comment'''
        p[0] = p[1]

    def p_block_item_switch(self,p):                   # item inside compound statement
        ''' block_item_switch : declaration
                              | assignment 
                              | statement
                              | comment'''
        p[0] = p[1]

    def p_inside_block_list(self,p):
        ''' inside_block_list : block_item
                              | inside_block_list block_item '''
        if len(p) == 2:  # or p[2] == [None]:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[2]
            else:
                p[0] = p[1]+(p[2],)             # append to the tuple

    def p_inside_block_list_switch(self,p):
        ''' inside_block_list_switch : block_item_switch
                                     | inside_block_list_switch block_item_switch '''
        if len(p) == 2:  # or p[2] == [None]:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[2]
            else:
                p[0] = p[1]+(p[2],)             # append to the tuple

    def p_const_compound_list(self,p):
        ''' const_compound_list : const_compound
                                | const_compound_list comma const_compound'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1][0],tuple):
                p[0] = p[1],p[3]
            else:
                p[0] = p[1]+(p[3],)

    def p_const_compound(self,p):
        ''' const_compound : LCBR const_list RCBR '''
        p[0] = p[2]

    def p_const_list(self,p):
        ''' const_list : const
                       | const_list comma const '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[3]
            else:
                p[0] = p[1]+(p[3],)

    def p_string_list(self,p):
        ''' string_list : char_string
                        | string_list comma char_string '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if not isinstance(p[1],tuple):
                p[0] = p[1],p[3]
            else:
                p[0] = p[1]+(p[3],)

    def p_compound_statement(self,p):               # i.e. { .... }
        ''' compound_statement : LCBR RCBR
                               | LCBR inside_block_list RCBR '''
        if len(p) == 3:
            pass
        else:
            p[0] = p[2]

    def p_if_statement(self,p):
        ''' if_statement : IF LPAR expression RPAR compound_statement
                         | IF LPAR expression RPAR compound_statement ELSE compound_statement'''
        if len(p) == 6:
            p[0] = Node("IF",p[5],p[3])
        else:
            p[0] = Node("IF-ELSE",(p[5],p[7]),p[3])

    def p_while_statement(self,p):
        ''' while_statement : WHILE LPAR expression RPAR compound_statement'''
        p[0] = Node("WHILE",p[5],p[3])

    def p_do_while_statement(self,p):
        ''' do_while_statement : DO compound_statement WHILE LPAR expression RPAR SMC'''
        p[0] = Node("DO-WHILE",p[2],p[5])

    def p_for_statement(self,p):
        ''' for_statement : FOR LPAR declaration expression SMC expression RPAR compound_statement
                          | FOR LPAR declaration_single SMC expression SMC expression RPAR compound_statement'''    # declaration ends with SMC
        if len(p) == 9:
            p[0] = Node("FOR",p[8],(p[3],p[4],p[6]))
        else:
            print("chuuuuuuuuligan")
            p[0] = Node("FOR",p[8],(p[3],p[5],p[7]))

    def p_switch_statement(self,p):
        ''' switch_statement : SWITCH LPAR expression RPAR compound_statement'''
        p[0] = Node("SWITCH",p[5],p[3])

    def p_case_statement(self,p):
        ''' case_statement : CASE KEY COL inside_block_list_switch
                           | CASE const COL inside_block_list_switch
                           | DEFAULT COL inside_block_list_switch'''
        if len(p) == 5:
            p[0] = Node("Case",p[4],p[2])             # since we wanna get tuple
        else:
            p[0] = Node("Case",p[3],'Default')

    def p_jump_statement_break(self,p):
        ''' jump_statement : BREAK SMC'''
        p[0] = Node("BREAK",None,None)

    def p_jump_statement_continue(self,p):
        ''' jump_statement : CONTINUE SMC'''
        p[0] = Node("CONTINUE",None,None)

    def p_jump_statement_return(self,p):
        ''' jump_statement : RETURN expression SMC'''
        p[0] = Node("RETURN",None,p[2])

    def p_capl_function(self,p):                    # e.g. ILSetSignal( Ctrl_C_Stat1_AR::ReturnKey_Psd_UB, 1);
        ''' capl_function : capl_function_body SMC '''
        p[0] = p[1]

    def p_unary_expression(self,p):
        ''' unary_expression : value_expression
                             | single_expression 
                             | capl_function_body'''
        p[0] = p[1]

    def p_single_expression_pre(self,p):
        ''' single_expression : INCREMENT value_expression
                              | DECREMENT value_expression
                              | COMPLEMENT value_expression
                              | NOT value_expression '''
        p[0] = Node("Expression",p[2],p[1])

    def p_single_expression_post(self,p):
        ''' single_expression : value_expression INCREMENT
                              | value_expression DECREMENT '''
        p[0] = Node("Expression",p[1],p[2])

    def p_value_expression(self,p):
        ''' value_expression : entry
                             | entry array_brackets
                             | const
                             | message_signal'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('Array',None,(p[1],p[2]))

    def p_capl_function_body(self,p):               
        ''' capl_function_body : declaration_single LPAR RPAR
                               | declaration_single LPAR parameter_list RPAR'''
                        #       | declaration_single LPAR const_list RPAR
                        #       | declaration_single LPAR string_list RPAR'''
        if len(p) == 4:
            p[0] = Node('CAPL_fcn',None,p[1])
        else:
            p[0] = Node('CAPL_fcn',p[3],p[1])

    def p_message_signal(self,p):                   # e.g. Ctrl_C_Stat1_AR::ReturnKey_Psd_UB
        ''' message_signal : declaration_single dcol declaration_single '''
        p[0] = Node("msg_sig",None,(p[1],p[3]))

    def p_entry_ID(self,p):                  
        ''' entry : ID '''                    # single identifier
        p[0] = Node('ID', None ,p[1])

    def p_entry_this(self,p):                   # word this
        ''' entry : THIS '''
        p[0] = Node('This',None,p[1])

    def p_entry_thisDot(self,p):                # e.g. this.ID, this.CAN, this.BYTE(0)
        ''' entry : THIS DOT ID
                  | THIS DOT BYTE
                  | THIS DOT LONG
                  | THIS DOT WORD
                  | THIS DOT DWORD
                  | THIS DOT BYTE LPAR DEC_NUM RPAR
                  | THIS DOT LONG LPAR DEC_NUM RPAR
                  | THIS DOT WORD LPAR DEC_NUM RPAR
                  | THIS DOT DWORD LPAR DEC_NUM RPAR'''
        if len(p) == 4:
            p[0] = Node('ThisDot',None,p[1]+p[2]+p[3])
        else:
            p[0] = Node('ThisDot',None,p[1]+p[2]+p[3]+p[4]+p[5]+p[6])

    def p_entry_signal(self,p):                 # message.signal
        ''' entry : ID DOT ID '''
        p[0] = Node("Signal",None,p[1]+p[2]+p[3])

    def p_entry_key(self,p):
        ''' entry : KEY '''
        p[0] = Node("Key",None,p[1])

    def p_on_event(self,p):                         # "on" is used at the beginning of CAPL events
        ''' on_event : CAPLEVENT '''
        p[0] = p[1]

    def p_variables_keyword(self,p):                # word 'variables'; used for declaring global vars.
        ''' variables_keyword : VARS '''
        p[0] = p[1]

    def p_comment(self,p):
        ''' comment : COMMENT
                    | CppCOMMENT '''
        p[0] = Node("COMMENT",None,p[1]) 

    def p_char_string(self,p):
        ''' char_string : STRING '''
        p[0] = Node("STRING",None,p[1])

    def p_const_int(self,p):                     # numerical constant
        ''' const : DEC_NUM
                  | MINUS DEC_NUM'''
        if len(p) == 2:
            p[0] = Node("INT",None,p[1])
        else:
            p[0] = Node("INT",None,p[1]+p[2])

    def p_const_hex(self,p):
        ''' const : HEX_NUM
                  | MINUS HEX_NUM'''
        if len(p) == 2:
            p[0] = Node("HEX",None,p[1])
        else:
            p[0] = Node("HEX",None,p[1]+p[2])

    def p_const_float(self,p):
        ''' const : FLOAT_NUM 
                  | MINUS FLOAT_NUM'''
        if len(p) == 2:
            p[0] = Node("FLOAT",None,p[1])
        else:
            p[0] = Node("FLOAT",None,p[1]+p[2])

    def p_const_char(self,p):
        ''' const : CHARC '''
        p[0] = Node("CHAR",None,p[1])

    def p_array_brackets(self,p):
        ''' array_brackets : ARRAY '''
        p[0] = p[1]

    def p_dcol(self,p):                         # double-colon (i.e. ::)
        ''' dcol : DCOL '''
        p[0] = p[1]

    def p_comma(self,p):                         # comma
        '''comma : COM
                 | empty'''
        p[0] = p[1]

    def p_equals(self,p):
        ''' equals : EQ '''
        p[0] = p[1]

    def p_type(self,p):
        ''' type :  BYTE
                 | INT
                 | WORD
                 | DWORD
                 | LONG
                 | FLOAT
                 | DOUBLE
                 | TIMER
                 | MSTIMER
                 | CHAR
                 | VOID '''
        p[0] = p[1]

    def p_assign_operator(self,p):
        ''' assign_operator : ADD_EQ
                            | SUB_EQ
                            | MULT_EQ
                            | DIV_EQ
                            | MOD_EQ
                            | LSHIFT_EQ
                            | RSHIFT_EQ
                            | OR_EQ
                            | AND_EQ
                            | XOR_EQ'''
        p[0] = p[1]

    def p_empty(self,p):
        '''empty :'''
        pass

    def p_error(self,p):
        if p:
            print('Syntax error %s' % p.value,p.lineno)
        else:
            print('Syntax error at the end of input')

    def is_number(self,num):
        try:
            int(num)
            return True
        except ValueError:
            return False

    def get_array_dims(self,array_brackets):
        array_dims = []
        array_split = array_brackets.split('[')
        array_split = array_split[1:]
        for array_split_i in array_split:
            array_split_i = array_split_i.split(']')
            array_dims.append(array_split_i[0])
        #if len(array_dims) == 1:
        #    if self.is_number(array_dims[0]):
        #        dim = int(array_dims[0])-1
        #        dim = str(dim)
        #    else:
        #        dim = "%s - 1" % array_dims[0]
        #    self.string += "%s)" % dim
        #else:
        #    for i in range(0,len(array_dims)):
        #        if self.is_number(array_dims[i]):
        #            dim = int(array_dims[i])-1
        #            dim = str(dim)
        #        else:
        #            dim = "%s - 1" % array_dims[i]
        #        if not i == (len(array_dims)-1):  
        #            self.string += "%s," % dim
        #        else:
        #            self.string += "%s)" % dim
        
        return array_dims

    def generate_array(self,variable_name,array_brackets,var_type_first=None,var_type_rest=None): 
        if var_type_first == None:                          # used during array assignment, i.e. no declaration
            pass
        else:
            self.string += "\tDim %s(" % variable_name
        array_dims = self.get_array_dims(array_brackets)
        if len(array_dims) == 1:
            if self.is_number(array_dims[0]):
                dim = int(array_dims[0])
                dim = str(dim)
            else:
                dim = "%s" % array_dims[0]
            self.string += "%s)" % dim
        else:
            for i in range(0,len(array_dims)):
                if self.is_number(array_dims[i]):
                    dim = int(array_dims[i])
                    dim = str(dim)
                else:
                    dim = "%s" % array_dims[i]
                if not i == (len(array_dims)-1):  
                    self.string += "%s," % dim
                else:
                    self.string += "%s)" % dim
        if var_type_first == None:                          # used during array assignment, i.e. no declaration
            pass
        else:
            self.string += " As %s%s\n" % (var_type_first,var_type_rest)

        return array_dims

    def generate_declaration(self,declaration_param,isInside):
        variable_type = declaration_param.leaf.leaf
        variable_type_first = (variable_type[0]).upper()    # make first letter uppercase
        variable_type_rest = variable_type[1:len(variable_type)]

        if not isinstance(declaration_param.children,tuple):    # single declaration
            variable = declaration_param.children
            if variable.type == 'Array':
                variable_name = variable.leaf[0].leaf
                array_brackets = variable.leaf[1]
                if not variable_type == 'char':
                    self.generate_array(variable_name,array_brackets,variable_type_first,variable_type_rest)   
                else:
                    if len(array_brackets) > 3:
                        dim = int(array_brackets[4])
                        self.string += "\tDim %s(%s) as String\n"   % (variable_name,dim)     # 2-dim array of strings
                    else:
                        self.string += "\tDim %s as String\n" % variable_name     # string = array of chars

            elif variable.type == 'Assign_Array':
                variable_name = variable.children[0].leaf
                array_brackets = variable.children[1]
                if not variable_type == 'char':
                    array_dims = self.generate_array(variable_name,array_brackets,variable_type_first,variable_type_rest)

                    values_array = []
                    val_entry = []
                    if len(array_dims) == 2:
                        for val in variable.leaf:
                            for val_dim in val:
                                val_entry.append(val_dim.leaf)
                            values_array.append(val_entry)
                            val_entry = []

                        if self.is_number(array_dims[0]):
                            for i in range(0,int(array_dims[0])):
                                for j in range(0,int(array_dims[1])):
                                    self.string += "\t%s(%d,%d) = %s\n" % (variable_name,i,j,values_array[i][j])
                        else:
                            print("Cannot declare an array with no position numbers!")
                            self.string += "Cannot declare an array with no position numbers!\n"
                    elif len(array_dims) == 1:
                        if self.is_number(array_dims[0]):
                            if isinstance(variable.leaf,tuple):
                                for val_dim in variable.leaf:
                                    values_array.append(val_dim.leaf)
                            else:
                                values_array.append(variable.leaf.leaf)         # one entry array
                            for i in range(0,int(array_dims[0])):
                                self.string += "\t%s(%d) = %s\n" % (variable_name,i,values_array[i])
                        else:
                            print("Cannot declare an array with no position numbers!")
                            self.string += "Cannot declare an array with no position numbers!\n"
                else:       # array of chars = string
                   array_dims = self.get_array_dims(array_brackets)
                   if len(array_dims) > 1:
                       dim = len(array_dims) - 1
                       self.string += "\tDim %s(%s) as String\n"   % (variable_name,dim)     # 2-dim array of strings
                       for i in range(0,len(variable.leaf)):
                           self.string += "\t%s(%s) = %s\n" % (variable_name,i,variable.leaf[i].leaf)                      
                   else:
                       self.string += "\tDim %s as String\n" % variable_name
                       self.string += "\t%s = %s\n" % (variable_name,variable.leaf.leaf)     # assign string
                        
            elif variable.type == 'Assign':                 # declaration with assignment
                if variable_type == 'timer' or variable_type == 'msTimer':
                    self.string += "\'Timers declaration not supported!\'\n"
                else: 
                    self.string += "\tDim %s" % variable.children.leaf
                    self.string += " As %s%s\n" % (variable_type_first,variable_type_rest) 
                    self.generate_code(variable)                # generate assignment
            else: 
                variable_name = variable.leaf               # declaration without assignment

                if variable_type == 'timer' or variable_type == 'msTimer':
                    self.string += "\'Timers declaration not supported!\'\n"
                else: 
                    self.string += "\tDim %s" % variable_name
                    self.string += " As %s%s\n" % (variable_type_first,variable_type_rest) 
        else:                                               # multiple declarations, e.g. int j, k = 2;
            for variable in declaration_param.children:
                if variable.type == 'Array':                # during multiple declarations is assumed that no array is assigned values
                    variable_name = variable.leaf[0].leaf
                    array_brackets = variable.leaf[1]   
                    self.generate_array(variable_name,array_brackets,variable_type_first,variable_type_rest)  

                if variable.type == 'Assign':           # declaration with assignment
                    if (variable_type_first+variable_type_rest) == "Timer":
                        self.string += "\'Timers not supported!\'\n"
                    else: 
                        self.string += "\tDim %s" % variable.children.leaf
                        self.string += " As %s%s\n" % (variable_type_first,variable_type_rest) 
                        self.generate_code(variable)        # generate assignment
                else:
                    variable_name = variable.leaf       # declaration without assignment
                    if (variable_type_first+variable_type_rest) == "Timer":
                        self.string += "\'Timers not supported!\'\n"
                    else: 
                        self.string += "\tDim %s" % variable_name
                        self.string += " As %s%s\n" % (variable_type_first,variable_type_rest)   

    def generate_assignment(self,var,isInside):       
        if var.type == 'Assign':
            variable_name = var.children.leaf
            assign_value = var.leaf.leaf
            if not var.leaf.type == 'Array':                 
                if var.leaf.type == 'Key':              # single quotes needs to be replaced by double quotes
                    assign_value = assign_value.split("'")
                    self.string += "\t%s = \"%s\"\n" % (variable_name,assign_value[1])
                elif var.leaf.children == []:
                    self.string += "\t%s = %s\n" % (variable_name,assign_value)
                else:                                   # expression
                    self.string += "\t%s = " % variable_name
                    self.generate_code(var.leaf)
                    self.string += "\n"
            else:
                array_brackets = assign_value[1]
                array_name = assign_value[0].leaf
                self.string += "\t%s = %s(" % (variable_name,array_name)
                self.generate_array(None,array_brackets,None,None)
                self.string += "\n"
        elif var.type == 'Assign_Array':
            variable_name = var.children[0].leaf
            assign_value = var.leaf.leaf
            if not var.leaf.type == 'Array':
                array_brackets = var.children[1]
                self.string += "\t%s(" % variable_name
                array_dims = self.generate_array(variable_name,array_brackets,None,None)
                self.string += " = %s\n" % assign_value
            else:
                array_brackets_init = var.children[1]
                array_brackets_assign = assign_value[1]
                array_name = assign_value[0].leaf
                self.string += "\t%s(" % variable_name
                array_dims = self.generate_array(variable_name,array_brackets_init,None,None)
                self.string += " = %s(" % array_name
                self.generate_array(None,array_brackets_assign,None,None)
                self.string += "\n"

    def generate_function(self,function_param,isInside):
        if isInside == 1:
            string_param = "\t"
        else:
            string_param = ""

        if function_param.type == 'Function_UD':
           
            function_UD_declar = function_param.leaf
            if function_UD_declar[0].type == 'ID':
                function_UD_name = function_UD_declar[0].leaf
                function_UD_name_first = (function_UD_name[0]).upper()    # make first letter uppercase
                function_UD_name_rest = function_UD_name[1:len(function_UD_name)]
                function_UD_type = ""
            else:
                function_UD_type = function_UD_declar[0].leaf
                function_UD_type_first = (function_UD_type[0]).upper()    # make first letter uppercase
                function_UD_type_rest = function_UD_type[1:len(function_UD_type)]
                function_UD_name = function_UD_declar[1].leaf
                function_UD_name_first = (function_UD_name[0]).upper()    # make first letter uppercase
                function_UD_name_rest = function_UD_name[1:len(function_UD_name)]

            if (function_UD_type == 'void' or function_UD_type == ''):
                # either type name() or name()
                if (len(function_param.leaf) < 2) or (len(function_param.leaf) == 2 and not function_param.leaf[0].type == 'ID'):
                    self.string += "Sub %s%s()\n" % (function_UD_name_first,function_UD_name_rest)
                # name(parameters)
                elif len(function_param.leaf) == 2 and function_param.leaf[0].type == 'ID': 
                    self.string += "Sub %s%s" % (function_UD_name_first,function_UD_name_rest)
                    parameters = function_param.leaf[1]

                    if not isinstance(parameters,tuple):                # only one parameter...
                        if isinstance(parameters.leaf,Node):            # ...without specified type
                            param_name = parameters.leaf.leaf 
                            self.string += "(%s)\n" % param_name
                        else:                                           # ... with specified type
                            param_type_first = (parameters.leaf[0].leaf[0]).upper()
                            param_type_rest = parameters.leaf[0].leaf[1:len(parameters.leaf[0].leaf)]
                            param_name = parameters.leaf[1].leaf
                            self.string += "(%s As %s%s)\n" % (param_name,param_type_first,param_type_rest)
                    else:
                        for i in range(0,len(parameters)):                    # several parameters...
                            if isinstance(parameters[i].leaf,Node):           # ...without specified type
                                param_name = parameters[i].leaf.leaf
                                if i == 0: 
                                    self.string += "(%s," % param_name
                                elif i == (len(parameters)-1):
                                    self.string += "%s)\n" % param_name
                                else:
                                    self.string += "%s," % param_name
                            else:                                             # ... with specified type
                                param_type_first = (parameters[i].leaf[0].leaf[0]).upper()
                                param_type_rest = parameters[i].leaf[0].leaf[1:len(parameters[i].leaf[0].leaf)]
                                param_name = parameters[i].leaf[1].leaf
                                if i == 0:
                                    self.string += "(%s As %s%s," % (param_name,param_type_first,param_type_rest)
                                elif i == (len(parameters)-1):
                                    self.string += "%s As %s%s)\n" % (param_name,param_type_first,param_type_rest)
                                else: 
                                    self.string += "%s As %s%s," % (param_name,param_type_first,param_type_rest)
                # type name(parameters)
                else:
                    self.string += "Sub %s%s" % (function_UD_name_first,function_UD_name_rest)
                    parameters = function_param.leaf[2]

                    if not isinstance(parameters,tuple):                # only one parameter...
                        if isinstance(parameters.leaf,Node):            # ...without specified type
                            param_name = parameters.leaf.leaf 
                            self.string += "(%s)\n" % param_name
                        else:                                           # ... with specified type
                            param_type_first = (parameters.leaf[0].leaf[0]).upper()
                            param_type_rest = parameters.leaf[0].leaf[1:len(parameters.leaf[0].leaf)]
                            param_name = parameters.leaf[1].leaf
                            self.string += "(%s As %s%s)\n" % (param_name,param_type_first,param_type_rest)
                    else:
                        for i in range(0,len(parameters)):                    # several parameters...
                            if isinstance(parameters[i].leaf,Node):           # ...without specified type
                                param_name = parameters[i].leaf.leaf
                                if i == 0: 
                                    self.string += "(%s," % param_name
                                elif i == (len(parameters)-1):
                                    self.string += "%s)\n" % param_name
                                else:
                                    self.string += "%s," % param_name
                            else:                                             # ... with specified type
                                param_type_first = (parameters[i].leaf[0].leaf[0]).upper()
                                param_type_rest = parameters[i].leaf[0].leaf[1:len(parameters[i].leaf[0].leaf)]
                                param_name = parameters[i].leaf[1].leaf
                                if i == 0:
                                    self.string += "(%s As %s%s," % (param_name,param_type_first,param_type_rest)
                                elif i == (len(parameters)-1):
                                    self.string += "%s As %s%s)\n" % (param_name,param_type_first,param_type_rest)
                                else: 
                                    self.string += "%s As %s%s," % (param_name,param_type_first,param_type_rest)

                statements = function_param.children 
                self.inside = 1
                if statements == []:
                    self.string += '\n'
                elif not isinstance(statements,tuple):
                    self.generate_code(statements)
                else:
                    for statement in statements:
                        self.generate_code(statement)
                self.string += "End Sub\n"
            else:
                if len(function_param.leaf) == 2:
                    self.string += "Function %s%s()\n" % (function_UD_name_first,function_UD_name_rest)
                else:
                    self.string += "Function %s%s" % (function_UD_name_first,function_UD_name_rest)
                    parameters = function_param.leaf[2]

                    if not isinstance(parameters,tuple):                # only one parameter...
                        if isinstance(parameters.leaf,Node):            # ...without specified type
                            param_name = parameters.leaf.leaf 
                            self.string += "(%s)\n" % param_name
                        else:                                           # ... with specified type
                            param_type_first = (parameters.leaf[0].leaf[0]).upper()
                            param_type_rest = parameters.leaf[0].leaf[1:len(parameters.leaf[0].leaf)]
                            param_name = parameters.leaf[1].leaf
                            self.string += "(%s As %s%s)\n" % (param_name,param_type_first,param_type_rest)
                    else:
                        for i in range(0,len(parameters)):                    # several parameters...
                            if isinstance(parameters[i].leaf,Node):           # ...without specified type
                                param_name = parameters[i].leaf.leaf
                                if i == 0: 
                                    self.string += "(%s," % param_name
                                elif i == (len(parameters)-1):
                                    self.string += "%s) as %s%s\n" % (param_name,function_UD_type_first,function_UD_type_rest)
                                else:
                                    self.string += "%s," % param_name
                            else:                                             # ... with specified type
                                param_type_first = (parameters[i].leaf[0].leaf[0]).upper()
                                param_type_rest = parameters[i].leaf[0].leaf[1:len(parameters[i].leaf[0].leaf)]
                                param_name = parameters[i].leaf[1].leaf
                                if i == 0:
                                    self.string += "(%s As %s%s," % (param_name,param_type_first,param_type_rest)
                                elif i == (len(parameters)-1):
                                    self.string += "%s As %s%s) as %s%s\n" % (param_name,param_type_first,param_type_rest,function_UD_type_first,function_UD_type_rest)
                                else: 
                                    self.string += "%s As %s%s," % (param_name,param_type_first,param_type_rest)

                statements = function_param.children  
                self.inside = 1
                if statements == []:
                    self.string += '\n'
                elif not isinstance(statements,tuple):
                    self.generate_code(statements)
                else:
                    for statement in statements:
                        self.generate_code(statement)
                self.string += "End Function\n"

        if function_param.type == 'CAPL_fcn':
               
            function_name = function_param.leaf.leaf          # leaf: {ID, _ , ILSetSignal}

            if function_name == 'ILSetSignal':          # sets the transferred signal to the provided physical value
                self.string += "\tSystem.SetSignal"
                parameters = function_param.children
                message_name = parameters[0].leaf.leaf[0].leaf
                signal_name = parameters[0].leaf.leaf[1].leaf
                signal_value = parameters[1].leaf.leaf
                self.string += "(\"TX.CTRL_C.%s.%s\", %s)\n" % (message_name,signal_name,signal_value)

            elif function_name == 'getSignal':          # gets the valueo of a signal
                self.string += "System.GetSignal"
                parameter = function_param.children.leaf
                values = parameter.leaf
                if(parameter.type == 'msg_sig'):
                    message_name = values[0].leaf
                    signal_name = values[1].leaf
                    self.string += "(\"TX.CTRL_C.%s.%s\")\n" % (message_name,signal_name)

            elif function_name == 'getFirstCANdbName':
                self.string += "System.GetDatabase"
                index = self.string.rfind('S')
                next_index = self.string.rfind('\n',0,index)            # since we want to delete variable before fcn. name  
                self.string = self.string[:next_index+1] + self.string[index:]
                parameters = function_param.children
                buffer_name = parameters[0].leaf.leaf
                self.string += "(%s)\n" % buffer_name

            elif function_name == 'write':              # prints to a console
                parameters = function_param.children
                if not isinstance(parameters,tuple):
                   self.string += "\tDebug.Print %s\n" % parameters.leaf.leaf
                else:
                    for i in range (0,len(parameters)):
                        if parameters[i].leaf.type == 'STRING':         # must be in format "text", i.e. not single quotes
                            self.string += "\tDebug.Print " + parameters[i].leaf.leaf + " "
                        elif i == 0:        # id at first place
                            self.string += "\tDebug.Print " + parameters[i].leaf.leaf + " & \" \" "
                        elif i == len(parameters)-1:
                            self.string += "& " + parameters[i].leaf.leaf + "\n"
                        else:
                            self.string += "& " + parameters[i].leaf.leaf + " & \" \" "

            elif function_name == 'output':             # outputs a message
                message_name = function_param.children.leaf.leaf
                self.string += "\'Warning: check whether Channel, Id and Data are initiliazed.\'\n"
                self.string += "\t"+message_name + ".Send\n"

                                
            else:
                parameters = function_param.children
                self.string += "\t%s" % function_name
                if not isinstance(parameters,tuple):
                    if parameters == []:         # no parameters
                        self.string += "()"
                    elif parameters.leaf.type == 'CAPL_fcn':
                        self.string += "("
                        self.generate_function(parameters.leaf,isInside)
                        self.string += ")"      # \n
                    elif parameters.leaf.type == 'Expression':
                         self.string += "("
                         self.generate_code(parameters.leaf) # change to separate function
                         self.string += ")"
                    else:
                        self.string += "(%s)" % parameters.leaf.leaf    #\n
                else:
                    for i in range (0,len(parameters)):
                        if parameters[i] == []:
                            self.string += "()"     # no parameters
                        if parameters[i].leaf.type == 'CAPL_fcn':
                            if i == 0:
                                self.string += "("
                                self.generate_function(parameters[i].leaf,isInside)
                            elif i == len(parameters)-1:
                                self.generate_function(parameters[i].leaf,isInside)
                                self.string += ")"
                            else:
                                self.generate_function(parameters[i].leaf,isInside)
                                self.string += ","
                        elif parameters[i].leaf.type == 'Expression':
                            if i == 0:
                                self.string += "("
                                self.generate_code(parameters[i].leaf) # change to separate function
                            elif i == len(parameters)-1:
                                self.generate_code(parameters[i].leaf) # change to separate function
                                self.string += ")"
                            else:
                                self.generate_code(parameters[i].leaf) # change to separate function
                                self.string += ","
                        else:
                            param_name = parameters[i].leaf.leaf
                            if i == 0:
                                self.string += "(%s," % param_name
                            elif i == len(parameters)-1:
                                self.string += "%s)" % param_name   # \n
                            else:
                                self.string += "%s," % param_name

    def generate_message_declaration(self,message):
        message_id = message.leaf.leaf
        message_name = message.children.leaf
        self.string += "\tDim %s as New CanMsg\n" % message_name
        self.string += "\t%s.Id = %s\n" % (message_name,message_id)


    def generate_code(self,tree):
        #if self.string == "":
        #    f = open('testScript.txt','w')
        #else:
        #    f = open('testScript.txt','a')
        
        print(tree)                        # print whole tree - type Node
        print("-------------")

        root = tree             # start with root
        if not isinstance(root,tuple):
            if root.type == 'GlobalVars_decl':      # translation of global variables declaration
                self.string += "Sub Main\n"         # global variables will appear in Sub Main
                declarations = root.children
                self.inside = 0
                if not isinstance(declarations,tuple):
                    if declarations.type == 'Decl-MSG':
                        self.generate_message_declaration(declarations)
                    elif declarations.type == 'COMMENT':
                        self.generate_code(declarations)
                    else:
                        self.generate_declaration(declarations,self.inside)
                else:
                    for declaration in declarations:
                        if declaration.type == 'Decl-MSG':
                            self.generate_message_declaration(declaration)
                        elif declaration.type == 'COMMENT':
                            self.generate_code(declaration)
                        else:
                            self.generate_declaration(declaration,self.inside)
                self.string += "End Sub\n\n"

            elif root.type == 'Declaration':
                #self.generate_declaration(root.children,self.inside)
                self.generate_declaration(root,self.inside)

            elif root.type == 'Decl-MSG':
                self.generate_message_declaration(root)

            elif root.type == 'Assign' or root.type == 'Assign_Array': #root.type == 'Assign_OP':
                self.generate_assignment(root,self.inside)

            elif root.type == 'Expression' or root.type == 'Assign_OP':
                operator = root.leaf
                if not isinstance(root.children,tuple):         # unary expression
                    if operator == '!' or operator == '~':
                        self.string += "Not %s" % root.children.leaf
                    elif operator == '++':
                        print(root)
                        self.string += "%s + 1" % root.children.leaf
                    elif operator == '--':
                        self.string += "%s - 1" % root.children.leaf
                else:
                    if operator == '%':
                        operator = 'Mod'
                    elif operator == '&':
                        operator = 'And'
                    elif operator == '&&':
                        operator = 'AndAlso'
                    elif operator == '|':
                        operator = 'Or'
                    elif operator == '||':
                        operator = 'OrElse'
                    elif operator == '==':
                        operator = '='
                    elif operator == '!=':
                        operator = '<>'
                    if isinstance(root.children[0].leaf,Node) and isinstance(root.children[1].leaf,Node):      # both leaves are functions
                        self.generate_function(root.children[0],self.inside)
                        self.string += " %s " % operator
                        self.generate_function(root.children[1],self.inside)
                    elif isinstance(root.children[0].leaf,Node) and not isinstance(root.children[1].leaf,Node):      # leaf is a function
                        self.generate_function(root.children[0],self.inside)
                        self.string += " %s %s" % (operator,root.children[1].leaf)
                    elif not isinstance(root.children[0].leaf,Node) and isinstance(root.children[1].leaf,Node):      # leaf is a function
                        self.string += "\t%s %s " % (root.children[0].leaf,operator)
                        self.generate_function(root.children[1],self.inside)
                    else:
                        self.string += "\t%s %s %s" % (root.children[0].leaf,operator,root.children[1].leaf)
                    if root.type == 'Assign_OP':
                        self.string += '\n'                     # new line follows assignment

            elif root.type == 'Logic_EXPR':
                for i in range(0,len(root.children)):
                    self.generate_code(root.children[i])            # iterate through expressions
                    if not i == len(root.children)-1:
                        if not isinstance(root.leaf,tuple):
                            operator = root.leaf
                        else:   
                            operator = root.leaf[i]
                        if operator == '&&':
                            operator = 'AndAlso'
                        elif operator == '||':
                            operator = 'OrElse'
                        self.string += " %s " % operator

            elif root.type == 'Function_UD':             # translation of user-defined functions
                #self.string += self.generate_function(root,self.inside)
                self.generate_function(root,self.inside)
                self.string += "\n"

            elif root.type == 'CAPL_fcn':             # translation of CAPL defined functions
                self.generate_function(root,self.inside)
                self.string += "\n"

            elif root.type == 'IF':                    # if statement
                self.string += '\tIf '
                self.generate_code(root.leaf)
                self.string += ' Then\n'
                if not isinstance(root.children,tuple):
                    self.string += '\t'
                    self.generate_code(root.children)
                else:
                    for root_children in root.children:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += '\tEnd If\n'

            elif root.type == 'IF-ELSE':
                self.string += '\tIf '
                self.generate_code(root.leaf)
                self.string += ' Then\n'
                if not isinstance(root.children[0],tuple):
                    self.string += '\t'
                    self.generate_code(root.children[0])
                else:
                    for root_children in root.children[0]:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += '\tElse\n'
                if not isinstance(root.children[1],tuple):
                    self.string += '\t'
                    self.generate_code(root.children[1])
                else:
                    for root_children in root.children[1]:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += '\tEnd If\n'

            elif root.type == 'WHILE':
                self.string += '\tWhile '
                self.generate_code(root.leaf)
                self.string += '\n'
                if not isinstance(root.children,tuple):
                    self.string += '\t'
                    self.generate_code(root.children)
                else:
                    for root_children in root.children:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += '\tWend\n'

            elif root.type == 'DO-WHILE':
                self.string += '\tDo\n'
                if not isinstance(root.children,tuple):
                    self.string += '\t'
                    self.generate_code(root.children)
                else:
                    for root_children in root.children:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += '\tLoop Until '
                self.generate_code(root.leaf)
                self.string += '\n'

            elif root.type == 'FOR':
                self.string += "\' If iteration variable not declared ---> declare by Dim! \'\n"
                self.string += '\tFor '
                iter_var = root.leaf                # manipulating with iteration variable
                iter_var_name = iter_var[0].children.leaf      # in WWB we don't care about iter_var type, just the name
                final_iter_num = int(iter_var[1].children[1].leaf) - 1     # to what number we iterate
                if iter_var[2].leaf == '++':
                    step_size = 1                   # iteration step size
                self.string += "%s = 0 To %s Step %s\n" % (iter_var_name,final_iter_num,step_size)
                if not isinstance(root.children,tuple):
                    self.string += '\t'
                    self.generate_code(root.children)
                else:
                    for root_children in root.children:
                        self.string += '\t'
                        self.generate_code(root_children)
                self.string += "\tNext %s\n" % iter_var_name

            elif root.type == 'SWITCH':
                self.string += '\tSelect Case '
                case_var = root.leaf.leaf
                self.string += '%s\n' % case_var
                for case_single in root.children:
                    self.string += "\t\tCase "
                    case = case_single.leaf
                    if case == 'Default':
                        self.string += "Else\n"
                    else:
                        if type(case) == Node:
                            case = case.leaf
                        self.string += "%s\n" % case
                    self.string += "\t"
                    for stmt in case_single.children:        # translation of statements after case
                        if stmt.type == 'BREAK':
                            pass
                        else:
                            self.generate_code(stmt)
                self.string += "\tEnd Select\n"

            elif root.type == 'RETURN':
                self.string += '\tReturn '
                if isinstance(root.leaf,Node):
                    self.string += '%s\n' % root.leaf.leaf

            elif root.type == 'COMMENT':
                self.string += "\' %s \'\n" % root.leaf

            elif root.type == 'CAPL_event':           # translation of CAPL events
                statements = root.children
                if isinstance(root.leaf,tuple):
                    event_name = root.leaf[0]       # on envVar, ...
                else:
                    event_name = root.leaf.split("on ")[1]   # get event name, i.e. preStart, start, ...       
                if event_name == 'on envVar':     # Provetech doesn't really support on envVar
                    self.string += "Sub On_EnvVar\n"
                    print("Found \'on envVar\' event")     
                elif event_name == 'on key':
                    key = root.leaf[1].leaf.split('\'')[1]
                    #self.string += "Sub On_key_%s(char keyName)\n" 
                    self.string += "Sub On_key_%s()\n" 
                elif event_name == 'on message':
                    message = root.leaf[1].leaf
                    #self.string += "Sub On_message_%s(CAPLMessage Rx)\n" % message
                    self.string += "Sub On_message_%s()\n" % message
                elif event_name == 'on timer':
                    timer = root.leaf[1].leaf
                    self.string += "Sub On_timer_%s()\n" % timer
                else:
                    self.string += "Sub On_%s()\n" % event_name
                self.inside = 1 
                if not isinstance(statements,tuple):
                    self.generate_code(statements)
                else:
                    for statement in statements:
                        self.generate_code(statement)
                self.string += "End Sub\n\n"

        else:
            for entry in root:
                self.generate_code(entry)

    def write_to_file(self):
        f = open('testScript.txt','w')
        self.string = (self.string).replace("Int","Integer")
        self.string = (self.string).replace("Word","UInteger")      # unsigned 16-bits
        self.string = (self.string).replace("Dword","ULong")        # unsigned 32-bits
        self.string = (self.string).replace("Char","String")        # char not supported by WWB
        self.string = (self.string).replace("Float","Decimal")
        self.string = (self.string).replace("0x","&H")              # hex numbers

        f.write(self.string)
        print("WWB Script generated.")

    def __init__(self,caplFile):

        lexer_init = Lexer()                         # create instance of Lexer
        lexer_init.build()                           # build the lexer
        if isinstance(caplFile,str):                # program called from command line
            lexer_init.test(caplFile)                   # analyze an input file
            # Build the lexer and parser
            yacc.yacc(module = self)
            ast_tree = yacc.parse(open(caplFile).read())
        else:                                       # program called from GUI
            lexer_init.test(caplFile.get())              # analyze an input file
            # Build the lexer and parser
            yacc.yacc(module = self)
            ast_tree = yacc.parse(open(caplFile.get()).read())

        
        #if isinstance(ast_tree,tuple):
        #    for node in ast_tree:
        #        print(str(node)+"\n")  
        #else:
        #    if isinstance(ast_tree.children,tuple):
        #        for node in ast_tree.children:
        #            print(str(node))
        #    else:
        #        pass
                #print("WHOLE TREE:")
                #print(ast_tree)

        self.generate_code(ast_tree) 
        self.write_to_file()
        #ast_tree = ast.parse(open(caplFile.get()).read())
        #print(ast.dump(ast_tree))
        ##exec(compile(ast_tree, filename="<ast>", mode="exec"))

