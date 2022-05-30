#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


class MakeHTML:
    def __init__(self, bibtex_filename):
        self.bib = open(bibtex_filename, "r")
        self.ja_name = "河原塚"  # no space
        self.en_name = "Kawaharazuka"  # no space

        self.conference_name = {}
        self.state = None
        self.current = {}
        # keyはuniqであり, かつ包含関係があってはならない. aとabとかはダメ
        self.papers = {"ijournal_papers": [],
                       "djournal_papers": [],
                       "reviewed_iconference": [],
                       "reviewed_dconference": [],
                       "non_dconference": [],
                       "invited": []}

    def parse_bib(self):
        for line in self.bib:
            if line == "\n":
                continue
            if "@string" in line:
                name = line.split('{')[1].split(' ')[0]
                conference_name = line.split('"')[1]
                self.conference_name[name] = conference_name
                continue
            is_continue = False
            for k in self.papers.keys():
                if k in line:
                    is_continue = True
                    self.state = k
            if is_continue:
                continue

            if line == "}\n":
                self.papers[self.state].append(self.current)
                self.current = {}
            else:
                if "@" in line:
                    continue
                name = line.split("=")[0]
                content = line.split("=")[1].replace("{", "").replace("}", "").replace("\n", "")
                content = content[:-1] if content[-1] == ',' else content
                if "author" in name:
                    self.current["author"] = content.replace(" and", ",")
                    continue
                if ("title" in name) and (not ("booktitle" in name)):
                    self.current["title"] = content
                    continue
                if ("journal" in name) or ("booktitle" in name):
                    if content.upper() in self.conference_name:
                        self.current["booktitle"] = self.conference_name[content.upper()] + " (<b>" + content.upper() + "</b>)"
                        self.current["booktitle2"] = self.conference_name[content.upper()] + " (\\textit{\\textbf{" + content.upper() + "}})"
                    else:
                        self.current["booktitle"] = content
                        self.current["booktitle2"] = content
                    continue
                if "volume" in name:
                    self.current["volume"] = content
                    continue
                if "number" in name:
                    self.current["number"] = content
                    continue
                if "pages" in name:
                    self.current["pages"] = content.replace("--", "-")
                    continue
                if "year" in name:
                    self.current["year"] = content
                    continue
                if "award" in name:
                    if "award" not in self.current:
                        self.current["award"] = []
                    self.current["award"].append(content)
                    continue
                if "note" in name:
                    self.current["note"] = content
                    continue
                if "date" in name:
                    self.current["date"] = content
                    continue
                if "doi" in name:
                    self.current["doi"] = content
                    continue

    def make_pub(self):
        self.html_pub = ""

        self.html_award_list = []
        self.html_award = ""
        self.html_award += ('<ol>')

        self.tex_journal = ""

        self.tex_proceedings = ""

        papers = self.papers["ijournal_papers"]
        self.html_pub += ('<h3> International Journal Papers </h3>')
        self.html_pub += ('<ol>')
        self.tex_journal += '\\begin{enumerate}\n'
        for paper in papers:
            author = paper["author"].split(", ")
            author2 = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            for i, a in enumerate(author2):
                if self.en_name in a:
                    author2[i] = "\\underline{\\textbf{"+a+"}}"
                    break
            author_joined = ", ".join(author)
            author_joined2 = ", ".join(author2)
            line = author_joined
            line2 = author_joined2
            line += '<br>' + paper["title"]
            line2 += ": ``" + paper["title"] + "''"
            line += ', <i>' + paper["booktitle"] + '</i>'
            line2 += ", \\textit{" + paper["booktitle2"] + "}"
            if "volume" in paper:
                line += ", vol. " + paper["volume"]
                line2 += ", vol. " + paper["volume"]
            if "number" in paper:
                line += ", no. " + paper["number"]
                line2 += ", no. " + paper["number"]
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
                line2 += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
                line2 += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
                line2 += ", (\\textbf{" + paper["note"] + "})"
            if "doi" in paper:
                line += ", <a href=https://doi.org/" + paper["doi"] + " target='_blank'>Paper Link</a>"

            self.html_pub += ("<li>"+line+"</li>")
            self.tex_journal += ("\\item "+line2+"\n")
        self.html_pub += ('</ol>')
        self.tex_journal += '\\end{enumerate}\n'

        papers = self.papers["djournal_papers"]
        self.html_pub += ('<h3> Domestic Journal Papers </h3>')
        self.html_pub += ('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            line += ', <i>' + paper["booktitle"] + '</i>'
            if "volume" in paper:
                line += ", vol. " + paper["volume"]
            if "number" in paper:
                line += ", no. " + paper["number"]
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if "doi" in paper:
                line += ", <a href=https://doi.org/" + paper["doi"] + " target='_blank'>Paper Link</a>"

            self.html_pub += ("<li>"+line+"</li>")
        self.html_pub += ('</ol>')

        papers = self.papers["reviewed_iconference"]
        self.html_pub += ('<h3> International Conference Proceedings (Peer Reviewed) </h3>')
        self.html_pub += ('<ol>')
        self.tex_proceedings += '\\begin{enumerate}\n'
        for paper in papers:
            author = paper["author"].split(", ")
            author2 = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            for i, a in enumerate(author2):
                if self.en_name in a:
                    author2[i] = "\\underline{\\textbf{"+a+"}}"
                    break
            author_joined = ", ".join(author)
            author_joined2 = ", ".join(author2)
            line = author_joined
            line2 = author_joined2
            line += '<br>' + paper["title"]
            line2 += ": ``" + paper["title"] + "''"
            line += ', in <i>' + paper["booktitle"] + '</i>'
            line2 += ", \\textit{" + paper["booktitle2"] + "}"
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
                line2 += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
                line2 += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
                line2 += ", (\\textbf{" + paper["note"] + "})"
            if "doi" in paper:
                line += ", <a href=https://doi.org/" + paper["doi"] + " target='_blank'>Paper Link</a>"

            self.html_pub += ("<li>"+line+"</li>")
            self.tex_proceedings += ("\\item "+line2+"\n")
        self.html_pub += ('</ol>')
        self.tex_proceedings += '\\end{enumerate}\n'

        papers = self.papers["reviewed_dconference"]
        self.html_pub += ('<h3> Domestic Conference Proceedings (Peer Reviewed) </h3>')
        self.html_pub += ('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"

            self.html_pub += ("<li>"+line+"</li>")
        self.html_pub += ('</ol>')

        papers = self.papers["non_dconference"]
        self.html_pub += ('<h3> Domestic Conference Proceedings (No Reviewed) </h3>')
        self.html_pub += ('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "pages" in paper:
                line += ", " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if "doi" in paper:
                line += ", <a href=https://doi.org/" + paper["doi"] + " target='_blank'>Paper Link</a>"

            self.html_pub += ("<li>"+line+"</li>")
        self.html_pub += ('</ol>')

        papers = self.papers["invited"]
        self.html_pub += ('<h3> Invited Lecture, Commentary Articles, etc.</h3>')
        self.html_pub += ('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            if "note" in paper:
                line += ', ' + paper["note"]
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>'
                    self.html_award_list.append((paper["year"], html_award_tmp))
            if "date" in paper:
                line += ", " + paper["date"]

            self.html_pub += ("<li>"+line+"</li>")
        self.html_pub += ('</ol>')

        self.html_award_list.sort(reverse=True)
        for html_award_tmp in self.html_award_list:
            self.html_award += html_award_tmp[1]
        self.html_award += ('</ol>')

    def integrate_html(self, base_filename, out_filename):
        base = open(base_filename, "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("<!-- This file is automatically generated. Do not modify -->\n")
        for line in base:
            if "publication_replace_by_python" in line:
                lines.append(self.html_pub)
            if "award_replace_by_python" in line:
                lines.append(self.html_award)
            lines.append(line)
        out.writelines(lines)

    def integrate_tex(self, base_filename, out_filename):
        base = open(base_filename, "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("%This file is automatically generated. Do not modify\n")
        for line in base:
            if "journal_replace_by_python" in line:
                lines.append(self.tex_journal)
            if "proceedings_replace_by_python" in line:
                lines.append(self.tex_proceedings)
            lines.append(line)
        out.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        description="make_html_from_bib")
    parser.add_argument('--file', '-f', type=str, default="main.bib",
                        help='bibtex file')
    parser.add_argument('--base', '-b', type=str, default="base.html",
                        help='base html file')
    parser.add_argument('--cvbase', '-cb', type=str, default="cv/base.tex",
                        help='base cv tex file')
    parser.add_argument('--out', '-o', type=str, default="index.html",
                        help='output html file')
    parser.add_argument('--cvout', '-co', type=str, default="cv/main.tex",
                        help='output cv tex file')
    args = parser.parse_args()
    makeHTML = MakeHTML(args.file)
    makeHTML.parse_bib()
    makeHTML.make_pub()
    makeHTML.integrate_html(args.base, args.out)
    makeHTML.integrate_tex(args.cvbase, args.cvout)


if __name__ == '__main__':
    main()
