import unittest
import vimcalc
import math

class SanityCheckTestCase(unittest.TestCase):
    def runTest(self):
        self.assertEqual(vimcalc.parse("5*4"), "ans = 20.0", 'sanity check.')

class OperatorTestCase(unittest.TestCase):
    def testAddition(self):
        self.assertEqual(vimcalc.parse("5+4"), "ans = 9.0", 'addition')

    def testSubtraction(self):
        self.assertEqual(vimcalc.parse("5-4"), "ans = 1.0", 'subtraction')

    def testMultiplication(self):
        self.assertEqual(vimcalc.parse("5*4"), "ans = 20.0", 'multiplication')

    def testDivision(self):
        self.assertEqual(vimcalc.parse("5/4"), "ans = 1.25", 'division')

    def testModulo(self):
        self.assertEqual(vimcalc.parse("5%4"), "ans = 1.0", 'modulo')
        self.assertEqual(vimcalc.parse("4%5"), "ans = 4.0", 'modulo')

    def testAnd(self):
        self.assertEqual(vimcalc.parse("5&3"),  "ans = 1", 'bitwise and')
        self.assertEqual(vimcalc.parse("3&2"),  "ans = 2", 'bitwise and')
        self.assertEqual(vimcalc.parse("6&13"), "ans = 4", 'bitwise and')

    def testOr(self):
        self.assertEqual(vimcalc.parse("5|3"), "ans = 7", 'bitwise or')

    def testXor(self):
        self.assertEqual(vimcalc.parse("5^3"),  "ans = 6", 'bitwise xor')
        self.assertEqual(vimcalc.parse("2^10"), "ans = 8", 'bitwise xor')

    def testExponent(self):
        self.assertEqual(vimcalc.parse("5**4"), "ans = 625.0", 'exponent')

    def testLeftShift(self):
        self.assertEqual(vimcalc.parse("16<<1"), "ans = 32", 'left shift')
        self.assertEqual(vimcalc.parse("16<<2"), "ans = 64", 'left shift')

    def testRightShift(self):
        self.assertEqual(vimcalc.parse("16>>1"), "ans = 8", 'right shift')
        self.assertEqual(vimcalc.parse("16>>2"), "ans = 4", 'right shift')

    def testFactorial(self):
        self.assertEqual(vimcalc.parse("5!"), "ans = 120", 'factorial')

    def testComplicatedNested(self):
        self.assertEqual(vimcalc.parse("sin(sqrt(((pi/2)*2)**2)/2-(3-3))"),  "ans = 1.0")

    def testFloatFormats(self):
        self.assertEqual(vimcalc.parse(".5"), "ans = 0.5")

class OperatorPrecedenceTestCase(unittest.TestCase):
    #this could do with being better in every way.
    def testAllPrecedenceAtOnce(self):
        self.assertEqual(vimcalc.parse("5*4+2/sin(pi/2)**2+-1"),  "ans = 21.0")

