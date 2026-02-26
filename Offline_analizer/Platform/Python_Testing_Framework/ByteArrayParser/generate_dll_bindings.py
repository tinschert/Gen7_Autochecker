import pefile
import os

# Define MSVC mapping types
MSVC_TYPES = {
    "B": "ctypes.c_uchar",    # unsigned char
    "Q": "ctypes.POINTER(ctypes.c_ubyte)",    # unsigned char
    "H": "ctypes.c_int",      # int
    "I": "ctypes.c_uint",     # unsigned int
    "J": "ctypes.c_long",     # long
    "K": "ctypes.c_ulong",    # unsigned long
    "N": "ctypes.c_double",   # double
    "X": "ctypes.c_void_p",   # void*
}
CALLING_CONVENTIONS = {
    "A": "__declspec(dllexport)",
    "Y": "__stdcall",
}

def parse_msvc_signature(mangled_name):
    """
    Parses a Microsoft Visual C++ (MSVC) mangled function signature to extract the return type,
    argument types, and calling convention.
    Args:
        mangled_name (str): The mangled function name containing the MSVC signature.
    Returns:
        tuple: A tuple containing:
            - return_type (str): The return type of the function.
            - argtypes (list): A list of argument types for the function.
            - calling_convention (str): The calling convention of the function.
    """
    # Find index of the char array where msvc types of the functions are defined
    msvc_type_index = 0
    k = 0
    for k in range(len(mangled_name)-1):
        if mangled_name[k] == '@' and mangled_name[k+1] == '@':
            msvc_type_index = k+2
    
    # Delete everything before the msvc types
    signature = mangled_name[msvc_type_index:]

    # Read return value and calling convention
    calling_convention = CALLING_CONVENTIONS.get(signature[0], "__stdcall") + " " + CALLING_CONVENTIONS.get(signature[1], "__stdcall")
    return_type = MSVC_TYPES.get(signature[2], "ctypes.c_void_p")
    
    # Read argument types of the functions
    argtypes = []
    i = 3  # Start at index 3
    while i < len(signature) and signature[i] != '@':  # '@' ends the args list
        argtypes.append(MSVC_TYPES.get(signature[i], "ctypes.c_void_p"))
        if signature[i] == "Q":
            i = i+4
        else:
            i += 1
    return return_type, argtypes, calling_convention

def extract_functions_from_dll(dll_path):
    """
    Extracts function names from the export table of a given DLL.
    Args:
        dll_path (str): The file path to the DLL.
    Returns:
        list of tuple: A list of tuples where each tuple contains the mangled name and the demangled function name.
                       Returns an empty list if no functions are found or if an error occurs.
    Example:
        >>> extract_functions_from_dll('example.dll')
        [('??0ExampleClass@@QAE@XZ', 'ExampleClass')]
    """
    try:
        pe = pefile.PE(dll_path)
        export_functions = []

        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                if symbol.name:
                    mangled_name = symbol.name.decode('utf-8')
                    if "@" in mangled_name and "?" in mangled_name:
                        # Extract function name between ? und @@
                        start = mangled_name.find("?") + 1
                        end = mangled_name.find("@@")
                        function_name = mangled_name[start:end]
                        export_functions.append((mangled_name, function_name))
        return export_functions
    except Exception as e:
        print(f"Error when analyzing the DLL: {e}")
        return []

def generate_python_bindings(dll_path, output_path):
    """
    Generates Python bindings for the exported functions of a given DLL and writes them to a specified output file.
    Args:
        dll_path (str): The path to the DLL file from which to generate bindings.
        output_path (str): The path to the output file where the generated bindings will be written.
    Returns:
        None
    The function performs the following steps:
    1. Loads the DLL file using the pefile library.
    2. Extracts the names of the exported functions from the DLL.
    3. Filters the exported functions to include only those with mangled names starting with "oa".
    4. Parses the MSVC signature of each filtered function to determine its return type, argument types, and calling convention.
    5. Writes the generated Python bindings to the specified output file, including the function aliases, return types, and argument types.
    Example for mangled name:
        ?getDistance@@YAJIH@Z   The structure is "?" -> function name -> "@@" -> MSVC types -> "@Z"
    """
    pe = pefile.PE(dll_path)
    exports = [exp.name.decode() for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols if exp.name]
    aliases = []
    for export in exports:
        # Check that functions name is mangled indicated by "?"
        # Also only export functions starting their name with oa, which are specifically implemented for the Offline Analyzer
        if export.startswith("?") and export[1] == "o" and export[2] == "a":  
            alias = export.split("@@")[0][1:] # Function names are between `?` and `@@`
            return_type, argtypes, calling_convention = parse_msvc_signature(export)
            
            aliases.append({
                "alias": alias,
                "mangled_name": export,
                "return_type": return_type,
                "argtypes": argtypes
            })
            
    with open(output_path, "w") as f:
        f.write("import ctypes\n\n")
        f.write(f"dll = ctypes.WinDLL(r'{dll_path}')\n\n")
        for alias in aliases:
            f.write(f"# Alias für: {alias['mangled_name']}\n")
            f.write(f"{alias['alias']} = getattr(dll, '{alias['mangled_name']}')\n")
            f.write(f"{alias['alias']}.restype = {alias['return_type']}\n")
            f.write(f"{alias['alias']}.argtypes = [\n")
            for arg in alias['argtypes']:
                f.write(f"    {arg},\n")
            f.write("]\n\n")

    print(f"Binding '{output_path}' generated successfully.")

def main():
    # Give DLL path and file name for the library that shall be generated
    dll_path = "../../Classe/DLL/Release64/RoadObj.dll"
    output_file = "dll_bindings.py"
    
    # Search for DLL
    if not os.path.exists(dll_path):
        print(f"Can not find '{dll_path}'.")
        return

    # Generate python library
    generate_python_bindings(dll_path, output_file)

if __name__ == "__main__":
    main()
