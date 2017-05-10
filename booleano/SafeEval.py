# Copyright (c) 2017 by Michael Dombrowski <http://MikeDombrowski.com/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.

import ast
import operator as op
import math

# supported operators
operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: math.pow, ast.BitXor: op.xor,
             ast.USub: op.neg, ast.Mod: op.mod
             }


def eval_expr(expr):
	return eval_(ast.parse(expr, mode='eval').body)


def eval_(node):
	if isinstance(node, ast.Num):  # <number>
		return node.n
	elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
		return operators[type(node.op)](eval_(node.left), eval_(node.right))
	elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
		return operators[type(node.op)](eval_(node.operand))
	else:
		raise TypeError(node)
