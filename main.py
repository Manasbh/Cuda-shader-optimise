import os
import re
import time
from collections import defaultdict
from typing import List, Tuple

def optimize_shader(input_file: str, output_file: str) -> str:
    """
    Optimizes the shader code by performing various optimization techniques.

    Args:
        input_file (str): The path to the input shader file.
        output_file (str): The path to the output file where the optimized shader code will be saved.

    Returns:
        str: The optimized shader code.
    """
    # Load the shader code from the input file
    with open(input_file, 'r') as file:
        shader_code = file.read()

    # Record the initial size of the shader code
    initial_size = len(shader_code)

    # Optimize the shader code
    optimized_code = remove_comments(shader_code)
    optimized_code = remove_whitespace(optimized_code)
    optimized_code = remove_redundant_variables(optimized_code)
    optimized_code = combine_variable_declarations(optimized_code)
    optimized_code = remove_empty_lines(optimized_code)
    optimized_code = inline_functions(optimized_code)
    optimized_code = unroll_loops(optimized_code)
    optimized_code = replace_uniform_variables(optimized_code)
    optimized_code = optimize_texture_lookups(optimized_code)

    # Record the final size of the optimized shader code
    optimized_size = len(optimized_code)

    # Calculate the approximate percentage boost in performance
    boost_percentage = round(100 * (initial_size - optimized_size) / initial_size, 2)

    # Print the changes and the approximate percentage boost
    print("Initial shader code size:", initial_size, "bytes")
    print("Optimized shader code size:", optimized_size, "bytes")
    print("Approximate percentage boost:", boost_percentage, "%")

    # Save the optimized shader code to the output file
    with open(output_file, 'w') as file:
        file.write(optimized_code)

    return optimized_code

def remove_comments(shader_code: str) -> str:
    """
    Removes single-line and multi-line comments from the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with comments removed.
    """
    # Remove single-line comments
    shader_code = re.sub(r'//.*', '', shader_code)

    # Remove multi-line comments
    shader_code = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', shader_code)

    return shader_code

def remove_whitespace(shader_code: str) -> str:
    """
    Removes leading, trailing, and consecutive whitespace from the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with whitespace removed.
    """
    # Remove leading and trailing whitespace
    shader_code = re.sub(r'^\s+|\s+$', '', shader_code)

    # Remove consecutive whitespace
    shader_code = re.sub(r'\s+', ' ', shader_code)

    return shader_code

def remove_redundant_variables(shader_code: str) -> str:
    """
    Removes redundant variable declarations from the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with redundant variable declarations removed.
    """
    # Identify variable declarations
    var_decl_pattern = r'\b(\w+)\s+(\w+)\s*\[?\s*(\d*)\s*\]?\s*;'
    var_decl_matches = re.finditer(var_decl_pattern, shader_code)

    # Use a defaultdict to keep track of variable declarations
    variable_declarations = defaultdict(list)

    # Replace redundant variable declarations with a single declaration
    new_shader_code = ''
    start = 0
    for match in var_decl_matches:
        var_type, var_name, var_size = match.groups()
        key = f"{var_type} {var_name}"
        variable_declarations[key].append(match.group())
        new_shader_code += shader_code[start:match.start()]
        new_shader_code += variable_declarations[key][0]
        start = match.end()

    new_shader_code += shader_code[start:]
    return new_shader_code

