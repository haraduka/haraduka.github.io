#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

class MakeHTML:
    def __init__(self, bibtex_filename):
        self.bib = open(bibtex_filename, "r")
        self.ja_name = "河原塚" # no space
        self.en_name = "Kawaharazuka" # no space

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
                if "booktitle" in name:
                    self.current["booktitle"] = self.conference_name[content.upper()]
                    continue
                if "journal" in name:
                    self.current["booktitle"] = self.conference_name[content.upper()]
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

    def make_html(self, out_filename):
        out = open(out_filename, "w")

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
            line += ', ' + paper["booktitle"]
            if paper["volume"]:
                line += ", vol. " + paper["volume"]
            if paper["number"]:
                line += ", no. " + paper["number"]
            if paper["pages"]:
                line += ", pp. " + paper["pages"]
            if paper["year"]:
                line += ", " + paper["year"]

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
            line += ', in ' + paper["booktitle"]
            if paper["pages"]:
                line += ", pp. " + paper["pages"]
            if paper["year"]:
                line += ", " + paper["year"]

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
            line += ', in ' + paper["booktitle"]
            if paper["pages"]:
                line += ", pp. " + paper["pages"]
            if paper["year"]:
                line += ", " + paper["year"]

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
            line += ', in ' + paper["booktitle"]
            if paper["pages"]:
                line += ", " + paper["pages"]
            if paper["year"]:
                line += ", " + paper["year"]

            out.write("<li>"+line+"</li>")
        out.write('</ol>')

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
    makeHTML.make_html(args.out)

if __name__ == '__main__':
    main()
