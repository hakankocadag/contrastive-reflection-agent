"""
Ayristirma (parsing) boru hatti.
Gorev: Sentetik Python dosyalarini Python'un yerlesik 'ast' modulu ile
statik olarak analiz ederek, GroundTruthSchema'ya %100 uyumlu,
deterministik bir graph.json referans dosyasi uretmek.

Kullanim:
    python3 parser.py synthetic_files/ -o graph.json
"""
import argparse
import ast
import builtins
import json
import sys
from pathlib import Path

from schemas import ArchitectureError, FunctionCall, GroundTruthSchema

BUILTIN_NAMES = set(dir(builtins))


# --------------------------------------------------------------------------
# 1. Tek dosyadan ham bilgi cikarma (imports, tanimli fonksiyonlar, cagrilar)
# --------------------------------------------------------------------------

class FileFacts:
    """Bir sentetik dosyadan cikarilan ham, dosyaya-ozel bilgiler."""

    def __init__(self, file_id: str, tree: ast.Module):
        self.file_id = file_id
        self.tree = tree
        self.defined_functions: set[str] = set()
        # "from X import Y" -> {Y: X}; hangi ismin hangi modulden geldigini tutar
        self.from_imports: dict[str, str] = {}
        # "import X" / "import X as Y" -> {Y: X}; alias -> gercek modul adi
        self.module_imports: dict[str, str] = {}
        # (imported_module_stem, lineno) - sadece bizim sentetik dosya kumemizdeki
        # modullere yapilan importlar icin (dongusel bagimlilik analizinde kullanilir)
        self.internal_import_edges: list[tuple[str, int]] = []
        self.calls: list[tuple[str, ast.Call]] = []  # (caller_name, call_node)