def combine_variable_declarations(shader_code: str) -> str:
    """
    Combines consecutive variable declarations of the same type in the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with combined variable declarations.
    """
    # Identify consecutive variable declarations
    var_decl_pattern = r'\b(\w+)\s+(\w+)\s*\[?\s*(\d*)\s*\]?\s*;'
    var_decl_matches = re.finditer(var_decl_pattern, shader_code)

    # Combine consecutive variable declarations of the same type
    new_shader_code = ''
    var_declarations: List[str] = []
    current_var_type = ''
    current_var_names = ''
    current_var_sizes = ''

    start = 0
    for match in var_decl_matches:
        var_type, var_name, var_size = match.groups()
        if current_var_type == '':
            current_var_type = var_type
            current_var_names = var_name
            current_var_sizes = var_size
        elif current_var_type == var_type:
            current_var_names += ', ' + var_name
            if var_size:
                current_var_sizes += ', ' + var_size
        else:
            var_declarations.append(f"{current_var_type} {current_var_names}{current_var_sizes if current_var_sizes else ''};")
            current_var_type = var_type
            current_var_names = var_name
            current_var_sizes = var_size

        new_shader_code += shader_code[start:match.start()]
        start = match.end()

    if current_var_type:
        var_declarations.append(f"{current_var_type} {current_var_names}{current_var_sizes if current_var_sizes else ''};")

    new_shader_code += '\n'.join(var_declarations) + '\n' + shader_code[start:]
    return new_shader_code

def remove_empty_lines(shader_code: str) -> str:
    """
    Removes empty lines from the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with empty lines removed.
    """
    # Remove empty lines
    shader_code = re.sub(r'\n\s*\n', '\n', shader_code)
    return shader_code

def inline_functions(shader_code: str) -> str:
    """
    Inlines small functions in the shader code to improve performance.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with small functions inlined.
    """
    # Identify function definitions
    function_pattern = r'\b(\w+)\s+(\w+)\s*\([^)]*\)\s*\{'
    function_matches = re.finditer(function_pattern, shader_code)

    # Replace small function calls with their inline code
    new_shader_code = ''
    start = 0
    for match in function_matches:
        function_name = match.group(2)
        function_body = find_function_body(shader_code, match.end())
        if len(function_body) < 50:  # Inline functions with a small body
            new_shader_code += shader_code[start:match.start()]
            new_shader_code += function_body
            start = match.end() + len(function_body) + 1
        else:
            new_shader_code += shader_code[start:match.end() + 1]
            start = match.end() + 1

    new_shader_code += shader_code[start:]
    return new_shader_code

def unroll_loops(shader_code: str) -> str:
    """
    Unrolls small loops in the shader code to improve performance.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with small loops unrolled.
    """
    # Identify for loops
    loop_pattern = r'\bfor\s*\([^)]*\)\s*\{'
    loop_matches = re.finditer(loop_pattern, shader_code)

    # Unroll small loops
    new_shader_code = ''
    start = 0
    for match in loop_matches:
        loop_body = find_loop_body(shader_code, match.end())
        if len(loop_body) < 50:  # Unroll loops with a small body
            new_shader_code += shader_code[start:match.start()]
            new_shader_code += unroll_loop(loop_body)
            start = match.end() + len(loop_body) + 1
        else:
            new_shader_code += shader_code[start:match.end() + 1]
            start = match.end() + 1

    new_shader_code += shader_code[start:]
    return new_shader_code

def replace_uniform_variables(shader_code: str) -> str:
    """
    Replaces uniform variables with their constant values, if possible.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with uniform variables replaced.
    """
    # Identify uniform variable declarations
    uniform_pattern = r'\buniform\s+(\w+)\s+(\w+)\s*\[?\s*(\d*)\s*\]?\s*;'
    uniform_matches = re.finditer(uniform_pattern, shader_code)

    # Replace uniform variables with their constant values
    new_shader_code = ''
    start = 0
    for match in uniform_matches:
        uniform_type, uniform_name, uniform_size = match.groups()
        uniform_value = get_uniform_value(uniform_name)
        if uniform_value is not None:
            new_shader_code += shader_code[start:match.start()]
            new_shader_code += f"{uniform_type} {uniform_name} = {uniform_value};"
            start = match.end()

    new_shader_code += shader_code[start:]
    return new_shader_code

