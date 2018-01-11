# MAINTAINER:  Leonid V. Fedorenchik <leonid@fedorenchik.com>
# ORIGINAL AUTHOR:     Greg Sexton <gregsexton@gmail.com>
# WEBSITE:             https://github.com/fedorenchik/VimCalc3
# VERSION:             3.3, for Vim 7.0+
# LICENSE:             Same terms as Vim itself (see :help license).

import math, re, random

#### LEXICAL ANALYSIS FUNCTIONS ################################################

#lexemes
#digit  = [0-9]
#digits = digit+

#uppercase = [A-Z]
#lowercase = [a-z]

#alpha        = (uppercase|lowercase)
#alphanumeric = (alpha|digits)

#hexdigit  = [0-9a-fA-F]
#hexdigits = hexdigit+

#octdigit  = [0-7]
#octdigits = octdigit+

#bindigit  = [01]
#bindigits = bindigit+

#decnumber   = digits(. digits)?(e[+-]? digits)?
#hexnumber   = 0xhexdigits
#octalnumber = 0 octdigits
#binnumber   = 0bbindigits

#whitespace = [\t ]+

#ident = (alpha|_)(alphanumeric|_)*'?

#plus      = '+'
#subtract  = '-'
#multiply  = '*'
#divide    = '/'
#modulo    = '%'
#exponent  = '**'
#lShift    = '<<'
#rShift    = '>>'
#factorial = '!'

#unaryOp  = factorial
#binaryOp = plus|subtract|multiply|divide|modulo|exponent|lShift|rShift
#operator = unaryOp|binaryOp

#lParen    = '('
#rParen    = ')'
#comma     = ','
#assign    = '='
#pAssign   = '+='
#sAssign   = '-='
#mAssign   = '*='
#dAssign   = '/='
#modAssign = '%='
#expAssign = '**='

#delimiters = lParen|rParen|comma|assign|pAssign|sAssign|mAssign|dAssign|modAssign|expAssign

#let = 'let'
#keywords = let

#decDir     = ':dec'
#hexDir     = ':hex'
#octDir     = ':oct'
#binDir     = ':bin'
#intDir     = ':int'
#floatDir   = ':float'
#statusDir  = ':status' | ':s'
#varDir     = ':vars'
#quitDir    = ':q'
#directives = decDir | hexDir | octDir | binDir | intDir | floatDir | statusDir | varDir | quitDir

class VimCalcToken(object):
    def __init__(self, tokenID, attrib):
        self._tokenID = tokenID
        self._attrib = attrib
    def __repr__(self):
        return str(self._tokenID) + ':' + str(self._attrib)
    def __str__(self):
        return str(self._tokenID) + ':' + str(self._attrib)
    def getID(self):
        return self._tokenID
    def getAttrib(self):
        return self._attrib
    ID = property(getID, doc='VimCalcToken ID [string].')
    attrib = property(getAttrib, doc='VimCalcToken attribute [string].')

class VimCalcLexeme(object):
    def __init__(self, identifier, regex):
        self._ID = identifier
        self._regex = regex
    def getID(self):
        return self._ID
    def getRegex(self):
        return self._regex
    ID = property(getID, doc='VimCalcLexeme ID [string].')
    regex = property(getRegex, doc='Regex to match the VimCalcLexeme.')

