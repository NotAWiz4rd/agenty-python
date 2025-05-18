# calculator_tool.py
# A tool to perform various mathematical calculations safely.
# This calculator uses a restricted evaluation environment to prevent code injection
# and only allows specific mathematical operations from the math module.

import json
import math
import operator
from functools import reduce  # For Python 3
from tools.base_tool import ToolDefinition

# ------------------------------------------------------------------
# Input‐schema for the calculator tool
# ------------------------------------------------------------------
CalculatorInputSchema = {
    "type": "object",
    "properties": {
        "expression": {
            "type": "string",
            "description": "Mathematical expression to evaluate. Can include numbers, operators (+, -, *, /, **), functions (sin, cos, tan, sqrt, log, etc.)"
        },
        "operation": {
            "type": "string",
            "description": "Alternative to expression: specify the specific operation (add, subtract, multiply, divide, power, sqrt, sin, cos, tan, log, etc.)"
        },
        "operands": {
            "type": "array",
            "description": "Array of numeric values to use with the specified operation",
            "items": {
                "type": "number"
            }
        }
    },
    "required": ["expression"]
}

def calculator(input_data: dict) -> str:
    """
    Evaluates mathematical expressions or performs specific operations on operands.
    
    Can be used in two ways:
    1. Provide an 'expression' string to evaluate
    2. Provide an 'operation' and 'operands' to perform a specific operation
    
    Returns the result as a string, or an error message if the calculation fails.
    """
    # Allow raw JSON string or parsed dict
    if isinstance(input_data, str):
        input_data = json.loads(input_data)
    
    try:
        # Method 1: Expression evaluation
        if "expression" in input_data:
            expression = input_data.get("expression", "")
            
            # Create a safe environment with only math functions
            safe_env = {
                "abs": abs,
                "max": max,
                "min": min,
                "pow": pow,
                "round": round,
                "sum": sum,
                # Math module functions
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "asin": math.asin,
                "acos": math.acos,
                "atan": math.atan,
                "sqrt": math.sqrt,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "floor": math.floor,
                "ceil": math.ceil,
                "factorial": math.factorial,
                "pi": math.pi,
                "e": math.e
            }
            
            # Safety check - reject expressions with potential security issues 
            # Disallow expressions with imports, builtins, attribute access, etc.
            forbidden = ['__', 'import', 'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr', 
                        'globals', 'locals', 'open', 'file', 'os.', 'sys.']
            if any(x in expression for x in forbidden):
                return "Error: Expression contains forbidden elements"
                
            # Evaluate the expression in a restricted environment
            try:
                result = eval(expression, {"__builtins__": {}}, safe_env)
                return str(result)
            except Exception as e:
                return f"Error evaluating expression: {str(e)}"
        
        # Method 2: Operation with operands
        elif "operation" in input_data and "operands" in input_data:
            operation = input_data.get("operation", "").lower()
            operands = input_data.get("operands", [])
            
            if not operands:
                return "Error: No operands provided"
            
            # Dictionary of available operations with their implementations
            # Each operation is a function that accepts a list of numeric operands
            operations = {
                "add": sum,
                "subtract": lambda nums: nums[0] - sum(nums[1:]) if nums else 0,
                "multiply": math.prod if hasattr(math, 'prod') else lambda nums: operator.reduce(operator.mul, nums, 1),
                "divide": lambda nums: nums[0] / nums[1] if len(nums) >= 2 else 0,
                "power": lambda nums: nums[0] ** nums[1] if len(nums) >= 2 else 0,
                "sqrt": lambda nums: math.sqrt(nums[0]) if nums else 0,
                "sin": lambda nums: math.sin(nums[0]) if nums else 0,
                "cos": lambda nums: math.cos(nums[0]) if nums else 0,
                "tan": lambda nums: math.tan(nums[0]) if nums else 0,
                "log": lambda nums: math.log(nums[0]) if nums else 0,
                "log10": lambda nums: math.log10(nums[0]) if nums else 0,
                "exp": lambda nums: math.exp(nums[0]) if nums else 0,
                "factorial": lambda nums: math.factorial(int(nums[0])) if nums else 0,
                "abs": lambda nums: abs(nums[0]) if nums else 0,
                "floor": lambda nums: math.floor(nums[0]) if nums else 0,
                "ceil": lambda nums: math.ceil(nums[0]) if nums else 0,
                "gcd": lambda nums: math.gcd(*[int(n) for n in nums]) if len(nums) >= 2 else 0,
                "lcm": lambda nums: math.lcm(*[int(n) for n in nums]) if hasattr(math, 'lcm') and len(nums) >= 2 else 0,
                "max": max,
                "min": min,
                "average": lambda nums: sum(nums) / len(nums) if nums else 0
            }
            
            if operation not in operations:
                return f"Error: Unknown operation '{operation}'"
            
            try:
                result = operations[operation](operands)
                return str(result)
            except Exception as e:
                return f"Error performing {operation}: {str(e)}"
        else:
            return "Error: Please provide either an 'expression' or both 'operation' and 'operands'"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# ------------------------------------------------------------------
# ToolDefinition instance
# ------------------------------------------------------------------
CalculatorDefinition = ToolDefinition(
    name="calculator",
    description=(
        "Performs mathematical calculations. Can evaluate expressions or perform specific operations. "
        "Supports basic arithmetic, trigonometric functions, logarithms, square roots, and more."
    ),
    input_schema=CalculatorInputSchema,
    function=calculator
)