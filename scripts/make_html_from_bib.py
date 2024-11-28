#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
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
                       "reviewed_iconference": [],
                       "workshop_abstract": [],
                       "arxiv_papers": [],
                       "djournal_papers": [],
                       "reviewed_dconference": [],
                       "non_dconference": [],
                       "invited": []}

        self.project_template = """
          <div class='col-md-4 mb-4'>
            <a href='{website_url}' target='blank_' class='text-decoration-none'>
              <div class='card pt-3 pb-3 ps-3 pe-3 ' id='{card_name}'>
                <img class='card-img-top' alt='{card_title}'>
                <div class='card-body'>
                  <h5 class='card-title'>{card_title}</h5>
                  <p class='card-text'>{card_text}</p>
                </div>
              </div>
            </a>
          </div>

          <script>
            $(document).ready(function() {{
              setCardImage('#{card_name}', '{website_url}');
            }});
          </script>
        """

        self.video_template = """
        <div class="col-md-6 mb-4">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{video_title}</h5>
              <div class="embed-responsive embed-responsive-16by9" style="width: 100%; padding-bottom: 56.25%; position: relative;">
                <iframe class="embed-responsive-item" src="https://www.youtube.com/embed/{video_id}" allowfullscreen style="width: 100%; height: 100%; position: absolute; top: 0; left: 0;"></iframe>
              </div>
            </div>
          </div>
        </div>
        """

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
                if "@" in line[0]:
                    self.current["key"] = line.split('{')[1].split(',')[0]
                    continue
                name = line.split("=")[0]
                content = "=".join(line.split("=")[1:]).replace("{", "").replace("}", "").replace("\n", "")
                content = content[:-1] if content[-1] == ',' else content
                if "author" in name:
                    self.current["author"] = content.replace(" and", ",")
                    continue
                if ("title" in name) and (not ("booktitle" in name)):
                    self.current["title"] = content
                    continue
                if ("journal" in name) or ("booktitle" in name):
                    if content in self.conference_name:
                        self.current["booktitle"] = self.conference_name[content] + " (<b>" + content + "</b>)"
                        self.current["booktitle2"] = self.conference_name[content] + " (\\textit{\\textbf{" + content + "}})"
                        self.current["booktitle3"] = self.conference_name[content]
                    else:
                        self.current["booktitle"] = content
                        self.current["booktitle2"] = content
                        self.current["booktitle3"] = content
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
                if "award_personal" in name:
                    if "award_personal" not in self.current:
                        self.current["award_personal"] = []
                    self.current["award_personal"].append(content)
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
                if "arxiv" in name:
                    self.current["arxiv"] = content
                    continue
                if "website" in name:
                    self.current["website"] = content
                    continue
                if "code" in name:
                    self.current["code"] = content
                    continue
                if "slide" in name:
                    self.current["slide"] = content
                    continue
                if "video" in name:
                    self.current["video"] = content
                    continue
                if "howpublished" in name:
                    self.current["howpublished"] = content
                    continue
                if "robots" in name:
                    self.current["robots"] = content.split("+")
                    continue

    def make_pub(self):
        self.html_pub = ""

        self.html_award_list = []
        self.html_award = ""
        self.html_award += ('\n<ol>\n')

        self.projects_pub = ""
        self.videos_pub = ""
        robots_set = set()
        self.robots_pub = {}
        for papers in self.papers.values():
            for paper in papers:
                if "robots" in paper:
                    for robot in paper["robots"]:
                        robots_set.add(robot)
        print(robots_set)
        for robot in robots_set:
            self.robots_pub[robot] = ""

        self.tex_journal = ""

        self.tex_proceedings = ""

        self.csv_text = ""

        # International Journal Papers
        papers = self.papers["ijournal_papers"]
        self.html_pub += ('<h3> International Journal Papers </h3>')
        self.html_pub += ('\n<ol>\n')
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    if self.en_name in paper["author"].split(", ")[0]:
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
                line2 += ", (\\textbf{" + paper["note"] + "})"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
                self.projects_pub += self.project_template.format(
                        card_name=paper["key"],
                        card_title=paper["title"],
                        card_text=author_joined+"<br>"+paper["booktitle"],
                        website_url=paper["website"])
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"
                self.videos_pub += self.video_template.format(
                        video_title=paper["title"],
                        video_id=paper["video"].split("=")[1],
                        )
            if "robots" in paper:
                for robot in paper["robots"]:
                    self.robots_pub[robot] += "<li>"+line+"</li>\n"

            self.html_pub += ("<li>"+line+"</li>\n")
            self.tex_journal += ("\\item "+line2+"\n")

            csv_one_data = [
                    paper["doi"] if "doi" in paper else "-",
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["volume"] if "volume" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    paper["pages"] if "pages" in paper else "-",
                    "1", "0", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')
        self.tex_journal += '\\end{enumerate}\n'

        # International Conference Proceedings (Peer Reviewed)
        papers = self.papers["reviewed_iconference"]
        self.html_pub += ('<h3> International Conference Proceedings (Peer Reviewed) </h3>')
        self.html_pub += ('\n<ol>\n')
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    if self.en_name in paper["author"].split(", ")[0]:
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    line2 += ", \\textbf{\\textcolor{red}{"+award+"}}"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
                line2 += ", (\\textbf{" + paper["note"] + "})"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code"in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
                self.projects_pub += self.project_template.format(
                        card_name=paper["key"],
                        card_title=paper["title"],
                        card_text=author_joined+"<br>"+paper["booktitle"],
                        website_url=paper["website"])
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"
                self.videos_pub += self.video_template.format(
                        video_title=paper["title"],
                        video_id=paper["video"].split("=")[1],
                        )
            if "robots" in paper:
                for robot in paper["robots"]:
                    self.robots_pub[robot] += "<li>"+line+"</li>\n"

            self.html_pub += ("<li>"+line+"</li>\n")
            self.tex_proceedings += ("\\item "+line2+"\n")

            csv_one_data = [
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["year"] if "year" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    "0", "1"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')
        self.tex_proceedings += '\\end{enumerate}\n'

        # International Workshop, Extended Abstract, etc.
        papers = self.papers["workshop_abstract"]
        self.html_pub += ('<h3> International Workshop, Extended Abstract, etc. </h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    if self.en_name in paper["author"].split(", ")[0]:
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "note" in paper:
                            html_award_tmp += ", (<b>" + paper["note"] + "</b>)"
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "note" in paper:
                        html_award_tmp += ", (<b>" + paper["note"] + "</b>)"
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"

            self.html_pub += ("<li>"+line+"</li>\n")

            csv_one_data = [
                    paper["doi"] if "doi" in paper else "-",
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["volume"] if "volume" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    paper["pages"] if "pages" in paper else "-",
                    "1", "0", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')

        papers = self.papers["arxiv_papers"]
        self.html_pub += ('<h3> arXiv </h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if self.en_name in a:
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            if "howpublished" in paper:
                line += ", " + paper["howpublished"]
            if "year" in paper:
                line += ", " + paper["year"]
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
                self.projects_pub += self.project_template.format(
                        card_name=paper["key"],
                        card_title=paper["title"],
                        card_text=author_joined+"<br>"+"arXiv",
                        website_url=paper["website"])
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"
                self.videos_pub += self.video_template.format(
                        video_title=paper["title"],
                        video_id=paper["video"].split("=")[1],
                        )
            if "robots" in paper:
                for robot in paper["robots"]:
                    self.robots_pub[robot] += "<li>"+line+"</li>\n"

            self.html_pub += ("<li>"+line+"</li>\n")

        self.html_pub += ('</ol>\n')

        # Domestic Journal Papers
        papers = self.papers["djournal_papers"]
        self.html_pub += ('<h3> Domestic Journal Papers </h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if (self.ja_name in a) or (self.en_name in a):
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    if (self.ja_name in paper["author"].split(", ")[0]) or (self.en_name in paper["author"].split(", ")[0]):
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"

            self.html_pub += ("<li>"+line+"</li>\n")

            csv_one_data = [
                    paper["doi"] if "doi" in paper else "-",
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["volume"] if "volume" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    paper["pages"] if "pages" in paper else "-",
                    "1", "0", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')

        # Domestic Conference Proceedings
        papers = self.papers["reviewed_dconference"]
        self.html_pub += ('<h3> Domestic Conference Proceedings (Peer Reviewed) </h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if (self.ja_name in a) or (self.en_name in a):
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    if (self.ja_name in paper["author"].split(", ")[0]) or (self.en_name in paper["author"].split(", ")[0]):
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"

            self.html_pub += ("<li>"+line+"</li>\n")

            csv_one_data = [
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["year"] if "year" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    "0", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')

        # Domestic Conference Proceedings (No Reviewed)
        papers = self.papers["non_dconference"]
        self.html_pub += ('<h3> Domestic Conference Proceedings (No Reviewed) </h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if (self.ja_name in a) or (self.en_name in a):
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
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    if (self.ja_name in paper["author"].split(", ")[0]) or (self.en_name in paper["author"].split(", ")[0]):
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "note" in paper:
                line += ", (<b>" + paper["note"] + "</b>)"
            if ("doi" in paper) or ("arxiv" in paper) or ("website" in paper) or ("code" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "doi" in paper:
                line += " <a href=https://doi.org/" + paper["doi"] + " target='_blank'>[Paper Link]</a>"
            if "arxiv" in paper:
                line += " <a href=" + paper["arxiv"] + " target='_blank'>[Arxiv Link]</a>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Project Page]</a>"
            if "code" in paper:
                line += " <a href=" + paper["code"] + " target='_blank'>[Source Code]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"

            self.html_pub += ("<li>"+line+"</li>\n")

            csv_one_data = [
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["year"] if "year" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    "0", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')

        # Invited Talks, etc.
        papers = self.papers["invited"]
        self.html_pub += ('<h3> Invited Talks, etc.</h3>')
        self.html_pub += ('\n<ol>\n')
        for paper in papers:
            author = paper["author"].split(", ")
            for i, a in enumerate(author):
                if (self.ja_name in a) or (self.en_name in a):
                    author[i] = "<b><u>"+a+"</u></b>"
                    break
            author_joined = ", ".join(author)
            line = author_joined
            line += '<br>' + paper["title"]
            if "note" in paper:
                line += ', ' + paper["note"]
            line += ', in <i>' + paper["booktitle"] + '</i>'
            if "award_personal" in paper:
                for award in paper["award_personal"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    if (self.ja_name in paper["author"].split(", ")[0]) or (self.en_name in paper["author"].split(", ")[0]):
                        html_award_tmp = ("<li>" + author_joined.split(", ")[0] + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                        if "date" in paper:
                            html_award_tmp += (", " + paper["date"])
                        html_award_tmp += '</li>\n'
                        if "date" in paper:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                        else:
                            self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "award" in paper:
                for award in paper["award"]:
                    line += ", <b><font color='red'>"+award+"</font></b>"
                    html_award_tmp = ("<li>" + author_joined + "<br>" + award + ", <i>" + paper["booktitle"] + '</i>')
                    if "date" in paper:
                        html_award_tmp += (", " + paper["date"])
                    html_award_tmp += '</li>\n'
                    if "date" in paper:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y.%m.%d"), html_award_tmp))
                    else:
                        self.html_award_list.append((time.strptime(paper["date"], "%Y"), html_award_tmp))
            if "date" in paper:
                line += ", " + paper["date"]
            if ("website" in paper) or ("slide" in paper) or ("video" in paper):
                line += "<br>"
            if "website" in paper:
                line += " <a href=" + paper["website"] + " target='_blank'>[Website]</a>"
            if "slide" in paper:
                line += " <a href=" + paper["slide"] + " target='_blank'>[Slide]</a>"
            if "video" in paper:
                line += " <a href=" + paper["video"] + " target='_blank'>[Video]</a>"

            self.html_pub += ("<li>"+line+"</li>\n")

            csv_one_data = [
                    paper["author"],
                    paper["title"],
                    paper["booktitle3"],
                    paper["year"] if "year" in paper else "-",
                    paper["year"] if "year" in paper else "-",
                    "1", "0"
            ]
            csv_one_data = ['\"'+ data + '\"' for data in csv_one_data]
            self.csv_text += ",".join(csv_one_data) + "\n"
        self.html_pub += ('</ol>\n')

        self.html_award_list.sort(reverse=True)
        for html_award_tmp in self.html_award_list:
            self.html_award += html_award_tmp[1]
        self.html_award += ('</ol>\n')

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

    def integrate_projects_html(self, base_filename, out_filename):
        base = open(base_filename, "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("<!-- This file is automatically generated. Do not modify -->\n")
        for line in base:
            if "projects_replace_by_python" in line:
                lines.append(self.projects_pub)
            lines.append(line)
        out.writelines(lines)

    def integrate_robots_html(self, base_filename, out_filename):
        base = open(base_filename, "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("<!-- This file is automatically generated. Do not modify -->\n")
        for line in base:
            matches = re.findall(r'\s*<!--\s*([^>]+)_replace_by_python\s*-->\s*', line)
            if len(matches) > 0:
                robot = matches[0]
                lines.append(self.robots_pub[robot])
            lines.append(line)
        out.writelines(lines)

    def integrate_videos_html(self, base_filename, out_filename):
        base = open(base_filename, "r")
        out = open(out_filename, "w")
        lines = []
        lines.append("<!-- This file is automatically generated. Do not modify -->\n")
        for line in base:
            if "videos_replace_by_python" in line:
                lines.append(self.videos_pub)
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

    def integrate_csv(self, out_filename):
        out = open(out_filename, "w", encoding="utf8")
        lines = []
        lines.append("%This file is automatically generated. Do not modify\n")
        lines.append(self.csv_text)
        out.writelines(lines)


def main():
    parser = argparse.ArgumentParser(
        description="make_html_from_bib")
    parser.add_argument('--file', '-f', type=str, default="main.bib",
                        help='bibtex file')
    parser.add_argument('--base', '-b', type=str, default="base.html",
                        help='base html file')
    parser.add_argument('--projects_base', type=str, default="projects_base.html",
                        help='projects base html file')
    parser.add_argument('--robots_base', type=str, default="robots_base.html",
                        help='robots base html file')
    parser.add_argument('--videos_base', type=str, default="videos_base.html",
                        help='videos base html file')
    parser.add_argument('--cvbase', '-cb', type=str, default="cv/base.tex",
                        help='base cv tex file')
    parser.add_argument('--out', '-o', type=str, default="index.html",
                        help='output html file')
    parser.add_argument('--projects_out', type=str, default="projects.html",
                        help='projects output html file')
    parser.add_argument('--robots_out', type=str, default="robots.html",
                        help='robots output html file')
    parser.add_argument('--videos_out', type=str, default="videos.html",
                        help='videos output html file')
    parser.add_argument('--cvout', '-co', type=str, default="cv/main.tex",
                        help='output cv tex file')
    parser.add_argument('--csvout', '-csvo', type=str, default="main.csv",
                        help='output csv tex file')
    args = parser.parse_args()
    makeHTML = MakeHTML(args.file)
    makeHTML.parse_bib()
    makeHTML.make_pub()
    makeHTML.integrate_html(args.base, args.out)
    makeHTML.integrate_projects_html(args.projects_base, args.projects_out)
    makeHTML.integrate_robots_html(args.robots_base, args.robots_out)
    makeHTML.integrate_videos_html(args.videos_base, args.videos_out)
    makeHTML.integrate_tex(args.cvbase, args.cvout)
    makeHTML.integrate_csv(args.csvout)


if __name__ == '__main__':
    main()