#language lexemes NOTE: don't change these without changing syntax file
vimcalc_lexemes = [VimCalcLexeme('whitespace', r'\s+'),
                   VimCalcLexeme('hexnumber',  r'0[xX][0-9a-fA-F]+'),
                   VimCalcLexeme('octnumber',  r'0[0-7]+'),
                   VimCalcLexeme('binnumber',  r'0[bB][01]+'),
                   VimCalcLexeme('decnumber',  r'[0-9]*\.?([0-9]+)?([eE][+-]?[0-9]+)?'),
                   VimCalcLexeme('let',        r'let'),
                   VimCalcLexeme('ident',      r"[A-Za-z_][A-Za-z0-9_]*'?"),
                   VimCalcLexeme('expAssign',  r'\*\*='),
                   VimCalcLexeme('modAssign',  r'%='),
                   VimCalcLexeme('dAssign',    r'/='),
                   VimCalcLexeme('mAssign',    r'\*='),
                   VimCalcLexeme('sAssign',    r'-='),
                   VimCalcLexeme('pAssign',    r'\+='),
                   VimCalcLexeme('andAssign',  r'\&='),
                   VimCalcLexeme('orAssign',   r'\|='),
                   VimCalcLexeme('xorAssign',  r'\^='),
                   VimCalcLexeme('lShift',     r'<<'),
                   VimCalcLexeme('rShift',     r'>>'),
                   VimCalcLexeme('exponent',   r'\*\*'),
                   VimCalcLexeme('assign',     r'='),
                   VimCalcLexeme('comma',      r','),
                   VimCalcLexeme('lParen',     r'\('),
                   VimCalcLexeme('rParen',     r'\)'),
                   VimCalcLexeme('factorial',  r'!'),
                   VimCalcLexeme('modulo',     r'%'),
                   VimCalcLexeme('divide',     r'/'),
                   VimCalcLexeme('multiply',   r'\*'),
                   VimCalcLexeme('subtract',   r'-'),
                   VimCalcLexeme('plus',       r'\+'),
                   VimCalcLexeme('and',        r'\&'),
                   VimCalcLexeme('or',         r'\|'),
                   VimCalcLexeme('xor',        r'\^'),
                   VimCalcLexeme('decDir',     r':dec'),
                   VimCalcLexeme('hexDir',     r':hex'),
                   VimCalcLexeme('octDir',     r':oct'),
                   VimCalcLexeme('binDir',     r':bin'),
                   VimCalcLexeme('statusDir',  r':status'),
                   VimCalcLexeme('statusDir',  r':s'),         #shorthand
                   VimCalcLexeme('varDir',     r':vars'),
                   VimCalcLexeme('quitDir',    r':q'),
                   VimCalcLexeme('intDir',     r':int'),
                   VimCalcLexeme('floatDir',   r':float') ]

#takes an expression and uses the language lexemes
#to produce a sequence of tokens
def vimcalc_tokenize(expr):
    tokens = []
    while expr != '':
        matchedLexeme = False
        for lexeme in vimcalc_lexemes:
            match = vimcalc_matchesFront(lexeme.regex, expr)
            if match != '':
                tokens.append(VimCalcToken(lexeme.ID, match))
                expr = expr[len(match):]
                matchedLexeme = True
                break
        if not matchedLexeme: return [VimCalcToken('ERROR', expr)]
    return [t for t in tokens if t.ID != 'whitespace']

#returns the match if regex matches beginning of string
#otherwise returns the emtpy string
def vimcalc_matchesFront(regex, string):
    rexp = re.compile(regex)
    m = rexp.match(string)
    if m:
        return m.group()
    else:
        return ''

#useful for testing vimcalc_tokenize with map(...)
def vimcalc_getAttrib(token):
    return token.attrib

def vimcalc_getID(token):
    return token.ID

#### PARSER FUNCTIONS ##########################################################

#TODO: this is all a bit messy due to passing essentially a vector around
# instead of a list and not having shared state. Could be made a
# lot simpler by using shared state...

#vcalc context-free grammar
#line      -> directive | expr | assign
#directive -> decDir | octDir | hexDir | binDir | intDir | floatDir | statusDir | varDir | quitDir
#assign    -> let assign' | assign'
#assign'   ->  ident = expr | ident += expr | ident -= expr
#             | ident *= expr | ident /= expr | ident %= expr | ident **= expr
#expr      -> expr + term | expr - term | term
#func      -> ident ( args )
#args      -> expr , args | expr
#term      -> term * factor | term / factor | term % factor
#             | term << factor | term >> factor | term ! | factor
#factor    -> expt ** factor | expt
#expt      -> func | ident | - number | number | ( expr )
#number    -> decnumber | hexnumber | octalnumber | binnumber

#vcalc context-free grammar LL(1) -- to be used with a recursive descent parser
#line       -> directive | assign | expr
#directive  -> decDir | octDir | hexDir | binDir | intDir | floatDir | statusDir | varDir | quitDir
#assign     -> [let] ident (=|+=|-=|*=|/=|%=|**=) expr
#expr       -> term {(+|-) term}
#func       -> ident ( args )
#args       -> expr {, expr}
#term       -> factor {(*|/|%|<<|>>) factor} [!]
#factor     -> {expt **} expt
#expt       -> func | ident | - number | number | ( expr )
#number     -> decnumber | hexnumber | octalnumber | binnumber

