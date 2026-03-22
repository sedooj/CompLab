grammar FunctionDef;

start
    : VAL IDENT COLON LPAREN type_list RPAREN ARROW type ASSIGN LBRACE param_list ARROW expr RBRACE SEMI EOF
    ;

type_list
    : type (COMMA type)*
    ;

param_list
    : param (COMMA param)*
    ;

param
    : IDENT
    | UNDERSCORE
    ;

type
    : INT_TYPE
    | STRING_TYPE
    | DOUBLE_TYPE
    | FLOAT_TYPE
    | BOOLEAN_TYPE
    ;

expr
    : term ((PLUS | MINUS) term)*
    ;

term
    : factor ((MUL | DIV | MOD) factor)*
    ;

factor
    : IDENT
    | NUMBER
    | LPAREN expr RPAREN
    ;

VAL         : 'val';
COLON       : ':';
LPAREN      : '(';
RPAREN      : ')';
ARROW       : '->';
ASSIGN      : '=';
SEMI        : ';';
LBRACE      : '{';
RBRACE      : '}';
COMMA       : ',';
PLUS        : '+';
MINUS       : '-';
MUL         : '*';
DIV         : '/';
MOD         : '%';
UNDERSCORE  : '_';

INT_TYPE        : 'Int';
STRING_TYPE     : 'String';
DOUBLE_TYPE     : 'Double';
FLOAT_TYPE      : 'Float';
BOOLEAN_TYPE    : 'Boolean';

IDENT       : [a-zA-Z_] [a-zA-Z0-9_]*;
NUMBER      : [0-9]+;

WS          : [ \t\r\n]+ -> skip;