class OperatorAssociativityTestCase(unittest.TestCase):
    def testMultiplication(self):
        self.assertEqual(vimcalc.parse("2*2*2"),    "ans = 8.0")
        self.assertEqual(vimcalc.parse("(2*2)*2"),  "ans = 8.0")
        self.assertEqual(vimcalc.parse("2*(2*2)"),  "ans = 8.0")

    def testDivision(self):
        self.assertEqual(vimcalc.parse("(2/2)/3"),  "ans = 0.3333333333333333")
        self.assertEqual(vimcalc.parse("2/(2/3)"),  "ans = 3.0")
        self.assertEqual(vimcalc.parse("2/2/3"),    "ans = 0.3333333333333333")

    def testModulo(self):
        self.assertEqual(vimcalc.parse("(5%4)%3"),  "ans = 1.0")
        self.assertEqual(vimcalc.parse("5%(4%3)"),  "ans = 0.0")
        self.assertEqual(vimcalc.parse("5%4%3"),    "ans = 1.0")

    def testLeftShift(self):
        self.assertEqual(vimcalc.parse("(8<<1)<<2"),  "ans = 64")
        self.assertEqual(vimcalc.parse("8<<(1<<2)"),  "ans = 128")
        self.assertEqual(vimcalc.parse("8<<1<<2"),    "ans = 64")

    def testRightShift(self):
        self.assertEqual(vimcalc.parse("(16>>2)>>1"),  "ans = 2")
        self.assertEqual(vimcalc.parse("16>>(2>>1)"),  "ans = 8")
        self.assertEqual(vimcalc.parse("16>>1>>2"),    "ans = 2")

    def testFactorial(self):
        self.assertEqual(vimcalc.parse("5!!"),    "Parse error: the expression is invalid.")
        self.assertEqual(vimcalc.parse("(3!)!"),  "ans = 720")

    def testAddition(self):
        self.assertEqual(vimcalc.parse("(2+3)+4"),  "ans = 9.0")
        self.assertEqual(vimcalc.parse("2+(3+4)"),  "ans = 9.0")
        self.assertEqual(vimcalc.parse("2+3+4"),    "ans = 9.0")

    def testSubtraction(self):
        self.assertEqual(vimcalc.parse("4-3-2"),    "ans = -1.0")
        self.assertEqual(vimcalc.parse("(4-3)-2"),  "ans = -1.0")
        self.assertEqual(vimcalc.parse("4-(3-2)"),  "ans = 3.0")

    def testAnd(self):
        self.assertEqual(vimcalc.parse("(1&3)&9"),  "ans = 1")
        self.assertEqual(vimcalc.parse("1&(3&9)"),  "ans = 1")
        self.assertEqual(vimcalc.parse("1&3&9"),    "ans = 1")

    def testOr(self):
        self.assertEqual(vimcalc.parse("(1|3)|9"),  "ans = 11")
        self.assertEqual(vimcalc.parse("1|(3|9)"),  "ans = 11")
        self.assertEqual(vimcalc.parse("1|3|9"),    "ans = 11")

    def testXor(self):
        self.assertEqual(vimcalc.parse("(1^3)^9"),  "ans = 11")
        self.assertEqual(vimcalc.parse("1^(3^9)"),  "ans = 11")
        self.assertEqual(vimcalc.parse("1^3^9"),    "ans = 11")

    #right-to-left
    def testExponent(self):
        self.assertEqual(vimcalc.parse("(2**2)**3"),  "ans = 64.0")
        self.assertEqual(vimcalc.parse("2**(2**3)"),  "ans = 256.0")
        self.assertEqual(vimcalc.parse("2**2**3"),    "ans = 256.0")