class VimCalcParseNode(object):
    def __init__(self, success, result, consumedTokens):
        self._success = success
        self._result = result
        self._consumedTokens = consumedTokens
        self._storeInAns = True
        self._assignedSymbol = ''
    def getSuccess(self):
        return self._success
    def getResult(self):
        return self._result
    def getConsumed(self):
        return self._consumedTokens
    def getStoreInAns(self):
        return self._storeInAns
    def setStoreInAns(self, val):
        self._storeInAns = val
    def getAssignedSymbol(self):
        return self._assignedSymbol
    def setAssignedSymbol(self, val):
        self._assignedSymbol = val
    success = property(getSuccess,
                       doc='Successfully evaluated?')
    result = property(getResult,
                      doc='The evaluated result at this node.')
    consumeCount = property(getConsumed,
                            doc='Number of consumed tokens.')
    storeInAns = property(getStoreInAns, setStoreInAns,
                          doc='Should store in ans variable?')
    assignedSymbol = property(getAssignedSymbol, setAssignedSymbol,
                              doc='Symbol expression assigned to.')

class VimCalcParseException(Exception):
    def __init__(self, message, consumedTokens):
        self._message = message
        self._consumed = consumedTokens
    def getMessage(self):
        return self._message
    def getConsumed(self):
        return self._consumed
    message = property(getMessage)
    consumed = property(getConsumed)

# recursive descent parser -- simple and befitting the needs of this small
# program generates the parse tree with evaluated decoration
def vimcalc_parse(expr):
    tokens = vimcalc_tokenize(expr)
    if vimcalc_symbolCheck('ERROR', 0, tokens):
        return 'Syntax error: ' + tokens[0].attrib
    try:
        lineNode = vimcalc_line(tokens)
        if lineNode.success:
            if lineNode.storeInAns:
                vimcalc_storeSymbol('ans', lineNode.result)
                return 'ans = ' + vimcalc_process(lineNode.result)
            else:
                if lineNode.assignedSymbol == None:
                    return str(lineNode.result)
                else:
                    return lineNode.assignedSymbol + ' = ' + vimcalc_process(lineNode.result)
        else:
            return 'Parse error: the expression is invalid.'
    except VimCalcParseException as pe:
        return 'Parse error: ' + pe.message

#this function returns an output string based on the global repl directives
def vimcalc_process(result):
    if VIMCALC_OUTPUT_BASE == 'decimal':
        output = result
    elif VIMCALC_OUTPUT_BASE == 'hexadecimal':
        return str(hex(int(result)))
    elif VIMCALC_OUTPUT_BASE == 'octal':
        return re.sub('0[Oo]|0[0o]0', '0', str(oct(int(result))))
    elif VIMCALC_OUTPUT_BASE == 'binary':
        return str(bin(int(result)))
    else:
        return 'ERROR'

    if VIMCALC_OUTPUT_PRECISION == 'int':
        return str(int(output))
    elif VIMCALC_OUTPUT_PRECISION == 'float':
        return str(output)
    else:
        return 'ERROR'


# Rename from line because there is an interference with plugin VOoM.
def vimcalc_line(tokens):
    directiveNode = vimcalc_directive(tokens)
    if directiveNode.success:
        if directiveNode.consumeCount == len(tokens):
            return directiveNode
        else:
            return VimCalcParseNode(False, 0, directiveNode.consumeCount)
    assignNode = vimcalc_assign(tokens)
    if assignNode.success:
        if assignNode.consumeCount == len(tokens):
            return assignNode
        else:
            return VimCalcParseNode(False, 0, assignNode.consumeCount)
    exprNode = vimcalc_expr(tokens)
    if exprNode.success:
        if exprNode.consumeCount == len(tokens):
            return exprNode
        else:
            return VimCalcParseNode(False, 0, exprNode.consumeCount)
    return VimCalcParseNode(False, 0, 0)

