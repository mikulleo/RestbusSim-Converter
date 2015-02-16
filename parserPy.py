# parser file 
#
# Author: Leos Mikulka (mikulkal@hotmail.com)
# Date:

from lexer import Lexer
import ply.lex as lex
import ply.yacc as yacc
import ast
import io

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

    tokens = Lexer().tokens                     # define tokens

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
        ''' code_fragment : capl_event_declaration compound_statement CAPLEND'''
        p[0] = Node('CAPL_event',p[2],p[1])

    def p_code_fragment_2(self,p):
        ''' code_fragment : globalVars_declaration compound_statement CAPLEND'''
        p[0] = Node('GlobalVars_decl',p[2],p[1])

    def p_code_fragment_3(self,p):
        ''' code_fragment : comment '''
        p[0] = p[1]

    def p_capl_event_declaration(self,p):           # e.g. on envVar initialize
        ''' capl_event_declaration : CAPLBEGIN on_event entry'''
        #p[0] = Node('CAPL_event',(p[1],p[2]))
        p[0] = p[2],p[3]

    def p_globalVars_declaration(self,p):
        ''' globalVars_declaration : CAPLBEGIN variables_keyword '''
        p[0] = p[2]

    def p_statement(self,p):
        ''' statement : capl_function
                      | compound_statement '''
        p[0] = p[1]

    def p_declaration(self,p):                      # terminated declaration with ;
        ''' declaration : declaration_body SMC '''
        p[0] = p[1]

    def p_declaration_body(self,p):
        ''' declaration_body : declaration_type declarations_list '''
        #p[0] = Node('Declaration',(p[1],p[2]))
        p[0] = Node('Declaration',p[2],p[1])

    def p_declaration_type(self,p):                # data types - doesn't include CHAR, VOID (specific for variables/functions)
        ''' declaration_type : BYTE
                             | INT
                             | WORD
                             | DWORD
                             | LONG
                             | FLOAT
                             | DOUBLE
                             | MESSAGE
                             | TIMER
                             | MSTIMER'''
        p[0] = Node('Type',None,p[1])

    def p_declarations_list(self,p):                # sequence of declarations; e.g. abc, cde
        ''' declarations_list : declaration_single
                              | declarations_list comma declaration_single '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1],p[3]

    def p_declaration_single(self,p):
        ''' declaration_single : entry
                               | entry equals initializer'''        # e.g. x = 5
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('Assign',p[1],p[3])

    def p_initializer(self,p):
        ''' initializer : unary_expression '''
        p[0] = p[1]

    def p_block_item(self,p):                   # item inside compound statement
        ''' block_item : declaration 
                       | statement '''
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

    def p_compound_statement(self,p):               # i.e. { .... }
        ''' compound_statement : LCBR RCBR
                               | LCBR inside_block_list RCBR '''
        if len(p) == 3:
            pass
        else:
            p[0] = p[2]

    def p_capl_function(self,p):                    # e.g. ILSetSignal( Ctrl_C_Stat1_AR::ReturnKey_Psd_UB, 1);
        ''' capl_function : capl_function_body SMC '''
        p[0] = p[1]

    def p_unary_expression(self,p):
        ''' unary_expression : entry
                             | const '''
        p[0] = p[1]

    # TODO!! NOT COMPLETE + create reserved words for functions!
    def p_capl_function_body(self,p):               
        ''' capl_function_body : declaration_single LPAR RPAR
                               | declaration_single LPAR capl_function_action RPAR '''
        if len(p) == 3:
            p[0] = Node('CAPL_fcn',None,p[1])
        else:
            p[0] = Node('CAPL_fcn',p[3],p[1])

    # TODO!! define more than message_signal
    def p_capl_function_action(self,p):             # e.g. Ctrl_C_Stat1_AR::ReturnKey_Psd_UB, 1
        ''' capl_function_action : message_signal comma const'''
        p[0] = Node("action",p[1],p[3])

    def p_message_signal(self,p):                   # e.g. Ctrl_C_Stat1_AR::ReturnKey_Psd_UB
        ''' message_signal : declaration_single dcol declaration_single '''
        p[0] = Node("msg_sig",None,(p[1],p[3]))

    def p_entry_ID(self,p):                  
        ''' entry : ID '''                    # single identifier
        p[0] = Node('ID', None ,p[1])
        #p[0] = ast.Str(p[1])

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

    def p_const_int(self,p):                     # numerical constant
        ''' const : DEC_NUM '''
        p[0] = Node("INT",None,p[1])

    def p_const_float(self,p):
        ''' const : FLOAT_NUM '''
        p[0] = Node("FLOAT",None,p[1])

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

    def p_empty(self,p):
        '''empty :'''
        pass

    def p_error(self,p):
        if p:
            print('Syntax error %s' % p.value,p.lineno)
        else:
            print('Syntax error at the end of input')

    def generate_declaration(self,declaration_param):
        string_param = "Dim "

        variable_type = declaration_param.leaf.leaf
        variable_type_first = (variable_type[0]).upper()    # make first letter uppercase
        variable_type_rest = variable_type[1:len(variable_type)]

        if not isinstance(declaration_param.children,tuple):
            if declaration_param.children.type == 'Assign':
                variable_name = declaration_param.children.children.leaf
                assign_value = declaration_param.children.leaf.leaf

                string_param += variable_name
                string_param += " As %s%s\n" % (variable_type_first,variable_type_rest) 
                string_param += "%s = %s\n" % (variable_name,assign_value)
                
            else:
                variable_name = declaration_param.children.leaf
                string_param += variable_name
                string_param += " As %s%s\n" % (variable_type_first,variable_type_rest) 
            
        return string_param

    def generate_function(self,function_param):
        if function_param.type == 'CAPL_fcn':
            string_param = ""
               
            function_name = function_param.leaf.leaf          # leaf: {ID, _ , ILSetSignal}
            if function_name == 'ILSetSignal':
                string_param += "\tSystem.SetSignal"
                action = function_param.children
                signal_value = action.leaf.leaf

                # TODO! CHANGE TO ---> if isinstance(action.children,tuple): ---> prob. don't define alone mes_sig
                if(action.children.type == 'msg_sig'):
                    values = action.children.leaf
                    if isinstance(values,tuple):
                        message_name = values[0].leaf
                        signal_name = values[1].leaf
                string_param += "(\"TX.CTRL_C.%s.%s\", %s)\n" % (message_name,signal_name,signal_value)
        
        return string_param

    def generate_code(self,tree):
        if self.string == "":
            f = open('testScript.txt','w')
        else:
            f = open('testScript.txt','a')
        
        #print(tree)                        # print whole tree - type Node

        root = tree             # start with root
        if not isinstance(root,tuple):
            if root.type == 'CAPL_event':
                self.string += "Sub Main\n"
      
                functions = root.children
                event_name = root.leaf[0]
                if event_name == 'on envVar':     # Provetech doesn't really support on envVar ---> can be dissmissed
                    print("Found \'on envVar\' event")      
                    if not isinstance(functions,tuple):     # single function
                        self.string += self.generate_function(functions)
                    else:
                        for function in functions:             # multiple functions
                            self.string += self.generate_function(function)
                    self.string += "End Sub\n"
                else:
                    for function in functions:
                        pass

            if root.type == 'GlobalVars_decl':
                declarations = root.children
                if not isinstance(declarations,tuple):
                    self.string += self.generate_declaration(declarations)
                else:
                    for declaration in declarations:
                        self.string += self.generate_declaration(declaration)
        else:
            for entry in root:
                self.generate_code(entry)

            f.write(self.string)
            print("WWB Script generated.")

    def __init__(self,caplFile):

        lexer_init = Lexer()                         # create instance of Lexer
        lexer_init.build()                           # build the lexer
        lexer_init.test(caplFile.get())              # analyze an input file

        # Build the lexer and parser
        yacc.yacc(module = self)
        ast_tree = yacc.parse(open(caplFile.get()).read())
          
        self.generate_code(ast_tree) 
        #ast_tree = ast.parse(open(caplFile.get()).read())
        #print(ast.dump(ast_tree))
        ##exec(compile(ast_tree, filename="<ast>", mode="exec"))