def _dotted_attr_name(node: ast.expr) -> str | None:
    """ast.Attribute zincirini 'module.sub.func' seklinde duz metne cevirir."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def extract_file_facts(path: Path, known_module_stems: set[str]) -> FileFacts:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    facts = FileFacts(file_id=path.stem, tree=tree)

    # -- ust seviye import'lari topla --
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name
                facts.module_imports[local_name] = alias.name
                if alias.name in known_module_stems:
                    facts.internal_import_edges.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                local_name = alias.asname or alias.name
                facts.from_imports[local_name] = node.module
            if node.module in known_module_stems:
                facts.internal_import_edges.append((node.module, node.lineno))

    # -- fonksiyon tanimlari + her fonksiyonun icindeki cagrilar --
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            facts.defined_functions.add(node.name)

    for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for inner in ast.walk(func):
            if isinstance(inner, ast.Call):
                facts.calls.append((func.name, inner))

    return facts


# --------------------------------------------------------------------------
# 2. Cagri cozumleme (resolution) - FunctionCall + UndefinedCall tespiti
# --------------------------------------------------------------------------

def resolve_calls(
    facts: FileFacts, all_facts: dict[str, FileFacts]
) -> tuple[list[FunctionCall], list[ArchitectureError]]:
    detected_calls: list[FunctionCall] = []
    errors: list[ArchitectureError] = []

    for caller, call_node in facts.calls:
        func = call_node.func
        line = call_node.lineno

        if isinstance(func, ast.Name):
            callee = func.id
            detected_calls.append(
                FunctionCall(caller=caller, callee=callee, line_number=line)
            )
            is_defined = callee in facts.defined_functions
            is_builtin = callee in BUILTIN_NAMES
            is_from_import = callee in facts.from_imports
            if is_from_import:
                src_module = facts.from_imports[callee]
                src_facts = all_facts.get(src_module)
                is_from_import = src_facts is not None and (
                    callee in src_facts.defined_functions
                )
            if not (is_defined or is_builtin or is_from_import):
                errors.append(
                    ArchitectureError(
                        error_type="UndefinedCall",
                        target_node=callee,
                        line_number=line,
                    )
                )

        elif isinstance(func, ast.Attribute):
            dotted = _dotted_attr_name(func)
            if dotted is None:
                continue  # karmasik ifade (orn. metod zinciri), atla
            root_alias, attr = dotted.split(".", 1)
            detected_calls.append(
                FunctionCall(caller=caller, callee=dotted, line_number=line)
            )
            target_module = facts.module_imports.get(root_alias)
            if target_module is None:
                continue  # bilinmeyen/harici obje, yanlis pozitif uretmemek icin atla
            target_facts = all_facts.get(target_module)
            if target_facts is not None and attr not in target_facts.defined_functions:
                errors.append(
                    ArchitectureError(
                        error_type="UndefinedCall",
                        target_node=dotted,
                        line_number=line,
                    )
                )
        # diger cagri turleri (orn. lambda sonucu cagirma) su an kapsam disi

    return detected_calls, errors


# --------------------------------------------------------------------------
# 3. Dongusel bagimlilik (CircularDependency) tespiti
# --------------------------------------------------------------------------

def detect_circular_dependencies(
    all_facts: dict[str, FileFacts]
) -> dict[str, list[ArchitectureError]]:
    """DFS renklendirme ile import grafindeki tum dongulerdeki kenarlari bulur."""
    graph = {
        file_id: facts.internal_import_edges for file_id, facts in all_facts.items()
    }
    errors_by_file: dict[str, list[ArchitectureError]] = {
        f: [] for f in all_facts
    }

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {f: WHITE for f in all_facts}

    def dfs(node: str, stack: list[str]):
        color[node] = GRAY
        stack.append(node)
        for neighbor, lineno in graph.get(node, []):
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                # dongu bulundu: stack icinde neighbor'dan node'a kadar olan kisim dongudedir
                cycle_start = stack.index(neighbor)
                cycle_nodes = stack[cycle_start:] + [neighbor]
                for a, b in zip(cycle_nodes, cycle_nodes[1:]):
                    # kenar (a -> b) hatasini a dosyasina yaz
                    edge_lines = [
                        ln for tgt, ln in graph.get(a, []) if tgt == b
                    ]
                    for ln in edge_lines:
                        errors_by_file[a].append(
                            ArchitectureError(
                                error_type="CircularDependency",
                                target_node=b,
                                line_number=ln,
                            )
                        )
            elif color[neighbor] == WHITE:
                dfs(neighbor, stack)
        stack.pop()
        color[node] = BLACK

    for f in list(all_facts):
        if color[f] == WHITE:
            dfs(f, [])

    # ayni (target,line) hatasinin tekrar eklenmesini engelle (deterministik, tekil liste)
    for f, errs in errors_by_file.items():
        seen = set()
        unique = []
        for e in errs:
            key = (e.error_type, e.target_node, e.line_number)
            if key not in seen:
                seen.add(key)
                unique.append(e)
        errors_by_file[f] = unique

    return errors_by_file


# --------------------------------------------------------------------------
# 4. Ana boru hatti (pipeline)
# --------------------------------------------------------------------------

def build_graph(source_dir: Path) -> list[GroundTruthSchema]:
    py_files = sorted(source_dir.glob("*.py"))
    known_stems = {p.stem for p in py_files}

    all_facts: dict[str, FileFacts] = {
        p.stem: extract_file_facts(p, known_stems) for p in py_files
    }

    circular_errors = detect_circular_dependencies(all_facts)

    results: list[GroundTruthSchema] = []
    for file_id, facts in sorted(all_facts.items()):
        calls, undefined_errors = resolve_calls(facts, all_facts)
        all_errors = undefined_errors + circular_errors.get(file_id, [])

        calls.sort(key=lambda c: c.line_number)
        all_errors.sort(key=lambda e: (e.error_type, e.line_number))

        results.append(
            GroundTruthSchema(
                file_id=file_id,
                detected_calls=calls,
                reported_errors=all_errors,
            )
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_dir", type=Path, help="Sentetik .py dosyalarinin bulundugu klasor"
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("graph.json"),
        help="Cikti graph.json dosyasinin yolu (varsayilan: graph.json)",
    )
    args = parser.parse_args()

    if not args.source_dir.is_dir():
        print(f"Hata: '{args.source_dir}' bir klasor degil.", file=sys.stderr)
        sys.exit(1)

    graph = build_graph(args.source_dir)
    payload = [g.model_dump() for g in graph]
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    total_calls = sum(len(g.detected_calls) for g in graph)
    total_errors = sum(len(g.reported_errors) for g in graph)
    print(f"{len(graph)} dosya islendi -> {args.output}")
    print(f"  Toplam tespit edilen cagri: {total_calls}")
    print(f"  Toplam raporlanan hata:     {total_errors}")


if __name__ == "__main__":
    main()