VIMCALC_OUTPUT_BASE      = 'decimal'
VIMCALC_OUTPUT_PRECISION = 'float'

def vimcalc_directive(tokens):
    #TODO: refactor this -- extract method
    global VIMCALC_OUTPUT_BASE
    global VIMCALC_OUTPUT_PRECISION
    if vimcalc_symbolCheck('decDir', 0, tokens):
        VIMCALC_OUTPUT_BASE = 'decimal'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT BASE TO DECIMAL.')
    if vimcalc_symbolCheck('hexDir', 0, tokens):
        VIMCALC_OUTPUT_BASE = 'hexadecimal'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT BASE TO HEXADECIMAL.')
    if vimcalc_symbolCheck('octDir', 0, tokens):
        VIMCALC_OUTPUT_BASE = 'octal'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT BASE TO OCTAL.')
    if vimcalc_symbolCheck('binDir', 0, tokens):
        VIMCALC_OUTPUT_BASE = 'binary'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT BASE TO BINARY.')
    if vimcalc_symbolCheck('floatDir', 0, tokens):
        VIMCALC_OUTPUT_PRECISION = 'float'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT PRECISION TO FLOATING POINT.')
    if vimcalc_symbolCheck('intDir', 0, tokens):
        VIMCALC_OUTPUT_PRECISION = 'int'
        return vimcalc_createDirectiveParseNode('CHANGED OUTPUT PRECISION TO INTEGER.')
    if vimcalc_symbolCheck('statusDir', 0, tokens):
        return vimcalc_createDirectiveParseNode(vimcalc_statusMessage())
    if vimcalc_symbolCheck('varDir', 0, tokens):
        return vimcalc_createDirectiveParseNode(vimcalc_variablesMessage())
    if vimcalc_symbolCheck('quitDir', 0, tokens):
        return vimcalc_createDirectiveParseNode('!!!q!!!')
    return VimCalcParseNode(False, 0, 0)

def vimcalc_assign(tokens):
    if vimcalc_symbolCheck('ident', 0, tokens):
        assignPos = 1
    elif list(map(vimcalc_getID, tokens[0:2])) == ['let', 'ident']:
        assignPos = 2
    else:
        return VimCalcParseNode(False, 0, 0)

    exprNode = vimcalc_expr(tokens[assignPos+1:])
    if exprNode.consumeCount+assignPos+1 == len(tokens):
        symbol = tokens[assignPos-1].attrib

        #perform type of assignment
        if vimcalc_symbolCheck('assign', assignPos, tokens):
            result = exprNode.result
        else:
            result = vimcalc_lookupSymbol(symbol)
            if vimcalc_symbolCheck('pAssign', assignPos, tokens):
                result = result + exprNode.result
            elif vimcalc_symbolCheck('sAssign', assignPos, tokens):
                result = result - exprNode.result
            elif vimcalc_symbolCheck('mAssign', assignPos, tokens):
                result = result * exprNode.result
            elif vimcalc_symbolCheck('dAssign', assignPos, tokens):
                result = result / exprNode.result
            elif vimcalc_symbolCheck('modAssign', assignPos, tokens):
                result = result % exprNode.result

            #arguments to bitwise operations must be plain or long integers
            elif vimcalc_symbolCheck('andAssign', assignPos, tokens):
                result = int(result) & int(exprNode.result)
            elif vimcalc_symbolCheck('orAssign', assignPos, tokens):
                result = int(result) | int(exprNode.result)
            elif vimcalc_symbolCheck('xorAssign', assignPos, tokens):
                result = int(result) ^ int(exprNode.result)

            elif vimcalc_symbolCheck('expAssign', assignPos, tokens):
                result = result ** exprNode.result
            else:
                return VimCalcParseNode(False, 0, assignPos)

        vimcalc_storeSymbol(symbol, result)
        node = VimCalcParseNode(True, result, exprNode.consumeCount+assignPos+1)
        node.storeInAns = False
        node.assignedSymbol = symbol
        return node
    else:
        return VimCalcParseNode(False, 0, exprNode.consumeCount+assignPos+1)

