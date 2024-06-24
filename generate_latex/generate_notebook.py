"""
Copyright (c) 2024 kyomi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import shutil
import subprocess


def get_item_name(item: str) -> str:
    if item == "dp":
        return "DP"
    elif item == "ds":
        return "DS"

    return item.capitalize()


def cpy_template() -> None:
    shutil.copyfile(
        "templates/notebook.tex", "templates/saved_notebook.tex"
    )


def get_blocked() -> set[str]:
    blocked = set()
    with open("generate_latex/block_from_notebook.txt") as f:
        for line in f:
            # Remove comments
            line = line.split("#")[0]
            # Normalize filename
            line = line.strip().lower().replace(" ", "_") + ".cpp"
            blocked.add(line)
    return blocked


def remove_aux() -> None:
    items = [
        "saved_notebook.aux",
        "saved_notebook.log",
        "saved_notebook.toc",
        "saved_notebook.tex",
        "texput.log",
        "templates/saved_notebook.tex",
    ]

    for item in items:
        if os.path.exists(item):
            os.remove(item)


def move_output() -> None:
    if os.path.exists("notebook.pdf"):
        os.remove("notebook.pdf")

    if os.path.exists("saved_notebook.pdf"):
        shutil.move("saved_notebook.pdf", "notebook.pdf")


def get_dir() -> list[tuple[str, list[str]]]:
    path = "code"
    section_list = os.listdir(path)
    section = []
    for section_name in section_list:
        subsection = []
        section_path = os.path.join(path, section_name)
        items = os.listdir(section_path)
        for file_name in items:
            if file_name.endswith(".cpp"):
                subsection.append(file_name)
            elif os.path.isdir(os.path.join(section_path, file_name)):
                # Sub Directory
                sub_files = os.listdir(os.path.join(section_path, file_name))
                subsection.extend([
                    os.path.join(file_name, name)
                    for name in sub_files
                    if name.endswith(".cpp")
                ])

        section.append((section_name, subsection))
    return section


def create_notebook(
    section: list[tuple[str, list[str]]], blocked: set[str]
) -> None:
    path = "code"
    aux = ""
    with open("templates/saved_notebook.tex", "a") as texfile:
        for item, subsection in section:
            aux += "\\section{%s}\n" % get_item_name(item)

            for file in subsection:
                if file in blocked:
                    continue

                name, ext = os.path.splitext(file)
                name = os.path.split(name)[1]  # Remove Segtree/ prefix
                file_name = " ".join([x.capitalize() for x in name.split("_")])
                file_path = os.path.join(path, item, file).replace("\\", "/")

                aux += "\\includes{%s}{%s}\n" % (file_name, file_path)

        aux += "\n\\end{multicols}\n\\end{document}\n"
        texfile.write(aux)


def main() -> None:
    cpy_template()
    section = get_dir()
    blocked = get_blocked()
    create_notebook(section, blocked)

    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "templates/saved_notebook.tex",
    ]
    with open(os.devnull, "w") as DEVNULL:
        try:
            subprocess.check_call(cmd, stdout=DEVNULL)
            subprocess.check_call(cmd, stdout=DEVNULL)
        except Exception:
            print("Erro na transformação de LaTex para pdf.")
            print("Execute manualmente para entender o erro:")
            print(
                "pdflatex -interaction=nonstopmode -halt-on-error "
                "templates/saved_notebook.tex"
            )
            exit(1)

    remove_aux()
    move_output()

    print("O PDF foi gerado com sucesso!")


if __name__ == "__main__":
    main()
