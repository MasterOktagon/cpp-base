
#!/usr/bin/env python3
import sys
from pathlib import Path

# Configuration: adjust these to your convention
START_MARKER = r'/// ```cpp'
END_MARKER   = r'/// ```'

HEADER = r'''
// This file is generated. Do not edit by hand.

#if(CATCH2_VERSION < 3)
    #include <catch2/catch.hpp>
#else
    #include <catch2/catch_all.hpp>
#endif

// redefine assert to use catch2's REQUIRE
#pragma push_macro("assert")
#undef assert
#define assert REQUIRE

#pragma push_macro("CATCH_INTERNAL_LINEINFO")
#undef CATCH_INTERNAL_LINEINFO
#define CATCH_INTERNAL_LINEINFO ::Catch::SourceLineInfo(DOCTEST_FILE, (__LINE__ - LINE_ORIGIN) + DOCTEST_ORIGIN)
'''

END = r'''

#undef assert
#pragma pop_macro("assert")
#pragma pop_macro("CATCH_INTERNAL_LINEINFO")

'''

includes = []

def extract_examples_from_file(path: Path):
    examples = []
    with path.open(encoding='utf-8') as f:
        lines = f.readlines()

    inside_block = False
    current_lines = []
    current_name = None
    start_line_idx = 1

    for line_idx, line in enumerate(lines):
        stripped = line.strip().rstrip('\n')

        if not inside_block:
            if stripped.startswith(START_MARKER):
                inside_block = True
                current_lines = []
                current_name = "Testing doc test: " + str(path) + ":" + str(line_idx + 1)
                start_line_idx = line_idx + 1
            continue


        # inside a ```cpp block
        if len(stripped) == 0 or stripped.startswith(END_MARKER) or not stripped.startswith("///"):
            if current_lines and current_name:
                examples.append((str(path), start_line_idx, current_name, current_lines))
            inside_block = False
            current_lines = []
            current_name = None
            continue

        # Remove leading comment slashes for content lines
        if stripped.startswith('/// '):
            stripped = stripped[4:]
            if stripped.startswith("# "):
                stripped = stripped[2:]
            if stripped.lstrip().startswith("#include "):
                includes.append(stripped.lstrip())
            current_lines += [stripped]

        ## Check for test name marker
        #if content.startswith('// test:'):
        #    current_name = content[len('// test:'):].strip()
        #    continue

    return examples

gen_ns = 0
def generate_tests(examples):
    global gen_ns
    out = includes
    out.append(HEADER)
    for filename, origin, name, code_lines in examples:
        out.append(f"#define DOCTEST_FILE \"{filename}\"")
        out.append(f"#define DOCTEST_ORIGIN {origin}")
        out.append("namespace _generated_" + str(gen_ns) + "{ constexpr size_t LINE_ORIGIN = __LINE__ + 1;")
        gen_ns += 1
        out.append("TEST_CASE(\"" + name + "\", \"[doctests]\") {")
        for c in code_lines:
            out.append(f'    {c}')
        out.append('}}\n')
        out.append("#undef DOCTEST_FILE")
        out.append("#undef DOCTEST_ORIGIN")
    return '\n'.join(out) + END

def main():
    if len(sys.argv) < 3:
        print("Usage: gen_doc_tests.py output.cpp input1.cpp [input2.cpp ...]")
        sys.exit(1)

    out_path = Path(sys.argv[1])
    in_paths = [Path(p) for p in sys.argv[2:]]

    all_examples = []
    for p in in_paths:
        all_examples.extend(extract_examples_from_file(p))

    print(f"\t{len(all_examples)} doc tests found")

    out_code = generate_tests(all_examples)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(out_code)

if __name__ == "__main__":
    main()

