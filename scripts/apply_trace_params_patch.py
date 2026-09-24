from pathlib import Path

root = Path("upstream/quadwild")
trace_h = root / "trace.h"
trace_cpp = root / "trace.cpp"
cli_cpp = root / "cli_trace.cpp"

old_h = trace_h.read_text(encoding="utf-8")
expected_h = "#pragma once\n#include <string>\n#include <tracing/mesh_type.h>\n\nbool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh);"
if old_h.strip() != expected_h.strip():
    raise RuntimeError("Unexpected upstream trace.h; refusing to patch blindly")

new_h = r'''#pragma once
#include <string>
#include <tracing/mesh_type.h>

struct TraceParameters
{
    double drift = 100.0;
    double sample_ratio = 0.01;
    int max_val = 5;
    double cclarkability = 1.0;
    bool split_on_removal = true;
    bool match_valence = true;
    bool add_only_needed = true;
    bool final_removal = true;
    bool force_split = false;
    bool meta_mesh_collapse = true;
};

bool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh);
bool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh, const TraceParameters& params);
'''
trace_h.write_text(new_h, encoding="utf-8", newline="\n")

text = trace_cpp.read_text(encoding="utf-8")
old_sig = "bool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh)\n{"
new_sig = """bool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh)\n{\n    return trace(filename_prefix, traceTrimesh, TraceParameters{});\n}\n\nbool trace(const std::string& filename_prefix, TraceMesh& traceTrimesh, const TraceParameters& params)\n{"""
if text.count(old_sig) != 1:
    raise RuntimeError("Unexpected upstream trace() signature")
text = text.replace(old_sig, new_sig, 1)

old_params = '''    TraceMesh::ScalarType Drift=100;
    bool add_only_needed=true;
    bool final_removal=true;
    bool meta_mesh_collapse=true;
    bool force_split=false;
    PTr.sample_ratio=0.01;
    PTr.CClarkability=1;
    PTr.split_on_removal=true;
    PTr.away_from_singular=true;
    PTr.match_valence=true;
    PTr.check_quality_functor=false;
    PTr.MinVal=3;
    PTr.MaxVal=5;
    PTr.Concave_Need=1;
'''
new_params = '''    TraceMesh::ScalarType Drift=(TraceMesh::ScalarType)params.drift;
    bool add_only_needed=params.add_only_needed;
    bool final_removal=params.final_removal;
    bool meta_mesh_collapse=params.meta_mesh_collapse;
    bool force_split=params.force_split;
    PTr.sample_ratio=(TraceMesh::ScalarType)params.sample_ratio;
    PTr.CClarkability=(TraceMesh::ScalarType)params.cclarkability;
    PTr.split_on_removal=params.split_on_removal;
    PTr.away_from_singular=true;
    PTr.match_valence=params.match_valence;
    PTr.check_quality_functor=false;
    PTr.MinVal=3;
    PTr.MaxVal=params.max_val;
    PTr.Concave_Need=1;

    std::cout << "TRACE_PARAMS"
              << " drift=" << params.drift
              << " srate=" << params.sample_ratio
              << " maxval=" << params.max_val
              << " cclark=" << params.cclarkability
              << " split=" << params.split_on_removal
              << " match=" << params.match_valence
              << " addneed=" << params.add_only_needed
              << " finalrem=" << params.final_removal
              << " forcesplit=" << params.force_split
              << " metacollapse=" << params.meta_mesh_collapse
              << std::endl;
'''
if text.count(old_params) != 1:
    raise RuntimeError("Unexpected upstream hard-coded tracing parameter block")
text = text.replace(old_params, new_params, 1)
trace_cpp.write_text(text, encoding="utf-8", newline="\n")

old_cli = cli_cpp.read_text(encoding="utf-8")
if "bool success = trace(argv[1], tm);" not in old_cli:
    raise RuntimeError("Unexpected upstream cli_trace.cpp")

new_cli = r'''#include "trace.h"
#include <iostream>
#include <stdexcept>

static bool parse_bool(const char* value)
{
    return std::stoi(value) != 0;
}

int main(int argc, char *argv[])
{
    if (argc < 2 || argc > 12) {
        std::cerr << "usage: " << argv[0]
                  << " <prefix> [drift] [sample_ratio] [max_val] [cclarkability]"
                  << " [split_on_removal] [match_valence] [add_only_needed]"
                  << " [final_removal] [force_split] [meta_mesh_collapse]" << std::endl;
        return 1;
    }

    TraceParameters p;
    try {
        if (argc > 2) p.drift = std::stod(argv[2]);
        if (argc > 3) p.sample_ratio = std::stod(argv[3]);
        if (argc > 4) p.max_val = std::stoi(argv[4]);
        if (argc > 5) p.cclarkability = std::stod(argv[5]);
        if (argc > 6) p.split_on_removal = parse_bool(argv[6]);
        if (argc > 7) p.match_valence = parse_bool(argv[7]);
        if (argc > 8) p.add_only_needed = parse_bool(argv[8]);
        if (argc > 9) p.final_removal = parse_bool(argv[9]);
        if (argc > 10) p.force_split = parse_bool(argv[10]);
        if (argc > 11) p.meta_mesh_collapse = parse_bool(argv[11]);
    } catch (const std::exception& e) {
        std::cerr << "invalid tracing parameter: " << e.what() << std::endl;
        return 1;
    }

    TraceMesh tm;
    bool success = trace(argv[1], tm, p);
    if (success) {
        std::cout << "success." << std::endl;
        return 0;
    }
    std::cout << "trace() failed." << std::endl;
    return 2;
}
'''
cli_cpp.write_text(new_cli, encoding="utf-8", newline="\n")

print("Applied parameterized cli_trace patch")
