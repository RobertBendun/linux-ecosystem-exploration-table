from glob import glob
from string import Template
from types import SimpleNamespace
from html import escape

class Technology:
    ALL = []

    def __init__(self, name: str, url: str = ""):
        self.name = name
        self.url = url
        Technology.ALL.append(self)

    def __str__(self):
        return self.name

Awk       = Technology("AWK")
Coreutils = Technology("Coreutils")
Perl      = Technology("Perl")
Python    = Technology("Python")
Ruby      = Technology("Ruby")
Tcl       = Technology("TCL")
Shell     = Technology("Shell")

class Database(list):
    def add(self, title: str, id: str, task: str):
        w = Ways(title = title, id = id, task = task)
        self.append(w)
        return w

    def generate_html(self):
        templates = self._load_templates()

        table_of_contents = '\n'.join(
            templates.toc_entry.substitute({ "title": ways.title, "id": ways.id })
            for ways in self
        )

        content = '\n'.join(
            templates.ways.substitute({
                "title": escape(ways.title),
                "content": '\n'.join(templates.way.substitute(
                    dict(
                        (k, escape(str(v))) for k, v in way.items()
                    ) | {
                        'char_count': len(way['command'])
                    }
                ) for way in sorted(ways, key=lambda x: (x['technology'].name, x['command']))),
                "id": ways.id,
                "task": escape(ways.task)
            })
            for ways in self)

        site_content = templates.site.substitute({ "content": content, "toc": table_of_contents })
        with open('index.html', 'w') as site:
            site.write(site_content)

    def _load_templates(self):
        d, suffix = {}, ".template.html"
        for template in glob(f"*{suffix}"):
            with open(template) as f:
                d[template.removesuffix(suffix)] = Template(f.read())
        return SimpleNamespace(**d)

class Ways(list):
    def __init__(self, title: str, id: str, task: str):
        self.title = title
        self.id = id
        self.task = task

    def add(self, technology: Technology, command: str, comment: str = ""):
        self.append({
            "technology": technology,
            "command": command.strip(),
            "comment": comment.strip(),
        })

db = Database()

ways = db.add(
    title="Print multiple files with each file prepended by file name",
    id="each-file-with-header",
    task="Print all text files with .log extension in the current directory. Prepend each file with header containing filename.")
ways.add(
    technology=Awk,
    command=r"""awk '(FNR==1){ print ">> " FILENAME " <<"}1' *.log""",
    comment=r"""
    trailing 1 is shorthand for print current line since AWK prints line on true condition.
    Same rule as leaving regex at the end.
    """
)
ways.add(
    technology=Coreutils,
    command="head -n -0 *.log",
)
ways.add(
    technology=Coreutils,
    command="tail -n +1 *.log",
)
ways.add(
    technology=Coreutils,
    command="find . -name '*.log' -type f -print -exec cat {} ';'",
)
ways.add(
    technology=Perl,
    command="""perl -nE 'print ">>> $ARGV <<<\n" if $. == 1; print; close ARGV if eof' *.log""",
)
ways.add(
    technology=Python,
    command="""python -c 'import sys; [print(file, open(file).read(), sep="\n") for file in sys.argv[1:]]' *.log""",
)
ways.add(
    technology=Coreutils,
    command="more *.log | cat",
    comment="Needs to be piped to cat to avoid more interactive mode."
)
ways.add(
    technology=Tcl,
    command="""echo 'foreach f [lrange $::argv 1 end] { puts ">>> $f <<<"; puts [read [open $f]] }' | tclsh - *.log"""
)
ways.add(
    technology=Ruby,
    command="""ruby -e 'ARGV.each{|f| puts ">> #{f} <<"; puts IO.read(f)}' *.log""",
)
ways.add(
    technology=Shell,
    command="""sh -c 'for f in "$@"; do echo ">> $f <<"; cat "$f"; done' -- *.log""",
)

ways = db.add(
    title="Print multiple files with each line prepended by file name",
    id="each-line-with-filename",
    task="Print all text files with .log extension in the current directory. Prepend each line of each file with it's filename.")
ways.add(
    technology=Perl,
    command="""perl -nE 'print "$ARGV:"; print; close ARGV if eof' *.log""",
)

ways.add(technology=Awk, command="""awk '{ print FILENAME ":" $0 }' *.log""")
ways.add(technology=Coreutils, command="""grep "" *.log""")
ways.add(technology=Python,
        command="""python -c 'import sys; [print(file, line, sep=":", end="") for file in sys.argv[1:]] for line in open(file)' *.log""")

ways.add(technology=Ruby, command="""ruby -e 'ARGV.each{|f| IO.readlines(f).each{|l| puts "#{f}:#{l}"}' *.log""")

if __name__ == "__main__":
    db.generate_html()