class AssignmentTestCase(unittest.TestCase):
    def testAssign(self):
        self.assertEqual(vimcalc.parse("let x = 2"),   "x = 2.0", 'test assign.')
        self.assertEqual(vimcalc.parse("let x = 2.0"), "x = 2.0", 'test assign.')

    def testAssignNoLet(self):
        self.assertEqual(vimcalc.parse("x = 2"),   "x = 2.0", 'test assign.')
        self.assertEqual(vimcalc.parse("x = 2.0"), "x = 2.0", 'test assign.')

    def testUsingAssigned(self):
        vimcalc.parse("let a = 2")
        vimcalc.parse("let b = 8")
        vimcalc.parse("x = 2")
        vimcalc.parse("y = 8")
        self.assertEqual(vimcalc.parse("a + b"), "ans = 10.0", 'test using assignment')
        self.assertEqual(vimcalc.parse("x + 2"), "ans = 4.0", 'test using assignment')
        self.assertEqual(vimcalc.parse("x + y"), "ans = 10.0", 'test using assignment')

    def testAssignUsingAssigned(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let z = x * y"), "z = 20.0", 'test assign assigned.')

    def testPAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let x += y"), "x = 9.0")

    def testSAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let y -= x"), "y = 1.0")

    def testMAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let x *= y"), "x = 20.0")

    def testDAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let x /= y"), "x = 0.8")

    def testModAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let x %= y"), "x = 4.0")
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let y %= x"), "y = 1.0")

    def testAndAssign(self):
        vimcalc.parse("x = 5")
        vimcalc.parse("y = 3")
        self.assertEqual(vimcalc.parse("let x &= y"), "x = 1")
        vimcalc.parse("x = 3")
        vimcalc.parse("y = 2")
        self.assertEqual(vimcalc.parse("let x &= y"), "x = 2")
        vimcalc.parse("x = 6")
        vimcalc.parse("y = 13")
        self.assertEqual(vimcalc.parse("let x &= y"), "x = 4")

    def testOrAssign(self):
        vimcalc.parse("x = 5")
        vimcalc.parse("y = 3")
        self.assertEqual(vimcalc.parse("let x |= y"), "x = 7")

    def testXorAssign(self):
        vimcalc.parse("x = 5")
        vimcalc.parse("y = 3")
        self.assertEqual(vimcalc.parse("let x ^= y"),  "x = 6")
        vimcalc.parse("x = 2")
        vimcalc.parse("y = 10")
        self.assertEqual(vimcalc.parse("let x ^= y"), "x = 8")

    def testExpAssign(self):
        vimcalc.parse("x = 4")
        vimcalc.parse("y = 5")
        self.assertEqual(vimcalc.parse("let x **= y"), "x = 1024.0")

class ConstantsTestCase(unittest.TestCase):
    def testConstants(self):
        self.assertEqual(vimcalc.parse("e"),    "ans = 2.718281828459045")
        self.assertEqual(vimcalc.parse("pi"),   "ans = 3.141592653589793")
        self.assertEqual(vimcalc.parse("phi"),  "ans = 1.618033988749895")

class BasesTestCase(unittest.TestCase):
    def tearDown(self):
        vimcalc.parse(":dec")

    def testDecimal(self):
        self.assertEqual(vimcalc.parse(":dec"),  "CHANGED OUTPUT BASE TO DECIMAL.")
        self.assertEqual(vimcalc.parse("10"),    "ans = 10.0")
        self.assertEqual(vimcalc.parse("0x10"),  "ans = 16")
        self.assertEqual(vimcalc.parse("010"),   "ans = 8")

    def testHexadecimal(self):
        self.assertEqual(vimcalc.parse(":hex"),  "CHANGED OUTPUT BASE TO HEXADECIMAL.")
        self.assertEqual(vimcalc.parse("10"),    "ans = 0xa")
        self.assertEqual(vimcalc.parse("0x10"),  "ans = 0x10")
        self.assertEqual(vimcalc.parse("010"),   "ans = 0x8")

    def testOctal(self):
        self.assertEqual(vimcalc.parse(":oct"),  "CHANGED OUTPUT BASE TO OCTAL.")
        self.assertEqual(vimcalc.parse("10"),   "ans = 012")
        self.assertEqual(vimcalc.parse("0x10"), "ans = 020")
        self.assertEqual(vimcalc.parse("010"),  "ans = 010")

class PrecisionTestCase(unittest.TestCase):
    def tearDown(self):
        vimcalc.parse(":float")

    def testInteger(self):
        self.assertEqual(vimcalc.parse(":int"),  "CHANGED OUTPUT PRECISION TO INTEGER.")
        self.assertEqual(vimcalc.parse("(8/3) * (4/3)"), "ans = 2")

    def testFloat(self):
        self.assertEqual(vimcalc.parse(":float"),  "CHANGED OUTPUT PRECISION TO FLOATING POINT.")
        self.assertEqual(vimcalc.parse("(8/3) * (4/3)"), "ans = 3.5555555555555554")

class VarListingTestCase(unittest.TestCase):
    def setUp(self):
        self.resetSymbolTable()

    def tearDown(self):
        vimcalc.parse(":float")
        vimcalc.parse(":dec")

    def resetSymbolTable(self):
        temp = { 'ans' : 0,
                 'e'   : vimcalc.VCALC_SYMBOL_TABLE['e'],
                 'pi'  : vimcalc.VCALC_SYMBOL_TABLE['pi'],
                 'phi' : vimcalc.VCALC_SYMBOL_TABLE['phi'] }
        vimcalc.VCALC_SYMBOL_TABLE = temp

    def testSanity(self):
        self.assertEqual(len(vimcalc.VCALC_SYMBOL_TABLE),   4)
        self.assertEqual(vimcalc.VCALC_SYMBOL_TABLE['ans'], 0)
        self.assertEqual(vimcalc.VCALC_SYMBOL_TABLE['e'],   math.e)
        self.assertEqual(vimcalc.VCALC_SYMBOL_TABLE['pi'],  math.pi)
        self.assertEqual(vimcalc.VCALC_SYMBOL_TABLE['phi'], 1.6180339887498948482)

    def testDefault(self):
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0\n e   : 2.718281828459045\n phi : 1.618033988749895\n pi  : 3.141592653589793\n")

    def testAddVars(self):
        #tests they get added and alphabetically
        self.assertEqual(vimcalc.parse("x = 2"), "x = 2.0")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0\n e   : 2.718281828459045\n phi : 1.618033988749895\n pi  : 3.141592653589793\n x   : 2.0\n")
        self.assertEqual(vimcalc.parse("a = 2"), "a = 2.0")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n a   : 2.0\n ans : 0\n e   : 2.718281828459045\n phi : 1.618033988749895\n pi  : 3.141592653589793\n x   : 2.0\n")

    def testChangeMode(self):
        vimcalc.parse(":dec")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0\n e   : 2.718281828459045\n phi : 1.618033988749895\n pi  : 3.141592653589793\n")
        vimcalc.parse(":hex")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0x0\n e   : 0x2\n phi : 0x1\n pi  : 0x3\n")
        vimcalc.parse(":oct")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 00\n e   : 02\n phi : 01\n pi  : 03\n")

    def testChangePrecision(self):
        vimcalc.parse(":float")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0\n e   : 2.718281828459045\n phi : 1.618033988749895\n pi  : 3.141592653589793\n")
        vimcalc.parse(":int")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans : 0\n e   : 2\n phi : 1\n pi  : 3\n")

    def testAlignment(self):
        self.assertEqual(vimcalc.parse("let reallyLongName = 2"), "reallyLongName = 2.0")
        self.assertEqual(vimcalc.parse(":vars"),  "VARIABLES:\n----------\n ans            : 0\n e              : 2.718281828459045\n phi            : 1.618033988749895\n pi             : 3.141592653589793\n reallyLongName : 2.0\n")

class MiscDirectivesTestCase(unittest.TestCase):
    def setUp(self):
        vimcalc.parse(":dec")
        vimcalc.parse(":float")

    def tearDown(self):
        vimcalc.parse(":dec")
        vimcalc.parse(":float")

    def testStatusSanity(self):
        self.assertNotEqual(vimcalc.parse(":status"), "Syntax error: :status")

    def testStatus(self):
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: DECIMAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":hex")
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: HEXADECIMAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":oct")
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: OCTAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":int")
        vimcalc.parse(":dec")
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: DECIMAL; PRECISION: INTEGER.")
        vimcalc.parse(":hex")
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: HEXADECIMAL; PRECISION: INTEGER.")
        vimcalc.parse(":oct")
        self.assertEqual(vimcalc.parse(":status"),  "STATUS: OUTPUT BASE: OCTAL; PRECISION: INTEGER.")

    def testStatusShorthand(self):
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: DECIMAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":hex")
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: HEXADECIMAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":oct")
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: OCTAL; PRECISION: FLOATING POINT.")
        vimcalc.parse(":int")
        vimcalc.parse(":dec")
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: DECIMAL; PRECISION: INTEGER.")
        vimcalc.parse(":hex")
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: HEXADECIMAL; PRECISION: INTEGER.")
        vimcalc.parse(":oct")
        self.assertEqual(vimcalc.parse(":s"),  "STATUS: OUTPUT BASE: OCTAL; PRECISION: INTEGER.")

    def testQuitDirective(self):
        self.assertEqual(vimcalc.parse(":q"),  "!!!q!!!")