def vimcalc_expr(tokens):
    termNode = vimcalc_term(tokens)
    consumed = termNode.consumeCount
    if termNode.success:
        foldNode = vimcalc_foldlParseMult(vimcalc_term,
                                  [lambda x, y:x+y, lambda x, y:x-y],
                                  ['plus', 'subtract'],
                                  termNode.result,
                                  tokens[consumed:])
        consumed += foldNode.consumeCount
        return VimCalcParseNode(foldNode.success, foldNode.result, consumed)
    else:
        return VimCalcParseNode(False, 0, consumed)

def vimcalc_func(tokens):
    if list(map(vimcalc_getID, tokens[0:2])) == ['ident', 'lParen']:
        sym = tokens[0].attrib
        argsNode = vimcalc_args(tokens[2:])
        if vimcalc_symbolCheck('rParen', argsNode.consumeCount+2, tokens):
            try:
                result = vimcalc_lookupFunc(sym)(*argsNode.result)
                return VimCalcParseNode(True, result, argsNode.consumeCount+3)
            except TypeError as e:
                raise VimCalcParseException(str(e), argsNode.consumeCount+3)
            except ValueError as e:
                raise VimCalcParseException(str(e), argsNode.consumeCount+3)
        else:
            error = 'missing matching parenthesis for function ' + sym + '.'
            raise VimCalcParseException(error, argsNode.consumeCount+2)
    else:
        return VimCalcParseNode(False, 0, 0)

def vimcalc_args(tokens):
    #returns a list of exprNodes to be used as function arguments
    exprNode = vimcalc_expr(tokens)
    consumed = exprNode.consumeCount
    if exprNode.success:
        foldNode = vimcalc_foldlParse(vimcalc_expr, vimcalc_snoc, 'comma', [exprNode.result], tokens[consumed:])
        return VimCalcParseNode(foldNode.success, foldNode.result, consumed+foldNode.consumeCount)
    else:
        return VimCalcParseNode(False, [], consumed)

def vimcalc_term(tokens):
    factNode = vimcalc_factor(tokens)
    consumed = factNode.consumeCount
    if factNode.success:
        foldNode = vimcalc_foldlParseMult(vimcalc_factor,
                                  [lambda x, y:x*y,
                                      lambda x, y: x/y if VIMCALC_OUTPUT_PRECISION == 'float' else x//y,
                                      lambda x, y:x%y,
                                      lambda x, y:int(x)&int(y),
                                      lambda x, y:int(x)|int(y),
                                      lambda x, y:int(x)^int(y),
                                      lambda x, y:int(x)<<int(y), lambda x, y:int(x)>>int(y)],
                                  ['multiply', 'divide', 'modulo', 'and', 'or',
                                      'xor', 'lShift', 'rShift'],
                                  factNode.result,
                                  tokens[consumed:])
        consumed += foldNode.consumeCount
        if vimcalc_symbolCheck('factorial', consumed, tokens):
            return VimCalcParseNode(foldNode.success, vimcalc_factorial(foldNode.result), consumed+1)
        else:
            return VimCalcParseNode(foldNode.success, foldNode.result, consumed)
    else:
        return VimCalcParseNode(False, 0, consumed)

def vimcalc_factor(tokens):
    exptNode = vimcalc_expt(tokens)
    consumed = exptNode.consumeCount
    result = exptNode.result
    if exptNode.success:
        foldNode = vimcalc_foldrParse(vimcalc_expt, lambda x, y:x**y, 'exponent', result, tokens[consumed:])
        return VimCalcParseNode(foldNode.success, foldNode.result, consumed+foldNode.consumeCount)
    else:
        return VimCalcParseNode(False, 0, consumed)

def vimcalc_expt(tokens):
    #function
    funcNode = vimcalc_func(tokens)
    if funcNode.success:
        return funcNode
    #identifier
    if vimcalc_symbolCheck('ident', 0, tokens):
        return VimCalcParseNode(True, vimcalc_lookupSymbol(tokens[0].attrib), 1)
    #unary -
    if vimcalc_symbolCheck('subtract', 0, tokens):
        numberNode = vimcalc_number(tokens[1:])
        if numberNode.success:
            return VimCalcParseNode(True, numberNode.result*-1, numberNode.consumeCount+1)
    #plain number
    numberNode = vimcalc_number(tokens)
    if numberNode.success:
        return numberNode
    #(expr)
    if vimcalc_symbolCheck('lParen', 0, tokens):
        exprNode = vimcalc_expr(tokens[1:])
        if exprNode.success:
            if vimcalc_symbolCheck('rParen', exprNode.consumeCount+1, tokens):
                return VimCalcParseNode(True, exprNode.result, exprNode.consumeCount+2)
            else:
                error = 'missing matching parenthesis in expression.'
                raise VimCalcParseException(error, exprNode.consumeCount+1)
    return VimCalcParseNode(False, 0, 0)

