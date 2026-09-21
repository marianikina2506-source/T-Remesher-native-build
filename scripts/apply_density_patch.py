from pathlib import Path

path = Path('upstream/components/quad_from_patches/main.cpp')
text = path.read_text(encoding='utf-8')

replacements = [
    (
        '#include <iostream>\n',
        '#include <iostream>\n#include <fstream>\n#include <algorithm>\n#include <limits>\n',
    ),
    (
        '    if(argc<2 || argc > 5)\n    {\n        std::cerr << "usage: " << argv[0] << " <input.obj> [num] [setup.txt] [out_stats.json]"\n',
        '    if(argc<2 || argc > 6)\n    {\n        std::cerr << "usage: " << argv[0] << " <input.obj> [num] [setup.txt] [out_stats.json] [density.txt]"\n',
    ),
    (
        '    if (argc>4) {\n        json_filename = argv[4];\n    }\n    QuadRetopology::Parameters parameters;\n',
        '    if (argc>4) {\n        json_filename = argv[4];\n    }\n    std::string densityFilename = "";\n    if (argc>5) {\n        densityFilename = argv[5];\n    }\n    QuadRetopology::Parameters parameters;\n',
    ),
    (
        '    const std::vector<double> edgeFactor(trimeshPartitions.size(), EdgeSize);\n    auto qfp_result = qfp::quadrangulationFromPatches(trimesh, trimeshPartitions, trimeshCorners, edgeFactor, parameters, fixedChartClusters, quadmesh, quadmeshPartitions, quadmeshCorners, ilpResult);\n',
        '''    std::vector<double> edgeFactor(trimeshPartitions.size(), EdgeSize);\n\n    // T-Remesher native adaptive density.\n    // File format: patch count, followed by one target-edge multiplier per patch.\n    // multiplier < 1 => denser; multiplier > 1 => coarser.\n    if (!densityFilename.empty())\n    {\n        std::ifstream densityInput(densityFilename.c_str());\n        if (!densityInput.is_open())\n        {\n            std::cerr << "ERROR LOADING DENSITY FILE " << densityFilename << std::endl;\n            return 2;\n        }\n\n        size_t densityCount = 0;\n        densityInput >> densityCount;\n        if (densityCount != edgeFactor.size())\n        {\n            std::cerr << "DENSITY PATCH COUNT MISMATCH: file=" << densityCount\n                      << " mesh=" << edgeFactor.size() << std::endl;\n            return 3;\n        }\n\n        double minMultiplier = std::numeric_limits<double>::max();\n        double maxMultiplier = 0.0;\n        for (size_t i = 0; i < densityCount; ++i)\n        {\n            double multiplier = 1.0;\n            if (!(densityInput >> multiplier))\n            {\n                std::cerr << "INVALID DENSITY VALUE AT PATCH " << i << std::endl;\n                return 4;\n            }\n            multiplier = std::max(0.10, std::min(4.00, multiplier));\n            edgeFactor[i] = EdgeSize * multiplier;\n            minMultiplier = std::min(minMultiplier, multiplier);\n            maxMultiplier = std::max(maxMultiplier, multiplier);\n        }\n        std::cout << "Native density: " << densityCount << " patches, multiplier range "\n                  << minMultiplier << " .. " << maxMultiplier << std::endl;\n    }\n\n    auto qfp_result = qfp::quadrangulationFromPatches(trimesh, trimeshPartitions, trimeshCorners, edgeFactor, parameters, fixedChartClusters, quadmesh, quadmeshPartitions, quadmeshCorners, ilpResult);\n''',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f'Expected source block not found:\n{old[:160]}')
    text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')
print('Patched', path)