class ErrorMessagesTestCase(unittest.TestCase):
    def testNonExistantBuiltin(self):
        self.assertEqual(vimcalc.parse("foo()"),  "Parse error: built-in function 'foo' does not exist.")

    def testUnmatchedParens(self):
        self.assertEqual(vimcalc.parse("(5"),    "Parse error: missing matching parenthesis in expression.")
        self.assertEqual(vimcalc.parse("((5)"),  "Parse error: missing matching parenthesis in expression.")
        self.assertEqual(vimcalc.parse("(()"),   "Parse error: the expression is invalid.")

    def testUndefinedSymbol(self):
        self.assertEqual(vimcalc.parse("thisshouldnotexist"),  "Parse error: symbol 'thisshouldnotexist' is not defined.")

    def testSyntaxError(self):
        self.assertEqual(vimcalc.parse("\"string\""),  "Syntax error: \"string\"")
        self.assertEqual(vimcalc.parse("'string'"),    "Syntax error: 'string'")

    def testParseError(self):
        self.assertEqual(vimcalc.parse("9**5/)"),   "Parse error: the expression is invalid.")
        self.assertEqual(vimcalc.parse("4//5"),     "Parse error: the expression is invalid.")
        self.assertEqual(vimcalc.parse("--1"),      "Parse error: the expression is invalid.")
        self.assertEqual(vimcalc.parse("!4"),       "Parse error: the expression is invalid.")
        self.assertEqual(vimcalc.parse("2***3"),    "Parse error: the expression is invalid.")
        #self.assertEqual(vimcalc.parse("sin(2,)"),  "Parse error: apply() arg 2 expected sequence, found int")
        #TODO: where this message comes from??? O_o
        self.assertEqual(vimcalc.parse("sin(2,)"),  "Parse error: sin() argument after * must be an iterable, not int")