def vimcalc_number(tokens):
    if vimcalc_symbolCheck('decnumber', 0, tokens):
        if VIMCALC_OUTPUT_PRECISION == 'float':
            num = float(tokens[0].attrib)
        elif VIMCALC_OUTPUT_PRECISION == 'int':
            num = int(float(tokens[0].attrib)) #int from float as string input
        else:
            num = 0 #error
        return VimCalcParseNode(True, num, 1)
    elif vimcalc_symbolCheck('hexnumber', 0, tokens):
        return VimCalcParseNode(True, int(tokens[0].attrib, 16), 1)
    elif vimcalc_symbolCheck('octnumber', 0, tokens):
        return VimCalcParseNode(True, int(tokens[0].attrib, 8), 1)
    elif vimcalc_symbolCheck('binnumber', 0, tokens):
        return VimCalcParseNode(True, int(tokens[0].attrib, 2), 1)
    else:
        return VimCalcParseNode(False, 0, 0)

#### HELPER FUNCTIONS FOR USE BY THE PARSER AND REPL ###########################

def vimcalc_foldlParse(parsefn, resfn, symbol, initial, tokens):
    consumed = 0
    result = initial
    if tokens == []:
        return VimCalcParseNode(True, result, consumed)
    else:
        while tokens[consumed].ID == symbol:
            parseNode = parsefn(tokens[consumed+1:])
            consumed += parseNode.consumeCount+1
            if parseNode.success:
                result = resfn(result, parseNode.result)
                if consumed >= len(tokens): return VimCalcParseNode(True, result, consumed)
            else:
                return VimCalcParseNode(False, 0, consumed)
        return VimCalcParseNode(True, result, consumed)

def vimcalc_foldlParseMult(parsefn, resfns, syms, initial, tokens):
    consumed = 0
    result = initial
    if tokens == []:
        return VimCalcParseNode(True, result, consumed)
    else:
        while tokens[consumed].ID in syms:
            sym = tokens[consumed].ID
            parseNode = vimcalc_foldlParse(parsefn, resfns[syms.index(sym)], sym, result, tokens[consumed:])
            if parseNode.success:
                result = parseNode.result
                consumed += parseNode.consumeCount
                if consumed >= len(tokens): return VimCalcParseNode(True, result, consumed)
            else:
                return VimCalcParseNode(False, 0, consumed)
        return VimCalcParseNode(True, result, consumed)

def vimcalc_foldrParse(parsefn, resfn, symbol, initial, tokens):
    # vimcalc_foldlParse into a sequence and then do a vimcalc_foldr to evaluate
    parseNode = vimcalc_foldlParse(parsefn, vimcalc_snoc, symbol, [], tokens)
    if parseNode.success:
        result = vimcalc_foldr(resfn, initial, parseNode.result)
        return VimCalcParseNode(parseNode.success, result, parseNode.consumeCount)
    else:
        return parseNode

def vimcalc_createDirectiveParseNode(outputMsg):
    node = VimCalcParseNode(True, outputMsg, 1)
    node.storeInAns = False
    node.assignedSymbol = None
    return node

def vimcalc_statusMessage():
    global VIMCALC_OUTPUT_BASE
    global VIMCALC_OUTPUT_PRECISION

    base = VIMCALC_OUTPUT_BASE.upper()
    if VIMCALC_OUTPUT_PRECISION   == 'float' : precision = 'FLOATING POINT'
    elif VIMCALC_OUTPUT_PRECISION == 'int'   : precision = 'INTEGER'
    else: VIMCALC_OUTPUT_PRECISION = 'ERROR'
    msg = "STATUS: OUTPUT BASE: %s; PRECISION: %s." % (base, precision)
    return msg

