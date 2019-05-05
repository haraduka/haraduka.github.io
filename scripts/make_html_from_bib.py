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
        self.papers = {"journal_papers": [],
                       "reviewed_iconference": [],
                       "reviewed_dconference": [],
                       "non_dconference": []}

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
                content = line.split("=")[1].replace("{", "").replace("}", "").replace("\n", "").replace(",", "")
                if "author" in name:
                    self.current["author"] = content.replace(" and", ",")
                    continue
                if ("title" in name) and (not ("booktitle" in name)):
                    self.current["title"] = content
                    continue
                if ("journal" in name) or ("booktitle" in name):
                    self.current["booktitle"] = self.conference_name[content.upper()] + " (" + content.upper() + ")"
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

    def make_pub(self):
        out = open("publication.html", "w")

        aout = open("award.html", "w")
        aout.write('<ol>')

        papers = self.papers["journal_papers"]
        out.write('<h3> Journal Papers </h3>')
        out.write('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += ', "' + paper["title"] + '"'
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
                    line += ", <b>"+award+"</b>"
                    aout.write("<li>" + author_joined + ", <b>" + award +
                               "</b>, <i>" + paper["booktitle"] + '</i> </li>')
            if "note" in paper:
                line += ", (" + paper["note"] + ")"

            out.write("<li>"+line+"</li>")
        out.write('</ol>')

        papers = self.papers["reviewed_iconference"]
        out.write('<h3> International Conference Proceedings (Peer Reviewed) </h3>')
        out.write('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += ', "' + paper["title"] + '"'
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b>"+award+"</b>"
                    aout.write("<li>" + author_joined + ", <b>" + award +
                               "</b>, <i>" + paper["booktitle"] + '</i> </li>')
            if "note" in paper:
                line += ", (" + paper["note"] + ")"

            out.write("<li>"+line+"</li>")
        out.write('</ol>')

        papers = self.papers["reviewed_dconference"]
        out.write('<h3> Domestic Conference Proceedings (Peer Reviewed) </h3>')
        out.write('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += ', "' + paper["title"] + '"'
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "pages" in paper:
                line += ", pp. " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b>"+award+"</b>"
                    aout.write("<li>" + author_joined + ", <b>" + award +
                               "</b>, <i>" + paper["booktitle"] + '</i> </li>')
            if "note" in paper:
                line += ", (" + paper["note"] + ")"

            out.write("<li>"+line+"</li>")
        out.write('</ol>')

        papers = self.papers["non_dconference"]
        out.write('<h3> Domestic Conference Proceedings (No Reviewed) </h3>')
        out.write('<ol>')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.ja_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += ', "' + paper["title"] + '"'
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "pages" in paper:
                line += ", " + paper["pages"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b>"+award+"</b>"
                    aout.write("<li>" + author_joined + ", <b>" + award +
                               "</b>, <i>" + paper["booktitle"] + '</i> </li>')
            if "note" in paper:
                line += ", (" + paper["note"] + ")"

            out.write("<li>"+line+"</li>")
        out.write('</ol>')

        aout.write('</ol>')

    def integrate_html(self, base_filename, out_filename):
        base = open(base_filename, "r")
        pub = open("publication.html", "r")
        award = open("award.html", "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("<!-- This file is automatically generated. Do not modify -->\n")
        for line in base:
            if "publication_replace_by_python" in line:
                for publine in pub:
                    lines.append(publine)
            if "award_replace_by_python" in line:
                for awardline in award:
                    lines.append(awardline)
            lines.append(line)
        out.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        description="make_html_from_bib")
    parser.add_argument('--file', '-f', type=str, default="main.bib",
                        help='bibtex file')
    parser.add_argument('--base', '-b', type=str, default="base.html",
                        help='base html file')
    parser.add_argument('--out', '-o', type=str, default="publication.html",
                        help='output html file')
    args = parser.parse_args()
    makeHTML = MakeHTML(args.file)
    makeHTML.parse_bib()
    makeHTML.make_pub()
    makeHTML.integrate_html(args.base, args.out)


if __name__ == '__main__':
    main()