class FunctionsTestCase(unittest.TestCase):
    def testAbs(self):
        self.assertEqual(vimcalc.parse("abs(-4.2)"),     "ans = 4.2", 'test abs(x)')
    def testAcos(self):
        self.assertEqual(vimcalc.parse("acos(1)"),       "ans = 0.0", 'test acos(x)')
    def testAsin(self):
        self.assertEqual(vimcalc.parse("asin(0)"),       "ans = 0.0", 'test asin(x)')
    def testAtan(self):
        self.assertEqual(vimcalc.parse("atan(0)"),       "ans = 0.0", 'test atan(x)')
    def testAtan2(self):
        self.assertEqual(vimcalc.parse("atan2(1,1)"),    "ans = 0.7853981633974483", 'test atan2(y,x)')
    def testCeil(self):
        self.assertEqual(vimcalc.parse("ceil(4.2)"),     "ans = 5", 'test ceil(x)')
    def testChoose(self):
        self.assertEqual(vimcalc.parse("choose(3,2)"),   "ans = 3", 'test choose(n,k)')
        self.assertEqual(vimcalc.parse("choose(3,2.2)"), "ans = 3", 'test choose(n,k)')
    def testCos(self):
        self.assertEqual(vimcalc.parse("cos(0)"),        "ans = 1.0", 'test cos(x)')
    #TODO:
    def testCosh(self):
        self.assertEqual(vimcalc.parse("cosh(1)"),       "ans = 1.5430806348152437", 'test cosh(x)')
    def testDeg(self):
        self.assertEqual(vimcalc.parse("deg(pi)"),       "ans = 180.0", 'test deg(x)')
        self.assertEqual(vimcalc.parse("deg(pi/2)"),     "ans = 90.0", 'test deg(x)')
        self.assertEqual(vimcalc.parse("deg(2*pi)"),     "ans = 360.0", 'test deg(x)')
        self.assertEqual(vimcalc.parse("deg(2*pi+1)"),   "ans = 417.2957795130823", 'test deg(x)')
    def testExp(self):
        self.assertEqual(vimcalc.parse("exp(1)/e"),      "ans = 1.0", 'test exp(x)')
    def testFloor(self):
        self.assertEqual(vimcalc.parse("floor(4.7)"),    "ans = 4", 'test floor(x)')
    def testHypot(self):
        self.assertEqual(vimcalc.parse("hypot(3,4)"),    "ans = 5.0", 'test hypot(x,y)')
    def testInv(self):
        self.assertEqual(vimcalc.parse("inv(2)"),        "ans = 0.5", 'test inv(x)')
    #TODO:
    #def testLdexp(self):
        #self.assertEqual(vimcalc.parse("ldexp(2,2)"),   "ans = ", 'test ldexp(x,i)')
    def testLg(self):
        self.assertEqual(vimcalc.parse("lg(0)"),         "Parse error: math domain error", 'test lg(x)')
        self.assertEqual(vimcalc.parse("lg(1)"),         "ans = 0.0", 'test lg(x)')
        self.assertEqual(vimcalc.parse("lg(4)"),         "ans = 2.0", 'test lg(x)')
    def testLn(self):
        self.assertEqual(vimcalc.parse("ln(0)"),         "Parse error: math domain error", 'test ln(x)')
        self.assertEqual(vimcalc.parse("ln(1)"),         "ans = 0.0", 'test ln(x)')
        self.assertEqual(vimcalc.parse("ln(e)"),         "ans = 1.0", 'test ln(x)')
    def testLog(self):
        self.assertEqual(vimcalc.parse("log(9,3)"),      "ans = 2.0", 'test log(x,b)')
        self.assertEqual(vimcalc.parse("log(1,3)"),      "ans = 0.0", 'test log(x,b)')
        self.assertEqual(vimcalc.parse("log(0,3)"),      "Parse error: math domain error", 'test log(x,b)')
    def testLog10(self):
        self.assertEqual(vimcalc.parse("log10(100)"),    "ans = 2.0", 'test log10(x)')
        self.assertEqual(vimcalc.parse("log10(1)"),      "ans = 0.0", 'test log10(x)')
        self.assertEqual(vimcalc.parse("log10(0)"),      "Parse error: math domain error", 'test log10(x)')
    def testMax(self):
        self.assertEqual(vimcalc.parse("max(3,7)"),      "ans = 7.0", 'test max(x,y)')
        self.assertEqual(vimcalc.parse("max(3.2,7.6)"),  "ans = 7.6", 'test max(x,y)')
    def testMin(self):
        self.assertEqual(vimcalc.parse("min(3,7)"),      "ans = 3.0", 'test min(x,y)')
        self.assertEqual(vimcalc.parse("min(3.2,7.6)"),  "ans = 3.2", 'test min(x,y)')
    def testNrt(self):
        self.assertEqual(vimcalc.parse("nrt(27,3)"),     "ans = 3.0", 'test nrt(x,n)')
    def testPerms(self):
        self.assertEqual(vimcalc.parse("perms(3,2)"),    "ans = 6", 'test perms(n,k)')
    def testPow(self):
        self.assertEqual(vimcalc.parse("pow(2,5)"),      "ans = 32.0", 'test pow(x,y)')
    def testRad(self):
        self.assertEqual(vimcalc.parse("rad(0)"),        "ans = 0.0", 'test rad(x)')
        self.assertEqual(vimcalc.parse("rad(180)"),      "ans = 3.141592653589793", 'test rad(x)')
        self.assertEqual(vimcalc.parse("rad(360)"),      "ans = 6.283185307179586", 'test rad(x)')
    #def testRand(self):
        #self.assertEqual(vimcalc.parse("rand()"),       "ans = ", 'test rand()')
    def testRound(self):
        self.assertEqual(vimcalc.parse("round(4.2)"),    "ans = 4", 'test round(x)')
        self.assertEqual(vimcalc.parse("round(4.7)"),    "ans = 5", 'test round(x)')
    def testSin(self):
        self.assertEqual(vimcalc.parse("sin(pi/2)"),     "ans = 1.0", 'test sin.')
        self.assertEqual(vimcalc.parse("sin(0)"),        "ans = 0.0", 'test sin.')
    #TODO:
    def testSinh(self):
        self.assertEqual(vimcalc.parse("sinh(0)"),       "ans = 0.0", 'test sinh(x)')
    def testSqrt(self):
        self.assertEqual(vimcalc.parse("sqrt(64)"),      "ans = 8.0", 'test sqrt(x)')
        self.assertEqual(vimcalc.parse("sqrt(0)"),       "ans = 0.0", 'test sqrt(x)')
        self.assertEqual(vimcalc.parse("sqrt(2)"),       "ans = 1.4142135623730951", 'test sqrt(x)')
    def testTan(self):
        self.assertEqual(vimcalc.parse("tan(0)"),        "ans = 0.0", 'test tan(x)')
    def testTanh(self):
        self.assertEqual(vimcalc.parse("tanh(0)"),       "ans = 0.0", 'test tanh(x)')

if __name__ == "__main__":
    unittest.main()