def vimcalc_variablesMessage():
    msg = "VARIABLES:\n----------\n"
    #find the longest variable length for alignment
    width = 0
    for k in list(VIMCALC_SYMBOL_TABLE.keys()):
        width = max(width, len(k))

    items = sorted(VIMCALC_SYMBOL_TABLE.items())
    for k, v in items:
        msg += " " + k.ljust(width) + " : " + vimcalc_process(v) + "\n"
    return msg

# Rather literal haskell implementation of this, proably very unpythonic and
# inefficient. Should do for the needs of vimcalc however. TODO: in the future
# improve this!
def vimcalc_foldr(fn, init, lst):
    if lst == []:
        return init
    else:
        return fn(init, vimcalc_foldr(fn, lst[0], lst[1:]))

def vimcalc_symbolCheck(symbol, index, tokens):
    if index < len(tokens):
        if tokens[index].ID == symbol:
            return True
    return False

def vimcalc_snoc(seq, x):  #TODO: find more pythonic way of doing this
    a = seq
    a.append(x)
    return a

#### SYMBOL TABLE MANIPULATION FUNCTIONS #######################################

#global symbol table NOTE: these can be rebound
VIMCALC_SYMBOL_TABLE = {'ans':0,
                        'e':math.e,
                       'pi':math.pi,
                      'phi':1.6180339887498948482}

def vimcalc_lookupSymbol(symbol):
    if symbol in VIMCALC_SYMBOL_TABLE:
        return VIMCALC_SYMBOL_TABLE[symbol]
    else:
        error = "symbol '" + symbol + "' is not defined."
        raise VimCalcParseException(error, 0)

def vimcalc_storeSymbol(symbol, value):
    VIMCALC_SYMBOL_TABLE[symbol] = value


#### VIMCALC BUILTIN FUNCTIONS #################################################

def vimcalc_loge(n):
    return math.log(n)

def vimcalc_log2(n):
    return math.log(n, 2)

def vimcalc_nrt(x, y):
    return x**(1/y)

def vimcalc_factorial(n):
    acc = 1
    for i in range(int(n)):
        acc *= i+1
    return acc

def vimcalc_perms(n, k):
    return int(vimcalc_factorial(n)/vimcalc_factorial(n-k))

def vimcalc_choose(n, k):
    denominator = vimcalc_factorial(k) * vimcalc_factorial(n-k)
    return int(vimcalc_factorial(n)/denominator)

# Global built-in function table
#NOTE: variables do not share the same namespace as functions
#NOTE: if you change the name or add a function remember to update the syntax file

VIMCALC_FUNCTION_TABLE = {
        'abs'   : math.fabs,
        'acos'  : math.acos,
        'asin'  : math.asin,
        'atan'  : math.atan,
        'atan2' : math.atan2,
        'ceil'  : math.ceil,
        'choose': vimcalc_choose,
        'cos'   : math.cos,
        'cosh'  : math.cosh,
        'deg'   : math.degrees,
        'exp'   : math.exp,
        'floor' : math.floor,
        'hypot' : math.hypot,
        'inv'   : lambda n: 1/n,
        'ldexp' : math.ldexp,
        'lg'    : vimcalc_log2,
        'ln'    : vimcalc_loge,
        'log'   : math.log, #allows arbitrary base, defaults to e
        'log10' : math.log10,
        'max'   : max,
        'min'   : min,
        'nrt'   : vimcalc_nrt,
        'perms' : vimcalc_perms,
        'pow'   : math.pow,
        'rad'   : math.radians,
        'rand'  : random.random, #random() -> x in the interval [0, 1).
        'round' : round,
        'sin'   : math.sin,
        'sinh'  : math.sinh,
        'sqrt'  : math.sqrt,
        'tan'   : math.tan,
        'tanh'  : math.tanh
        }

def vimcalc_lookupFunc(symbol):
    if symbol in VIMCALC_FUNCTION_TABLE:
        return VIMCALC_FUNCTION_TABLE[symbol]
    else:
        error = "built-in function '" + symbol + "' does not exist."
        raise VimCalcParseException(error, 0)
