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
	if isinstance(node, ast.Num): # <number>
		return node.n
	elif isinstance(node, ast.BinOp): # <left> <operator> <right>
		return operators[type(node.op)](eval_(node.left), eval_(node.right))
	elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
		return operators[type(node.op)](eval_(node.operand))
	else:
		raise TypeError(node)