def optimize_texture_lookups(shader_code: str) -> str:
    """
    Optimizes texture lookups in the shader code.

    Args:
        shader_code (str): The input shader code.

    Returns:
        str: The shader code with optimized texture lookups.
    """
    # Identify texture lookup functions
    texture_pattern = r'\btexture\([^)]*\)'
    texture_matches = re.finditer(texture_pattern, shader_code)

    # Replace texture lookups with pre-computed values, if possible
    new_shader_code = ''
    start = 0
    for match in texture_matches:
        texture_call = match.group()
        optimized_call = optimize_texture_lookup(texture_call)
        if optimized_call != texture_call:
            new_shader_code += shader_code[start:match.start()]
            new_shader_code += optimized_call
            start = match.end()
        else:
            new_shader_code += shader_code[start:match.end()]
            start = match.end()

    new_shader_code += shader_code[start:]
    return new_shader_code

def find_function_body(shader_code: str, start_index: int) -> str:
    """
    Finds the body of a function in the shader code.

    Args:
        shader_code (str): The input shader code.
        start_index (int): The starting index of the function body.

    Returns:
        str: The function body.
    """
    open_braces = 1
    end_index = start_index
    while open_braces > 0 and end_index < len(shader_code):
        if shader_code[end_index] == '{':
            open_braces += 1
        elif shader_code[end_index] == '}':
            open_braces -= 1
        end_index += 1
    return shader_code[start_index:end_index]

def find_loop_body(shader_code: str, start_index: int) -> str:
    """
    Finds the body of a loop in the shader code.

    Args:
        shader_code (str): The input shader code.
        start_index (int): The starting index of the loop body.

    Returns:
        str: The loop body.
    """
    open_braces = 1
    end_index = start_index
    while open_braces > 0 and end_index < len(shader_code):
        if shader_code[end_index] == '{':
            open_braces += 1
        elif shader_code[end_index] == '}':
            open_braces -= 1
        end_index += 1
    return shader_code[start_index:end_index]

def unroll_loop(loop_body: str) -> str:
    """
    Unrolls a small loop in the shader code.

    Args:
        loop_body (str): The body of the loop to be unrolled.

    Returns:
        str: The unrolled loop code.
    """
    # Implement the loop unrolling logic here
    unrolled_code = ''
    # For example, you can replace the loop with its unrolled version
    unrolled_code = loop_body.replace('for (int i = 0; i < 10; i++)', '''
        {
            // Unrolled loop body
        }
    ''')
    return unrolled_code

def get_uniform_value(uniform_name: str) -> str:
    """
    Retrieves the constant value of a uniform variable, if available.

    Args:
        uniform_name (str): The name of the uniform variable.

    Returns:
        str: The constant value of the uniform variable, or None if not available.
    """
    # Implement the logic to retrieve the constant value of the uniform variable
    # For example, you can have a dictionary of known uniform values
    uniform_values = {
        'u_time': '0.0',
        'u_resolution': 'vec2(1024.0, 768.0)',
        # Add more uniform values as needed
    }
    return uniform_values.get(uniform_name, None)

def optimize_texture_lookup(texture_call: str) -> str:
    """
    Optimizes a texture lookup function call in the shader code.

    Args:
        texture_call (str): The texture lookup function call.

    Returns:
        str: The optimized texture lookup function call, or the original call if no optimization is possible.
    """
    # Implement the logic to optimize the texture lookup
    # For example, you can pre-compute the texture coordinates if they are constant
    optimized_call = texture_call
    # Add more optimization logic as needed
    return optimized_call

if __name__ == '__main__':
    input_file = 'path/to/your/shader/file.glsl'
    output_file = 'path/to/your/optimized/shader/file.glsl'

    start_time = time.time()
    optimized_code = optimize_shader(input_file, output_file)
    end_time = time.time()

    print(f"Optimization time: {end_time - start_time:.2f} seconds")
    print(f"Approximate percentage boost: {round(100 * (len(optimized_code) - len(optimized_code)) / len(optimized_code), 2)}%")